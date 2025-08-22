from flask import Blueprint, jsonify, current_app, Response, request
from ..models import Hike

hike_signup: Blueprint = Blueprint("hike-signup", __name__)


@hike_signup.route("", methods=["GET", "POST"])
def signup() -> tuple[Response, int]:
    if request.method == "GET":
        token = request.args.get("token")
        if not token:
            return jsonify({"error": "Token is missing"}), 400

        data = current_app.extensions["magic_link_manager"].validate(token)
        status = data["status"]
        if status != "valid":
            return jsonify({"status": status, "formData": None}), 200

        magic_link = data["magic_link"]
        user = magic_link.user

        hike = Hike.query.get(magic_link.hike_id) if magic_link.hike_id else None
        trail = hike.trail if (hike and hike.trail_id) else None  # Hike.trail backref from Trail.hikes

        return jsonify({
            "status": status,
            "formData": {
                "name": user.name,
                "email": user.email,
                "tel": user.tel,
            },
            "hike": {
                # If trail not yet chosen (e.g., during voting), keep strings to avoid FE breakage
                "title": trail.name if trail else "",
                "description": (trail.description or "") if trail else ""
            }
        }), 200

    if request.method == "POST":
        raise NotImplementedError("")
