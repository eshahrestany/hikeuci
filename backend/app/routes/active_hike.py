from flask import Blueprint, jsonify, current_app, Response, request
from sqlalchemy.orm import joinedload

from .. import db
from ..models import ActiveHike, Trail, Vote, Member, Signup, Vehicle, Waiver
from ..decorators import admin_required
from typing import List, Optional


active_hike: Blueprint = Blueprint("active-hike", __name__)

@active_hike.route('/upcoming', methods=['GET'])
@admin_required
def get_active_hike() -> Response:
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
                Signup.is_checked_in,
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
        for member, is_driver, is_checked_in, waiver_id in rows:
            users.append({
                "member_id": member.id,
                "first_name": member.first_name,
                "last_name": member.last_name,
                "is_driver": is_driver,
                "has_waiver": waiver_id is not None,
                "is_checked_in": is_checked_in
            })

        return_data["users"] = users

        return jsonify(return_data)


    else:
        return jsonify({"status": None})


@active_hike.route('/check-in', methods=['POST'])
@admin_required
def check_in():
    data = request.get_json() or {}
    hike_id = data.get('hike_id')
    user_id = data.get('user_id')

    # 1) Basic payload validation
    if user_id is None:
        return jsonify(error="Missing 'user_id'"), 400

    # 2) Fetch the active hike and verify phase
    active = ActiveHike.query.first()
    if not active:
        return jsonify(error="No current active hike"), 400
    if active.status.lower() != 'waiver':
        return jsonify(error="Hike is not in waiver phase"), 400


    # 3) Verify member exists
    member = Member.query.get(user_id)
    if not member:
        return jsonify(error="Member id not found"), 400

    # 4) Verify waiver exists for this member/hike
    waiver = Waiver.query.filter_by(
        member_id=user_id,
        active_hike_id=active.id
    ).first()
    if not waiver:
        return jsonify(error="Waiver not on file for this member"), 400

    # 5) Fetch the signup record (so we can flip is_checked_in)
    signup = Signup.query.filter_by(
        active_hike_id=active.id,
        member_id=user_id
    ).first()
    if not signup:
        return jsonify(error="Member is not signed up for this hike"), 400

    # 6) If already checked in, just return success
    if signup.is_checked_in:
        return jsonify(already_checked_in=True), 208

    # 7) Mark checked in and commit
    signup.is_checked_in = True
    db.session.commit()

    return jsonify(success=True), 200