"""
Realtime SSE infrastructure: lightweight Redis pub/sub fanout to admin
dashboards.

Producers (route handlers, Celery tasks) call `publish_event(topic, event, data)`
after committing a state change. The SSE endpoint in `routes/stream.py` opens
a long-lived greenlet (gevent worker) per client that subscribes to the
client's requested topics and yields SSE-formatted lines as messages arrive.

Payloads are intentionally small — IDs only. Clients refetch existing REST
endpoints to reconcile state. This keeps the producer and the REST schema
on a single source of truth and makes missed events / reconnects naturally
idempotent.
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
from typing import Any, Iterable, Iterator, Optional

import redis
from flask import current_app

log = logging.getLogger(__name__)

# Heartbeat cadence for SSE clients. Comfortably under the 60s default
# nginx idle-close window and any browser/proxy buffering thresholds.
KEEPALIVE_SEC = 25

# Per-message poll cadence inside the stream loop. Short enough that a
# disconnect is detected promptly when we try to write the next chunk.
POLL_SEC = 1.0


_redis_lock = threading.Lock()
_redis: Optional[redis.Redis] = None


def _get_redis() -> redis.Redis:
    """Lazy singleton Redis client, shared across requests/tasks."""
    global _redis
    if _redis is not None:
        return _redis
    with _redis_lock:
        if _redis is not None:
            return _redis
        url = _broker_url()
        _redis = redis.Redis.from_url(url, decode_responses=True)
        return _redis


def _broker_url() -> str:
    # Prefer Flask config (works inside web requests AND Celery tasks, since
    # Celery's task base sets up the Flask app context). Fall back to env so
    # this stays callable from one-off scripts/devtools.
    try:
        cfg = current_app.config.get("CELERY") or {}
        url = cfg.get("broker_url")
        if url:
            return url
    except RuntimeError:
        pass  # outside app context
    return os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")


def publish_event(topic: str, event: str, data: Optional[dict] = None) -> None:
    """
    Best-effort publish to a Redis channel. Never raises into the caller —
    realtime is an enhancement, not a correctness requirement, so a Redis
    blip must not break a write path.
    """
    payload = json.dumps({"event": event, "data": data or {}})
    try:
        _get_redis().publish(topic, payload)
    except Exception:
        log.exception("publish_event failed (topic=%r, event=%r)", topic, event)


def stream(topics: Iterable[str]) -> Iterator[bytes]:
    """
    Generator that yields SSE-formatted byte chunks for the given topics.

    Subscribes via Redis pubsub, emits events as they arrive, and inserts
    a `:keepalive` comment every ~25s of silence so intermediaries don't
    close the idle connection.

    Cleans up the pubsub on generator close (client disconnect / reload).
    """
    topics = list(topics)
    r = _get_redis()
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    try:
        pubsub.subscribe(*topics)
        # Initial flush: tells the client the stream is live, also forces
        # any proxy to commit headers immediately.
        yield b": connected\n\n"
        last_send = time.monotonic()
        while True:
            msg = pubsub.get_message(timeout=POLL_SEC)
            if msg is not None:
                # msg = {'type': 'message', 'channel': 'hike:42', 'data': '{...}'}
                channel = msg.get("channel") or ""
                raw = msg.get("data") or "{}"
                try:
                    parsed = json.loads(raw)
                    event_name = parsed.get("event") or "message"
                    payload = parsed.get("data") or {}
                except (ValueError, TypeError):
                    event_name = "message"
                    payload = {"raw": raw}
                # Wrap the payload so the client knows which topic fired.
                payload = {"topic": channel, **payload}
                chunk = (
                    f"event: {event_name}\n"
                    f"data: {json.dumps(payload)}\n\n"
                ).encode("utf-8")
                yield chunk
                last_send = time.monotonic()
            elif time.monotonic() - last_send >= KEEPALIVE_SEC:
                yield b": keepalive\n\n"
                last_send = time.monotonic()
    except (GeneratorExit, KeyboardInterrupt):
        # Normal client disconnect.
        raise
    except Exception:
        log.exception("SSE stream errored (topics=%r)", topics)
    finally:
        try:
            pubsub.unsubscribe()
        except Exception:
            pass
        try:
            pubsub.close()
        except Exception:
            pass
