import time
from datetime import datetime
from html import escape as _html_escape
from typing import List
from make_celery import celery_app
from flask import current_app

from . import db
from .models import EmailCampaign, EmailTask, Member, MagicLink, Trail, Signup, Hike
from .lib.emails import EmailConnection
from .lib.email_templates import render_phase_email


def start_email_campaign(hike_id: int) -> int:
    """
    Create a new email campaign based on the provided hike's phase,
    clear & repopulate EmailTask with one row per member,
    clear previous MagicLinks, and pre-generate a MagicLink for each member.
    Finally, enqueue the Celery batch sender.
    """
    # 0) Safety checks
    hike = Hike.query.get(hike_id)
    if hike.status != "active":
        raise RuntimeError("Can only start email campaigns for active hikes")
    phase = hike.phase
    if hike.email_campaign_completed:
        raise RuntimeError(f"{phase} phase email campaign already completed for this hike")

    # 1) Create campaign
    campaign = EmailCampaign(type=phase, date_created=datetime.now())
    db.session.add(campaign)
    db.session.commit()

    # 2) Clear prior tasks
    EmailTask.query.delete()
    db.session.commit()

    # 3) Populate tasks from all members
    mlm = current_app.extensions.get("magic_link_manager")
    if mlm is None:
        raise RuntimeError("MagicLinkManager is not initialized")

    if phase in ("voting", "signup"):
        members: List[Member] = Member.query.all()
    else:
        # send waivers only to confirmed hikers
        members: List[Member] = (
            Member.query
            .join(Signup, Signup.member_id == Member.id)
            .filter(Signup.hike_id == hike_id, Signup.status == "confirmed")
            .distinct()
            .all()
        )

    tasks: List[EmailTask] = []

    for m in members:
        to_email = getattr(m, "email", None)
        if not to_email:
            continue

        # create token + row in MagicLink table
        token = mlm.generate(user_id=m.id, hike_id=hike_id, phase=phase)
        ml = MagicLink.query.filter_by(token=token).first()

        tasks.append(
            EmailTask(
                campaign_id=campaign.id,
                member_id=m.id,
                magic_link_id=ml.id if ml else None,
                status="pending",
                attempts=0,
                sent_at=None,
            )
        )

    if tasks:
        db.session.add_all(tasks)
        db.session.commit()

    # 4) Kick off Celery
    batch_send_emails.delay(campaign_id=campaign.id, hike_id=hike_id)
    return campaign.id



@celery_app.task(name="app.tasks.batch_send_emails")
def batch_send_emails(*, campaign_id: int, hike_id: int) -> dict:
    """
    Process pending EmailTask rows for this campaign in batches.
    Opens one SMTP connection per batch via EmailConnection.connect()
    and personalizes each message using the pre-generated magic link.
    Sends up to MAIL_BATCH_SIZE emails per batch, then pauses for MAIL_BATCH_PAUSE_SEC.
    Retries up to MAIL_MAX_ATTEMPTS per recipient.
    """
    cfg = current_app.config
    batch_size = int(cfg.get("MAIL_BATCH_SIZE", 50))
    max_attempts = int(cfg.get("MAIL_MAX_ATTEMPTS", 3))
    batch_pause_sec = float(cfg.get("MAIL_BATCH_PAUSE_SEC", 0.0))

    sent_total = failed_total = 0
    conn = EmailConnection()

    while True:
        batch: List[EmailTask] = (
            EmailTask.query
            .filter_by(campaign_id=campaign_id, status="pending")
            .order_by(EmailTask.id.asc())
            .limit(batch_size)
            .all()
        )
        if not batch:
            break

        with conn.connect() as server:
            for email_task in batch:
                member = Member.query.get(email_task.member_id)
                ml = MagicLink.query.get(email_task.magic_link_id)

                # Derive per-recipient context
                name = getattr(member, "name", None)
                to_email = getattr(member, "email", None)
                base_url = current_app.config.get("BASE_URL", "").rstrip("/")
                magic_url = f"{base_url}/vote?token={quote_plus(ml.token)}"  # change path per phase if needed

                # Trails list (compute once per batch if static)
                trail_options = Trail.query.filter_by(is_active_vote_candidate=True).all()
                trails = [{"name": t.name,
                           "difficulty": current_app.config["DIFFICULTY_INDEX"][t.difficulty]}
                          for t in trail_options]

                # Render from templates
                subj, text_body, html_body = render_phase_email(
                    phase,
                    name=name,
                    magic_url=magic_url,
                    trails=trails,
                    hike=hike,
                    member=member,
                )

                # send the email
                result = conn.send(to_email, subj, text_body, html_body)
                email_task.attempts += 1

                if result:
                    email_task.status = "sent"
                    email_task.sent_at = datetime.now()
                    db.session.commit()
                    sent_total += 1
                else:
                    if email_task.attempts >= max_attempts:
                        email_task.status = "failed"
                    db.session.commit()
                    failed_total += 1
                    current_app.logger.exception(
                        "Vote email send failed for member_id=%s (attempt %s/%s)",
                        member_id, email_task.attempts, max_attempts
                    )

        if batch_pause_sec > 0:
            time.sleep(batch_pause_sec)

    camp = EmailCampaign.query.get(campaign_id)
    if camp:
        camp.date_completed = datetime.now()
        db.session.commit()

    return {"campaign_id": campaign_id, "sent": sent_total, "failed": failed_total}
