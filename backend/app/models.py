from datetime import datetime
from .extensions import db


class Member(db.Model):
    __tablename__ = 'members'
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    tel        = db.Column(db.String(32), nullable=True)  # E164
    joined_on  = db.Column(db.DateTime, default=datetime.now, nullable=False)
    is_officer = db.Column(db.Boolean, default=False, nullable=False)


class Trail(db.Model):
    __tablename__ = 'trails'
    id                       = db.Column(db.Integer, primary_key=True)
    name                     = db.Column(db.String(150), nullable=False)
    length_mi                = db.Column(db.Float, nullable=True)
    difficulty               = db.Column(db.Integer, nullable=True)  # 0=e,1=m,2=d,3=vd
    added_on                 = db.Column(db.DateTime, default=datetime.now, nullable=False)
    alltrails_endpoint       = db.Column(db.String(300), nullable=True)
    trailhead_gmaps_endpoint = db.Column(db.String(300), nullable=True)
    trailhead_amaps_endpoint = db.Column(db.String(300), nullable=True)
    notes                    = db.Column(db.String(300), nullable=True)
    description              = db.Column(db.Text, nullable=True)


class Hike(db.Model):
    """
    Hikes table. Use `status` to indicate lifecycle:
    'active' current weekly hike and has non-null phase, 'completed' (past), 'canceled' (past)
    """
    __tablename__ = 'hikes'
    id        = db.Column(db.Integer, primary_key=True)
    trail_id  = db.Column(db.Integer, db.ForeignKey('trails.id'), default=None, nullable=True)
    hike_date = db.Column(db.DateTime, nullable=False, index=True)
    status    = db.Column(db.String(20), nullable=False, index=True, default='scheduled')
    phase     = db.Column(db.String(20), nullable=True, default='pre-hike')  #  for status=active: 'voting', 'signups', 'waiver'
    notes     = db.Column(db.Text, nullable=True)



class Signup(db.Model):
    __tablename__ = 'signups'
    id             = db.Column(db.Integer, primary_key=True)
    member_id      = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    hike_id        = db.Column(db.Integer, db.ForeignKey('hikes.id'), nullable=False)
    signup_date    = db.Column(db.DateTime, default=datetime.now, nullable=False)
    transport_type = db.Column(db.String(20), nullable=False)  # 'passenger','driver','self'
    is_checked_in  = db.Column(db.Boolean, nullable=False, default=False)
    vehicle_id     = db.Column(db.Integer, db.ForeignKey('vehicles.id'), default=None, nullable=True)
    status         = db.Column(db.String(50), nullable=False, default='pending')  # 'pending','confirmed','waitlisted'
    waitlist_pos   = db.Column(db.Integer, nullable=True)


class Waiver(db.Model):
    __tablename__ = 'waivers'
    id        = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    hike_id   = db.Column(db.Integer, db.ForeignKey('hikes.id'), nullable=False)
    signed_on = db.Column(db.DateTime, default=datetime.now, nullable=False)


class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    id              = db.Column(db.Integer, primary_key=True)
    member_id       = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    year            = db.Column(db.Integer, nullable=False)
    make            = db.Column(db.String(50), nullable=False)
    model           = db.Column(db.String(50), nullable=False)
    passenger_seats = db.Column(db.Integer, nullable=False)


class AdminUser(db.Model):
    __tablename__ = 'admin_users'
    id               = db.Column(db.Integer, primary_key=True)
    provider         = db.Column(db.String(50), nullable=False, default='google')
    provider_user_id = db.Column(db.String(255), unique=True, nullable=False)
    email            = db.Column(db.String(120), unique=True, nullable=False)
    created_on       = db.Column(db.DateTime, default=datetime.now, nullable=False)


class Vote(db.Model):
    __tablename__ = "votes"
    id        = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=True)
    trail_id  = db.Column(db.Integer, db.ForeignKey('trails.id'), nullable=False)
    hike_id   = db.Column(db.Integer, db.ForeignKey('hikes.id'), nullable=False)


class MagicLink(db.Model):
    __tablename__ = 'magic_links'
    id         = db.Column(db.Integer, primary_key=True)
    token      = db.Column(db.String(64), unique=True, nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    hike_id    = db.Column(db.Integer, db.ForeignKey('hikes.id'), nullable=False)
    user       = db.relationship('Member', backref=db.backref('magic_links', lazy=True))
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used    = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __repr__(self):
        return f'<MagicLink {self.token}>'
