"""Add optional public profile links.

Revision ID: e82a4c16b905
Revises: d71f3b29e604
"""
from alembic import op
import sqlalchemy as sa

revision = 'e82a4c16b905'
down_revision = 'd71f3b29e604'
branch_labels = None
depends_on = None

columns = ('github_url', 'google_scholar_url', 'researchgate_url',
           'orcid_url', 'website_url', 'other_url')


def upgrade():
    for name in columns:
        op.add_column('users', sa.Column(name, sa.String(2048), nullable=True))


def downgrade():
    with op.batch_alter_table('users') as batch:
        for name in reversed(columns):
            batch.drop_column(name)
