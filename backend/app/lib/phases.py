""" Scripts that run at the turn of a phase """

import random
from ..models import Hike, Trail, Vote, Signup, MagicLink
from .. import db
from . import selection_algorithm


def initiate_signup_phase(hike_id: int):
    ah = Hike.query.get(hike_id)
    if not ah: raise Exception("Invalid hike ID")
    if ah.phase not in [None, "voting"]:
        raise Exception(f"Hike {ah.id} has improper phase of {ah.phase}, cannot start signup phase")

    if ah.phase == "voting":
        # count votes and select trail
        candidates = Trail.query.filter_by(is_active_vote_candidate=True).all()
        counts = {t.id: Vote.query.filter_by(hike_id=ah.id, trail_id=t.id).count() for t in candidates}
        top = max(counts.values(), default=0)
        top_ids = [tid for tid, c in counts.items() if c == top]
        winner = Trail.query.get(random.choice(top_ids))

        ah.trail_id = winner.id
        for trail in candidates:
            trail.is_active_vote_candidate = False

    ah.phase = "signup"
    ah.email_campaign_completed = False
    db.session.commit()


def initiate_waiver_phase(hike_id: int):
    ah = Hike.query.get(hike_id)
    if not ah: raise Exception("Invalid hike ID")
    if ah.phase != "signup":
        raise Exception(f"Hike {ah.id} has improper phase of {ah.phase}, cannot start waiver phase")

    confirmed, waitlisted = selection_algorithm.run(ah.id)
    ah.phase = "waiver"
    ah.email_campaign_completed = False
    # update signups
    print(f"confirmed signup IDs: {confirmed}")
    print(f"waitlisted signup IDs: {waitlisted}")
    Signup.query.filter(Signup.id.in_(confirmed)).update({Signup.status: "confirmed"}, synchronize_session='auto')

    for pos, sid in enumerate(waitlisted, 1):
        s = Signup.query.get(sid)
        s.status = "waitlisted"
        s.waitlist_pos = pos

    db.session.commit()


def complete_hike(hike_id: int):
    ah = Hike.query.get(hike_id)
    if not ah: raise Exception("Invalid hike ID")
    if ah.phase != "waiver":
        raise Exception(f"Hike {ah.id} has improper phase of {ah.phase}, cannot mark hike as completed")

    MagicLink.query.filter_by(hike_id=ah.id).delete()

    ah.status = "past"
    ah.phase = None
    db.session.commit()