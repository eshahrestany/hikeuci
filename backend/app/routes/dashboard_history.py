from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from sqlalchemy import and_, func, case

from ..decorators import admin_required
from ..extensions import db
from ..lib.model_utils import get_current_ay_start
from ..models import Hike, Trail, Signup, Member, Waiver, Vehicle

dashboard_history = Blueprint("dashboard_history", __name__)


def _hike_date_to_ay_label(dt: datetime) -> str:
    """Convert a hike date to an academic year label like '2025-2026'."""
    if dt.month >= 8:
        return f"{dt.year}-{dt.year + 1}"
    else:
        return f"{dt.year - 1}-{dt.year}"


@dashboard_history.route("/academic-years", methods=["GET"])
@admin_required
def get_academic_years():
    hikes = (
        db.session.query(Hike.hike_date)
        .filter(Hike.status.in_(["past", "cancelled"]), Hike.hike_date.isnot(None))
        .all()
    )

    ay_set = set()
    for (hike_date,) in hikes:
        ay_set.add(_hike_date_to_ay_label(hike_date))

    ay_start = get_current_ay_start()
    current_ay = _hike_date_to_ay_label(ay_start.replace(month=10))  # Oct is always in the current AY

    academic_years = sorted(ay_set, reverse=True)

    # Ensure current AY is in the list even if no past hikes exist for it
    if current_ay not in academic_years:
        academic_years.insert(0, current_ay)

    return jsonify({"academic_years": academic_years, "current": current_ay})


def _parse_ay(ay_str: str) -> tuple[datetime, datetime]:
    """Parse '2025-2026' into (ay_start, ay_end) as UTC datetimes."""
    import re
    if not re.fullmatch(r"\d{4}-\d{4}", ay_str):
        raise ValueError(f"Invalid academic year format: {ay_str}")
    start_year = int(ay_str.split("-")[0])
    ay_start = datetime(start_year, 8, 1, tzinfo=timezone.utc)
    ay_end = datetime(start_year + 1, 8, 1, tzinfo=timezone.utc)
    return ay_start, ay_end


