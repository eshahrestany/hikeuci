from flask import Blueprint, jsonify, current_app, Response
from sqlalchemy.orm import joinedload

from .. import db
from ..models import ActiveHike, Trail, Vote, Member, Signup, Vehicle, Waiver
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

    phase = active_hike.status
    return_data = {"status": phase}

    # voting phase: two or more hikes are slated for voting
    if phase == "voting":
        # return the list of trails being voted with detailed info about the vote
        candidate_hikes: List[ActiveHike] = ActiveHike.query.all()
        return_data["candidates"] = []
        for hike in candidate_hikes:
            trail: Trail = Trail.query.get(hike.trail_id)

            rows = (
                db.session.query(Member.first_name, Member.last_name)
                .join(Vote, Member.id == Vote.member_id)
                .filter(Vote.active_hike_id == hike.id)
                .all()
            )

            voter_names = [fname + " " + lname for (fname, lname) in rows]

            return_data["candidates"].append({
                "trail_id": trail.id,
                "trail_name": trail.name,
                "candidate_id": hike.id,
                "candidate_num_votes": len(voter_names),
                "candidate_voters": voter_names
            })

        return jsonify(return_data)



    # signup phase: a trail is planned and members are currently signing up
    elif phase == "signup":
        trail: Trail = Trail.query.get(active_hike.trail_id)
        return_data["trail_id"] = trail.id
        return_data["trail_name"] = trail.name

        passenger_members = (
            db.session.query(Member)
            .join(Signup, Member.id == Signup.member_id)
            .filter_by(
                active_hike_id=active_hike.id,
                is_driver=False
            )
            .all()
        )
        driver_members = (
            db.session.query(Member)
            .join(Signup, Member.id == Signup.member_id)
            .filter_by(
                active_hike_id=active_hike.id,
                is_driver=True
            )
            .all()
        )

        return_data["num_signups"] = len(passenger_members) + len(driver_members)
        return_data["passengers"] = [m.first_name + " " + m.last_name for m in passenger_members]
        return_data["num_passengers"] = len(passenger_members)
        return_data["drivers"] = [m.first_name + " " + m.last_name for m in driver_members]
        return_data["num_drivers"] = len(driver_members)

        passenger_capacity = 0
        for signup in Signup.query.all():
            if signup.is_driver:
                num_passengers = Vehicle.query.get(signup.vehicle_id).passenger_seats
                passenger_capacity += num_passengers

        return_data["passenger_capacity"] = passenger_capacity

        return jsonify(return_data)

    # waiver phase: hikers for this trail have been selected and waivers have been sent
    elif phase == "waiver":
        trail: Trail = Trail.query.get(active_hike.trail_id)
        return_data["trail_id"] = trail.id
        return_data["trail_name"] = trail.name

        rows = (
            db.session
            .query(
                Member,
                Signup.is_driver,
                Waiver.id.label("waiver_id")
            )
            .join(
                Signup,
                Member.id == Signup.member_id
            )
            .outerjoin(
                Waiver,
                Member.id == Waiver.member_id
            )
            .filter(
                Signup.active_hike_id == active_hike.id
            )
            .all()
        )

        users = []
        for member, is_driver, waiver_id in rows:
            users.append({
                "member_id": member.id,
                "first_name": member.first_name,
                "last_name": member.last_name,
                "is_driver": is_driver,
                "has_waiver": waiver_id is not None
            })

        return_data["users"] = users

        return jsonify(return_data)


    else:
        return jsonify({"status": None})
