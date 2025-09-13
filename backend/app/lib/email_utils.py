from ..models import Member, MagicLink, Signup, Hike, Vote
from flask import current_app


def flatten_num(x: float or int) -> float or int:
    """
    If x is a float and represents an integer value (e.g., 3.0), return it as an int.
    Otherwise, return x unchanged.
    This is useful for displaying numbers in emails without unnecessary decimal points.
    """
    if isinstance(x, float) and x.is_integer():
        return int(x)
    return x


def _remove_magic_link(member_id: int, hike_id: int, email_type: str):
    ml = MagicLink.query.filter_by(member_id=member_id, hike_id=hike_id, type=email_type)
    if not ml:
        return False

    ml.delete()
    return True


def get_personalization(email_type, hike: Hike, member: Member):
    personalization = {
        "name": member.name,
    }

    # Transactional Emails
    if email_type == "waiver_confirmation":
        raise NotImplementedError()

    # Access-Protected Emails (Needs Magic Link)

    # First check for existing ML. Clear it and associated data if found.
    _remove_magic_link(member.id, hike.hike_id, email_type)

    mlm = current_app.extensions.get("magic_link_manager")
    token = mlm.generate(member_id=member.id, hike_id=hike.id, type=email_type)

    base_url = current_app.config.get("BASE_URL", "").rstrip("/")
    endpoint_dict = {
        "voting": "vote",
        "signup": "signup",
        "waiver": "waiver"
    }

    personalization["magic_url"] = f"{base_url}/{endpoint_dict[email_type]}?token={token}"

    if email_type in ["voting", "signup"]:
        # good to go (member_name, magic_url)
        return personalization

    elif email_type == "waiver":
        # Add signup transport data to waivers
        signup = Signup.query.filter_by(hike_id=hike.id, member_id=member.id).first()
        personalization["transport_type"] = signup.transport_type
        return personalization

    else:
        raise Exception(f"Unknown email type: {email_type}")
