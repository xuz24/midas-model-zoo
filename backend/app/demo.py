"""Prepare the local demo from versioned fixtures, preserving existing accounts."""
from datetime import datetime
import os
from pathlib import Path

import click
from flask.cli import with_appcontext
from flask_migrate import upgrade
import yaml

from .database import db
from .db_models import User
from .profile_links import PROFILE_LINK_FIELDS

ROOT = Path(__file__).resolve().parents[2]
DEMO_USERS = ROOT / "demo" / "researchers.yaml"


def seed_researchers(session, refresh_links=False):
    entries = yaml.safe_load(DEMO_USERS.read_text(encoding="utf-8"))
    added = 0
    for entry in entries:
        # Fixture identities can never match a Google account's numeric subject.
        subject = f"demo:{entry['username']}"
        existing = session.get(User, entry['username'])
        if existing is not None:
            if refresh_links and existing.google_sub == subject:
                for field in [name for name, _, _ in PROFILE_LINK_FIELDS] + ['additional_links']:
                    setattr(existing, field, entry.get(field))
                existing.other_url = ''
            continue
        if session.scalar(db.select(User).filter_by(google_sub=subject)) is not None:
            continue
        fields = dict(entry)
        fields['created_at'] = datetime.fromisoformat(str(fields['created_at']))
        session.add(User(google_sub=subject, **fields))
        added += 1
    session.commit()
    return added


@click.command("prepare-demo")
@click.option('--refresh-links', is_flag=True, help='Refresh links on existing fictional demo accounts.')
@with_appcontext
def prepare_demo(refresh_links=False):
    """Apply migrations and seed fictional researchers for the local demo."""
    if os.environ.get("DEMO_DATA", "1").lower() in {"0", "false", "no"}:
        click.echo("Demo data disabled (DEMO_DATA=0).")
        return
    upgrade(directory=str(ROOT / "migrations"))
    added = seed_researchers(db.session, refresh_links=refresh_links)
    click.echo(f"Demo ready: added {added} fictional researcher profiles.")
    if refresh_links:
        click.echo('Refreshed placeholder links on fictional demo accounts.')