@dashboard_history.route("/hikes", methods=["GET"])
@admin_required
def get_hikes():
    ay = request.args.get("ay")
    if not ay:
        return jsonify({"error": "Missing 'ay' query parameter"}), 400

    try:
        ay_start, ay_end = _parse_ay(ay)
    except (ValueError, IndexError):
        return jsonify({"error": "Invalid academic year format"}), 400

    hikes = (
        db.session.query(Hike, Trail)
        .outerjoin(Trail, Hike.trail_id == Trail.id)
        .filter(
            Hike.status.in_(["past", "cancelled"]),
            Hike.hike_date >= ay_start,
            Hike.hike_date < ay_end,
        )
        .order_by(Hike.hike_date.desc())
        .all()
    )

    hike_ids = [h.id for h, _ in hikes]

    # Batch query signup stats for all hikes at once
    signup_stats = {}
    if hike_ids:
        stats = (
            db.session.query(
                Signup.hike_id,
                func.sum(case((Signup.status == "confirmed", 1), else_=0)).label("num_confirmed"),
                func.sum(case((Signup.status == "waitlisted", 1), else_=0)).label("num_waitlisted"),
                func.sum(case((Signup.is_checked_in.is_(True), 1), else_=0)).label("num_checked_in"),
                func.sum(case((and_(Signup.transport_type == "driver", Signup.status == "confirmed"), 1), else_=0)).label("num_drivers"),
                func.sum(case((and_(Signup.transport_type == "passenger", Signup.status == "confirmed"), 1), else_=0)).label("num_passengers"),
                func.sum(case((and_(Signup.transport_type == "passenger", Signup.is_checked_in.is_(True)), 1), else_=0)).label("num_checked_in_passengers"),
            )
            .filter(Signup.hike_id.in_(hike_ids))
            .group_by(Signup.hike_id)
            .all()
        )
        for row in stats:
            signup_stats[row.hike_id] = {
                "num_confirmed": int(row.num_confirmed or 0),
                "num_waitlisted": int(row.num_waitlisted or 0),
                "num_checked_in": int(row.num_checked_in or 0),
                "num_drivers": int(row.num_drivers or 0),
                "num_passengers": int(row.num_passengers or 0),
                "num_checked_in_passengers": int(row.num_checked_in_passengers or 0),
            }

    # Batch query passenger capacity per hike (sum of vehicle seats for confirmed drivers)
    capacity_by_hike = {}
    checked_in_capacity_by_hike = {}
    if hike_ids:
        cap_rows = (
            db.session.query(
                Signup.hike_id,
                func.coalesce(func.sum(Vehicle.passenger_seats), 0).label("passenger_capacity"),
            )
            .join(Vehicle, Signup.vehicle_id == Vehicle.id)
            .filter(
                Signup.hike_id.in_(hike_ids),
                Signup.transport_type == "driver",
                Signup.status == "confirmed",
            )
            .group_by(Signup.hike_id)
            .all()
        )
        for row in cap_rows:
            capacity_by_hike[row.hike_id] = int(row.passenger_capacity)

        # Capacity from checked-in drivers only
        checked_in_cap_rows = (
            db.session.query(
                Signup.hike_id,
                func.coalesce(func.sum(Vehicle.passenger_seats), 0).label("passenger_capacity"),
            )
            .join(Vehicle, Signup.vehicle_id == Vehicle.id)
            .filter(
                Signup.hike_id.in_(hike_ids),
                Signup.transport_type == "driver",
                Signup.is_checked_in.is_(True),
            )
            .group_by(Signup.hike_id)
            .all()
        )
        for row in checked_in_cap_rows:
            checked_in_capacity_by_hike[row.hike_id] = int(row.passenger_capacity)

    result = []
    for hike, trail in hikes:
        s = signup_stats.get(hike.id, {
            "num_confirmed": 0,
            "num_waitlisted": 0,
            "num_checked_in": 0,
            "num_drivers": 0,
            "num_passengers": 0,
            "num_checked_in_passengers": 0,
        })
        num_confirmed = s["num_confirmed"]
        num_checked_in = s["num_checked_in"]
        attendance_rate = round(num_checked_in / num_confirmed, 2) if num_confirmed > 0 else 0
        passenger_capacity = capacity_by_hike.get(hike.id, 0)

        result.append({
            "hike_id": hike.id,
            "trail_id": hike.trail_id,
            "trail_name": trail.name if trail else "Unknown",
            "trail_alltrails_url": trail.alltrails_url if trail else None,
            "trail_difficulty": trail.difficulty if trail else None,
            "status": hike.status,
            "hike_date": hike.get_localized_time("hike_date").isoformat(),
            "num_confirmed": num_confirmed,
            "num_waitlisted": s["num_waitlisted"],
            "num_checked_in": num_checked_in,
            "attendance_rate": attendance_rate,
            "num_drivers": s["num_drivers"],
            "num_passengers": s["num_passengers"],
            "num_checked_in_passengers": s["num_checked_in_passengers"],
            "passenger_capacity": passenger_capacity,
            "checked_in_capacity": checked_in_capacity_by_hike.get(hike.id, 0),
        })

    return jsonify(result)


@dashboard_history.route("/hikes/<int:hike_id>", methods=["GET"])
@admin_required
def get_hike_detail(hike_id: int):
    hike = db.session.get(Hike, hike_id)
    if not hike or hike.status not in ("past", "cancelled"):
        return jsonify({"error": "Hike not found"}), 404

    trail = db.session.get(Trail, hike.trail_id) if hike.trail_id else None

    rows = (
        db.session.query(
            Member.id,
            Member.name,
            Member.email,
            Member.tel,
            Signup.transport_type,
            Signup.status,
            Signup.is_checked_in,
            Signup.signup_date,
            Waiver.id.label("waiver_id"),
        )
        .join(Signup, Member.id == Signup.member_id)
        .outerjoin(
            Waiver,
            db.and_(Waiver.member_id == Member.id, Waiver.hike_id == hike_id),
        )
        .filter(Signup.hike_id == hike_id)
        .order_by(Signup.signup_date.asc())
        .all()
    )

    signups = []
    for member_id, name, email, tel, transport_type, signup_status, is_checked_in, signup_date, waiver_id in rows:
        signups.append({
            "member_id": member_id,
            "name": name,
            "email": email,
            "phone": tel,
            "transport_type": transport_type,
            "signup_status": signup_status,
            "is_checked_in": is_checked_in,
            "has_waiver": waiver_id is not None,
            "signup_date": signup_date.isoformat() if signup_date else None,
        })

    num_confirmed = sum(1 for s in signups if s["signup_status"] == "confirmed")
    num_waitlisted = sum(1 for s in signups if s["signup_status"] == "waitlisted")
    num_checked_in = sum(1 for s in signups if s["is_checked_in"])

    return jsonify({
        "hike_id": hike.id,
        "status": hike.status,
        "hike_date": hike.get_localized_time("hike_date").isoformat(),
        "trail_name": trail.name if trail else "Unknown",
        "trail_alltrails_url": trail.alltrails_url if trail else None,
        "num_signups": len(signups),
        "num_confirmed": num_confirmed,
        "num_waitlisted": num_waitlisted,
        "num_checked_in": num_checked_in,
        "attendance_rate": round(num_checked_in / num_confirmed, 2) if num_confirmed > 0 else 0,
        "signups": signups,
    })


