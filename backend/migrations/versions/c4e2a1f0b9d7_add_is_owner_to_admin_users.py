"""add is_owner to admin_users

Revision ID: c4e2a1f0b9d7
Revises: 020c14b054b6
Create Date: 2026-04-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'c4e2a1f0b9d7'
down_revision = '020c14b054b6'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('admin_users', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('is_owner', sa.Boolean(), nullable=False, server_default=sa.false())
        )
        batch_op.alter_column('is_owner', server_default=None)

    op.create_index(
        'ix_admin_users_single_owner',
        'admin_users',
        ['is_owner'],
        unique=True,
        postgresql_where=sa.text('is_owner IS TRUE'),
    )


def downgrade():
    op.drop_index('ix_admin_users_single_owner', table_name='admin_users')
    with op.batch_alter_table('admin_users', schema=None) as batch_op:
        batch_op.drop_column('is_owner')
