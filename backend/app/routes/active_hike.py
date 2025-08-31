from flask import Blueprint, jsonify, request
from sqlalchemy import and_, func

from .. import db
from ..decorators import admin_required, waiver_phase_required
from ..models import Hike, Trail, Vote, Member, Signup, Vehicle, Waiver

active_hike: Blueprint = Blueprint("active-hike", __name__)


def _current_active_hike() -> Hike | None:
    return (
        Hike.query
        .filter_by(status="active")
        .first()
    )


@active_hike.route('/upcoming', methods=['GET'])
@admin_required
def get_active_hike_info():
    # Determine current active hike + phase
    hike = _current_active_hike()
    if hike is None:
        return jsonify(status="None"), 200

    phase = (hike.phase or "").lower()
    return_data = {"status": phase}

    # VOTING: summarize candidate trails + voters (from Vote rows)
    if phase == "voting":
        # Each vote row ties this active hike to a candidate Trail via Vote.trail_id
        # Build candidate list with counts, then attach voter names per trail.
        candidates = Trail.query.filter_by(is_active_vote_candidate=True).all()

        results = []
        for row in candidates:
            # Names of voters for this trail in this active hike
            voter_rows = (
                db.session.query(Member.name)
                .join(Vote, Member.id == Vote.member_id)
                .filter(and_(Vote.hike_id == hike.id, Vote.trail_id == row.id))
                .all()
            )
            names = [r.name for r in voter_rows]
            results.append({
                "trail_id": row.id,
                "trail_name": row.name,
                "trail_num_votes": len(names),
                "trail_voters": names,
            })

        return_data["trails"] = results
        return jsonify(return_data), 200

    # SIGNUPS or WAIVER: report selected trail + roster + capacity
    elif phase in ("signup", "waiver"):
        if not hike.trail_id:
            # Should not happen once a trail is chosen, but guard anyway.
            return jsonify(error="Active hike has no trail selected yet"), 409

        trail: Trail | None = Trail.query.get(hike.trail_id)
        if not trail:
            return jsonify(error="Selected trail not found"), 404

        return_data["trail_id"] = trail.id
        return_data["trail_name"] = trail.name

        # Pull signups for THIS active hike; include vehicle info and whether waiver exists FOR THIS HIKE
        rows = (
            db.session.query(
                Member,
                Signup.transport_type,
                Signup.is_checked_in,
                Signup.vehicle_id,
                Vehicle.passenger_seats,
                Waiver.id.label("waiver_id"),
            )
            .join(Signup, Member.id == Signup.member_id)
            .outerjoin(Vehicle, Signup.vehicle_id == Vehicle.id)
            .outerjoin(
                Waiver,
                and_(Waiver.member_id == Member.id, Waiver.hike_id == hike.id),
            )
            .filter(Signup.hike_id == hike.id)
            .all()
        )

        users = []
        total_capacity = 0
        for member, transport_type, is_checked_in, vehicle_id, seats, waiver_id in rows:
            user_obj = {
                "member_id": member.id,
                "name": member.name,
                "transport_type": transport_type,
                "has_waiver": waiver_id is not None,
                "is_checked_in": is_checked_in,
            }
            if transport_type == "driver":
                user_obj["vehicle_id"] = vehicle_id
                user_obj["vehicle_capacity"] = int(seats or 0)
                total_capacity += int(seats or 0)
            users.append(user_obj)

        return_data["users"] = users
        return_data["passenger_capacity"] = total_capacity
        return jsonify(return_data), 200

    # Any other phase → just return the phase for now
    return jsonify(return_data), 200


@active_hike.route('/waitlist', methods=['GET'])
@admin_required
@waiver_phase_required
def get_waitlist():
    hike = _current_active_hike()
    if not hike:
        return jsonify(error="No active hike"), 400

    waitlist_signups = (
        Signup.query
        .filter_by(hike_id=hike.id, status="waitlisted")
        .order_by(Signup.waitlist_pos.asc())
        .all()
    )

    waitlist_users = []
    for s in waitlist_signups:
        m = Member.query.get(s.member_id)
        if m:
            waitlist_users.append({
                "member_id": m.id,
                "name": m.name,
                "waitlist_pos": s.waitlist_pos,
            })

    return jsonify(waitlist_users), 200


