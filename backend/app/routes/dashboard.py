from flask import Blueprint, jsonify, request, current_app
from sqlalchemy import and_
from datetime import datetime, timezone, timedelta

from .. import db
from ..decorators import admin_required, waiver_phase_required
from ..models import Trail, Vote, Member, Signup, Vehicle, Waiver, MagicLink, Hike
from ..lib.model_utils import current_active_hike, update_waitlist
from ..lib import phases

dashboard: Blueprint = Blueprint("dashboard", __name__)


@dashboard.route('/upcoming', methods=['GET'])
@admin_required
def get_active_hike_info():
    # Determine current active hike + phase
    hike = current_active_hike()
    if hike is None:
        return jsonify(status=None), 200

    return_data = {}
    phase = (hike.phase or "").lower()
    if not phase:
        return_data["status"] = 'awaiting_vote_start'
        return_data["vote_start"] = hike.get_localized_time('created_date').strftime("%c")
    else:
        return_data["status"] = phase


    # timeline block
    # add timeline metadata
    return_data["has_vote"] = bool(getattr(hike, "has_vote", False))
    return_data["phase"] = phase

    # Build timeline datetimes: frontend expects array length 3 (skipped vote) or 4 (has_vote)
    if return_data["has_vote"]:
        return_data["timeline"] = {
            "vote_date": hike.get_localized_time('created_date').isoformat() if hike.signup_date else None,
            "signup_date": hike.get_localized_time('signup_date').isoformat() if hike.signup_date else None,
            "waiver_date": hike.get_localized_time('waiver_date').isoformat() if hike.waiver_date else None,
            "hike_date": hike.get_localized_time('hike_date').isoformat() if hike.hike_date else None,
        }
    else:
        return_data["timeline"] = {
            "signup_date": hike.get_localized_time('signup_date').isoformat() if hike.signup_date else None,
            "waiver_date": hike.get_localized_time('waiver_date').isoformat() if hike.waiver_date else None,
            "hike_date": hike.get_localized_time('hike_date').isoformat() if hike.hike_date else None,
        }

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
                "trail_alltrails_url": row.alltrails_url,
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
        return_data["trail_alltrails_url"] = trail.alltrails_url

        rows = (
            db.session.query(
                Member,
                Signup.status,
                Signup.transport_type,
                Signup.is_checked_in,
                Signup.vehicle_id,
                Waiver.id.label("waiver_id"),
            )
            .join(Signup, Member.id == Signup.member_id)
            .outerjoin(
                Waiver,
                and_(Waiver.member_id == Member.id, Waiver.hike_id == hike.id),
            )
            .filter(Signup.hike_id == hike.id)
            .all()
        )

        users = []
        total_capacity = 0
        for member, signup_status, transport_type, is_checked_in, vehicle_id, waiver_id in rows:
            user_obj = {
                "member_id": member.id,
                "name": member.name,
                "transport_type": transport_type,
                "has_waiver": waiver_id is not None,
                "is_checked_in": is_checked_in,
            }
            if transport_type == "driver":
                vehicle = Vehicle.query.get(vehicle_id)
                user_obj["vehicle_id"] = vehicle_id
                user_obj["vehicle_desc"] = f"{vehicle.year} {vehicle.make} {vehicle.model}"
                user_obj["vehicle_capacity"] = int(vehicle.passenger_seats)
                total_capacity += int(vehicle.passenger_seats)
            users.append(user_obj)

        return_data["users"] = users
        return_data["passenger_capacity"] = total_capacity
        if phase == "waiver":
            num_confirmed_passengers = (
                db.session.query(Signup)
                .filter_by(hike_id=hike.id, transport_type="passenger", status="confirmed")
                .count()
            )
            if total_capacity < num_confirmed_passengers:
                return_data["over_capacity_passengers"] = num_confirmed_passengers - total_capacity
        return jsonify(return_data), 200

    # Any other phase → just return the phase for now
    return jsonify(return_data), 200


