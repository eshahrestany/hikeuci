from ..models import Hike


def current_active_hike() -> Hike | None:
    return (
        Hike.query
        .filter_by(status="active")
        .first()
    )
