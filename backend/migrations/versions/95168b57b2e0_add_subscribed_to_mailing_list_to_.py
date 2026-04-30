"""add subscribed_to_mailing_list to members

Revision ID: 95168b57b2e0
Revises: e7d9a0f1c642
Create Date: 2026-04-30 06:56:34.985834

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '95168b57b2e0'
down_revision = 'e7d9a0f1c642'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('members', schema=None) as batch_op:
        batch_op.add_column(sa.Column('subscribed_to_mailing_list', sa.Boolean(), nullable=False, server_default=sa.true()))


def downgrade():
    with op.batch_alter_table('members', schema=None) as batch_op:
        batch_op.drop_column('subscribed_to_mailing_list')
