from flask import Blueprint, jsonify, current_app, Response, request
from ..models import Hike, Member, MagicLink, Trail, Vehicle

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

        mlm = current_app.extensions.get("magic_link_manager")
        if mlm.validate(token)["status"] != "valid":
            return jsonify({"error": "Token is invalid"}), 400

        magic_link = MagicLink.query.filter_by(token=token).first()
        member = Member.query.get(magic_link.member_id)

        hike = Hike.query.get(magic_link.hike_id) if magic_link.hike_id else None
        trail = Trail.query.get(hike.trail_id)

        vehicles = Vehicle.query.filter_by(member_id=member.id).all()
        vehicles_data = [{
            "id": v.id,
            "make": v.make,
            "model": v.model,
            "year": v.year,
            "passenger_seats": v.passenger_seats
        } for v in vehicles]

        return jsonify({
            "status": status,
            "formData": {
                "name": member.name,
                "email": member.email,
                "tel": member.tel,
            },
            "hike": {
                "title": trail.name,
            },
            "vehicles": vehicles_data
        }), 200

    if request.method == "POST":
        raise NotImplementedError("")
