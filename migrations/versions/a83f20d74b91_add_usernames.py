"""Add unique usernames for public profiles.

Revision ID: a83f20d74b91
Revises: 6923c1e17e1d
"""
from alembic import op
import sqlalchemy as sa

revision = 'a83f20d74b91'
down_revision = '6923c1e17e1d'
branch_labels = None
depends_on = None


def upgrade():
    # Google accounts exist before the user completes profile setup.
    with op.batch_alter_table('users') as batch:
        batch.add_column(sa.Column('username', sa.String(30), nullable=True))
        batch.create_unique_constraint('uq_users_username', ['username'])


def downgrade():
    with op.batch_alter_table('users') as batch:
        batch.drop_constraint('uq_users_username', type_='unique')
        batch.drop_column('username')
