from flask import Blueprint, jsonify, request, current_app
from sqlalchemy import func, or_, nullslast

from ..decorators import admin_required
from ..models import EmailCampaign, EmailTask, Hike, Member, Trail
from .. import db

email_campaigns: Blueprint = Blueprint("email_campaigns", __name__)

CAMPAIGN_TYPES = ("voting", "signup", "waiver", "waitlist")
SORT_FIELDS = {
    "sent_at": EmailTask.sent_at,
    "status": EmailTask.status,
    "attempts": EmailTask.attempts,
}
PAGE_SIZE = 50


@email_campaigns.route("/hikes", methods=["GET"])
@admin_required
def list_hikes_with_campaigns():
    rows = (
        db.session.query(Hike, Trail)
        .outerjoin(Trail, Hike.trail_id == Trail.id)
        .filter(db.session.query(EmailCampaign.id).filter(EmailCampaign.hike_id == Hike.id).exists())
        .order_by(Hike.hike_date.desc(), Hike.id.desc())
        .all()
    )
    return jsonify([
        {
            "id": hike.id,
            "hike_date": hike.get_localized_time("hike_date").isoformat(),
            "trail_name": trail.name if trail else None,
        }
        for hike, trail in rows
    ])


@email_campaigns.route("/hikes/<int:hike_id>/campaigns", methods=["GET"])
@admin_required
def list_campaigns_for_hike(hike_id: int):
    if not db.session.get(Hike, hike_id):
        return jsonify({"error": "Hike not found"}), 404

    campaigns = (
        EmailCampaign.query
        .filter_by(hike_id=hike_id)
        .order_by(EmailCampaign.date_created.asc())
        .all()
    )
    if not campaigns:
        return jsonify([])

    count_rows = (
        db.session.query(EmailTask.campaign_id, EmailTask.status, func.count(EmailTask.id))
        .filter(EmailTask.campaign_id.in_([c.id for c in campaigns]))
        .group_by(EmailTask.campaign_id, EmailTask.status)
        .all()
    )
    counts_by_campaign: dict[int, dict[str, int]] = {}
    for cid, status, n in count_rows:
        counts_by_campaign.setdefault(cid, {"pending": 0, "sent": 0, "failed": 0})[status] = n

    def _counts(cid: int) -> dict:
        c = counts_by_campaign.get(cid, {"pending": 0, "sent": 0, "failed": 0})
        return {**c, "total": c["pending"] + c["sent"] + c["failed"]}

    return jsonify([
        {
            "id": c.id,
            "type": c.type,
            "date_created": c.date_created.replace(tzinfo=None).isoformat() + "Z" if c.date_created else None,
            "date_completed": c.date_completed.replace(tzinfo=None).isoformat() + "Z" if c.date_completed else None,
            "in_progress": c.date_completed is None,
            "counts": _counts(c.id),
        }
        for c in campaigns
    ])


@email_campaigns.route("/<int:campaign_id>/tasks", methods=["GET"])
@admin_required
def list_campaign_tasks(campaign_id: int):
    campaign = db.session.get(EmailCampaign, campaign_id)
    if not campaign:
        return jsonify({"error": "Campaign not found"}), 404

    page = request.args.get("page", type=int)
    if page is None or page < 1:
        return jsonify({"error": "page must be >= 1"}), 400

    status = request.args.get("status")
    if status is not None and status not in ("pending", "sent", "failed"):
        return jsonify({"error": "status must be one of pending|sent|failed"}), 400

    q_str = (request.args.get("q") or "").strip()
    sort = request.args.get("sort", "sent_at")
    if sort not in SORT_FIELDS:
        return jsonify({"error": "sort must be one of sent_at|status|attempts"}), 400
    direction = request.args.get("dir", "desc")
    if direction not in ("asc", "desc"):
        return jsonify({"error": "dir must be asc or desc"}), 400

    base = (
        db.session.query(EmailTask, Member)
        .join(Member, EmailTask.member_id == Member.id)
        .filter(EmailTask.campaign_id == campaign_id)
    )
    if status:
        base = base.filter(EmailTask.status == status)
    if q_str:
        like = f"%{q_str}%"
        base = base.filter(or_(Member.name.ilike(like), Member.email.ilike(like)))

    total = base.count()

    sort_col = SORT_FIELDS[sort]
    sort_expr = sort_col.desc() if direction == "desc" else sort_col.asc()
    if sort == "sent_at":
        sort_expr = nullslast(sort_expr)
    rows = (
        base.order_by(sort_expr, EmailTask.id.asc())
        .offset((page - 1) * PAGE_SIZE)
        .limit(PAGE_SIZE)
        .all()
    )

    return jsonify({
        "page": page,
        "page_size": PAGE_SIZE,
        "total": total,
        "has_next": page * PAGE_SIZE < total,
        "max_attempts": int(current_app.config.get("MAIL_MAX_ATTEMPTS", 3)),
        "items": [
            {
                "id": task.id,
                "status": task.status,
                "attempts": task.attempts,
                "sent_at": task.sent_at.replace(tzinfo=None).isoformat() + "Z" if task.sent_at else None,
                "member": {
                    "id": member.id,
                    "name": member.name,
                    "email": member.email,
                },
            }
            for task, member in rows
        ],
    })
