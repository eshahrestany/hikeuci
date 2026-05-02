"""unique constraint on email_campaign hike_id type

Revision ID: d8f1a2b3c4e5
Revises: 8352b170c422
Create Date: 2026-05-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd8f1a2b3c4e5'
down_revision = '8352b170c422'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('email_campaigns', schema=None) as batch_op:
        batch_op.create_unique_constraint(
            'uq_email_campaigns_hike_id_type', ['hike_id', 'type']
        )


def downgrade():
    with op.batch_alter_table('email_campaigns', schema=None) as batch_op:
        batch_op.drop_constraint('uq_email_campaigns_hike_id_type', type_='unique')
