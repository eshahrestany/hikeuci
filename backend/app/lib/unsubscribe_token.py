import hmac
import hashlib
from flask import current_app


def generate_token(member_id: int) -> str:
    secret = current_app.config['JWT_SECRET_KEY'].encode()
    sig = hmac.new(secret, f"unsubscribe:{member_id}".encode(), hashlib.sha256).hexdigest()
    return f"{member_id}.{sig}"


def validate_token(token: str) -> int | None:
    try:
        member_id_str, sig = token.split('.', 1)
        member_id = int(member_id_str)
    except (ValueError, AttributeError):
        return None
    secret = current_app.config['JWT_SECRET_KEY'].encode()
    expected = hmac.new(secret, f"unsubscribe:{member_id}".encode(), hashlib.sha256).hexdigest()
    return member_id if hmac.compare_digest(expected, sig) else None
