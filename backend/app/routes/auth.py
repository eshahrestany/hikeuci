import os
import requests
import jwt
from datetime import datetime, timedelta
from flask import Blueprint, current_app, request, jsonify
from app import db
from app.models import AdminUser

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"

@auth_bp.route("/google", methods=["POST"])
def google_login():
    data = request.get_json()
    id_token = data.get("idToken")
    if not id_token:
        return jsonify({"error": "Missing idToken"}), 400

    # 1) Verify with Google's tokeninfo endpoint
    resp = requests.get(GOOGLE_TOKENINFO_URL, params={"id_token": id_token})
    if resp.status_code != 200:
        return jsonify({"error": "Invalid Google token"}), 401
    info = resp.json()

    # 2) Check audience and email_verified
    if info.get("aud") != os.getenv("GOOGLE_CLIENT_ID"):
        return jsonify({"error": "Unrecognized client"}), 401
    if info.get("email_verified") != "true":
        return jsonify({"error": "Email not verified"}), 403

    # 3) Lookup admin user by Google subject (sub)
    sub = info["sub"]
    admin = AdminUser.query.filter_by(provider_user_id=sub).first()
    if not admin:
        return jsonify({"error": "Not an admin user"}), 403

    now = datetime.utcnow()
    exp = now + timedelta(hours=int(os.getenv("JWT_EXP_HOURS")))
    payload = {
        "sub": str(admin.id),
        "email": admin.email,
        "iat": now,
        "exp": exp
    }
    token = jwt.encode(payload,
                       os.getenv("JWT_SECRET_KEY"),
                       algorithm=os.getenv("JWT_ALGORITHM", "HS256"))

    return jsonify(token=token), 200
