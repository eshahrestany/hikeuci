import requests
import jwt
from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, jsonify, Response, current_app
from typing import Optional, Dict, Any
from ..models import AdminUser
from .. import db

auth: Blueprint = Blueprint("auth", __name__, url_prefix="/api/auth")


def _create_access_token(admin: AdminUser) -> str:
    now: datetime = datetime.now(timezone.utc)
    exp: datetime = now + timedelta(minutes=int(current_app.config["JWT_ACCESS_EXP_MINUTES"]))
    payload: Dict[str, Any] = {
        "sub": str(admin.id),
        "email": admin.email,
        "type": "access",
        "iat": now,
        "exp": exp,
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm=current_app.config["JWT_ALGORITHM"])


def _create_refresh_token(admin: AdminUser) -> str:
    now: datetime = datetime.now(timezone.utc)
    exp: datetime = now + timedelta(days=int(current_app.config["JWT_REFRESH_EXP_DAYS"]))
    payload: Dict[str, Any] = {
        "sub": str(admin.id),
        "type": "refresh",
        "iat": now,
        "exp": exp,
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm=current_app.config["JWT_ALGORITHM"])


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

    # 3) Lookup admin user by email
    email: str = info["email"]
    admin: Optional[AdminUser] = AdminUser.query.filter_by(email=email).first()
    if not admin:
        return jsonify({"error": "Not an admin user"}), 403

    # 4) Check if sub has been set (not set on first login), otherwise set it
    sub: str = info["sub"]
    if admin.provider_user_id:
        if admin.provider_user_id != sub:
            return jsonify({"error": "Not an admin user (email/sub mismatch)"}), 403
    else:
        admin.provider_user_id = sub
        db.session.commit()

    # 5) Issue access + refresh tokens
    access_token: str = _create_access_token(admin)
    refresh_token: str = _create_refresh_token(admin)

    return jsonify(token=access_token, refreshToken=refresh_token), 200


@auth.route("/refresh", methods=["POST"])
def refresh() -> tuple[Response, int]:
    data: Optional[Dict[str, Any]] = request.get_json()
    refresh_token: Optional[str] = data.get("refreshToken") if data else None
    if not refresh_token:
        return jsonify({"error": "Missing refreshToken"}), 400

    try:
        payload: Dict[str, Any] = jwt.decode(
            refresh_token,
            current_app.config["JWT_SECRET_KEY"],
            algorithms=[current_app.config["JWT_ALGORITHM"]],
        )
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Refresh token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid refresh token"}), 401

    if payload.get("type") != "refresh":
        return jsonify({"error": "Invalid token type"}), 401

    admin_id: int = int(payload["sub"])
    admin: Optional[AdminUser] = db.session.get(AdminUser, admin_id)
    if not admin:
        return jsonify({"error": "Admin not found"}), 403

    access_token: str = _create_access_token(admin)
    return jsonify(token=access_token), 200