@active_hike.route("/list-emails-not-in-hike", methods=["GET"])
@admin_required
def list_emails_not_in_hike():
    hike = _current_active_hike()
    if not hike:
        return jsonify([]), 200

    # Members signed up for THIS active hike
    signed_ids = [mid for (mid,) in db.session.query(Signup.member_id).filter(Signup.hike_id == hike.id).all()]

    # Waitlisted members for THIS active hike
    waitlisted_ids = [mid for (mid,) in db.session.query(Signup.member_id)
                      .filter(Signup.hike_id == hike.id, Signup.status == "waitlisted").all()]

    waitlisted_members = (
        Member.query
        .filter(Member.id.in_(waitlisted_ids))
        .order_by(Member.email)
        .all()
    )

    # Members not signed up for THIS active hike
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
    if user_id is None:
        return jsonify(error="Missing 'user_id'"), 400

    hike = _current_active_hike()
    if not hike:
        return jsonify(error="No active hike"), 400

    member = Member.query.get(user_id)
    if not member:
        return jsonify(error="Member id not found"), 400

    waiver = Waiver.query.filter_by(member_id=user_id, hike_id=hike.id).first()
    if not waiver:
        return jsonify(error="Waiver not on file for this member"), 400

    signup = Signup.query.filter_by(member_id=user_id, hike_id=hike.id).first()
    if not signup:
        return jsonify(error="Member is not signed up for this hike"), 400

    if signup.is_checked_in:
        return jsonify(already_checked_in=True), 208

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

    if None in (user_id, name, transport_type):
        return jsonify(error="Missing fields"), 400

    hike = _current_active_hike()
    if not hike or (hike.phase or "").lower() != "waiver":
        return jsonify(error="Not in waiver phase"), 400

    signup = Signup.query.filter_by(member_id=user_id, hike_id=hike.id).first()
    if not signup:
        return jsonify(error="Signup not found"), 404

    member = Member.query.get(user_id)
    if not member:
        return jsonify(error="Member not found"), 404

    # If switching to driver, validate vehicle
    if transport_type == 'driver':
        vehicle_id = data.get('vehicle_id')
        if vehicle_id is None:
            return jsonify(error="vehicle_id required for driver"), 400

        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return jsonify(error="Vehicle not found"), 404
        if vehicle.member_id != user_id:
            return jsonify(error="Vehicle does not belong to this member"), 403

        signup.vehicle_id = vehicle_id
    else:
        # Non-driver: clear vehicle association
        signup.vehicle_id = None

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

    hike = _current_active_hike()
    if not hike or (hike.phase or "").lower() != 'waiver':
        return jsonify(error="Not in waiver phase"), 400

    # delete waiver for THIS hike
    Waiver.query.filter_by(member_id=user_id, hike_id=hike.id).delete()
    # delete signup for THIS hike
    Signup.query.filter_by(member_id=user_id, hike_id=hike.id).delete()

    db.session.commit()
    return jsonify(success=True), 200


@active_hike.route("/add-user", methods=["POST"])
@admin_required
def add_user():
    data = request.get_json() or {}
    member_id = data.get("member_id")
    transport_type = data.get("transport_type")
    vehicle_id = data.get("vehicle_id")  # may be None

    if None in (member_id, transport_type):
        return jsonify(error="member_id and transport_type required"), 400

    hike = _current_active_hike()
    if not hike or (hike.phase or "").lower() != "waiver":
        return jsonify(error="Hike not in waiver phase"), 400

    if Signup.query.filter_by(member_id=member_id, hike_id=hike.id).first():
        return jsonify(error="Member already signed up"), 409

    if transport_type == "driver":
        if not vehicle_id:
            return jsonify(error="vehicle_id required for driver"), 400
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return jsonify(error="Vehicle not found"), 404
        if vehicle.member_id != member_id:
            return jsonify(error="Vehicle does not belong to this member"), 403

    signup = Signup(
        hike_id=hike.id,
        member_id=member_id,
        transport_type=transport_type,
        vehicle_id=vehicle_id if transport_type == "driver" else None,
        is_checked_in=False,
        status="pending",
    )
    db.session.add(signup)
    db.session.commit()

    m = Member.query.get(member_id)
    user_obj = {
        "member_id": m.id,
        "name": m.name,
        "transport_type": transport_type,
        "has_waiver": False,
        "is_checked_in": False,
        "vehicle_id": vehicle_id if transport_type == "driver" else None,
    }
    return jsonify(user_obj), 201
