"""add elevation_gain_ft to trails

Revision ID: 8352b170c422
Revises: 4874262426a8
Create Date: 2026-05-02 02:19:54.847443

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8352b170c422'
down_revision = '4874262426a8'
branch_labels = None
depends_on = None

_METERS_TO_FEET = 3.28084
_NOISE_THRESHOLD_M = 1.0


def _calc_gain_ft(points: list) -> float:
    gain_m = 0.0
    for i in range(1, len(points)):
        delta = points[i]["ele"] - points[i - 1]["ele"]
        if delta > _NOISE_THRESHOLD_M:
            gain_m += delta
    return round(gain_m * _METERS_TO_FEET, 1)


def upgrade():
    with op.batch_alter_table('trails', schema=None) as batch_op:
        batch_op.add_column(sa.Column('elevation_gain_ft', sa.Float(), nullable=True))

    # Backfill all trails that already have elevation data
    conn = op.get_bind()
    rows = conn.execute(
        sa.text("SELECT id, elevation_data FROM trails WHERE elevation_data IS NOT NULL")
    ).fetchall()

    for row in rows:
        points = row.elevation_data  # already deserialized by psycopg2
        if isinstance(points, list) and len(points) > 1:
            gain = _calc_gain_ft(points)
            conn.execute(
                sa.text("UPDATE trails SET elevation_gain_ft = :gain WHERE id = :id"),
                {"gain": gain, "id": row.id},
            )


def downgrade():
    with op.batch_alter_table('trails', schema=None) as batch_op:
        batch_op.drop_column('elevation_gain_ft')
