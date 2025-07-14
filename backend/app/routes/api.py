from flask import Blueprint, jsonify, current_app
from ..models import Hike
from ..decorators import admin_required
import logging
logger = logging.getLogger(__name__)

api = Blueprint("api", __name__)

@api.route('/upcoming', methods=['GET'])
def get_upcoming():
    voting_hikes = Hike.query.filter_by(status="voting").all()
    if len(voting_hikes) != 0:
        pass

    signup_hike = Hike.query.filter_by(status="signup").first()
    if signup_hike is not None:
        pass

    waiver_hike = Hike.query.filter_by(status='waiver').first()
    if waiver_hike is not None:
        pass


    return jsonify({
        "test": "test"
    })


