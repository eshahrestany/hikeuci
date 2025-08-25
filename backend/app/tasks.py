import time
from datetime import datetime
from html import escape as _html_escape
from urllib.parse import quote_plus
from typing import List
from make_celery import celery_app
from flask import current_app

from . import db
from .models import EmailCampaign, EmailTask, Member, MagicLink, Trail
from .lib.emails import EmailConnection


def start_vote_campaign(hike_id: int) -> int:
    """
    Create a new 'voting' campaign, clear & repopulate EmailTask with one row per member,
    and pre-generate a MagicLink for each member (store magic_link_id on the task).
    Finally, enqueue the Celery batch sender.
    """
    # 1) Create campaign
    campaign = EmailCampaign(type="voting", date_created=datetime.now())
    db.session.add(campaign)
    db.session.commit()

    # 2) Clear prior tasks
    EmailTask.query.delete()
    db.session.commit()

    # 3) Populate tasks from all members (with pre-generated magic links)
    mlm = current_app.extensions.get("magic_link_manager")
    if mlm is None:
        raise RuntimeError("MagicLinkManager is not initialized")

    members: List[Member] = Member.query.all()
    tasks: List[EmailTask] = []

    for m in members:
        to_email = getattr(m, "email", None)
        if not to_email:
            continue

        # create token + row in MagicLink table
        token = mlm.generate(user_id=m.id, hike_id=hike_id, phase="voting")
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
    batch_send_vote_emails.delay(campaign_id=campaign.id, hike_id=hike_id)
    return campaign.id


@celery_app.task(name="app.tasks.batch_send_vote_emails")
def batch_send_vote_emails(*, campaign_id: int, hike_id: int) -> dict:
    """
    Process pending EmailTask rows for this campaign in batches.
    Opens one SMTP connection per batch via EmailConnection.connect()
    and personalizes each message using the pre-generated magic link.
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
                member_id = email_task.member_id
                ml = MagicLink.query.get(email_task.magic_link_id)
                token = ml.token

                base_url = current_app.config.get("BASE_URL", "").rstrip("/")
                if not base_url:
                    raise RuntimeError("BASE_URL must be set in app config")

                magic_url = f"{base_url}/vote?token={quote_plus(token)}"

                # Member display name
                member = Member.query.get(member_id)
                name = getattr(member, "name", None)
                to_email = getattr(member, "email", None)
                if not to_email:
                    raise ValueError("Member object must have an 'email' attribute")

                trail_options = Trail.query.filter_by(is_active_vote_candidate=True).all()
                items = [(t2.name, current_app.config["DIFFICULTY_INDEX"][t2.difficulty]) for t2 in trail_options]

                # plain-text body
                trails_text = "\n".join([f"- {n}" + (f" ({d})" if d else "") for n, d in items])

                subj = "Vote for this week's hike"

                text_body = f"""Hi {name},

    It's time to vote for this week's hike! Your voting link is below:

    {magic_url}

    Trail options:
    {trails_text}

    This link is personal to you and expires when voting ends. Please do not share it with others.

    — Hiking Club @ UCI
    """

                font_stack = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, 'Apple Color Emoji', 'Segoe UI Emoji'"
                trails_html = "".join(
                    f"<li style='margin:0 0 6px'>{_html_escape(n)}"
                    + (f" <span style=\"color:#6b7280\">({_html_escape(d)})</span>" if d else "")
                    + "</li>"
                    for n, d in items
                ) or "<li>(Options forthcoming)</li>"

                html_body = f"""\
    <!doctype html>
    <html>
      <body style="margin:0;padding:0;background:#f6f7f9;">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f6f7f9;">
          <tr>
            <td align="center" style="padding:24px;">
              <table role="presentation" width="600" cellpadding="0" cellspacing="0"
                     style="width:600px;max-width:100%;background:#ffffff;border-radius:8px;
                            padding:24px;font-family:{font_stack};color:#111827;">
                <tr><td>
                  <p style="margin:0 0 12px;">Hi {_html_escape(name)},</p>
    
                  <p style="margin:0 0 12px;">It’s time to <strong>vote for this week’s hike</strong>! Your single-use link is below:</p>
    
                  <p style="margin:0 0 20px;">
                    <a href="{_html_escape(magic_url)}"
                       style="display:inline-block;text-decoration:none;padding:12px 18px;border-radius:6px;
                              background:#1d4ed8;color:#ffffff;font-weight:600;">Vote Here</a>
                  </p>
    
                  <p style="margin:0 0 8px;"><strong>Trail options</strong>:</p>
                  <ul style="padding-left:20px;margin:0 0 16px;">
                    {trails_html}
                  </ul>
    
                  <p style="margin:0;color:#6b7280;">
                    This link is personal to you and expires soon. If you didn’t request this, you can ignore this email.
                  </p>
    
                  <p style="margin:16px 0 0;">— Hike UCI</p>
                </td></tr>
              </table>
            </td>
          </tr>
        </table>
      </body>
    </html>
    """
                # ================== END CONTENT BLOCK ==================

                # Build & send reusing the open server

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
