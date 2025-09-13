import time
from datetime import datetime
from typing import List

from celery.schedules import crontab
from make_celery import celery_app
from flask import current_app

from . import db
from .lib import phases
from .lib.email_connection import EmailConnection
from .lib.email_templates import render_phase_email
from .models import EmailCampaign, EmailTask, Member, MagicLink, Trail, Signup, Hike


def flatten_num(x: float or int) -> float or int:
    """
    If x is a float and represents an integer value (e.g., 3.0), return it as an int.
    Otherwise, return x unchanged.
    This is useful for displaying numbers in emails without unnecessary decimal points.
    """
    if isinstance(x, float) and x.is_integer():
        return int(x)
    return x

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
    campaign = EmailCampaign(hike_id=hike_id, type=phase, date_created=datetime.now())
    db.session.add(campaign)
    db.session.commit()

    # 2) Clear prior tasks
    EmailTask.query.delete()
    db.session.commit()

    # 3) Clear prior magic links for this hike
    MagicLink.query.filter_by(hike_id=hike_id).delete()
    db.session.commit()

    # 4) Populate tasks from all members
    mlm = current_app.extensions.get("magic_link_manager")

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

        tasks.append(
            EmailTask(
                campaign_id=campaign.id,
                member_id=m.id,
                status="pending",
                attempts=0,
                sent_at=None,
            )
        )

        mlm.generate(member_id=m.id, hike_id=hike_id, type=phase)

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
    phase = camp.type
    hike = Hike.query.get(hike_id)
    trail = Trail.query.get(hike.trail_id) if phase != "voting" else None

    if phase == "voting":
        trail_options = Trail.query.filter_by(is_active_vote_candidate=True).all()
        trails = [{"name": t.name,
                   "difficulty": current_app.config["DIFFICULTY_INDEX"][t.difficulty]}
                  for t in trail_options]
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

                ml = MagicLink.query.filter_by(member_id=member.id, hike_id=hike_id, type=phase).first()
                if not ml:
                    email_task.status = "failed"
                    db.session.commit()
                    break

                name = getattr(member, "name", None)
                to_email = getattr(member, "email", None)
                base_url = current_app.config.get("BASE_URL", "").rstrip("/")
                endpoint_dict = {
                    "voting": "vote",
                    "signup": "signup",
                    "waiver": "waiver"
                }
                magic_url = f"{base_url}/{endpoint_dict[phase]}?token={ml.token}"
                if phase == "waiver":
                    signup = Signup.query.filter_by(hike_id=hike_id, member_id=member.id).first()

                # Render the correct phase template with the necessary context
                if phase == "voting":
                    subj, text_body, html_body = render_phase_email(
                        phase,
                        member_name=name,
                        magic_url=magic_url,
                        trails=trails,
                    )
                elif phase == "signup":
                    subj, text_body, html_body = render_phase_email(
                        phase,
                        member_name=name,
                        magic_url=magic_url,
                        hike_day=hike.hike_date.strftime("%A %-m/%-d"),
                        hike_time=hike.hike_date.strftime("%-I:%M %p"),
                        hike_trail_name=trail.name,
                        hike_town_name=trail.location,
                        hike_length_mi=flatten_num(trail.length_mi),
                        hike_estimated_time_hr=flatten_num(trail.estimated_time_hr),
                        hike_difficulty=current_app.config["DIFFICULTY_INDEX"][trail.difficulty],
                        num_liters=flatten_num(trail.required_water_liters),
                        description=trail.description,
                    )
                elif phase == "waiver":
                    subj, text_body, html_body = render_phase_email(
                        phase,
                        member_name=name,
                        transport_type=signup.transport_type,
                        magic_url=magic_url,
                        hike_trail_gmap_link=trail.trailhead_gmaps_endpoint,
                        hike_trail_amap_link=trail.trailhead_amaps_endpoint,
                        hike_day=hike.hike_date.strftime("%A %-m/%-d"),
                        hike_time=hike.hike_date.strftime("%-I:%M %p"),
                        hike_trail_name=trail.name,
                        hike_town_name=trail.location,
                        hike_length_mi=flatten_num(trail.length_mi),
                        hike_estimated_time_hr=flatten_num(trail.estimated_time_hr),
                        hike_difficulty=current_app.config["DIFFICULTY_INDEX"][trail.difficulty],
                        num_liters=flatten_num(trail.required_water_liters),
                        description=trail.description,
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
                        f"{phase} email send failed for member_id=%s (attempt %s/%s)",
                        member.id, email_task.attempts, max_attempts
                    )

        if batch_pause_sec > 0:
            time.sleep(batch_pause_sec)

    camp.date_completed = datetime.now()
    hike.email_campaign_completed = True
    db.session.commit()

    return {"campaign_id": campaign_id, "sent": sent_total, "failed": failed_total}


@celery_app.task(name="app.tasks.check_and_update_phase")
def check_and_update_phase():
    ah = Hike.query.filter_by(status="active").first()
    if not ah: return

    now = datetime.now()

    if ah.phase is None:  # hike has just been created
        if ah.voting_date is not None:  # will this hike have a vote?
            if now >= ah.voting_date:
                phases.initiate_vote_phase(ah)
                #start_email_campaign(ah.id)

        else:  # no vote, skip to signup phase
            if now >= ah.signup_date:
                phases.initiate_signup_phase(ah)
                #start_email_campaign(ah.id)

    elif ah.phase == "voting":
        if now >= ah.signup_date:
            phases.initiate_signup_phase(ah)
            #start_email_campaign(ah.id)

    elif ah.phase == "signup":
        if now >= ah.waiver_date:
            phases.initiate_waiver_phase(ah)
            #start_email_campaign(ah.id)

    elif ah.phase == "waiver":
        if now >= ah.hike_date + current_app.config.get("HIKE_RESET_TIME_HR"):
            phases.complete_hike(ah)
