""" Scripts that run at the turn of a phase """

import random
from ..models import Hike, Trail, Vote, Signup
from .. import db
from . import selection_algorithm


def initiate_vote_phase(ah: Hike):
    if ah.phase is not None:
        raise Exception(f"Hike {ah.id} has improper phase of {ah.phase}, cannot start vote phase")

    ah.phase = "voting"
    ah.email_campaign_completed = False
    db.session.commit()
    print("vote phase initiated")


def initiate_signup_phase(ah: Hike):
    if ah.phase not in [None, "voting"]:
        raise Exception(f"Hike {ah.id} has improper phase of {ah.phase}, cannot start signup phase")

    if ah.phase == "voting":
        # count votes and select trail
        candidates = Trail.query.filter_by(is_active_vote_candidate=True).all()
        counts = {t.id: Vote.query.filter_by(hike_id=ah.id, trail_id=t.id).count() for t in candidates}
        top = max(counts.values(), default=0)
        top_ids = [tid for tid, c in counts.items() if c == top]
        winner = Trail.query.get(random.choice(top_ids))

        # votes will be deleted once complete_hike is called later on

        ah.trail_id = winner.id
        for trail in candidates:
            trail.is_active_vote_candidate = False

    ah.phase = "signup"
    ah.email_campaign_completed = False
    db.session.commit()


def initiate_waiver_phase(ah):
    if ah.phase != "signup":
        raise Exception(f"Hike {ah.id} has improper phase of {ah.phase}, cannot start waiver phase")

    selection_algorithm.run(ah.id)
    ah.phase = "waiver"


def complete_hike(ah):
    if ah.phase != "waiver":
        raise Exception(f"Hike {ah.id} has improper phase of {ah.phase}, cannot mark hike as completed")

    Vote.query.filter_by(hike_id=ah.id).delete()