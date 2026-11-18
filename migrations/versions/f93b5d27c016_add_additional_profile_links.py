"""Support additional labeled profile links.

Revision ID: f93b5d27c016
Revises: e82a4c16b905
"""
from alembic import op
import sqlalchemy as sa

revision = 'f93b5d27c016'
down_revision = 'e82a4c16b905'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('additional_links', sa.JSON(), nullable=True))


def downgrade():
    with op.batch_alter_table('users') as batch:
        batch.drop_column('additional_links')
