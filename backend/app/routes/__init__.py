from .auth import auth
from .active_hike import active_hike
from .images import images
from .signup import hike_signup
from .waiver import hike_waiver
from .vehicles import vehicles
from .members import members


def register_routes(app):
    app.register_blueprint(auth, url_prefix="/api/auth")
    app.register_blueprint(active_hike, url_prefix="/api/active-hike")
    app.register_blueprint(images, url_prefix="/api/images")
    app.register_blueprint(hike_signup, url_prefix="/api/hike-signup")
    app.register_blueprint(hike_waiver, url_prefix="/api/hike-waiver")
    app.register_blueprint(vehicles, url_prefix="/api/vehicles")
    app.register_blueprint(members, url_prefix="/api/members")
