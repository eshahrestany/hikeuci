from flask import Blueprint, jsonify, current_app, Response

from .. import db
from ..models import ActiveHike, Trail, Vote, Member
from ..decorators import admin_required
from typing import List, Optional


dashboard: Blueprint = Blueprint("dashboard", __name__)

@dashboard.route('/upcoming', methods=['GET'])
@admin_required
def get_upcoming_hike() -> Response:
    # find out the current phase

    # null phase: no scheduled hike
    active_hike: ActiveHike or None = ActiveHike.query.first()
    if active_hike is None:
        return jsonify({"status": None})

    # voting phase: two or more hikes are slated for voting
    if active_hike.status == "voting":
        # return the list of trails being voted with detailed info about the vote
        candidate_hikes: List[ActiveHike] = ActiveHike.query.all()
        return_data = {"status": "voting", "candidates": []}
        for hike in candidate_hikes:
            trail: Trail = Trail.query.get(hike.trail_id)

            rows = (
                db.session.query(Member.first_name, Member.last_name)
                .join(Vote, Member.id == Vote.member_id)
                .filter(Vote.active_hike_id == hike.id)
                .all()
            )

            voter_names = [fname + " " + lname for (fname,lname) in rows]

            return_data["candidates"].append({
                "trail_id": trail.id,
                "trail_name": trail.name,
                "candidate_id": hike.id,
                "candidate_num_votes": hike.num_votes,
                "candidate_voters": voter_names
            })

        return jsonify(return_data)



    # signup phase: a trail is planned and members are currently signing up


    # waiver phase: hikers for this trail have been selected and waivers have been sent




    return jsonify({"status": None})
