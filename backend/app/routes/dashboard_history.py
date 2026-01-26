from __future__ import annotations

import csv
from io import StringIO

from flask import Blueprint, request, jsonify, Response
from sqlalchemy import func, case, or_

from ..decorators import admin_required
from ..extensions import db
from ..models import Hike, Trail, Signup, Member, Vehicle

admin_history = Blueprint("admin_history", __name__, url_prefix="/api/admin/history")


def _past_hikes_query():
    return Hike.query.filter(Hike.status == "past")


def _serialize_hike_row(h, stats_row=None, capacity=0):
    total_signups = int(getattr(stats_row, "total_signups", 0) or 0)
    checked_in_total = int(getattr(stats_row, "checked_in_total", 0) or 0)
    noshow_total = total_signups - checked_in_total

    checked_in_driver = int(getattr(stats_row, "checked_in_driver", 0) or 0)
    checked_in_passenger = int(getattr(stats_row, "checked_in_passenger", 0) or 0)
    checked_in_self = int(getattr(stats_row, "checked_in_self", 0) or 0)

    cap = int(capacity or 0)
    utilization = (checked_in_passenger / cap) if cap > 0 else None

    trail = Trail.query.get(h.trail_id)

    return {
        "id": h.hike_id,
        "hike_date": h.hike_date.isoformat() if h.hike_date else None,
        "status": h.status,
        "tz": h.tz,
        "trail": {
            "id": trail.id,
            "name": trail.name,
            "location": trail.location,
            "difficulty": trail.difficulty,
            "length_mi": trail.length_mi,
        },
        "stats": {
            "total_signups": total_signups,
            "checked_in_total": checked_in_total,
            "noshow_total": noshow_total,
            "checked_in_driver": checked_in_driver,
            "checked_in_passenger": checked_in_passenger,
            "checked_in_self": checked_in_self,
            "passenger_capacity": cap,
            "passenger_utilization": utilization,  # null if cap=0
        },
    }


def _attendance_base_query(hike_id: int):
    return (
        db.session.query(Signup, Member)
        .join(Member, Member.id == Signup.member_id)
        .filter(Signup.hike_id == hike_id)
    )


def _apply_attendance_filters(q):
    view = (request.args.get("view") or "attended").strip()          # attended|noshow|all
    transport = (request.args.get("transport") or "any").strip()    # any|driver|passenger|self
    search = (request.args.get("q") or "").strip()

    if view not in {"attended", "noshow", "all"}:
        return None, {"error": "invalid view"}, 400

    if transport not in {"any", "driver", "passenger", "self"}:
        return None, {"error": "invalid transport"}, 400

    if view == "attended":
        q = q.filter(Signup.is_checked_in.is_(True))
    elif view == "noshow":
        q = q.filter(Signup.is_checked_in.is_(False))

    if transport != "any":
        q = q.filter(Signup.transport_type == transport)

    if search:
        like = f"%{search}%"
        q = q.filter(or_(Member.name.ilike(like), Member.email.ilike(like)))

    return q, None, None


def _serialize_attendance_row(signup: Signup, member: Member):
    return {
        "signup_id": signup.id,
        "member_id": member.id,
        "name": member.name,
        "email": member.email,
        "transport_type": signup.transport_type,
        "status": signup.status,
        "is_checked_in": bool(signup.is_checked_in),
        "signup_date": signup.signup_date.isoformat() if signup.signup_date else None,
        "waitlist_pos": signup.waitlist_pos,
        "vehicle_id": signup.vehicle_id,
    }


