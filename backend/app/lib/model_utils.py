from flask import current_app
from .. import db
from ..models import Hike, Signup


def current_active_hike() -> Hike | None:
    return (
        Hike.query
        .filter_by(status="active")
        .first()
    )

def bump_waitlist(hike_id: int, num_passengers: int):
    """
    Bump the specified number of passengers off the waitlist and update all waitlist positions.
    Can be called with num_passengers=0 to update all waitlist positions when a member has been bumped off outside this function.
    """
    hike = Hike.query.get(hike_id)
    waitlist = list(Signup.query
                    .with_entities(Signup.id)
                    .filter_by(hike_id=hike.id, status="waitlisted")
                    .order_by(Signup.waitlist_pos.asc())
                    )
    while num_passengers > 0 and len(waitlist) > 0:
        s = Signup.query.get(waitlist.pop(0))
        s.status = "confirmed"
        s.waitlist_pos = None
        current_app.extensions["celery"].send_task("app.tasks.send_email", args=["waiver", s.member_id, hike.id])
        num_passengers -= 1

    db.session.commit()

    # update remaining waitlist positions
    remaining = (Signup.query
                 .filter_by(hike_id=hike.id, status="waitlisted")
                 .order_by(Signup.waitlist_pos.asc())
                 .all())

    for idx, signup in enumerate(remaining, start=1):
        signup.waitlist_pos = idx

    db.session.commit()