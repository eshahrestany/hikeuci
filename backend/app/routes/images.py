import os

from flask import send_from_directory, Blueprint, jsonify, request
from ..decorators import admin_required
from ..models import Trail

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

images = Blueprint('images', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@images.route('/uploads/<int:trail_id>.png')
def trail_image(trail_id):
    return send_from_directory(
        'static/uploads',
        f'{trail_id}.png'
    )


@images.route('/uploads/<int:trail_id>', methods=['POST'])
@admin_required
def upload_trail_image(trail_id):
    _ = Trail.query.get_or_404(trail_id)

    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if file and allowed_file(file.filename):
        filename = f"{trail_id}.png"
        upload_path = os.path.join('static/uploads', filename)

        os.makedirs('static/uploads', exist_ok=True)

        file.save(upload_path)

        return jsonify({
            "message": f"Image for trail {trail_id} uploaded successfully.",
            "url": f"/uploads/{filename}"
        }), 201
    else:
        return jsonify({"error": "File type not allowed"}), 400