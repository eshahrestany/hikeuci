from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from .extensions import db


class Member(db.Model):
    __tablename__ = 'members'
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    tel        = db.Column(db.String(15), nullable=True)
    joined_on  = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    is_officer = db.Column(db.Boolean, default=False, nullable=False)


class Trail(db.Model):
    __tablename__ = 'trails'
    id                       = db.Column(db.Integer, primary_key=True)
    is_active_vote_candidate = db.Column(db.Boolean, default=False, nullable=False)
    name                     = db.Column(db.String(150), nullable=False)
    location                 = db.Column(db.String(150), nullable=False)
    length_mi                = db.Column(db.Float, nullable=False)
    estimated_time_hr        = db.Column(db.Float, nullable=False)
    required_water_liters    = db.Column(db.Float, nullable=False)
    difficulty               = db.Column(db.Integer, nullable=False)  # 0=e,1=m,2=d,3=vd
    added_on                 = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    alltrails_endpoint       = db.Column(db.String(300), nullable=True)
    trailhead_gmaps_endpoint = db.Column(db.String(300), nullable=True)
    trailhead_amaps_endpoint = db.Column(db.String(300), nullable=True)
    description              = db.Column(db.Text, nullable=True)


class Hike(db.Model):
    """
    Hikes table. Use `status` to indicate lifecycle:
    'active' current weekly hike and has non-null phase, 'completed' (past), 'canceled' (past)
    """
    __tablename__ = 'hikes'
    id        = db.Column(db.Integer, primary_key=True)
    trail_id  = db.Column(db.Integer, db.ForeignKey('trails.id'), default=None, nullable=True)
    status    = db.Column(db.String(20), nullable=False, index=True, default='active')  # 'active' or 'past'
    phase     = db.Column(db.String(20), nullable=True)  #  for status=active: None [pending vote start], 'voting', 'signups', 'waiver'
    email_campaign_completed = db.Column(db.Boolean, nullable=False, default=False)
    # dates
    created_date   = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    voting_date = db.Column(db.DateTime, nullable=False) # when votes are sent
    signup_date = db.Column(db.DateTime, nullable=False)
    waiver_date = db.Column(db.DateTime, nullable=False)
    hike_date = db.Column(db.DateTime, nullable=False, index=True)
    # future proofing for far-flung adventures // probably won't ever be needed
    tz = db.Column(db.String(64), nullable=False, default="America/Los_Angeles")

    def get_localized_time(self, date_var):
        dt = getattr(self, date_var, None)
        if type(dt) is not datetime:
            raise ValueError(f"{date_var} is not a valid date field on Hike")

        dt = dt.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo(self.tz))

        return dt

class Signup(db.Model):
    __tablename__ = 'signups'
    id             = db.Column(db.Integer, primary_key=True)
    member_id      = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    hike_id        = db.Column(db.Integer, db.ForeignKey('hikes.id'), nullable=False)
    signup_date    = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    transport_type = db.Column(db.String(20), nullable=False)  # 'passenger','driver','self'
    food_interest  = db.Column(db.Boolean, nullable=False)
    is_checked_in  = db.Column(db.Boolean, nullable=False, default=False)
    status = db.Column(db.String(50), nullable=False, default='pending')  # 'pending','confirmed','waitlisted'
    waitlist_pos = db.Column(db.Integer, nullable=True)
    vehicle_id     = db.Column(db.Integer, db.ForeignKey('vehicles.id'), default=None, nullable=True)


class Waiver(db.Model):
    __tablename__ = 'waivers'
    id        = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    hike_id   = db.Column(db.Integer, db.ForeignKey('hikes.id'), nullable=False)
    print_name = db.Column(db.String(50), nullable=False)
    is_minor  = db.Column(db.Boolean, nullable=False)
    age       = db.Column(db.Integer, nullable=True)
    signature_1_b64 = db.Column(db.Text, nullable=False)
    signature_2_b64 = db.Column(db.Text, nullable=False)
    signed_on = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)



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
    created_on       = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)


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
    member_id  = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    hike_id    = db.Column(db.Integer, db.ForeignKey('hikes.id'), nullable=False)
    type       = db.Column(db.String(20), nullable=False)  # 'voting', 'signups', 'waiver'
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    first_used = db.Column(db.DateTime, nullable=True)
    used_count = db.Column(db.Integer, nullable=False, default=0)


class EmailCampaign(db.Model):
    __tablename__ = 'email_campaigns'
    id             = db.Column(db.Integer, primary_key=True)
    hike_id        = db.Column(db.Integer, db.ForeignKey('hikes.id'), nullable=False)
    type           = db.Column(db.String(50), nullable=False)  # 'voting', 'signups', 'waiver'
    date_created   = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    date_completed = db.Column(db.DateTime, nullable=True)


class EmailTask(db.Model):
    __tablename__ = 'email_tasks'
    id                = db.Column(db.Integer, primary_key=True)
    campaign_id       = db.Column(db.Integer, db.ForeignKey('email_campaigns.id'), nullable=False)
    member_id         = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    status            = db.Column(db.String(20), nullable=False, default='pending')  # 'pending', 'sent', 'failed'
    attempts          = db.Column(db.Integer, nullable=False, default=0)
    sent_at           = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<MagicLink {self.token}>'
