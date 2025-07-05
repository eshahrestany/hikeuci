from flask import Flask
from .extensions import db, migrate
from .routes import register_routes


def create_app(config_object="config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_object)

    # extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # blueprints / routes
    register_routes(app)

    @app.shell_context_processor
    def _shell():
        from .models import Member, Trail  # noqa
        return dict(db=db, Member=Member, Trail=Trail)

    return app