@dashboard.route('/hike/trail', methods=['PUT'])
@admin_required
def switch_hike_trail():
    hike = current_active_hike()
    if not hike:
        return jsonify(error="No active hike"), 400

    if hike.phase not in ('signup', 'waiver'):
        return jsonify(error="Trail can only be switched during signup or waiver phase"), 400

    data = request.get_json() or {}
    trail_id = data.get('trail_id')
    if trail_id is None:
        return jsonify(error="Missing trail_id"), 400

    trail = Trail.query.get(trail_id)
    if not trail:
        return jsonify(error="Trail not found"), 404

    hike.trail_id = trail_id
    db.session.commit()

    return jsonify(
        trail_id=trail.id,
        trail_name=trail.name,
        trail_alltrails_url=trail.alltrails_url,
    ), 200


@dashboard.route('/hike/cancel', methods=['POST'])
@admin_required
def cancel_hike():
    hike = current_active_hike()
    if not hike:
        return jsonify(error="No active hike"), 400

    try:
        phases.cancel_hike(hike.id)
    except Exception as e:
        return jsonify(error=str(e)), 400

    return jsonify(message="Hike cancelled"), 200


@dashboard.route('/set-hike', methods=['POST'])
@admin_required
def set_next_hike():
    data = request.get_json()
    flow = data.get("flow")
    if not flow: return jsonify(error="missing flow param"), 400

    vote_trail_ids = []
    if flow == "vote":
        signup_date = data.get("signup_date")
        if not signup_date: return jsonify(error="missing signup_date"), 400

        vote_trail_ids = data.get("vote_trail_ids")
        if not vote_trail_ids: return jsonify(error="missing vote_trail_ids")

        if len(vote_trail_ids) == 0:
            return jsonify(error="invalid vote_trail_ids")

        for tid in vote_trail_ids:
            t = Trail.query.get(tid)
            if not t:
                return jsonify(error=f"invalid vote_trail_id {tid}")

    else:
        trail_id = data.get("trail_id")
        if not trail_id: return jsonify(error="Missing trail_id")
        trail = Trail.query.get(trail_id)
        if not trail: return jsonify(error=f"Invalid trail_id {trail_id}")

    waiver_date = data.get("waiver_date")
    if not waiver_date: return jsonify(error="missing waiver_date"), 400

    hike_date = data.get("hike_date")
    if not hike_date: return jsonify(error="missing hike_date"), 400

    try:
        if flow == "vote":
            signup_date = datetime.fromisoformat(signup_date).astimezone(timezone.utc)

        waiver_date = datetime.fromisoformat(waiver_date).astimezone(timezone.utc)
        hike_date = datetime.fromisoformat(hike_date).astimezone(timezone.utc)

    except ValueError as e:
        return jsonify(error=str(e)), 400

    if flow == "vote" and signup_date + timedelta(hours=1) > waiver_date:
        return jsonify(error="waiver_date is not at least 1 hour after signup_date"), 400

    if waiver_date + timedelta(hours=1) > hike_date:
        return jsonify(error="hike_date is not at least 1 hour after waiver_date"), 400

    new_hike = Hike(
        status="active",
        phase="voting" if flow == "vote" else "signup",
        trail_id=trail_id if flow == "signup" else None,
        has_vote=flow == "vote",
        signup_date=signup_date if flow == "vote" else datetime.now(timezone.utc),
        waiver_date=waiver_date,
        hike_date=hike_date
    )

    db.session.add(new_hike)
    for tid in vote_trail_ids:  # empty list if not vote flow
        t = Trail.query.get(tid)
        t.is_active_vote_candidate = True
    db.session.commit()

    current_app.extensions["celery"].send_task("app.tasks.start_email_campaign", args=[new_hike.id])

    return jsonify(success=True), 200


@dashboard.route('/waitlist', methods=['GET'])
@admin_required
@waiver_phase_required
def get_waitlist():
    hike = current_active_hike()
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

@dashboard.route("/list-emails", methods=["GET"])
@admin_required
def list_all_emails():
    return jsonify([m.email for m in Member.query.all()]), 200


@dashboard.route("/list-emails-in-hike", methods=["GET"])
@admin_required
def list_emails_in_hike():
    hike = current_active_hike()
    if not hike:
        return jsonify([]), 200

    signed_ids = [mid for (mid,) in db.session.query(Signup.member_id).filter(Signup.hike_id == hike.id).all()]
    members = (
        Member.query
        .filter(Member.id.in_(signed_ids))
        .order_by(Member.email)
        .all()
    )
    return jsonify([m.email for m in members]), 200


@dashboard.route("/list-emails-not-in-hike", methods=["GET"])
@admin_required
def list_emails_not_in_hike():
    hike = current_active_hike()
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


