from flask import Blueprint, Response, jsonify, request

from ..decorators import admin_required
from ..lib.realtime import stream

stream_bp = Blueprint("stream", __name__)

ALLOWED_PREFIXES = ("hike:", "email-campaigns:hike:", "campaign:")
MAX_TOPICS = 8


def _validate_topics(raw: str) -> tuple[list[str] | None, str | None]:
    if not raw:
        return None, "Missing required query parameter: topics"
    topics = [t.strip() for t in raw.split(",") if t.strip()]
    if not topics:
        return None, "topics must contain at least one entry"
    if len(topics) > MAX_TOPICS:
        return None, f"Too many topics (max {MAX_TOPICS})"
    for t in topics:
        if not any(t.startswith(p) for p in ALLOWED_PREFIXES):
            return None, f"Disallowed topic prefix: {t!r}"
    return topics, None


@stream_bp.route("", methods=["GET"])
@admin_required
def admin_stream():
    topics, err = _validate_topics(request.args.get("topics", ""))
    if err:
        return jsonify(error=err), 400

    response = Response(
        stream(topics),
        mimetype="text/event-stream",
    )
    # Disable proxy and downstream buffering so events flush immediately.
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    response.headers["Connection"] = "keep-alive"
    response.headers["Pragma"] = "no-cache"
    return response