@dashboard_history.route("/members/<int:member_id>", methods=["GET"])
@admin_required
def get_member_history(member_id: int):
    member = db.session.get(Member, member_id)
    if not member:
        return jsonify({"error": "Member not found"}), 404

    rows = (
        db.session.query(Signup, Hike, Trail)
        .join(Hike, Signup.hike_id == Hike.id)
        .outerjoin(Trail, Hike.trail_id == Trail.id)
        .filter(
            Signup.member_id == member_id,
            Hike.status.in_(["past", "cancelled"]),
        )
        .order_by(Hike.hike_date.desc())
        .all()
    )

    hikes = []
    total_checked_in = 0
    total_confirmed = 0
    times_driver = 0
    times_passenger = 0
    times_self = 0

    for signup, hike, trail in rows:
        is_confirmed = signup.status == "confirmed"
        if is_confirmed:
            total_confirmed += 1
        if signup.is_checked_in:
            total_checked_in += 1
        if signup.transport_type == "driver" and is_confirmed:
            times_driver += 1
        elif signup.transport_type == "passenger" and is_confirmed:
            times_passenger += 1
        elif signup.transport_type == "self" and is_confirmed:
            times_self += 1

        hikes.append({
            "hike_id": hike.id,
            "hike_date": hike.get_localized_time("hike_date").isoformat(),
            "trail_name": trail.name if trail else "Unknown",
            "trail_alltrails_url": trail.alltrails_url if trail else None,
            "hike_status": hike.status,
            "signup_status": signup.status,
            "transport_type": signup.transport_type,
            "is_checked_in": signup.is_checked_in,
        })

    return jsonify({
        "member": {
            "id": member.id,
            "name": member.name,
            "email": member.email,
            "phone": member.tel,
            "joined_on": member.joined_on.isoformat() if member.joined_on else None,
        },
        "summary": {
            "total_signups": len(hikes),
            "total_confirmed": total_confirmed,
            "total_checked_in": total_checked_in,
            "attendance_rate": round(total_checked_in / total_confirmed, 2) if total_confirmed > 0 else 0,
            "times_driver": times_driver,
            "times_passenger": times_passenger,
            "times_self": times_self,
        },
        "hikes": hikes,
    })


@dashboard_history.route("/reimbursements", methods=["POST"])
@admin_required
def calculate_reimbursements():
    data = request.get_json() or {}
    hike_ids = data.get("hike_ids", [])
    rate_per_mile = data.get("rate_per_mile")

    if not hike_ids:
        return jsonify(error="No hikes selected"), 400
    if not isinstance(rate_per_mile, (int, float)) or rate_per_mile <= 0:
        return jsonify(error="Invalid reimbursement rate"), 400

    # Validate hikes and check driving distances
    hikes = Hike.query.filter(Hike.id.in_(hike_ids)).all()
    if len(hikes) != len(hike_ids):
        return jsonify(error="One or more hikes not found"), 404

    trail_ids = set(h.trail_id for h in hikes if h.trail_id)
    trails = {t.id: t for t in Trail.query.filter(Trail.id.in_(trail_ids)).all()}

    for hike in hikes:
        trail = trails.get(hike.trail_id)
        if not trail:
            return jsonify(error=f"Trail not found for hike on {hike.hike_date.strftime('%Y-%m-%d')}"), 400
        if trail.driving_distance_mi is None:
            return jsonify(error=f"Driving distance not set for trail '{trail.name}'. Please update it in the Trails dashboard."), 400

    # Query checked-in drivers across all selected hikes
    driver_signups = (
        db.session.query(Signup.hike_id, Signup.member_id)
        .filter(
            Signup.hike_id.in_(hike_ids),
            Signup.transport_type == "driver",
            Signup.is_checked_in.is_(True),
        )
        .all()
    )

    # Aggregate miles per member
    hike_map = {h.id: h for h in hikes}
    member_miles = {}
    member_hike_count = {}
    for hike_id, member_id in driver_signups:
        hike = hike_map[hike_id]
        trail = trails[hike.trail_id]
        round_trip = trail.driving_distance_mi * 2

        member_miles[member_id] = member_miles.get(member_id, 0) + round_trip
        member_hike_count[member_id] = member_hike_count.get(member_id, 0) + 1

    if not member_miles:
        return jsonify(reimbursements=[], total_reimbursement=0, total_miles=0)

    # Fetch member details
    members = {m.id: m for m in Member.query.filter(Member.id.in_(member_miles.keys())).all()}

    reimbursements = []
    for member_id, miles in member_miles.items():
        member = members[member_id]
        reimbursements.append({
            "name": member.name,
            "email": member.email,
            "phone": member.tel or "",
            "total_miles": round(miles, 2),
            "reimbursement": round(miles * rate_per_mile, 2),
            "hikes_driven": member_hike_count[member_id],
        })

    reimbursements.sort(key=lambda r: r["total_miles"], reverse=True)
    total_reimbursement = round(sum(r["reimbursement"] for r in reimbursements), 2)
    total_miles = round(sum(r["total_miles"] for r in reimbursements), 2)

    return jsonify(
        reimbursements=reimbursements,
        total_reimbursement=total_reimbursement,
        total_miles=total_miles,
    )


