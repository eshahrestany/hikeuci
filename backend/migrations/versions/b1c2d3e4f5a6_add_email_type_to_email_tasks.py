"""add email_type to email_tasks

Revision ID: b1c2d3e4f5a6
Revises: 95168b57b2e0
Create Date: 2026-04-28 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'b1c2d3e4f5a6'
down_revision = '95168b57b2e0'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('email_tasks', sa.Column('email_type', sa.String(50), nullable=True))


def downgrade():
    op.drop_column('email_tasks', 'email_type')