@dashboard.route('/check-in', methods=['POST', 'DELETE'])
@admin_required
@waiver_phase_required
def check_in():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    if user_id is None:
        return jsonify(error="Missing 'user_id'"), 400

    hike = current_active_hike()
    if not hike:
        return jsonify(error="No active hike"), 400

    member = Member.query.get(user_id)
    if not member:
        return jsonify(error="Member id not found"), 400

    signup = Signup.query.filter_by(member_id=user_id, hike_id=hike.id).first()
    if not signup:
        return jsonify(error="Member is not signed up for this hike"), 400

    # POST → check-in (requires waiver)
    if request.method == 'POST':
        waiver = Waiver.query.filter_by(member_id=user_id, hike_id=hike.id).first()
        if not waiver:
            return jsonify(error="Waiver not on file for this member"), 400

        if signup.is_checked_in:
            return jsonify(already_checked_in=True), 208

        signup.is_checked_in = True
        db.session.commit()
        return jsonify(success=True), 200

    elif request.method == 'DELETE':
        # DELETE → undo check-in
        if not signup.is_checked_in:
            return jsonify(already_unchecked=True), 208

        signup.is_checked_in = False
        db.session.commit()
        return jsonify(success=True), 200

    return jsonify(error="Invalid request method"), 400


@dashboard.route('/modify-user', methods=['POST'])
@admin_required
def modify_user():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    name = data.get('name')
    transport_type = data.get('transport_type')

    if None in (user_id, name, transport_type):
        return jsonify(error="Missing fields"), 400

    hike = current_active_hike()
    if not hike or (hike.phase or "").lower() not in ("signup", "waiver"):
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

    if signup.status == "waitlisted":
        signup.status = "confirmed"
        signup.waitlist_pos = None
        current_app.extensions["celery"].send_task("app.tasks.send_email", args=["waiver", member.id, hike.id])

    db.session.commit()
    update_waitlist(hike.id)

    return jsonify(success=True), 200


@dashboard.route('/remove-user', methods=['POST'])
@admin_required
def remove_user():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    if user_id is None:
        return jsonify(error="Missing 'user_id'"), 400

    hike = current_active_hike()
    if not hike or (hike.phase or "").lower() not in ('signup', 'waiver'):
        return jsonify(error="Not in signup or waiver phase"), 400

    MagicLink.query.filter_by(member_id=user_id, hike_id=hike.id).delete()
    Signup.query.filter_by(member_id=user_id, hike_id=hike.id).delete()
    db.session.commit()

    return jsonify(success=True), 200


@dashboard.route("/add-user", methods=["POST"])
@admin_required
def add_user():
    data = request.get_json() or {}
    member_id = data.get("member_id")
    if member_id is None or Member.query.get(member_id) is None:
        return jsonify(error="Invalid member_id"), 400

    hike = current_active_hike()
    if not hike or (hike.phase or "").lower() not in ("signup", "waiver"):
        return jsonify(error="Hike not in waiver phase"), 400

    if Signup.query.filter_by(member_id=member_id, hike_id=hike.id).first():
        return jsonify(error="Member already signed up"), 409

    if hike.phase == "signup":
        # new signup, simply dispatch signup email task.
        current_app.extensions["celery"].send_task("app.tasks.send_email", args=["signup", member_id, hike.id])
        return jsonify(success=True), 201


    else:
        # late signup, first determine manual or userlink mode
        signup_mode = data.get("signup_mode")
        if not signup_mode or signup_mode not in ("userlink", "manual"):
            return jsonify(error="signup_mode missing or invalid"), 400

        if signup_mode == "userlink":
            current_app.extensions["celery"].send_task("app.tasks.send_email", args=["late_signup", member_id, hike.id])
            return jsonify(success=True), 201

        # otherwise signup is manual
        transport_type = data.get("transport_type")
        vehicle_id = data.get("vehicle_id")  # may be None

        if transport_type is None:
            return jsonify(error="transport_type required"), 400

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
            food_interest=False,
            vehicle_id=vehicle_id if transport_type == "driver" else None,
            is_checked_in=False,
            status="confirmed",
        )
        db.session.add(signup)
        db.session.commit()

        update_waitlist(hike.id)

        current_app.extensions["celery"].send_task("app.tasks.send_email", args=["waiver", member_id, hike.id])

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
