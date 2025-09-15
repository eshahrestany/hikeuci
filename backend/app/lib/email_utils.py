import base64
import mimetypes
from dataclasses import dataclass
from pathlib import Path

from ..models import Member, MagicLink, Signup, Hike, Vote
from flask import current_app

endpoint_dict = {
    "voting": "vote",
    "signup": "signup",
    "waiver": "waiver"
}


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

    base_url = current_app.config.get("BASE_URL", "").rstrip("/")

    # Transactional Emails
    if email_type == "waiver_confirmation":
        # re-use old (consumed) magic-url for cancellations
        ml = (MagicLink.query.filter_by
              (member_id=member.id,
               hike_id=hike.id,
               type="waiver")
              .first())

        personalization["magic_url"] = f"{base_url}/{endpoint_dict['waiver']}?token={ml.token}"

        return personalization

    # Access-Protected Emails (Needs new magic link)

    # First check for existing ML. Clear it if found.
    _remove_magic_link(member.id, hike.id, email_type)

    # Then, generate new ML.
    mlm = current_app.extensions.get("magic_link_manager")
    token = mlm.generate(member_id=member.id, hike_id=hike.id, type=email_type)

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


@dataclass
class EmailFile:
    filename: str
    file_bytes: bytes
    maintype: str = "application"
    subtype: str = "octet-stream"
    disposition: str = "inline"   # or "attachment"
    cid: str | None = None        # for inline images, e.g. Content-ID

    def to_dict(self) -> dict:
        return {
            "filename": self.filename,
            "maintype": self.maintype,
            "subtype": self.subtype,
            "disposition": self.disposition,
            "cid": self.cid,
            # JSON-safe: bytes -> base64 string
            "file_b64": base64.b64encode(self.file_bytes).decode("ascii"),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EmailFile":
        return cls(
            filename=data["filename"],
            file_bytes=base64.b64decode(data["file_b64"]),
            maintype=data.get("maintype", "application"),
            subtype=data.get("subtype", "octet-stream"),
            disposition=data.get("disposition", "inline"),
            cid=data.get("cid"),
        )

    @classmethod
    def from_path(cls, path: str | Path, *, disposition: str = "attachment", cid: str | None = None) -> "EmailFile":
        path = Path(path)
        file_bytes = path.read_bytes()
        mime, _ = mimetypes.guess_type(str(path))
        if mime:
            maintype, subtype = mime.split("/", 1)
        else:
            maintype, subtype = "application", "octet-stream"
        return cls(
            filename=path.name,
            file_bytes=file_bytes,
            maintype=maintype,
            subtype=subtype,
            disposition=disposition,
            cid=cid,
        )