from ..models import Hike

def initiate_vote_phase(ah: Hike):
    if ah.phase is not None:
        raise Exception(f"Hike {ah.id} has improper phase of {ah.phase}, cannot start vote phase")
    
    ah.email_campaign_completed = False


    print("vote phase initiated")


def initiate_signup_phase(ah: Hike):
    if ah.phase not in [None, "vote"]:
        raise Exception(f"Hike {ah.id} has improper phase of {ah.phase}, cannot start signup phase")


def initiate_waiver_phase(ah):
    if ah.phase != "signup":
        raise Exception(f"Hike {ah.id} has improper phase of {ah.phase}, cannot start waiver phase")


def complete_hike(ah):
    if ah.phase != "waiver":
        raise Exception(f"Hike {ah.id} has improper phase of {ah.phase}, cannot mark hike as completed")