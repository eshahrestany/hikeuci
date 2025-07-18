from datetime import datetime
from .extensions import db


class Member(db.Model):
    __tablename__ = 'members'
    id         = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name  = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    joined_on  = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_officer = db.Column(db.Boolean, default=False, nullable=False)


class Trail(db.Model):
    __tablename__ = 'trails'
    id                       = db.Column(db.Integer, primary_key=True)
    name                     = db.Column(db.String(150), nullable=False)
    length_mi                = db.Column(db.Float, nullable=True)
    difficulty               = db.Column(db.Integer, nullable=True)
    added_on                 = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    alltrails_endpoint       = db.Column(db.String(300), nullable=True)
    trailhead_gmaps_endpoint = db.Column(db.String(300), nullable=True)
    trailhead_amaps_endpoint = db.Column(db.String(300), nullable=True)
    notes                    = db.Column(db.String(300), nullable=True)


class Signup(db.Model):
    __tablename__ = 'signups'
    id          = db.Column(db.Integer, primary_key=True)
    member_id   = db.Column(db.Integer, db.ForeignKey('members.id', ondelete='CASCADE'), nullable=False)
    trail_id    = db.Column(db.Integer, db.ForeignKey('trails.id', ondelete='CASCADE'),  nullable=False)
    signup_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Waiver(db.Model):
    __tablename__ = 'waivers'
    id          = db.Column(db.Integer, primary_key=True)
    member_id   = db.Column(db.Integer, db.ForeignKey('members.id', ondelete='CASCADE'), nullable=False)
    signed_on   = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    waiver_text = db.Column(db.Text, nullable=True)


class HikersHistory(db.Model):
    __tablename__ = 'hikers_history'
    id         = db.Column(db.Integer, primary_key=True)
    member_id  = db.Column(db.Integer, db.ForeignKey('members.id', ondelete='CASCADE'), nullable=False)
    trail_id   = db.Column(db.Integer, db.ForeignKey('trails.id', ondelete='CASCADE'),  nullable=False)
    date_hiked = db.Column(db.DateTime, nullable=False)
    notes      = db.Column(db.Text, nullable=True)


class Hike(db.Model):
    __tablename__ = 'hikes'
    id         = db.Column(db.Integer, primary_key=True)
    trail_id   = db.Column(db.Integer, db.ForeignKey('trails.id'),  nullable=False)
    hike_date  = db.Column(db.DateTime, nullable=False)
    leader_id  = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=True)
    status    = db.Column(db.String, default=None, nullable=True)
    notes      = db.Column(db.Text, nullable=True)


class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    id              = db.Column(db.Integer, primary_key=True)
    member_id       = db.Column(db.Integer, db.ForeignKey('members.id', ondelete='CASCADE'), nullable=False)
    year            = db.Column(db.Integer, nullable=False)
    make            = db.Column(db.String(50), nullable=False)
    model           = db.Column(db.String(50), nullable=False)
    passenger_seats = db.Column(db.Integer, nullable=False)


class AdminUser(db.Model):
    __tablename__ = 'admin_users'

    id                 = db.Column(db.Integer, primary_key=True)
    provider           = db.Column(db.String(50), nullable=False, default='google')
    provider_user_id   = db.Column(db.String(255), unique=True, nullable=False)
    email              = db.Column(db.String(120), unique=True, nullable=False)
    created_on         = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Vote(db.Model):
    __tablename__ = "votes"

    id = db.Column(db.Integer, primary_key=True)
    member_id   = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=True)
    trail_id   = db.Column(db.Integer, db.ForeignKey('trails.id'),  nullable=False)
    active_hike_id = db.Column(db.Integer, db.ForeignKey('active_hike.id'))


class ActiveHike(db.Model):
    __tablename__ = "active_hike"

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50), nullable=False)
    planned_date = db.Column(db.DateTime, nullable=False)
    trail_id = db.Column(db.Integer, db.ForeignKey('trails.id'), nullable=False)
    num_votes = db.Column(db.Integer, nullable=True, default=0)
    num_signups = db.Column(db.Integer, nullable=True, default=0)
    num_waivers_sent = db.Column(db.Integer, nullable=True, default=0)
    num_waivers_filled = db.Column(db.Integer, nullable=True, default=0)

