from flask import send_from_directory, Blueprint, request, current_app, abort, jsonify
from ..decorators import admin_required
from ..models import Hike, Member
from ..lib.model_utils import current_active_hike

mail = Blueprint('mail', __name__)


@mail.route('/resend', methods=['POST'])
@admin_required
def resend_email():
    member_id = request.json.get('member_id', None)
    email_type = request.json.get('email_type', None)

    member = Member.query.filter_by(id=member_id).first()

    if not member:
        return jsonify({"message": "invalid member"}), 400

    if not email_type:
        return jsonify({"message": "JSON param email_type is required"}), 400

    hike_id = current_active_hike().id

    current_app.extensions["celery"].send_task("app.tasks.send_email", args=[email_type, member_id, hike_id])

    return jsonify({"message": "Email task queued successfully"})
