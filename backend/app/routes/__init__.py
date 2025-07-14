from .example_routes import example_bp
from .auth import auth_bp

def register_routes(app):
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(example_bp, url_prefix="/api/example")
