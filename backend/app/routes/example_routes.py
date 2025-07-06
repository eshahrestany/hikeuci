from flask import Blueprint, jsonify
from app.models import Hike

example_bp = Blueprint("example", __name__)


@example_bp.route('/', methods=['GET'])
def example():
    return jsonify({"message": "Hello World"})

@example_bp.route('/upcoming', methods=['GET'])
def upcoming_hike():
    hike = Hike.query.filter_by(is_upcoming=True).first()

    if not hike:
        return jsonify({"message": "No upcoming hikes found"})

    return jsonify({
            "trail_name": hike.trail.name,
            "hike_date": hike.hike_date.isoformat(),
            "notes": hike.notes
        })


__all__ = [example_bp]
