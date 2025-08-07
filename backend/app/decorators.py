from functools import wraps
from typing import Callable, Any, TypeVar, Optional, Dict, Union

import jwt
from flask import request, jsonify, current_app, g, Response

from .models import AdminUser, ActiveHike

F = TypeVar("F", bound=Callable[..., Any])

def admin_required(f: F) -> F:
    @wraps(f)
    def wrapped(*args: Any, **kwargs: Any) -> Union[Response, Any]:
        auth_header: Optional[str] = request.headers.get("Authorization", "")
        parts: list[str] = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify(error="Missing or malformed auth header"), 401

        token: str = parts[1]
        try:
            data: Dict[str, Any] = jwt.decode(
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
            admin_id: int = int(data["sub"])
        except (KeyError, ValueError):
            return jsonify(error="Bad subject claim"), 401

        admin: Optional[AdminUser] = AdminUser.query.get(admin_id)
        if not admin:
            return jsonify(error="Admin not found"), 403

        # stash on flask.g for handlers to use
        g.current_admin: AdminUser = admin  # type: ignore[attr-defined]
        return f(*args, **kwargs)
    return wrapped  # type: ignore[return-value]

def waiver_phase_required(f: F) -> F:
    @wraps(f)
    def wrapped(*args: Any, **kwargs: Any) -> Union[Response, Any]:
        active_hike = ActiveHike.query.first()
        if not active_hike:
            return jsonify(error="No current active hike"), 400
        if active_hike.status.lower() != "waiver":
            return jsonify(error="Hike is not in waiver phase"), 400
        return f(*args, **kwargs)
    return wrapped  # type: ignore[return-value]