import re
from flask import Blueprint, request, jsonify
from ..decorators import admin_required
from ..extensions import db
from ..models import Member

members = Blueprint("members", __name__, url_prefix="members")
email_pattern = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

def _serialize_member(member):
    return {
        'id': member.id,
        'name': member.name,
        'email': member.email,
        'tel': member.tel,
        'joined_on': member.joined_on.isoformat(),
        'is_officer': member.is_officer
    }

@members.route("", methods=['GET'])
@admin_required
def list_members():
    all_members = Member.query.order_by(Member.name.asc()).all()
    return jsonify([_serialize_member(member) for member in all_members])

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
    is_officer = data.get('is_officer', False)

    new_member = Member(
        name = name,
        email = email,
        tel = tel,
        is_officer = is_officer,
    )
    db.session.add(new_member)
    db.session.commit()

    return jsonify(_serialize_member(new_member)), 201

@members.route("/<int:member_id>", methods=["PUT"])
@admin_required
def update_member(member_id):
    member = Member.query.get_or_404(member_id)
    data = request.get_json()
    member.name = data.get('name', member.name)
    new_email = data.get('email')
    if not new_email or not email_pattern.match(new_email):
        return {"error": "invalid email address"}, 400

    member.email = new_email if new_email else member.email
    member.tel = data.get('tel', member.tel)
    member.is_officer = data.get('is_officer', member.is_officer)

    db.session.commit()

    return jsonify(_serialize_member(member))

@members.route("/<int:member_id>", methods=["DELETE"])
@admin_required
def delete(member_id):
    member = Member.query.get_or_404(member_id)
    db.session.delete(member)
    db.session.commit()
    return "Deleted Successfully", 200


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
            .filter(Member.email.in_(seen_emails_in_batch)).all()
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


