from flask import send_from_directory, Blueprint

images = Blueprint('images', __name__)

@images.route('/uploads/<int:trail_id>.png')
def trail_image(trail_id):
    return send_from_directory(
        'static/uploads',       # relative to your Flask app root
        f'{trail_id}.png'
    )