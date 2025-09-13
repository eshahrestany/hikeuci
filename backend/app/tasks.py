import time
from datetime import datetime
from typing import List
from make_celery import celery_app
from flask import current_app
from . import db
from .models import EmailCampaign, EmailTask, Member, MagicLink, Trail, Signup, Hike
from .lib.email_connection import EmailConnection
from .lib.email_templates import render_email_batch
from .lib.email_utils import get_personalization


def start_email_campaign(hike_id: int) -> int:
    """
    Create a new email campaign based on the provided hike's email_type,
    clear & repopulate EmailTask with one row per member,
    clear previous MagicLinks, and pre-generate a MagicLink for each member.
    Finally, enqueue the Celery batch sender.
    """
    # 0) Safety checks
    hike = Hike.query.get(hike_id)
    if hike.status != "active":
        raise RuntimeError("Can only start email campaigns for active hikes")
    email_type = hike.phase
    if hike.email_campaign_completed:
        raise RuntimeError(f"{email_type} phase email campaign already completed for this hike")

    # 1) Create campaign
    campaign = EmailCampaign(hike_id=hike_id, type=email_type, date_created=datetime.now())
    db.session.add(campaign)
    db.session.commit()

    # 2) Clear prior tasks
    EmailTask.query.delete()
    db.session.commit()

    # 3) Clear prior magic links for this hike
    MagicLink.query.filter_by(hike_id=hike_id).delete()
    db.session.commit()

    # 4) Populate tasks from all members

    if email_type in ("voting", "signup"):
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

        tasks.append(
            EmailTask(
                campaign_id=campaign.id,
                member_id=m.id,
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

    camp = EmailCampaign.query.get(campaign_id)
    email_type = camp.type
    hike = Hike.query.get(hike_id)

    # modularize email template w/ static batch data
    subj, text_body_mod, html_body_mod, batch = render_email_batch(email_type, hike)

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
                # derive per-recipient context
                member = Member.query.get(email_task.member_id)
                if not member:
                    email_task.status = "failed"
                    db.session.commit()
                    break

                to_email = getattr(member, "email", None)

                # Render modules to personalized emails
                personalization = get_personalization(email_type, hike, member)
                text_body = text_body_mod.email(personalization, batch)
                html_body = html_body_mod.email(personalization, batch)

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
                        f"{email_type} email send failed for member_id=%s (attempt %s/%s)",
                        member.id, email_task.attempts, max_attempts
                    )

        if batch_pause_sec > 0:
            time.sleep(batch_pause_sec)

    camp.date_completed = datetime.now()
    hike.email_campaign_completed = True
    db.session.commit()

    return {"campaign_id": campaign_id, "sent": sent_total, "failed": failed_total}


@celery_app.task(name="app.tasks.send_email")
def send_email(email_type: str, member_id: int, hike_id, repeat=False):
    """
    Task to send a singular email. Much of the code is re-used from the batch send function.
    I've abstracted a number of these out to lib/email_helpers.py but haven't done the same 4 batches.

    we're in a time crunch tho :(

    -GD
    """
    hike = Hike.query.get(hike_id)
    member = Member.query.get(member_id)
    if not hike:
        raise ValueError("invalid hike_id")
    if not member:
        raise ValueError("invalid member_id")

    # modularize email template w/ static batch data
    subj, text_body_mod, html_body_mod, batch = render_email_batch(email_type, hike)

    # render modules
    personalization = get_personalization(email_type, hike, member)
    text_body = text_body_mod.email(personalization, batch)
    html_body = html_body_mod.email(personalization, batch)

    conn = EmailConnection()

    with conn.connect() as server:
        to_email = getattr(member, "email", None)

        res = conn.send(to_email, subj, text_body, html_body)

        if not res:
            current_app.logger.exception(
                f"{email_type} email send failed for member_id=%s (attempt 1/1)",
                member.id
            )
