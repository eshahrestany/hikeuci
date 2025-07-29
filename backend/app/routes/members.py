from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import Member, Signup, ActiveHike
from ..decorators import admin_required

members = Blueprint("members", __name__, url_prefix="members")

@members.route("/list-emails-not-in-hike", methods=["GET"])
@admin_required
def list_emails_not_in_hike():
    # Already-signed-up member IDs
    signed_ids = (db.session.query(Signup.member_id).all())
    signed_ids = [mid for (mid,) in signed_ids]

    # Waitlisted members
    waitlisted_ids = (db.session.query(Signup.member_id).filter(Signup.status == "waitlisted").all())
    waitlisted_members = (
        Member.query
        .filter(Member.id.in_(waitlisted_ids))
        .order_by(Member.email)
        .all()
    )

    # Unsigned-up members
    unsigned_members = (
        Member.query
        .filter(~Member.id.in_(signed_ids))
        .order_by(Member.email)
        .all()
    )

    # Combine unsigned and waitlisted members
    rows = unsigned_members + waitlisted_members

    return jsonify([{"member_id": m.id, "email": m.email} for m in rows]), 200
