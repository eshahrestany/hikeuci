#!/usr/bin/env python3
"""
Seed and clear the HikeUCI database for three test scenarios (post-refactor):
  - voting: 1 active Hike in 'voting' phase (no trail selected), ~50 members voting among 3 Trails
  - signup: 1 active Hike in 'signups' phase with a Trail, ~50 signups incl. drivers & vehicles
  - waiver: 1 active Hike in 'waiver' phase with a Trail, ~40 confirmed + waitlist, ~20 waivers

Usage:
  python devtools.py voting
  python devtools.py signup
  python devtools.py waiver
"""
import random
from datetime import datetime, timedelta, timezone

from app.extensions import db
from app.models import (
    Member,
    Trail,
    Signup,
    Waiver,
    Vehicle,
    Vote,
    Hike,
    MagicLink,
    EmailCampaign,
    EmailTask
)


def clear_db():
    """Delete in child→parent order to satisfy FKs."""
    for model in (
        EmailTask,
        EmailCampaign,
        MagicLink,
        Signup,
        Vote,
        Waiver,
        Vehicle,
        Hike,
        Trail,
        Member,
    ):
        db.session.query(model).delete()
    db.session.commit()
    print("Database cleared.")


def seed_voting():
    clear_db()

    # 3 candidate trails
    trails = [
        Trail(
            name=f"Trail {i + 1}",
            location="Trail location",
            length_mi=round(random.uniform(3, 10), 1),
            estimated_time_hr=random.randint(2, 8) / 2.0,
            required_water_liters=random.randint(1, 4) / 2.0,
            difficulty=random.randint(0, 3),
            is_active_vote_candidate=True,
        )
        for i in range(3)
    ]
    db.session.add_all(trails)
    db.session.commit()

    # one active hike in VOTING phase, NO trail selected yet
    hike = Hike(
        status="active",
        phase="voting",
        voting_date=datetime.now(timezone.utc) + timedelta(days=1),
        signup_date=datetime.now(timezone.utc) + timedelta(days=3),
        waiver_date=datetime.now(timezone.utc) + timedelta(days=5),
        hike_date=datetime.now(timezone.utc) + timedelta(days=7)
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



def seed_email_vote():
    clear_db()

    # 3 candidate trails
    trails = [
        Trail(
            name=f"Trail {i+1}",
            location="Trail location",
            length_mi=round(random.uniform(3, 10), 1),
            estimated_time_hr=random.randint(2, 8)/2.0,
            required_water_liters=random.randint(1, 4)/2.0,
            difficulty=random.randint(0, 3),
            is_active_vote_candidate=True,
        )
        for i in range(3)
    ]
    db.session.add_all(trails)
    db.session.commit()

    # one active hike in voting phase, no trail selected yet
    hike = Hike(
        status="active",
        phase="voting",
        voting_date=datetime.now(timezone.utc) + timedelta(days=1),
        signup_date=datetime.now(timezone.utc) + timedelta(days=3),
        waiver_date=datetime.now(timezone.utc) + timedelta(days=5),
        hike_date=datetime.now(timezone.utc) + timedelta(days=7)
    )
    db.session.add(hike)
    db.session.commit()

    members = [Member(name="Evan Shahrestany", email="eashahre@uci.edu"),
               Member(name="Evan Shahrestany 2", email="evanshahrestany2@gmail.com"),
               Member(name="Evan Shahrestany 3", email="evanshahrestany3@gmail.com"),
               Member(name="Gabriel Dodge", email="gdodge@uci.edu"),
               Member(name="Sterling Radisay", email="sradisay@uci.edu")
               ]
    db.session.add_all(members)
    db.session.commit()

    print("Seeded 'email vote campaign' scenario.")



def seed_signup():
    """
    One active hike in 'signups' phase with a selected trail.
    ~50 members; ~10 drivers with vehicles; others passengers.
    """
    clear_db()

    # 1) Trails
    trails = [Trail(
        name="Santiago Creek Trail and Barnham Ridge",
        location="Santiago Canyon",
        length_mi=6.0,
        difficulty=2,  # Moderate
        estimated_time_hr=3.5,
        required_water_liters=1
    ), Trail(
        name="Crystal Cove Loop",
        location="Newport Coast",
        length_mi=7.5,
        difficulty=3,
        estimated_time_hr=4,
        required_water_liters=2,
    )]
    db.session.add_all(trails)
    db.session.commit()

    # 1.5) add some past hikes
    hikes = [Hike(
        trail_id=trails[0].id,
        status="past",
        phase=None,
        voting_date=datetime.now(timezone.utc) - timedelta(weeks=3, days=-1),
        signup_date=datetime.now(timezone.utc) - timedelta(weeks=3, days=-3),
        waiver_date=datetime.now(timezone.utc) - timedelta(weeks=3, days=-5),
        hike_date=datetime.now(timezone.utc) - timedelta(weeks=3, days=-7)
    ), Hike(
        trail_id=trails[1].id,
        status="past",
        phase=None,
        voting_date=datetime.now(timezone.utc) - timedelta(weeks=2, days=-1),
        signup_date=datetime.now(timezone.utc) - timedelta(weeks=2, days=-3),
        waiver_date=datetime.now(timezone.utc) - timedelta(weeks=2, days=-5),
        hike_date=datetime.now(timezone.utc) - timedelta(weeks=2, days=-7)
    ), Hike(
        trail_id=trails[0].id,
        status="past",
        phase=None,
        voting_date=datetime.now(timezone.utc) - timedelta(weeks=1, days=-1),
        signup_date=datetime.now(timezone.utc) - timedelta(weeks=1, days=-3),
        waiver_date=datetime.now(timezone.utc) - timedelta(weeks=1, days=-5),
        hike_date=datetime.now(timezone.utc) - timedelta(weeks=1, days=-6)
    ), Hike(
        trail_id=trails[1].id,
        status="active",
        phase="signup",
        voting_date=datetime.now(timezone.utc) + timedelta(days=1),
        signup_date=datetime.now(timezone.utc) + timedelta(days=3),
        waiver_date=datetime.now(timezone.utc) + timedelta(days=5),
        hike_date=datetime.now(timezone.utc) + timedelta(days=7)
    )]
    db.session.add_all(hikes)
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

    # 5) Random attendance for the last two past hikes (useful for testing selection script)
    # Build a quick lookup for each driver's vehicle
    vehicles_by_member = {v.member_id: v for v in vehicles}
    driver_ids = {m.id for m in drivers}

    # Find the last two past hikes by date (most recent first)
    past_sorted = sorted(
        [h for h in hikes if h.status == "past"],
        key=lambda h: h.hike_date,
        reverse=True
    )
    recent_two = past_sorted[:2]

    ATTEND_PROB = 0.35      # chance any member attended a given past hike
    DRIVER_PROB = 0.40      # if the member is a driver, chance they acted as driver
    SELF_PROB   = 0.10      # chance a non-driver goes as "self" instead of passenger

    past_signups = []
    for h in recent_two:
        for m in members:
            if random.random() < ATTEND_PROB:
                transport_type = "passenger"
                vehicle_id = None

                if m.id in driver_ids and random.random() < DRIVER_PROB:
                    transport_type = "driver"
                    vehicle_id = vehicles_by_member[m.id].id
                elif random.random() < SELF_PROB:
                    transport_type = "self"

                past_signups.append(
                    Signup(
                        member_id=m.id,
                        hike_id=h.id,
                        food_interest=random.choice([True, False]),
                        status="attended",          # counted by your priority logic
                        transport_type=transport_type,
                        vehicle_id=vehicle_id
                    )
                )

    db.session.add_all(past_signups)
    db.session.commit()


    # 6) Signups: drivers + passengers
    hike = hikes[3]
    signups = []
    for m in members:
        if m in drivers:
            vid = next(v.id for v in vehicles if v.member_id == m.id)
            signups.append(
                Signup(
                    member_id=m.id,
                    hike_id=hike.id,
                    transport_type="driver",
                    food_interest=random.choice([True, False]),
                    vehicle_id=vid,
                    status="pending",
                )
            )
        else:
            signups.append(
                Signup(
                    member_id=m.id,
                    hike_id=hike.id,
                    food_interest=random.choice([True, False]),
                    transport_type="passenger",
                    status="pending",
                )
            )
    db.session.add_all(signups)
    db.session.commit()

    print("Seeded 'signups' scenario.")

def seed_email_signup():
    clear_db()

    # 1) Trail
    trail = Trail(
        name="Santiago Creek Trail and Barnham Ridge",
        location="Santiago Canyon",
        length_mi=6.0,
        estimated_time_hr=3.5,
        required_water_liters=1,
        difficulty=2,  # Moderate
        description="important info about this specific trail!"
    )
    db.session.add(trail)
    db.session.commit()

    # 2) Active hike in SIGNUPS phase (trail chosen)
    hike = Hike(
        trail_id=trail.id,
        status="active",
        phase="signup",
        voting_date=datetime.now(timezone.utc) + timedelta(days=1),
        signup_date=datetime.now(timezone.utc)+ timedelta(days=3),
        waiver_date=datetime.now(timezone.utc) + timedelta(days=5),
        hike_date=datetime.now(timezone.utc) + timedelta(days=7)
    )
    db.session.add(hike)
    db.session.commit()

    members = [Member(name="Evan Shahrestany", email="eashahre@uci.edu"),
               Member(name="Evan Shahrestany 2", email="evanshahrestany2@gmail.com"),
               Member(name="Evan Shahrestany 3", email="evanshahrestany3@gmail.com"),
               Member(name="Gabriel Dodge", email="gdodge@uci.edu"),
               Member(name="Sterling Radisay", email="sradisay@uci.edu")
               ]
    db.session.add_all(members)
    db.session.commit()

    print("Seeded 'email signup campaign' scenario.")


def seed_waiver():
    """
    One ACTIVE hike in 'waiver' phase with a selected trail.
    ~40 confirmed spots (drivers/self/passengers up to capacity), rest waitlisted.
    ~20 waivers created.
    """
    clear_db()

    # 1) Trail
    trail = Trail(
        name="Santiago Creek Trail and Barnham Ridge",
        length_mi=6.0,
        difficulty=2,  # Moderate
        estimated_time_hr=3.5,
        location="Santiago Canyon",
        required_water_liters=1,
    )
    db.session.add(trail)
    db.session.commit()

    # 2) Active hike in WAIVER phase
    hike = Hike(
        trail_id=trail.id,
        status="active",
        phase="waiver",
        voting_date=datetime.now(timezone.utc) + timedelta(days=1),
        signup_date=datetime.now(timezone.utc) + timedelta(days=3),
        waiver_date=datetime.now(timezone.utc) + timedelta(days=5),
        hike_date=datetime.now(timezone.utc) + timedelta(days=7)
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
                food_interest=random.choice([True, False]),
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
                food_interest=random.choice([True, False]),
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
                food_interest=random.choice([True, False]),
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
            signed_on=datetime.now(timezone.utc) - timedelta(days=random.randint(0, 2)),
            print_name="",
            is_minor=False,
            signature_1_b64="",
            signature_2_b64=""
        )
        for mid in waiver_members
    ]
    db.session.add_all(waivers)
    db.session.commit()

    print("Seeded 'waiver' scenario.")


