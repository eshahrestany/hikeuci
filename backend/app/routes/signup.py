from flask import Blueprint, jsonify, current_app, Response, request

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
        trail = magic_link.active_hike.trail

        return jsonify({
            "status": status,
            "formData": {
                "name": f"{user.first_name} {user.last_name}",
                "email": user.email,
                "tel": user.tel,
            },
            "hike": {
                "title": trail.name,
                "description": trail.description or ''
            }
        }), 200

    if request.method == "POST":
        raise NotImplementedError("")
