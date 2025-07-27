from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import Member, Signup, ActiveHike
from ..decorators import admin_required

members = Blueprint("members", __name__, url_prefix="members")

@members.route("/list-emails-not-in-hike", methods=["GET"])
@admin_required
def list_emails_not_in_hike():
    hike_id = ActiveHike.query.first().id

    # Already-signed-up member IDs
    signed_ids = (
        db.session.query(Signup.member_id)
        .filter(Signup.active_hike_id == hike_id)
        .all()
    )
    signed_ids = [mid for (mid,) in signed_ids]

    # All other members
    rows = (
        Member.query
        .filter(~Member.id.in_(signed_ids))
        .order_by(Member.email)
        .all()
    )

    return jsonify([{"member_id": m.id, "email": m.email} for m in rows]), 200
