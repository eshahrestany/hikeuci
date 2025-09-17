import os

from flask import send_from_directory, Blueprint, jsonify, request, current_app
from ..decorators import admin_required
from ..models import Trail

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

images = Blueprint('images', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@images.route('/uploads/<int:trail_id>', methods=['GET'])
def trail_image(trail_id):
    print("trail id ", trail_id)
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
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
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)

        file.save(upload_path)

        return jsonify({
            "message": f"Image for trail {trail_id} uploaded successfully.",
            "url": f"/uploads/{trail_id}"
        }), 201
    else:
        return jsonify({"error": "File type not allowed"}), 400