"""
In-memory session store.

NOTE: This is intentionally simple for local dev / demo purposes.
For production, swap this for Redis (ephemeral, fast) or Postgres/Supabase
(persistent, supports user history). The interface below is designed so
that swap is a drop-in replacement — just reimplement these four methods
against your storage of choice.
"""
from __future__ import annotations

import time
import uuid
import logging
from threading import Lock

logger = logging.getLogger(__name__)

_SESSION_TTL_SECONDS = 60 * 60  # 1 hour


class SessionStore:
    def __init__(self) -> None:
        self._data: dict[str, dict] = {}
        self._lock = Lock()

    def create(self, payload: dict) -> str:
        session_id = str(uuid.uuid4())
        with self._lock:
            self._data[session_id] = {
                "payload": payload,
                "created_at": time.time(),
            }
        return session_id

    def get(self, session_id: str) -> dict | None:
        with self._lock:
            entry = self._data.get(session_id)
            if not entry:
                return None
            if time.time() - entry["created_at"] > _SESSION_TTL_SECONDS:
                del self._data[session_id]
                return None
            return entry["payload"]

    def update(self, session_id: str, patch: dict) -> None:
        with self._lock:
            entry = self._data.get(session_id)
            if entry:
                entry["payload"].update(patch)

    def delete(self, session_id: str) -> None:
        with self._lock:
            self._data.pop(session_id, None)

    def _cleanup_expired(self) -> None:
        now = time.time()
        with self._lock:
            expired = [
                sid for sid, entry in self._data.items()
                if now - entry["created_at"] > _SESSION_TTL_SECONDS
            ]
            for sid in expired:
                del self._data[sid]


# Singleton instance shared across the app
session_store = SessionStore()
