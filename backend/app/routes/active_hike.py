from typing import List
from flask import Blueprint, jsonify, Response, request, current_app
from .. import db
from ..decorators import admin_required, waiver_phase_required
from ..models import ActiveHike, Trail, Vote, Member, Signup, Vehicle, Waiver

active_hike: Blueprint = Blueprint("active-hike", __name__)


@active_hike.route('/upcoming', methods=['GET'])
@admin_required
def get_active_hike_info():
    # find out the current phase

    # null phase: no scheduled hike
    hike: ActiveHike or None = ActiveHike.query.first()
    if hike is None:
        return jsonify(status="None"), 200

    phase = hike.status
    return_data = {"status": phase}

    # voting phase: two or more hikes are slated for voting
    if phase == "voting":
        # return the list of trails being voted with detailed info about the vote
        candidate_hikes: List[ActiveHike] = ActiveHike.query.all()
        return_data["candidates"] = []
        for hike in candidate_hikes:
            trail: Trail = Trail.query.get(hike.trail_id)

            rows = (
                db.session.query(Member.name)
                .join(Vote, Member.id == Vote.member_id)
                .filter(Vote.active_hike_id == hike.id)
                .all()
            )

            names = [row.name for row in rows]

            return_data["candidates"].append({
                "trail_id": trail.id,
                "trail_name": trail.name,
                "candidate_id": hike.id,
                "candidate_num_votes": len(names),
                "candidate_voters": names
            })

        return jsonify(return_data), 200

    # signup phase: one hike has been selected and is open for signups
    # waiver phase: hikers for this trail have been selected and waivers have been sent
    elif phase in ["signup", "waiver"]:  # both phases require nearly identical data
        trail: Trail = Trail.query.get(hike.trail_id)
        return_data["trail_id"] = trail.id
        return_data["trail_name"] = trail.name

        rows = (
            db.session.query(Member, Signup.transport_type, Signup.is_checked_in, Waiver.id.label("waiver_id"))
            .join(Signup, Member.id == Signup.member_id)
            .outerjoin(Waiver, Member.id == Waiver.member_id)
            .filter(Signup.active_hike_id == hike.id)
            .all()
        )

        users = []
        for member, transport_type, is_checked_in, waiver_id in rows:
            user_obj = {
                "member_id": member.id,
                "name": member.name,
                "transport_type": transport_type,
                "has_waiver": waiver_id is not None,
                "is_checked_in": is_checked_in
            }
            if user_obj["transport_type"] == "driver":
                vehicle = Vehicle.query.get(Signup.query.filter_by(
                    active_hike_id=hike.id,
                    member_id=member.id
                ).first().vehicle_id)
                user_obj["vehicle_id"] = vehicle.id
                user_obj["vehicle_capacity"] = vehicle.passenger_seats
            users.append(user_obj)

        # compute capacity from drivers’ vehicles
        total_capacity = 0
        for user in users:
            if user["transport_type"] == "driver":
                total_capacity += user["vehicle_capacity"]

        return_data["users"] = users
        return_data["passenger_capacity"] = total_capacity
        return jsonify(return_data), 200


@active_hike.route('/waitlist', methods=['GET'])
@admin_required
@waiver_phase_required
def get_waitlist():
    # fetch all members who are signed up but on the waitlist
    waitlist_signups = Signup.query.filter_by(status="waitlisted").all()
    waitlist_users = []
    for signup in waitlist_signups:
        member = Member.query.get(signup.member_id)
        if member:
            user_obj = {
                "member_id": member.id,
                "name": member.name,
                'waitlist_pos': signup.waitlist_pos,
            }
            waitlist_users.append(user_obj)

    return jsonify(waitlist_users), 200



@active_hike.route("/list-emails-not-in-hike", methods=["GET"])
@admin_required
def list_emails_not_in_hike():
    # Already-signed-up member IDs
    signed_ids = (db.session.query(Signup.member_id).all())
    signed_ids = [mid for (mid,) in signed_ids]

    # Waitlisted members
    waitlisted_ids = (db.session.query(Signup.member_id).filter(Signup.status == "waitlisted").all())
    waitlisted_members = (
        Member.query
        .filter(Member.id.in_(waitlisted_ids))
        .order_by(Member.email)
        .all()
    )

    # Unsigned-up members
    unsigned_members = (
        Member.query
        .filter(~Member.id.in_(signed_ids))
        .order_by(Member.email)
        .all()
    )

    # Combine unsigned and waitlisted members
    rows = unsigned_members + waitlisted_members

    return jsonify([{"member_id": m.id, "email": m.email} for m in rows]), 200

