"""link admin_users to members, drop members.is_officer

Revision ID: e7d9a0f1c642
Revises: c4e2a1f0b9d7
Create Date: 2026-04-17 00:00:00.000001

"""
from alembic import op
import sqlalchemy as sa


revision = 'e7d9a0f1c642'
down_revision = 'c4e2a1f0b9d7'
branch_labels = None
depends_on = None


def upgrade():
    # 1) Add admin_users.member_id (nullable for backfill)
    with op.batch_alter_table('admin_users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('member_id', sa.Integer(), nullable=True))

    # 2) Backfill member_id by email match (case-insensitive).
    # If multiple members share an email, pick the most recent (joined_on DESC, id DESC).
    op.execute(sa.text("""
        UPDATE admin_users AS a
        SET member_id = m.id
        FROM (
            SELECT DISTINCT ON (LOWER(email)) id, email
            FROM members
            ORDER BY LOWER(email), joined_on DESC, id DESC
        ) AS m
        WHERE LOWER(a.email) = LOWER(m.email)
    """))

    # 3) Enforce NOT NULL, FK, and UNIQUE. The NOT NULL step will fail if any
    # admin_users row has no matching member — resolve by inserting the missing
    # member or removing the orphaned admin row, then re-run.
    with op.batch_alter_table('admin_users', schema=None) as batch_op:
        batch_op.alter_column('member_id', nullable=False)
        batch_op.create_foreign_key(
            'fk_admin_users_member_id_members', 'members', ['member_id'], ['id']
        )
        batch_op.create_unique_constraint('uq_admin_users_member_id', ['member_id'])

    # 4) Drop members.is_officer (superseded by admin_users.member_id presence)
    with op.batch_alter_table('members', schema=None) as batch_op:
        batch_op.drop_column('is_officer')


def downgrade():
    with op.batch_alter_table('members', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('is_officer', sa.Boolean(), nullable=False, server_default=sa.false())
        )
        batch_op.alter_column('is_officer', server_default=None)

    with op.batch_alter_table('admin_users', schema=None) as batch_op:
        batch_op.drop_constraint('uq_admin_users_member_id', type_='unique')
        batch_op.drop_constraint('fk_admin_users_member_id_members', type_='foreignkey')
        batch_op.drop_column('member_id')
