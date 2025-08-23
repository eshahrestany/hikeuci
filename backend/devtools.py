#!/usr/bin/env python3
"""
Seed and clear the HikeUCI database for three test scenarios (post-refactor):
  - voting: 1 active Hike in 'voting' phase (no trail selected), ~50 members voting among 3 Trails
  - signup: 1 active Hike in 'signups' phase with a Trail, ~50 signups incl. drivers & vehicles
  - waiver: 1 active Hike in 'waiver' phase with a Trail, ~40 confirmed + waitlist, ~20 waivers

Usage:
  python seed_db.py voting
  python seed_db.py signup
  python seed_db.py waiver
"""
import random
from datetime import datetime, timedelta

from app.extensions import db
from app.models import (
    Member,
    Trail,
    Signup,
    Waiver,
    Vehicle,
    Vote,
    Hike,
    MagicLink,   # if present; safe to import
)


def clear_db():
    """Delete in child→parent order to satisfy FKs."""
    for model in (
        MagicLink,
        Signup,
        Vote,
        Waiver,
        Vehicle,
        Hike,
        Trail,
        Member,
    ):
        try:
            db.session.query(model).delete()
        except Exception:
            # In case a model isn't present in your current app build
            pass
    db.session.commit()
    print("Database cleared.")


def seed_voting():
    clear_db()

    # 3 candidate trails
    trails = [
        Trail(
            name=f"Trail {i+1}",
            length_mi=round(random.uniform(3, 10), 1),
            difficulty=random.randint(0, 3),
            is_active_vote_candidate=True,
        )
        for i in range(3)
    ]
    db.session.add_all(trails)
    db.session.commit()

    # one active hike in VOTING phase, NO trail selected yet
    hike = Hike(
        hike_date=datetime.now() + timedelta(days=3),
        status="active",
        phase="voting",
    )
    db.session.add(hike)
    db.session.commit()

    # ~50 members
    members = [Member(name=f"Member{i}", email=f"user{i}@example.com") for i in range(50)]
    db.session.add_all(members)
    db.session.commit()

    # each member casts one vote for one of the 3 trails
    votes = [Vote(member_id=m.id, hike_id=hike.id, trail_id=random.choice(trails).id) for m in members]
    db.session.add_all(votes)
    db.session.commit()

    print("Seeded 'voting' scenario.")



def seed_signup():
    """
    One active hike in 'signups' phase with a selected trail.
    ~50 members; ~10 drivers with vehicles; others passengers.
    """
    clear_db()

    # 1) Trail
    trail = Trail(
        name="Santiago Creek Trail and Barnham Ridge",
        length_mi=6.0,
        difficulty=2,  # Moderate
        description=(
            "This Saturday, we will be hiking Santiago Creek Trail and Barnham Ridge in Santiago Oaks Park. "
            "The hike is around 6 miles (~2.5 hours), rated Moderate. Meet at UTC 7:45 AM, depart 8:00 AM. "
            "Drivers are guaranteed a spot; form closes Thursday evening. Bring at least 1L of water."
        ),
    )
    db.session.add(trail)
    db.session.commit()

    # 2) Active hike in SIGNUPS phase (trail chosen)
    hike = Hike(
        trail_id=trail.id,
        hike_date=datetime.now() + timedelta(days=7),
        status="active",
        phase="signup",
    )
    db.session.add(hike)
    db.session.commit()

    # 3) ~50 members
    members = [
        Member(name=f"Member{i}", email=f"member{i}@example.com")
        for i in range(50)
    ]
    db.session.add_all(members)
    db.session.commit()

    # 4) ~10 drivers with vehicles
    drivers = random.sample(members, k=10)
    vehicles = []
    for m in drivers:
        vehicles.append(
            Vehicle(
                member_id=m.id,
                year=2018 + random.randint(0, 6),
                make="MakeX",
                model="ModelY",
                passenger_seats=random.randint(2, 6),
            )
        )
    db.session.add_all(vehicles)
    db.session.commit()

    # 5) Signups: drivers + passengers
    signups = []
    for m in members:
        if m in drivers:
            vid = next(v.id for v in vehicles if v.member_id == m.id)
            signups.append(
                Signup(
                    member_id=m.id,
                    hike_id=hike.id,
                    transport_type="driver",
                    vehicle_id=vid,
                    status="pending",
                )
            )
        else:
            signups.append(
                Signup(
                    member_id=m.id,
                    hike_id=hike.id,
                    transport_type="passenger",
                    status="pending",
                )
            )
    db.session.add_all(signups)
    db.session.commit()

    print("Seeded 'signups' scenario.")


