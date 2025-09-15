from flask import Blueprint, jsonify, request, current_app
from ..decorators import admin_required
from ..models import Trail


trails: Blueprint = Blueprint("trails", __name__)

@trails.route("", methods=["GET"])
@admin_required
def list_trails():
    def _trail_dict(t):
        return {
            "id": t.id,
            "name": t.name,
            "location": t.location,
            "length_mi": t.length_mi,
            "estimated_time_hr": t.estimated_time_hr,
            "required_water_liters": t.required_water_liters,
            "difficulty": current_app.config["DIFFICULTY_INDEX"].get(t.difficulty),
            "alltrails_url": t.alltrails_endpoint,
            "trailhead_gmaps_url": t.trailhead_gmaps_endpoint,
            "trailhead_amaps_url": t.trailhead_amaps_endpoint,
            "description": t.description,
        }

    page = request.args.get("page", type=int)  # None => fetch all
    q = Trail.query.order_by(Trail.id.asc())

    if page is None:
        items = q.all()
        return jsonify([_trail_dict(t) for t in items])

    if page < 1:
        return jsonify({"error": "page must be >= 1"}), 400

    PAGE_SIZE = 50
    total = q.count()
    items = q.offset((page - 1) * PAGE_SIZE).limit(PAGE_SIZE).all()

    return jsonify({
        "page": page,
        "page_size": PAGE_SIZE,
        "total": total,
        "has_next": page * PAGE_SIZE < total,
        "items": [_trail_dict(t) for t in items],
    })