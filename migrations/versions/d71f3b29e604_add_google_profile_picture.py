"""Store Google profile picture URLs.

Revision ID: d71f3b29e604
Revises: c942ad18e530
"""
from alembic import op
import sqlalchemy as sa

revision = 'd71f3b29e604'
down_revision = 'c942ad18e530'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('picture_url', sa.String(2048), nullable=True))


def downgrade():
    with op.batch_alter_table('users') as batch:
        batch.drop_column('picture_url')