def seed_waiver():
    """
    One ACTIVE hike in 'waiver' phase with a selected trail.
    ~40 confirmed spots (drivers/self/passengers up to capacity), rest waitlisted.
    ~20 waivers created.
    """
    clear_db()

    # 1) Trail
    trail = Trail(name="Waiver Trail", length_mi=6.5, difficulty=3)
    db.session.add(trail)
    db.session.commit()

    # 2) Active hike in WAIVER phase
    hike = Hike(
        trail_id=trail.id,
        hike_date=datetime.now() + timedelta(days=3),
        status="active",
        phase="waiver",
    )
    db.session.add(hike)
    db.session.commit()

    # 3) Members
    members = [
        Member(name=f"Member{i}", email=f"waiver{i}@example.com")
        for i in range(50)
    ]
    db.session.add_all(members)
    db.session.commit()

    # Shuffle for random role assignment
    pool = members[:]
    random.shuffle(pool)

    num_drivers = random.randint(8, 10)
    num_self = random.randint(0, 4)
    total_signups_target = 40  # desired number of signups (confirmed+waitlist)

    drivers = pool[:num_drivers]
    self_transporters = pool[num_drivers:num_drivers + num_self]
    remaining = pool[num_drivers + num_self:]

    passenger_slots = max(0, total_signups_target - (num_drivers + num_self))
    passengers = random.sample(remaining, k=min(len(remaining), passenger_slots))

    # 4) Vehicles for drivers
    vehicles = []
    for d in drivers:
        seats = random.randint(3, 4)
        vehicles.append(
            Vehicle(
                member_id=d.id,
                year=random.randint(2015, 2022),
                make="MakeA",
                model="ModelB",
                passenger_seats=seats,
            )
        )
    db.session.add_all(vehicles)
    db.session.commit()

    # 5) Capacity based on vehicles
    capacity = sum(v.passenger_seats for v in vehicles)

    # 6) Build signups
    signups = []

    # Drivers (confirmed)
    for d in drivers:
        vid = next(v.id for v in vehicles if v.member_id == d.id)
        signups.append(
            Signup(
                member_id=d.id,
                hike_id=hike.id,
                transport_type="driver",
                vehicle_id=vid,
                status="confirmed",
            )
        )

    # Self-transport (confirmed)
    for s in self_transporters:
        signups.append(
            Signup(
                member_id=s.id,
                hike_id=hike.id,
                transport_type="self",
                status="confirmed",
            )
        )

    # Passengers — confirmed up to capacity, rest waitlisted
    confirmed_used = 0
    for idx, p in enumerate(passengers, start=1):
        if confirmed_used < capacity:
            status = "confirmed"
            waitlist_pos = None
            confirmed_used += 1
        else:
            status = "waitlisted"
            waitlist_pos = idx - capacity
        signups.append(
            Signup(
                member_id=p.id,
                hike_id=hike.id,
                transport_type="passenger",
                status=status,
                waitlist_pos=waitlist_pos,
            )
        )

    db.session.add_all(signups)
    db.session.commit()

    # 7) Create waivers for ~20 random members (of those signed up)
    signed_member_ids = [s.member_id for s in signups]
    waiver_members = random.sample(signed_member_ids, k=min(20, len(signed_member_ids)))
    waivers = [
        Waiver(
            member_id=mid,
            hike_id=hike.id,
            signed_on=datetime.now() - timedelta(days=random.randint(0, 2)),
        )
        for mid in waiver_members
    ]
    db.session.add_all(waivers)
    db.session.commit()

    print("Seeded 'waiver' scenario.")


if __name__ == '__main__':
    import sys
    from app import create_app

    app = create_app()
    with app.app_context():
        if len(sys.argv) != 2 or sys.argv[1] not in ('voting', 'signup', 'waiver'):
            print(__doc__)
            sys.exit(1)

        phase = sys.argv[1]
        if phase == 'voting':
            seed_voting()
        elif phase == 'signup':
            seed_signup()
        elif phase == 'waiver':
            seed_waiver()
