from flask import Blueprint, request, jsonify, current_app, render_template
from ..models import Member, Hike, Trail, MagicLink
from .. import db

hike_waiver: Blueprint = Blueprint("hike-waiver", __name__)

@hike_waiver.route("", methods=["GET", "POST"])
def hike_waiver_page():
    if request.method == "GET":
        token = request.args.get("token")
        if not token:
            return jsonify({"error": "Token is missing"}), 400

        data = current_app.extensions["magic_link_manager"].validate(token)
        status = data["status"]
        if status != "valid":
            return jsonify({"error": "Token is invalid"}), 400

        magic_link = MagicLink.query.filter_by(token=token).first()
        member = Member.query.get(magic_link.member_id)
        if not member:
            return jsonify({"error": "Member not found"}), 404

        hike = Hike.query.get(magic_link.hike_id) if magic_link.hike_id else None
        trail = Trail.query.get(hike.trail_id)

        content = render_template("waiver_content.html.j2", event_description=trail.name, event_date=hike.hike_date.strftime("%A, %B %d, %Y"))
        return jsonify({"status": "ready", "content": content}), 200
    elif request.method == "POST":
        raise NotImplementedError()