@active_hike.route('/check-in', methods=['POST'])
@admin_required
@waiver_phase_required
def check_in():
    data = request.get_json() or {}
    user_id = data.get('user_id')

    # 1) Basic payload validation
    if user_id is None:
        return jsonify(error="Missing 'user_id'"), 400

    # 3) Verify member exists
    member = Member.query.get(user_id)
    if not member:
        return jsonify(error="Member id not found"), 400

    # 4) Verify waiver exists for this member/hike
    waiver = Waiver.query.filter_by(
        member_id=user_id,
    ).first()
    if not waiver:
        return jsonify(error="Waiver not on file for this member"), 400

    # 5) Fetch the signup record (so we can flip is_checked_in)
    signup = Signup.query.filter_by(
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


@active_hike.route('/modify-user', methods=['POST'])
@admin_required
def modify_user():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    name = data.get('name')
    transport_type = data.get('transport_type')

    # 1) Validate payload
    if None in (user_id, name, transport_type):
        return jsonify(error="Missing fields"), 400

    # 2) ActiveHike must exist and be in waiver phase
    active = ActiveHike.query.first()
    if not active or active.status.lower() != "waiver":
        return jsonify(error="Not in waiver phase"), 400

    # 3) Signup must exist
    signup = Signup.query.filter_by(
        member_id=user_id
    ).first()
    if not signup:
        return jsonify(error="Signup not found"), 404

    # 4) Member exists?
    member = Member.query.get(user_id)
    if not member:
        return jsonify(error="Member not found"), 404

    # 5) Vehicle id must be valid if transport_type is 'driver'
    if transport_type == 'driver':
        vehicle_id = data.get('vehicle_id')
        if vehicle_id is None:
            return jsonify(error="vehicle_id required for driver"), 400

        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return jsonify(error="Vehicle not found"), 404

        # Ensure the vehicle is associated with the member
        if vehicle.member_id != user_id:
            return jsonify(error="Vehicle does not belong to this member"), 403

        # 6) Apply updates
        signup.vehicle_id = vehicle_id

    member.name = name
    signup.transport_type = transport_type

    db.session.commit()
    return jsonify(success=True), 200


@active_hike.route('/remove-user', methods=['POST'])
@admin_required
def remove_user():
    data = request.get_json() or {}
    user_id = data.get('user_id')

    if user_id is None:
        return jsonify(error="Missing 'user_id'"), 400

    active = ActiveHike.query.first()
    if not active or active.status.lower() != 'waiver':
        return jsonify(error="Not in waiver phase"), 400

    # delete waiver if exists
    w = Waiver.query.filter_by(member_id=user_id).first()
    if w:
        db.session.delete(w)

    # delete signup
    s = Signup.query.filter_by(member_id=user_id).first()
    if s:
        db.session.delete(s)

    db.session.commit()
    return jsonify(success=True), 200


@active_hike.route("/add-user", methods=["POST"])
@admin_required
def add_user():
    data = request.get_json() or {}
    member_id = data.get("member_id")
    transport_type = data.get("transport_type")
    vehicle_id = data.get("vehicle_id")  # may be None

    # ── validation ─────────────────────────────
    if None in (member_id, transport_type):
        return jsonify(error="hike_id, member_id, transport_type required"), 400

    active = ActiveHike.query.first()
    if not active or active.status.lower() != "waiver":
        return jsonify(error="Hike not in waiver phase"), 400

    # already signed up?
    if Signup.query.filter_by(member_id=member_id).first():
        return jsonify(error="Member already signed up"), 409

    # driver must supply vehicle_id
    if transport_type == "driver" and not vehicle_id:
        return jsonify(error="vehicle_id required for driver"), 400

    # ── create signup ──────────────────────────
    signup = Signup(
        active_hike_id=ActiveHike.query.first().id,
        member_id=member_id,
        transport_type=transport_type,
        vehicle_id=vehicle_id,
        is_checked_in=False,
    )
    db.session.add(signup)
    db.session.commit()

    # build response object similar to waiverData.users
    m = Member.query.get(member_id)
    user_obj = {
        "member_id": m.id,
        "name": m.name,
        "transport_type": transport_type,
        "has_waiver": False,
        "is_checked_in": False,
        "vehicle_id": vehicle_id,
    }

    return jsonify(user_obj), 201