@dashboard_history.route("/attendance-frequency", methods=["GET"])
@admin_required
def get_attendance_frequency():
    ay = request.args.get("ay")
    if not ay:
        return jsonify({"error": "Missing 'ay' query parameter"}), 400

    try:
        ay_start, ay_end = _parse_ay(ay)
    except (ValueError, IndexError):
        return jsonify({"error": "Invalid academic year format"}), 400

    # Count how many hikes each member checked into within the academic year
    member_counts = (
        db.session.query(
            Signup.member_id,
            func.count(Signup.id).label("hikes_attended"),
        )
        .join(Hike, Signup.hike_id == Hike.id)
        .filter(
            Hike.status == "past",
            Hike.hike_date >= ay_start,
            Hike.hike_date < ay_end,
            Signup.is_checked_in.is_(True),
        )
        .group_by(Signup.member_id)
        .subquery()
    )

    # Group by attendance count to get the frequency distribution
    freq_rows = (
        db.session.query(
            member_counts.c.hikes_attended,
            func.count().label("num_members"),
        )
        .group_by(member_counts.c.hikes_attended)
        .order_by(member_counts.c.hikes_attended)
        .all()
    )

    distribution = [
        {"hikes_attended": row.hikes_attended, "num_members": row.num_members}
        for row in freq_rows
    ]

    total_members = sum(row["num_members"] for row in distribution)
    repeat_members = sum(row["num_members"] for row in distribution if row["hikes_attended"] > 1)
    repeat_rate = round(repeat_members / total_members, 2) if total_members > 0 else 0

    return jsonify({
        "distribution": distribution,
        "total_members": total_members,
        "repeat_rate": repeat_rate,
    })


@dashboard_history.route("/attendance-frequency/members", methods=["GET"])
@admin_required
def get_attendance_frequency_members():
    ay = request.args.get("ay")
    count = request.args.get("count", type=int)
    if not ay or count is None or count < 1:
        return jsonify({"error": "Missing or invalid 'ay'/'count' parameters"}), 400

    try:
        ay_start, ay_end = _parse_ay(ay)
    except (ValueError, IndexError):
        return jsonify({"error": "Invalid academic year format"}), 400

    # Subquery: member_id -> hikes_attended count
    member_counts = (
        db.session.query(
            Signup.member_id,
            func.count(Signup.id).label("hikes_attended"),
        )
        .join(Hike, Signup.hike_id == Hike.id)
        .filter(
            Hike.status == "past",
            Hike.hike_date >= ay_start,
            Hike.hike_date < ay_end,
            Signup.is_checked_in.is_(True),
        )
        .group_by(Signup.member_id)
        .having(func.count(Signup.id) == count)
        .subquery()
    )

    members = (
        db.session.query(Member.id, Member.name, Member.email)
        .join(member_counts, Member.id == member_counts.c.member_id)
        .order_by(Member.name)
        .all()
    )

    return jsonify({
        "count": count,
        "members": [
            {"id": m.id, "name": m.name, "email": m.email}
            for m in members
        ],
    })
