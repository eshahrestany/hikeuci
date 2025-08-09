import secrets
import datetime
from flask import current_app
from ..models import MagicLink


class MagicLinkManager:
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    @property
    def db(self):
        return current_app.extensions['sqlalchemy'].db

    def init_app(self, app):
        app.extensions['magic_link_manager'] = self

    def generate(self, user, hike_id):
        token = secrets.token_urlsafe(32)
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=7)

        magic_link = MagicLink(
            token=token,
            user_id=user.id,
            expires_at=expires_at,
            hike_id=hike_id
        )
        self.db.session.add(magic_link)
        self.db.session.commit()

        return token

    def validate(self, token):
        magic_link = MagicLink.query.filter_by(token=token).first()

        if not magic_link:
            return {'status': 'not_found', 'user': None}

        if magic_link.expires_at < datetime.datetime.utcnow():
            return {'status': 'expired', 'user': magic_link.user}

        if magic_link.is_used:
            return {'status': 'used', 'user': magic_link.user}

        return {'status': 'valid', 'magic_link': magic_link}

    def mark_as_used(self, token):
        magic_link = MagicLink.query.filter_by(token=token).first()
        if magic_link and not magic_link.is_used and magic_link.expires_at >= datetime.datetime.utcnow():
            magic_link.is_used = True
            self.db.session.commit()
            return True
        return False
