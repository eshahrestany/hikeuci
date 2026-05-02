"""
Helper for recording manually-triggered individual email sends.

All officer-initiated sends (resend, late signup, transport bump) call
`create_manual_task` before dispatching the Celery task. This creates (or
reuses) a single "manual" EmailCampaign per hike and inserts an EmailTask
row so the send appears in the Emails dashboard and member email history.
"""

from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError

from .. import db
from ..models import EmailCampaign, EmailTask


def create_manual_task(hike_id: int, member_id: int, email_type: str) -> EmailTask:
    campaign = EmailCampaign.query.filter_by(hike_id=hike_id, type="manual").first()
    if not campaign:
        campaign = EmailCampaign(
            hike_id=hike_id,
            type="manual",
            date_created=datetime.now(timezone.utc),
        )
        db.session.add(campaign)
        try:
            db.session.flush()
        except IntegrityError:
            db.session.rollback()
            campaign = EmailCampaign.query.filter_by(hike_id=hike_id, type="manual").first()

    task = EmailTask(
        campaign_id=campaign.id,
        member_id=member_id,
        email_type=email_type,
        status="pending",
        attempts=0,
    )
    db.session.add(task)
    db.session.commit()
    return task
