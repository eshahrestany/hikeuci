import secrets
from datetime import datetime

from ..models import MagicLink, Hike


class MagicLinkManager:
    def __init__(self, app, db):
        if app:
            self.init_app(app)
        if db:
            self.db = db

    def init_app(self, app):
        app.extensions['magic_link_manager'] = self

    """Generates a magic link token, specific to a user, hike, and type. The link expires at the end of the current phase."""
    def generate(self, member_id: int, hike_id: int, type: str):
        token = secrets.token_urlsafe(32)

        magic_link = MagicLink(
            token=token,
            member_id=member_id,
            hike_id=hike_id,
            type=type
        )
        self.db.session.add(magic_link)
        self.db.session.commit()

        return token

    def validate(self, token):
        magic_link = MagicLink.query.filter_by(token=token).first()

        if not magic_link:
            return {'status': 'not_found', 'user': None}

        associated_hike = Hike.query.get(magic_link.hike_id)
        if not associated_hike:
            return {'status': 'invalid_hike_id', 'user': magic_link.user_id}

        if associated_hike.status != 'active' or magic_link.type != associated_hike.phase:
            return {'status': 'expired', 'user': magic_link.user_id}

        if not magic_link.first_used:
            magic_link.first_use = datetime.now()
        magic_link.used_count += 1

        return {'status': 'valid', 'magic_link': magic_link}
