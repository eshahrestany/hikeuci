from flask import Blueprint, jsonify, current_app, Response
from ..models import Hike
from ..decorators import admin_required
import logging
from typing import List, Optional

logger: logging.Logger = logging.getLogger(__name__)

api: Blueprint = Blueprint("api", __name__)

@api.route('/upcoming', methods=['GET'])
def get_upcoming() -> Response:
    voting_hikes: List[Hike] = Hike.query.filter_by(status="voting").all()
    if len(voting_hikes) != 0:
        pass  # You could later process or return these hikes

    signup_hike: Optional[Hike] = Hike.query.filter_by(status="signup").first()
    if signup_hike is not None:
        pass

    waiver_hike: Optional[Hike] = Hike.query.filter_by(status='waiver').first()
    if waiver_hike is not None:
        pass

    return jsonify({
        "test": "test"
    })
