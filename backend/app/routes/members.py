import re
from flask import Blueprint, request, jsonify
from sqlalchemy import or_, exists
from sqlalchemy.exc import IntegrityError
from ..decorators import admin_required
from ..extensions import db
from ..models import Member, AdminUser, Signup, Waiver, Vehicle, MagicLink, EmailTask
from ..lib.model_utils import get_current_ay_start

members = Blueprint("members", __name__, url_prefix="members")
email_pattern = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

def _serialize_member(member, is_officer=False, can_delete=True):
    return {
        'id': member.id,
        'name': member.name,
        'email': member.email,
        'tel': member.tel,
        'joined_on': member.joined_on.isoformat(),
        'is_officer': is_officer,
        'subscribed_to_mailing_list': member.subscribed_to_mailing_list,
        'can_delete': can_delete,
    }

def _referenced_member_ids() -> set:
    """Return member IDs that have any FK reference preventing deletion."""
    rows = db.session.query(Member.id).filter(
        or_(
            exists().where(Signup.member_id == Member.id),
            exists().where(Waiver.member_id == Member.id),
            exists().where(Vehicle.member_id == Member.id),
            exists().where(MagicLink.member_id == Member.id),
            exists().where(EmailTask.member_id == Member.id),
        )
    ).all()
    return {r[0] for r in rows}


def _officer_member_ids():
    return {mid for (mid,) in db.session.query(AdminUser.member_id).all()}

@members.route("", methods=['GET'])
@admin_required
def list_members():
    ay_start = get_current_ay_start()
    all_members = Member.query.filter(Member.joined_on >= ay_start).order_by(Member.name.asc()).all()
    officer_ids = _officer_member_ids()
    referenced_ids = _referenced_member_ids()
    return jsonify([
        _serialize_member(m, m.id in officer_ids, m.id not in referenced_ids)
        for m in all_members
    ])

@members.route("", methods=['POST'])
@admin_required
def create_member():
    data = request.get_json()

    name = data.get('name')
    if not name:
        return {"error": "please provide a name"}, 400

    email = data.get('email')
    if not email or not email_pattern.match(email):
        return {"error": "invalid email address"}, 400


    tel = data.get('tel', None)
    if tel == "":
        tel = None

    new_member = Member(
        name = name,
        email = email,
        tel = tel,
    )
    db.session.add(new_member)
    db.session.commit()

    return jsonify(_serialize_member(new_member, False)), 201

@members.route("/<int:member_id>", methods=["PUT"])
@admin_required
def update_member(member_id):
    member = Member.query.get_or_404(member_id)
    data = request.get_json()
    member.name = data.get('name', member.name)
    new_email = data.get('email')
    if not new_email or not email_pattern.match(new_email):
        return {"error": "invalid email address"}, 400

    email_changed = new_email != member.email
    member.email = new_email if new_email else member.email
    member.tel = data.get('tel', member.tel)
    if member.tel == "":
        member.tel = None

    admin = AdminUser.query.filter_by(member_id=member.id).first()
    if admin is not None and email_changed:
        admin.email = new_email

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "That email is already in use by another officer."}, 409

    return jsonify(_serialize_member(member, admin is not None))

@members.route("/<int:member_id>", methods=["DELETE"])
@admin_required
def delete(member_id):
    member = Member.query.get_or_404(member_id)
    if AdminUser.query.filter_by(member_id=member.id).first() is not None:
        return jsonify(error="This member is an officer; remove them from Officers first."), 409
    db.session.delete(member)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(error="Cannot delete member with existing records (signups, waivers, vehicles, etc.)."), 409
    return "Deleted Successfully", 200


@members.route("/<int:member_id>/mailing-list", methods=["PATCH"])
@admin_required
def toggle_mailing_list(member_id):
    member = Member.query.get_or_404(member_id)
    data = request.get_json(silent=True) or {}
    subscribed = data.get("subscribed")
    if not isinstance(subscribed, bool):
        return jsonify(error="'subscribed' must be a boolean."), 400
    member.subscribed_to_mailing_list = subscribed
    db.session.commit()
    officer_ids = _officer_member_ids()
    referenced_ids = _referenced_member_ids()
    return jsonify(_serialize_member(member, member.id in officer_ids, member.id not in referenced_ids))


@members.route("/batch", methods=["POST"])
@admin_required
def batch_add_members():
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({"error": "Request body must be a list of member objects."}), 400

    errors = []
    members_to_create = []
    seen_emails_in_batch = set()

    for i, item in enumerate(data, 1):
        name = item.get("name", "").strip()
        email = item.get("email", "").strip()
        if not name or not email:
            errors.append(f"Row {i}: Name and email are required.")
            continue

        if not email_pattern.match(item.get("email", "").strip().lower()):
            errors.append(f"Row {i}: Invalid email address.")
            continue

        if email in seen_emails_in_batch:
            errors.append(f"Row {i}: Email '{email}' is duplicated within your list.")
            continue

        seen_emails_in_batch.add(email)
        members_to_create.append(Member(name=name, email=email))

    if errors:
        return jsonify({
            "error": "Validation failed. No members were created.",
            "details": errors
        }), 400

    if seen_emails_in_batch:
        existing_emails = {
            result[0] for result in db.session.query(Member.email)
            .filter(Member.email.in_(seen_emails_in_batch))
            .filter(Member.joined_on >= get_current_ay_start())
            .all()
        }

        if existing_emails:
            for email in existing_emails:
                errors.append(f"Email '{email}' already exists in the database.")

            return jsonify({
                "error": "Validation failed. No members were created.",
                "details": errors
            }), 409


    if members_to_create:
        db.session.add_all(members_to_create)
        db.session.commit()
        return jsonify({
            "success": f"{len(members_to_create)} members added successfully."
        }), 201
    else:
        return jsonify({"message": "No new members to add."}), 200


