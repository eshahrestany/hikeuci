from flask import current_app
from .selection_algorithm import calc_passenger_capacity
from .. import db
from ..models import Hike, Signup


def current_active_hike() -> Hike | None:
    return (
        Hike.query
        .filter_by(status="active")
        .first()
    )

def update_waitlist(hike_id: int):
    """
    Calculates the number of passengers to bump off the waitlist based on current driver capacity,
    Bumps that number of passengers off the waitlist and update all waitlist positions.
    If no passengers need to be bumped, just updates waitlist positions.
    """
    hike = Hike.query.get(hike_id)

    # check if CONFIRMED signups are over capacity (only happens when drivers cancel or passengers are manually confirmed)
    capacity = calc_passenger_capacity(Signup.query.filter_by(hike_id=hike.id, transport_type="driver").all())
    num_confirmed_pasengers = Signup.query.filter_by(hike_id=hike.id, transport_type="passenger", status="confirmed").count()
    print(capacity, num_confirmed_pasengers)
    if num_confirmed_pasengers >= capacity:
        num_passengers_to_bump = 0

    num_passengers_to_bump = capacity - num_confirmed_pasengers

    waitlist = list(Signup.query
                    .with_entities(Signup.id)
                    .filter_by(hike_id=hike.id, status="waitlisted")
                    .order_by(Signup.waitlist_pos.asc())
                    )

    # bump waitlisted members
    while num_passengers_to_bump > 0 and len(waitlist) > 0:
        s = Signup.query.get(waitlist.pop(0))
        s.status = "confirmed"
        s.waitlist_pos = None
        current_app.extensions["celery"].send_task("app.tasks.send_email", args=["waiver", s.member_id, hike.id])
        num_passengers_to_bump -= 1

    db.session.commit()

    # update remaining waitlist positions
    remaining = (Signup.query
                 .filter_by(hike_id=hike.id, status="waitlisted")
                 .order_by(Signup.waitlist_pos.asc())
                 .all())

    for idx, signup in enumerate(remaining, start=1):
        signup.waitlist_pos = idx

    db.session.commit()