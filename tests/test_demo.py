from pathlib import Path
from types import SimpleNamespace
import os
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from backend.app import app
from backend.app.db_models import User
from backend.app.demo import seed_researchers
from backend.app.records import KINDS, load_records, researcher_records


class DemoTests(unittest.TestCase):
    def test_seed_is_repeatable_and_preserves_existing_profiles(self):
        engine = create_engine('sqlite:///:memory:')
        self.addCleanup(engine.dispose)
        User.__table__.create(engine)
        with Session(engine) as session:
            session.add(User(username='demo_maya', google_sub='real-sub', name='Existing account'))
            session.add(User(username='real_researcher', google_sub='another-sub', name='Real researcher'))
            session.commit()
            self.assertEqual(seed_researchers(session), 5)
            self.assertEqual(seed_researchers(session), 0)
            self.assertEqual(session.get(User, 'demo_maya').name, 'Existing account')
            self.assertEqual(session.get(User, 'real_researcher').name, 'Real researcher')
            priya = session.get(User, 'demo_priya')
            self.assertEqual(priya.google_sub, 'demo:demo_priya')
            self.assertIsNone(priya.email)
            self.assertEqual(priya.created_at.year, 2026)

    def test_fresh_checkout_migrates_without_env_or_google_credentials(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as folder:
            env = dict(os.environ, DATABASE_URL=f'sqlite:///{folder}/demo.db', DEMO_DATA='1',
                       FLASK_SECRET_KEY='', GOOGLE_CLIENT_ID='', PYTHON_DOTENV_DISABLED='1')
            for expected in (6, 0):
                result = subprocess.run(
                    [str(root / '.venv/bin/python'), '-m', 'flask', '--app', 'backend.app', 'prepare-demo'],
                    cwd=root, env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn(f'added {expected} fictional', result.stdout)

    def test_seeded_directory_profiles_filters_and_linked_records(self):
        engine = create_engine('sqlite:///:memory:')
        self.addCleanup(engine.dispose)
        User.__table__.create(engine)
        with Session(engine) as session, patch('backend.app.users.db', SimpleNamespace(select=select, session=session)):
            seed_researchers(session)
            # Use the actual routes/templates with an isolated database.
            client = app.test_client()
            html = client.get('/users?tag=Climate+science&role=Professor').get_data(as_text=True)
            self.assertIn('href="/user/demo_maya"', html)
            self.assertNotIn('href="/user/demo_priya"', html)
            html = client.get('/users?sort=joined').get_data(as_text=True)
            self.assertLess(html.index('href="/user/demo_taylor"'), html.index('href="/user/demo_maya"'))
            html = client.get('/user/demo_priya').get_data(as_text=True)
            for kind in KINDS:
                self.assertIn(f'href="/{kind}/demo-', html)
            self.assertNotIn('Edit profile', html)
            for kind in KINDS:
                for record in load_records(kind):
                    if record['id'].startswith('demo-'):
                        self.assertEqual(client.get(f"/{kind}/{record['id']}").status_code, 200)
            self.assertEqual(len(researcher_records('demo_priya')), 4)

    def test_disabled_startup_does_not_touch_database(self):
        with patch.dict(os.environ, DEMO_DATA='0'), patch('backend.app.demo.upgrade') as upgrade:
            result = app.test_cli_runner().invoke(args=['prepare-demo'])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIn('disabled', result.output)
            upgrade.assert_not_called()
