from flask import Blueprint, jsonify
from ..models import Hike
from ..decorators import admin_required

example_bp = Blueprint("example", __name__)


@example_bp.route('/', methods=['GET'])
def example():
    return jsonify({"message": "Hello World"})

@example_bp.route('/upcoming', methods=['GET'])
@admin_required
def upcoming_hike():
    hike = Hike.query.filter_by(status=2).first()

    if not hike:
        return jsonify({"message": "No upcoming hikes found"})

    return jsonify({
            "trail_name": hike.trail.name,
            "hike_date": hike.hike_date.isoformat(),
            "notes": hike.notes
        })


__all__ = [example_bp]
