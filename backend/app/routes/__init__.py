from .auth import auth
from .active_hike import active_hike
from .images import images


def register_routes(app):
    app.register_blueprint(auth, url_prefix="/api/auth")
    app.register_blueprint(active_hike, url_prefix="/api/active-hike")
    app.register_blueprint(images, url_prefix="/api/images")
