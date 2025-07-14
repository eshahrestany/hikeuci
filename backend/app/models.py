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

    signups        = db.relationship('Signup',        back_populates='member',       lazy=True)
    waivers        = db.relationship('Waiver',        back_populates='member',       lazy=True)
    hikers_history = db.relationship('HikersHistory', back_populates='member',       lazy=True)
    hikes_led      = db.relationship('Hike',         back_populates='leader',       lazy=True)
    vehicles       = db.relationship('Vehicle',       back_populates='member',       lazy=True)
    logs           = db.relationship('Log',           back_populates='member',       lazy=True)


class Trail(db.Model):
    __tablename__ = 'trails'
    id                       = db.Column(db.Integer, primary_key=True)
    name                     = db.Column(db.String(150), nullable=False)
    length_km                = db.Column(db.Float, nullable=True)
    difficulty               = db.Column(db.Integer, nullable=True)
    added_on                 = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    alltrails_endpoint       = db.Column(db.String(300), nullable=True)
    trailhead_gmaps_endpoint = db.Column(db.String(300), nullable=True)
    trailhead_amaps_endpoint = db.Column(db.String(300), nullable=True)
    notes                    = db.Column(db.String(300), nullable=True)

    signups        = db.relationship('Signup',       back_populates='trail',       lazy=True)
    hikers_history = db.relationship('HikersHistory', back_populates='trail',       lazy=True)
    hikes  = db.relationship('Hike',  back_populates='trail',       lazy=True)


class Signup(db.Model):
    __tablename__ = 'signups'
    id          = db.Column(db.Integer, primary_key=True)
    member_id   = db.Column(db.Integer, db.ForeignKey('members.id', ondelete='CASCADE'), nullable=False)
    trail_id    = db.Column(db.Integer, db.ForeignKey('trails.id', ondelete='CASCADE'),  nullable=False)
    signup_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    member = db.relationship('Member', back_populates='signups')
    trail  = db.relationship('Trail',  back_populates='signups')


class Waiver(db.Model):
    __tablename__ = 'waivers'
    id          = db.Column(db.Integer, primary_key=True)
    member_id   = db.Column(db.Integer, db.ForeignKey('members.id', ondelete='CASCADE'), nullable=False)
    signed_on   = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    waiver_text = db.Column(db.Text, nullable=True)

    member = db.relationship('Member', back_populates='waivers')


class HikersHistory(db.Model):
    __tablename__ = 'hikers_history'
    id         = db.Column(db.Integer, primary_key=True)
    member_id  = db.Column(db.Integer, db.ForeignKey('members.id', ondelete='CASCADE'), nullable=False)
    trail_id   = db.Column(db.Integer, db.ForeignKey('trails.id', ondelete='CASCADE'),  nullable=False)
    date_hiked = db.Column(db.DateTime, nullable=False)
    notes      = db.Column(db.Text, nullable=True)

    member = db.relationship('Member', back_populates='hikers_history')
    trail  = db.relationship('Trail',  back_populates='hikers_history')


class Hike(db.Model):
    __tablename__ = 'hikes'
    id         = db.Column(db.Integer, primary_key=True)
    trail_id   = db.Column(db.Integer, db.ForeignKey('trails.id', ondelete='CASCADE'),  nullable=False)
    hike_date  = db.Column(db.DateTime, nullable=False)
    leader_id  = db.Column(db.Integer, db.ForeignKey('members.id', ondelete='SET NULL'), nullable=True)
    is_upcoming= db.Column(db.Boolean, default=False, nullable=False)
    notes      = db.Column(db.Text, nullable=True)

    trail  = db.relationship('Trail',  back_populates='hikes')
    leader = db.relationship('Member', back_populates='hikes_led')


class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    id              = db.Column(db.Integer, primary_key=True)
    member_id       = db.Column(db.Integer, db.ForeignKey('members.id', ondelete='CASCADE'), nullable=False)
    year            = db.Column(db.Integer, nullable=False)
    make            = db.Column(db.String(50), nullable=False)
    model           = db.Column(db.String(50), nullable=False)
    passenger_seats = db.Column(db.Integer, nullable=False)

    member = db.relationship('Member', back_populates='vehicles')


class Log(db.Model):
    __tablename__ = 'logs'
    id          = db.Column(db.Integer, primary_key=True)
    timestamp   = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    member_id   = db.Column(db.Integer, db.ForeignKey('members.id', ondelete='SET NULL'), nullable=True)
    method      = db.Column(db.String(10), nullable=False)
    path        = db.Column(db.String(300), nullable=False)
    status_code = db.Column(db.Integer, nullable=False)
    extra       = db.Column(db.Text, nullable=True)

    member = db.relationship('Member', back_populates='logs')


class AdminUser(db.Model):
    __tablename__ = 'admin_users'

    id                 = db.Column(db.Integer, primary_key=True)
    provider           = db.Column(db.String(50), nullable=False, default='google')
    provider_user_id   = db.Column(db.String(255), unique=True, nullable=False)
    email              = db.Column(db.String(120), unique=True, nullable=False)
    created_on         = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

