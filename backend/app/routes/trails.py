from flask import Blueprint, jsonify, request, current_app
from ..decorators import admin_required
from ..models import Trail
from .. import db

trails: Blueprint = Blueprint("trails", __name__)

def _serialize_trail(t):
    return {
        "id": t.id,
        "name": t.name,
        "location": t.location,
        "length_mi": t.length_mi,
        "estimated_time_hr": t.estimated_time_hr,
        "required_water_liters": t.required_water_liters,
        "difficulty": t.difficulty,
        "alltrails_url": t.alltrails_endpoint,
        "trailhead_gmaps_url": t.trailhead_gmaps_endpoint,
        "trailhead_amaps_url": t.trailhead_amaps_endpoint,
        "description": t.description,
    }


@trails.route("", methods=["GET"])
@admin_required
def list_trails():
    page = request.args.get("page", type=int)  # None => fetch all
    q = Trail.query.order_by(Trail.id.asc())

    if page is None:
        items = q.all()
        return jsonify([_serialize_trail(t) for t in items])

    if page < 1:
        return jsonify({"error": "page must be >= 1"}), 400

    PAGE_SIZE = 10
    total = q.count()
    items = q.offset((page - 1) * PAGE_SIZE).limit(PAGE_SIZE).all()

    return jsonify({
        "page": page,
        "page_size": PAGE_SIZE,
        "total": total,
        "has_next": page * PAGE_SIZE < total,
        "items": [_serialize_trail(t) for t in items],
    })

@trails.route("", methods=["POST"])
@admin_required
def create_trail():
    data = request.get_json()
    if not data or not data.get('name') or not data.get('location'):
        return jsonify({"error": "Missing required fields: name, location"}), 400
    new_trail = Trail(
        name=data['name'],
        location=data['location'],
        length_mi=data.get('length_mi'),
        estimated_time_hr=data.get('estimated_time_hr'),
        required_water_liters=data.get('required_water_liters'),
        difficulty=data.get('difficulty'),
        alltrails_endpoint=data.get('alltrails_url'),
        trailhead_gmaps_endpoint=data.get('trailhead_gmaps_url'),
        trailhead_amaps_endpoint=data.get('trailhead_amaps_url'),
        description=data.get('description')
    )
    db.session.add(new_trail)
    db.session.commit()

    return jsonify(_serialize_trail(new_trail)), 201


@trails.route("/<int:trail_id>", methods=["PUT", 'DELETE'])
@admin_required
def update_trail(trail_id):
    if request.method == "PUT":
        trail = Trail.query.get_or_404(trail_id)
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request must be JSON"}), 400

        trail.name = data.get('name', trail.name)
        trail.location = data.get('location', trail.location)
        trail.length_mi = data.get('length_mi', trail.length_mi)
        trail.estimated_time_hr = data.get('estimated_time_hr', trail.estimated_time_hr)
        trail.required_water_liters = data.get('required_water_liters', trail.required_water_liters)
        trail.difficulty = data.get('difficulty', trail.difficulty)
        trail.alltrails_endpoint = data.get('alltrails_url', trail.alltrails_endpoint)
        trail.trailhead_gmaps_endpoint = data.get('trailhead_gmaps_url', trail.trailhead_gmaps_endpoint)
        trail.trailhead_amaps_endpoint = data.get('trailhead_amaps_url', trail.trailhead_amaps_endpoint)
        trail.description = data.get('description', trail.description)

        db.session.commit()
        return jsonify(_serialize_trail(trail))
    elif request.method == "DELETE":
        trail = Trail.query.get_or_404(trail_id)
        db.session.delete(trail)
        db.session.commit()
        return "Deleted Successfully", 200
    return "Bad Request: Invalid request method", 400





