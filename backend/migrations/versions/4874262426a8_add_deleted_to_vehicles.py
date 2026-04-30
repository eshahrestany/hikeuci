"""add deleted to vehicles

Revision ID: 4874262426a8
Revises: b1c2d3e4f5a6
Create Date: 2026-04-30 13:33:54.138769

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4874262426a8'
down_revision = 'b1c2d3e4f5a6'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('vehicles', schema=None) as batch_op:
        batch_op.add_column(sa.Column('deleted', sa.Boolean(), server_default='false', nullable=False))


def downgrade():
    with op.batch_alter_table('vehicles', schema=None) as batch_op:
        batch_op.drop_column('deleted')
