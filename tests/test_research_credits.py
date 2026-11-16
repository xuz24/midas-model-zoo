from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yaml

from backend.app import app
from backend.app.db_models import User
from backend.app.records import KINDS, load_records, researcher_records


class ResearchCreditTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        for kind in KINDS:
            (self.root / kind).mkdir()
        records = patch('backend.app.records.RECORDS_ROOT', self.root)
        records.start()
        self.addCleanup(records.stop)
        self.client = app.test_client()

    def write_record(self, kind, record_id, authors, updated='2026-11-15'):
        record = dict(id=record_id, summary='Research summary.', authors=authors,
                      last_updated=updated)
        record['title' if kind == 'papers' else 'name'] = record_id
        (self.root / kind / f'{record_id}.yaml').write_text(yaml.safe_dump(record))

    def test_profiles_show_explicit_credits_across_all_catalogs(self):
        for kind in KINDS:
            self.write_record(kind, f'{kind}-credited', ['Named Author', '@ALICE', '@alice', '@bob'])
            self.write_record(kind, f'{kind}-unrelated', ['Alice', 'alice', '@alice_other'])
        alice = User(username='alice', google_sub='alice-sub', email='private@example.org')
        with patch('backend.app.users.db.session.get', return_value=alice):
            response = self.client.get('/user/alice')
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        for kind in KINDS:
            self.assertEqual(html.count(f'href="/{kind}/{kind}-credited"'), 1)
            self.assertNotIn(f'{kind}-unrelated', html)
        self.assertNotIn('private@example.org', html)
        self.assertEqual(len(researcher_records('bob')), 4)
        self.assertEqual(researcher_records('ali'), [])

    def test_record_links_and_live_profile_updates(self):
        self.write_record('models', 'example', ['Named Author', '@ALICE'])
        response = self.client.get('/models/example')
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn('href="/user/alice">@alice</a>', html)
        self.assertIn('Named Author', html)
        self.write_record('models', 'older', ['@alice'], '2026-11-01')
        self.assertEqual([r['title'] for r in researcher_records('alice')[0]['records']], ['example', 'older'])
        self.write_record('models', 'example', ['@bob'])
        self.assertEqual([r['title'] for r in researcher_records('alice')[0]['records']], ['older'])

    def test_invalid_username_credits_are_rejected(self):
        for authors in ('@alice', ['@../../alice'], ['@ab'], ['@alice@example.org'], ['@<script>']):
            with self.subTest(authors=authors):
                self.write_record('models', 'example', authors)
                with self.assertRaisesRegex(ValueError, 'example.yaml'):
                    load_records('models')

    def test_empty_profile_explains_username_credits_to_owner(self):
        alice = User(username='alice', google_sub='alice-sub')
        with self.client.session_transaction() as session:
            session['username'] = 'alice'
        with patch('backend.app.users.db.session.get', return_value=alice):
            html = self.client.get('/user/alice').get_data(as_text=True)
        self.assertIn('Research that credits @alice will appear here.', html)
