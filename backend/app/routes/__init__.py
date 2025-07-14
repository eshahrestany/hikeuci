from .example_routes import example_bp
from .auth import auth
from .api import api

def register_routes(app):
    app.register_blueprint(auth, url_prefix="/api/auth")
    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(example_bp, url_prefix="/api/example")
