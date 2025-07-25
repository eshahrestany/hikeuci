from flask import Flask, send_from_directory
from flask_cors import CORS
from .extensions import db, migrate
from .lib.magic_link import MagicLinkManager
from .routes import register_routes


def create_app(config_object="config.Config"):
    module_name, class_name = config_object.rsplit('.', 1)
    mod = __import__(module_name, fromlist=[class_name])
    cfg_cls = getattr(mod, class_name)

    app = Flask(
        __name__,
        static_folder=cfg_cls.STATIC_FOLDER,
        static_url_path=cfg_cls.STATIC_URL_PATH,
        template_folder=cfg_cls.TEMPLATE_FOLDER,
    )

    app.config.from_object(config_object)

    # extensions
    db.init_app(app)
    migrate.init_app(app, db)
    magic_link_manager = MagicLinkManager()
    magic_link_manager.init_app(app)
    CORS(app, resources={r"/*": {"origins": cfg_cls.CORS_ORIGIN}})

    # bring in model classes
    from . import models

    # blueprints / routes
    register_routes(app)

    @app.shell_context_processor
    def _shell():
        from .models import Member, Trail  # noqa
        return dict(db=db, Member=Member, Trail=Trail)

    return app