@admin_history.route("/hikes", methods=["GET"])
@admin_required
def list_past_hikes():
    """
    Returns all past hikes (desc), each with:
      - trail summary
      - aggregated signup stats
      - passenger capacity (SQL aggregation; avoids N+1)
    """
    hikes_q = (
        _past_hikes_query()
        .outerjoin(Trail, Trail.id == Hike.trail_id)
        .with_entities(
            Hike.id.label("hike_id"),
            Hike.hike_date,
            Hike.status,
            Hike.tz,
            Trail.id.label("trail_id"),
            Trail.name.label("trail_name"),
            Trail.location.label("trail_location"),
            Trail.difficulty.label("trail_difficulty"),
            Trail.length_mi.label("trail_length_mi"),
        )
        .order_by(Hike.hike_date.desc())
    )

    hikes = hikes_q.all()
    hike_ids = [h.hike_id for h in hikes]
    if not hike_ids:
        return jsonify({"hikes": []})

    stats_rows = (
        db.session.query(
            Signup.hike_id.label("hike_id"),
            func.count(Signup.id).label("total_signups"),
            func.sum(case((Signup.is_checked_in.is_(True), 1), else_=0)).label("checked_in_total"),
            func.sum(case(((Signup.is_checked_in.is_(True)) & (Signup.transport_type == "driver"), 1), else_=0)).label("checked_in_driver"),
            func.sum(case(((Signup.is_checked_in.is_(True)) & (Signup.transport_type == "passenger"), 1), else_=0)).label("checked_in_passenger"),
            func.sum(case(((Signup.is_checked_in.is_(True)) & (Signup.transport_type == "self"), 1), else_=0)).label("checked_in_self"),
        )
        .filter(Signup.hike_id.in_(hike_ids))
        .group_by(Signup.hike_id)
        .all()
    )
    stats_by_hike = {r.hike_id: r for r in stats_rows}

    cap_rows = (
        db.session.query(
            Signup.hike_id.label("hike_id"),
            func.coalesce(func.sum(Vehicle.passenger_seats), 0).label("passenger_capacity"),
        )
        .join(Vehicle, Vehicle.id == Signup.vehicle_id)
        .filter(
            Signup.hike_id.in_(hike_ids),
            Signup.is_checked_in.is_(True),
            Signup.transport_type == "driver",
            Signup.vehicle_id.isnot(None),
            )
        .group_by(Signup.hike_id)
        .all()
    )
    cap_by_hike = {r.hike_id: int(r.passenger_capacity or 0) for r in cap_rows}

    out = []
    for h in hikes:
        out.append(
            _serialize_hike_row(
                h,
                stats_row=stats_by_hike.get(h.hike_id),
                capacity=cap_by_hike.get(h.hike_id, 0),
            )
        )

    return jsonify({"hikes": out})


@admin_history.route("/hikes/<int:hike_id>/attendance", methods=["GET"])
@admin_required
def get_hike_attendance(hike_id: int):
    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(max(int(request.args.get("page_size", 25)), 1), 200)

    q = _attendance_base_query(hike_id)
    q, err_body, err_code = _apply_attendance_filters(q)
    if err_body:
        return jsonify(err_body), err_code

    total = q.count()

    rows = (
        q.order_by(Member.name.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return jsonify(
        {
            "total": total,
            "page": page,
            "page_size": page_size,
            "rows": [_serialize_attendance_row(signup, member) for signup, member in rows],
        }
    )


@admin_history.route("/hikes/<int:hike_id>/attendance.csv", methods=["GET"])
@admin_required
def export_hike_attendance_csv(hike_id: int):
    q = _attendance_base_query(hike_id)
    q, err_body, err_code = _apply_attendance_filters(q)
    if err_body:
        return jsonify(err_body), err_code

    rows = q.order_by(Member.name.asc()).all()

    def generate():
        sio = StringIO()
        writer = csv.writer(sio)

        writer.writerow(["member_name", "member_email", "transport_type", "signup_status", "is_checked_in", "waitlist_pos"])
        yield sio.getvalue()
        sio.seek(0)
        sio.truncate(0)

        for signup, member in rows:
            writer.writerow(
                [
                    member.name,
                    member.email,
                    signup.transport_type,
                    signup.status,
                    "true" if signup.is_checked_in else "false",
                    signup.waitlist_pos if signup.waitlist_pos is not None else "",
                ]
            )
            yield sio.getvalue()
            sio.seek(0)
            sio.truncate(0)

    filename = f"hike_{hike_id}_attendance.csv"
    return Response(
        generate(),
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
