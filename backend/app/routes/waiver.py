from datetime import datetime

from flask import Blueprint, request, jsonify, current_app, render_template
from ..models import Member, Hike, Trail, MagicLink, Waiver, Signup
from .. import db

hike_waiver: Blueprint = Blueprint("hike-waiver", __name__)


@hike_waiver.route("", methods=["GET", "POST"])
def hike_waiver_page():
    token = request.args.get("token")
    if not token:
        return jsonify({"error": "Token is missing"}), 400

    data = current_app.extensions["magic_link_manager"].validate(token)
    status = data["status"]
    if status != "valid":
        return jsonify({"error": "This link is invalid or has expired."}), 400

    magic_link = MagicLink.query.filter_by(token=token).first()
    member = Member.query.get(magic_link.member_id)
    if not member:
        return jsonify({"error": "Member not found"}), 404

    hike = Hike.query.get(magic_link.hike_id) if magic_link.hike_id else None
    trail = Trail.query.get(hike.trail_id)

    signup = Signup.query.filter_by(member_id=member.id, hike_id=hike.id).first()
    if not signup:
        return jsonify({"error": "Member is not signed up for this hike"}), 404

    existing_waiver = Waiver.query.filter_by(hike_id=hike.id, member_id=member.id).first()
    if existing_waiver:
        return jsonify({"status": "signed"}), 200

    if request.method == "GET":
        content = render_template("waiver_content.html.j2", event_description=trail.name,
                                  event_date=hike.hike_date.strftime("%A, %B %d, %Y"))
        return jsonify({"status": "ready", "content": content}), 200
    elif request.method == "POST":
        form_data = request.json
        name = form_data.get("name")
        if not name:
            return jsonify({"error": "Name is missing"}), 400

        is_minor = form_data.get("is_minor") == True
        age = None
        if is_minor:
            age = form_data.get("age")
            if not age:
                return jsonify({"error": "Age is missing"}), 400
            if age > 18 or age < 0:
                return jsonify({"error": "Age is invalid"}), 400

        signature_1_b64 = form_data.get("signature1")
        if not signature_1_b64:
            return jsonify({"error": "Signature 1 is missing"}), 400
        signature_2_b64 = form_data.get("signature2")
        if not signature_2_b64:
            return jsonify({"error": "Signature 2 is missing"}), 400

        # we currently don't perform a check to make sure the signature fields aren't blank.
        # this may be a prudent "just-in-case" addition for the future;
        # I believe this would have to be done by checking if the resulting b64 image for any black pixels

        waiver = Waiver(
            member_id=member.id,
            hike_id=hike.id,
            print_name=name,
            is_minor=is_minor,
            age=age,
            signature_1_b64=signature_1_b64,
            signature_2_b64=signature_2_b64,
            signed_on=datetime.now(),
        )
        db.session.add(waiver)
        db.session.commit()

        current_app.extensions["celery"].send_task("app.tasks.generate_waiver_pdf", args=[waiver.id])

        return jsonify({"status": "submitted", "success": True}), 200


@hike_waiver.route("/cancel", methods=["POST"])
def cancel():
    token = request.args.get("token")
    if not token:
        return jsonify({"error": "Token is missing"}), 400

    data = current_app.extensions["magic_link_manager"].validate(token)
    status = data["status"]
    if status != "valid":
        return jsonify({"error": "This link is invalid or has expired."}), 400

    magic_link = MagicLink.query.filter_by(token=token).first()
    member = Member.query.get(magic_link.member_id)
    if not member:
        return jsonify({"error": "Member not found"}), 404

    hike = Hike.query.get(magic_link.hike_id) if magic_link.hike_id else None
    trail = Trail.query.get(hike.trail_id)

    existing_signup = Waiver.query.filter_by(hike_id=hike.id, member_id=member.id).first()
    if not existing_signup:
        return jsonify({"error": "User does not have a signup for this hike"})

    # just delete the signup and magic link, don't delete waiver.

    db.session.delete(existing_signup)
    db.session.delete(magic_link)
    db.session.commit()

    return jsonify({"status": "Cancelled successfully", "success": True}), 200
