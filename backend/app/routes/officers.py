from flask import Blueprint, request, jsonify, g
from sqlalchemy.exc import IntegrityError

from ..decorators import admin_required, owner_required
from ..extensions import db
from ..models import AdminUser, Member

officers = Blueprint("officers", __name__)


def _serialize(admin: AdminUser):
    member = admin.member
    return {
        "id": admin.id,
        "member_id": admin.member_id,
        "name": member.name if member else None,
        "email": member.email if member else admin.email,
        "created_on": admin.created_on.isoformat(),
        "is_owner": admin.is_owner,
        "has_logged_in": admin.provider_user_id is not None,
    }


@officers.route("", methods=["GET"])
@admin_required
@owner_required
def list_officers():
    rows = AdminUser.query.order_by(AdminUser.is_owner.desc(), AdminUser.created_on.asc()).all()
    return jsonify([_serialize(a) for a in rows])


@officers.route("/candidate-members", methods=["GET"])
@admin_required
@owner_required
def candidate_members():
    # Intentionally not filtered by current academic year: officers are chosen from
    # members of any tenure, unlike the /members roster which shows the current AY only.
    officer_ids = {mid for (mid,) in db.session.query(AdminUser.member_id).all()}
    rows = Member.query.order_by(Member.name.asc()).all()
    return jsonify([
        {"member_id": m.id, "name": m.name, "email": m.email}
        for m in rows if m.id not in officer_ids
    ])


@officers.route("", methods=["POST"])
@admin_required
@owner_required
def create_officer():
    data = request.get_json() or {}
    member_id = data.get("member_id")
    if not isinstance(member_id, int):
        return jsonify(error="member_id is required"), 400

    member = db.session.get(Member, member_id)
    if member is None:
        return jsonify(error="Member not found"), 404

    if AdminUser.query.filter_by(member_id=member.id).first():
        return jsonify(error="That member is already an officer"), 409

    if AdminUser.query.filter_by(email=member.email).first():
        return jsonify(error="An officer already exists with that email"), 409

    admin = AdminUser(email=member.email, member_id=member.id, is_owner=False)
    db.session.add(admin)
    db.session.commit()
    return jsonify(_serialize(admin)), 201


@officers.route("/<int:officer_id>", methods=["DELETE"])
@admin_required
@owner_required
def delete_officer(officer_id: int):
    target = db.session.get(AdminUser, officer_id)
    if target is None:
        return jsonify(error="Officer not found"), 404
    if target.is_owner:
        return jsonify(error="Cannot remove the owner. Transfer ownership first."), 400
    if target.id == g.current_admin.id:
        return jsonify(error="Cannot remove yourself"), 400

    db.session.delete(target)
    db.session.commit()
    return jsonify(success=True), 200


@officers.route("/<int:officer_id>/transfer", methods=["POST"])
@admin_required
@owner_required
def transfer_ownership(officer_id: int):
    target = db.session.get(AdminUser, officer_id)
    if target is None:
        return jsonify(error="Officer not found"), 404
    if target.id == g.current_admin.id:
        return jsonify(error="You are already the owner"), 400
    if target.provider_user_id is None:
        return jsonify(error="Cannot transfer ownership to an officer who hasn't signed in yet"), 400

    current_owner = g.current_admin
    try:
        current_owner.is_owner = False
        db.session.flush()
        target.is_owner = True
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(error="Transfer failed due to a concurrent change"), 409

    return jsonify(success=True, new_owner_id=target.id), 200
