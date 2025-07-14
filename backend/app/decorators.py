import jwt
from functools import wraps
from flask import request, jsonify, current_app, g
from app.models import AdminUser

def admin_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        parts = auth.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify(error="Missing or malformed auth header"), 401

        token = parts[1]
        try:
            data = jwt.decode(
                token,
                current_app.config["JWT_SECRET_KEY"],
                algorithms=[current_app.config["JWT_ALGORITHM"]],
            )
        except jwt.ExpiredSignatureError:
            return jsonify(error="Token expired"), 401
        except jwt.InvalidTokenError as e:
            current_app.logger.error(f"JWT decode error: {e!r}")
            return jsonify(error="Invalid token"), 401

        # Double-check user still exists
        try:
            admin_id = int(data["sub"])
        except (KeyError, ValueError):
            return jsonify(error="Bad subject claim"), 401

        admin = AdminUser.query.get(admin_id)
        if not admin:
            return jsonify(error="Admin not found"), 403

        # stash on flask.g for handlers to use
        g.current_admin = admin
        return f(*args, **kwargs)
    return wrapped