def seed_email_waiver():
    clear_db()

    # 1) Trail
    trail = Trail(
        name="Santiago Creek Trail and Barnham Ridge",
        location="Santiago Canyon",
        length_mi=6.0,
        difficulty=2,  # Moderate
        estimated_time_hr=3.5,
        required_water_liters=1,
        description="important info about this specific trail!"
    )
    db.session.add(trail)
    db.session.commit()

    # 2) Active hike in WAIVER phase
    hike = Hike(
        trail_id=trail.id,
        status="active",
        phase="waiver",
        voting_date=datetime.now(timezone.utc) + timedelta(days=1),
        signup_date=datetime.now(timezone.utc) + timedelta(days=3),
        waiver_date=datetime.now(timezone.utc) + timedelta(days=5),
        hike_date=datetime.now(timezone.utc) + timedelta(days=7)
    )
    db.session.add(hike)
    db.session.commit()

    members = [Member(name="Evan Shahrestany", email="eashahre@uci.edu"),
               Member(name="Evan Shahrestany 2", email="evanshahrestany2@gmail.com"),
               Member(name="Evan Shahrestany 3", email="evanshahrestany3@gmail.com"),
               Member(name="Gabriel Dodge", email="gdodge@uci.edu"),
               Member(name="Sterling Radisay", email="sradisay@uci.edu")
               ]
    db.session.add_all(members)
    db.session.commit()

    transports = ["driver"] * 2 + ["passenger"] * 2 + ["self"]

    signups = []
    i = 0
    for member in members:
        transport_type = transports.pop(random.randint(0, len(transports)-1))
        if transport_type == "driver":
            new_vehicle = Vehicle(
                member_id=member.id,
                year=2018 + random.randint(0, 6),
                make="MakeX",
                model="ModelY",
                passenger_seats=random.randint(2, 6),
            )
            db.session.add(new_vehicle)
            db.session.commit()

        signups.append(Signup(
            member_id=member.id,
            hike_id=hike.id,
            signup_date=datetime.now(timezone.utc) + timedelta(minutes=i),
            transport_type=transport_type,
            food_interest=random.choice([True, False]),
            status="confirmed",
            vehicle_id=
                Vehicle.query.filter_by(member_id=member.id).first().id
                if transport_type == "driver"
                else None
        ))
        i += 1

    db.session.add_all(signups)
    db.session.commit()

    print("Seeded 'email signup campaign' scenario.")


if __name__ == '__main__':
    import sys
    from app import create_app

    app = create_app()
    with app.app_context():
        scenario = sys.argv[1]
        if scenario == 'voting':
            seed_voting()
        elif scenario == 'signup':
            seed_signup()
        elif scenario == 'waiver':
            seed_waiver()
        elif scenario == 'email_voting':
            seed_email_vote()
        elif scenario == 'email_signup':
            seed_email_signup()
        elif scenario == 'email_waiver':
            seed_email_waiver()
        elif scenario == "clear":
            clear_db()
        else:
            print(__doc__)
            sys.exit(1)
