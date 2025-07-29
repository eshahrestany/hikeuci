import requests
import jwt
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, Response, current_app
from typing import Optional, Dict, Any
from ..models import AdminUser

auth: Blueprint = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth.route("/google", methods=["POST"])
def google_login() -> tuple[Response, int]:
    data: Optional[Dict[str, Any]] = request.get_json()
    id_token: Optional[str] = data.get("idToken") if data else None
    if not id_token:
        return jsonify({"error": "Missing idToken"}), 400

    # 1) Verify with Google's tokeninfo endpoint
    resp: requests.Response = requests.get(current_app.config.get("GOOGLE_TOKEN_INFO_URL"), params={"id_token": id_token})
    if resp.status_code != 200:
        return jsonify({"error": "Invalid Google token"}), 401
    info: Dict[str, str] = resp.json()

    # 2) Check audience and email_verified
    if info.get("aud") != current_app.config.get("GOOGLE_CLIENT_ID"):
        return jsonify({"error": "Unrecognized client"}), 401
    if info.get("email_verified") != "true":
        return jsonify({"error": "Email not verified"}), 403

    # 3) Lookup admin user by Google subject (sub)
    sub: str = info["sub"]
    admin: Optional[AdminUser] = AdminUser.query.filter_by(provider_user_id=sub).first()
    if not admin:
        return jsonify({"error": "Not an admin user"}), 403

    # 4) Prepare JWT to send to client
    now: datetime = datetime.utcnow()
    exp: datetime = now + timedelta(hours=int(current_app.config.get("JWT_EXP_HOURS")))
    payload: Dict[str, Any] = {
        "sub": str(admin.id),
        "email": admin.email,
        "iat": now,
        "exp": exp
    }

    token: str = jwt.encode(
        payload,
        current_app.config.get("JWT_SECRET_KEY"),
        algorithm=current_app.config.get("JWT_ALGORITHM", "HS256")
    )

    return jsonify(token=token), 200
