from .example_routes import example_bp


def register_routes(app):
    app.register_blueprint(example_bp, url_prefix="/api/example")
