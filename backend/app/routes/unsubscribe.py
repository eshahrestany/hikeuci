from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import Member
from ..lib.unsubscribe_token import validate_token

unsubscribe = Blueprint("unsubscribe", __name__)


@unsubscribe.route("", methods=["POST"])
def handle_unsubscribe():
    data = request.get_json(silent=True) or {}
    token = data.get("token", "")
    member_id = validate_token(token)
    if member_id is None:
        return jsonify({"error": "Invalid or expired unsubscribe link."}), 400

    member = Member.query.get(member_id)
    if member is None:
        return jsonify({"error": "Member not found."}), 400

    member.subscribed_to_mailing_list = False
    db.session.commit()
    return jsonify({"success": True, "name": member.name})
