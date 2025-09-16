import re

from flask import Blueprint, request, jsonify

from ..decorators import admin_required
from ..extensions import db
from ..models import Member

members = Blueprint("members", __name__, url_prefix="members")

def _serialize_member(member):
    return {
        'id': member.id,
        'name': member.name,
        'email': member.email,
        'tel': member.tel,
        'joined_on': member.joined_on.isoformat(),
        'is_officer': member.is_officer
    }

def _is_email_valid(email: str) -> str | None:
    pattern = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    if pattern.match(email):
        return email
    return None

@members.route("", methods=['GET'])
@admin_required
def list_members():
    all_members = Member.query.order_by(Member.name.asc()).all()
    return jsonify([_serialize_member(member) for member in all_members])

@members.route("", methods=['POST'])
@admin_required
def create_member():
    data = request.get_json()

    name = data['name'].strip()
    if not name:
        return {"error": "please provide a name"}, 400

    email = _is_email_valid(data['email'].strip().lower())
    if not email:
        return {"error": "invalid email address"}, 400

    tel = data['tel'].strip()
    is_officer = data['is_officer']

    new_member = Member(
        name = name,
        email = email,
        tel = tel,
        is_officer = is_officer,
    )
    db.session.add(new_member)
    db.session.commit()

    return  jsonify(_serialize_member(new_member)), 201

@members.route("/<int:member_id>", methods=["PUT"])
def update_member(member_id):
    member = Member.query.get_or_404(member_id)
    data = request.get_json()

    member.name = data.get('name', member.name).strip()
    member.email = _is_email_valid(data.get('email', member.email).strip().lower())
    member.tel = data.get('tel', member.tel).strip()
    member.is_officer = data.get('is_officer', member.is_officer)

    db.session.commit()
    return jsonify(_serialize_member(member))

@members.route("/<int:member_id>", methods=["DELETE"])
def delete(member_id):
    member = Member.query.get_or_404(member_id)
    db.session.delete(member)
    db.session.commit()
    return "Deleted Successfully", 200
