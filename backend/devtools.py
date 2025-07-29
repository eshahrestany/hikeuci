#!/usr/bin/env python3
"""
Seed and clear the HikeUCI database for three test scenarios:
  - voting: 3 active hikes in 'voting' phase, ~50 members & votes per hike
  - signup: 1 active hike in 'signup' phase, ~50 signups with drivers & vehicles
  - waiver: 1 active hike in 'waiver' phase, ~50 members & waivers

Usage:
  python seed_db.py voting
  python seed_db.py signup
  python seed_db.py waiver
"""
import random
from datetime import datetime, timedelta, UTC

from app.extensions import db
from app.models import (
    Member,
    Trail,
    Signup,
    Waiver,
    Vehicle,
    Vote,
    ActiveHike, HikersHistory, Hike,
)


def clear_db():
    # 1) dependent child tables first
    for model in (
        Signup, Vote, Waiver, Vehicle, ActiveHike,
        HikersHistory, Hike, Trail, Member
    ):
        db.session.query(model).delete()
    db.session.commit()
    print("Database cleared.")


def seed_voting():
    clear_db()
    # Create 3 sample trails
    trails = [
        Trail(name=f"Trail {i+1}", length_mi=random.uniform(3, 10), difficulty=random.randint(1, 5))
        for i in range(3)
    ]
    db.session.add_all(trails)
    db.session.commit()

    # Create 3 active hikes (voting phase)
    active_hikes = []
    base = datetime.now(UTC)
    for i, trail in enumerate(trails):
        ah = ActiveHike(
            status='voting',
            planned_date=base + timedelta(days=i + 1),
            trail_id=trail.id,
        )
        active_hikes.append(ah)
    db.session.add_all(active_hikes)
    db.session.commit()

    # Generate members: ~50 per hike
    members = []
    total_members = 50 * len(active_hikes)
    for i in range(total_members):
        m = Member(
            name=f"Member{i}",
            email=f"user{i}@example.com"
        )
        members.append(m)
    db.session.add_all(members)
    db.session.commit()

    # Create votes: each member votes for one random hike
    votes = [
        Vote(
            member_id=m.id,
            active_hike_id=random.choice(active_hikes).id
        )
        for m in members
    ]
    db.session.add_all(votes)
    db.session.commit()

    print("Seeded 'voting' scenario.")


def seed_signup():
    clear_db()
    # Create one trail
    trail = Trail(name="Signup Trail", length_mi=5.0, difficulty=3)
    db.session.add(trail)
    db.session.commit()

    # Create one active hike (signup phase)
    ah = ActiveHike(
        status='signup',
        planned_date=datetime.now(UTC) + timedelta(days=7),
        trail_id=trail.id
    )
    db.session.add(ah)
    db.session.commit()

    # Create ~50 members
    members = []
    for i in range(50):
        m = Member(
            name=f"Member{i}",
            email=f"member{i}@example.com"
        )
        members.append(m)
    db.session.add_all(members)
    db.session.commit()

    # Pick ~10 drivers and give them vehicles
    drivers = random.sample(members, 10)
    vehicles = []
    for m in drivers:
        v = Vehicle(
            member_id=m.id,
            year=2018 + random.randint(0, 3),
            make="MakeX",
            model="ModelY",
            passenger_seats=random.randint(2, 6)
        )
        vehicles.append(v)
    db.session.add_all(vehicles)
    db.session.commit()

    # Create signups: drivers + passengers
    signups = []
    for m in members:
        if m in drivers:
            vid = next(v.id for v in vehicles if v.member_id == m.id)
            signups.append(Signup(
                member_id=m.id,
                active_hike_id=ah.id,
                transport_type="driver",
                vehicle_id=vid
            ))
        else:
            signups.append(Signup(
                member_id=m.id,
                active_hike_id=ah.id,
                transport_type="passenger",
                vehicle_id=None
            ))
    db.session.add_all(signups)
    db.session.commit()

    print("Seeded 'signup' scenario.")


def seed_waiver():
    clear_db()
    # Create one trail
    trail = Trail(name="Waiver Trail", length_mi=6.5, difficulty=4)
    db.session.add(trail)
    db.session.commit()

    # Create one active hike (waiver phase)
    ah = ActiveHike(
        status='waiver',
        planned_date=datetime.now(UTC) + timedelta(days=3),
        trail_id=trail.id
    )
    db.session.add(ah)
    db.session.commit()

    members = []
    for i in range(50):
        m = Member(
            name=f"Member{i}",
            email=f"waiver{i}@example.com"
        )
        members.append(m)
    db.session.add_all(members)
    db.session.commit()

    # Create vehicles and signups similar to signup scenario
    drivers = random.sample(members, 8)
    vehicles = []
    for m in drivers:
        v = Vehicle(
            member_id=m.id,
            year=2015 + random.randint(0, 5),
            make="MakeA",
            model="ModelB",
            passenger_seats=random.randint(2, 7)
        )
        vehicles.append(v)
    db.session.add_all(vehicles)
    db.session.commit()

    signups = []
    for m in random.sample(members, 40):
        if m in drivers:
            vid = next(v.id for v in vehicles if v.member_id == m.id)
            signups.append(Signup(
                member_id=m.id,
                active_hike_id=ah.id,
                transport_type="driver",
                vehicle_id=vid
            ))
        else:
            signups.append(Signup(
                member_id=m.id,
                active_hike_id=ah.id,
                transport_type="passenger",
                vehicle_id=None
            ))
    db.session.add_all(signups)
    db.session.commit()

    # No votes in waiver scenario

    # Create waivers for half the members
    waivers = [
        Waiver(
            member_id=m.id,
            signed_on=datetime.now(UTC) - timedelta(days=random.randint(0, 2)),
            active_hike_id=ah.id
        )
        for m in random.sample(members, 25)
    ]
    db.session.add_all(waivers)
    db.session.commit()

    print("Seeded 'waiver' scenario.")


if __name__ == '__main__':
    import sys
    from app import create_app
    app = create_app()

    with app.app_context():
        if len(sys.argv) != 2 or sys.argv[1] not in ('voting','signup','waiver'):
            print(__doc__)
            sys.exit(1)
        phase = sys.argv[1]
        if phase == 'voting':
            seed_voting()
        elif phase == 'signup':
            seed_signup()
        elif phase == 'waiver':
            seed_waiver()

