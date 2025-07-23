from .auth import auth
from .dashboard import dashboard
from .images import images


def register_routes(app):
    app.register_blueprint(auth, url_prefix="/api/auth")
    app.register_blueprint(dashboard, url_prefix="/api/dashboard")
    app.register_blueprint(images, url_prefix="/api/images")
