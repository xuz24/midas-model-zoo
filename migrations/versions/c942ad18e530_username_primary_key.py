"""Use username as the users primary key.

Revision ID: c942ad18e530
Revises: a83f20d74b91
"""
from alembic import op
import sqlalchemy as sa

revision = 'c942ad18e530'
down_revision = 'a83f20d74b91'
branch_labels = None
depends_on = None

NAMING = {"pk": "pk_%(table_name)s"}


def upgrade():
    connection = op.get_bind()
    if connection.execute(sa.text('SELECT count(*) FROM users WHERE username IS NULL')).scalar():
        raise RuntimeError('All existing users must choose a username before this migration.')
    pk_name = sa.inspect(connection).get_pk_constraint('users')['name'] or 'pk_users'
    with op.batch_alter_table('users', naming_convention=NAMING, recreate='always') as batch:
        batch.drop_constraint(pk_name, type_='primary')
        batch.drop_constraint('uq_users_username', type_='unique')
        batch.drop_column('id')
        batch.alter_column('username', existing_type=sa.String(30), nullable=False)
        batch.create_primary_key('pk_users', ['username'])


def downgrade():
    # Recreate integer identifiers; the original numeric IDs cannot be recovered.
    op.add_column('users', sa.Column('id', sa.Integer(), nullable=True))
    connection = op.get_bind()
    usernames = connection.execute(sa.text('SELECT username FROM users ORDER BY username')).scalars().all()
    for identifier, username in enumerate(usernames, start=1):
        connection.execute(sa.text('UPDATE users SET id = :id WHERE username = :username'),
                           {'id': identifier, 'username': username})
    with op.batch_alter_table('users', naming_convention=NAMING, recreate='always') as batch:
        batch.drop_constraint('pk_users', type_='primary')
        batch.alter_column('id', existing_type=sa.Integer(), nullable=False)
        batch.alter_column('username', existing_type=sa.String(30), nullable=True)
        batch.create_primary_key('pk_users', ['id'])
        batch.create_unique_constraint('uq_users_username', ['username'])
