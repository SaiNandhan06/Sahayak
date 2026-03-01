"""
history.py
----------
In-memory session history manager for Sahayak.
Encapsulates session storage and provides a clean interface
for adding, retrieving, and clearing conversation turns.
"""

from typing import Dict, List


class SessionHistory:
    """
    Manages conversation history across multiple sessions using an in-memory dict.

    Each session stores a list of turns:
        [{"role": "user"|"assistant", "content": "..."}]
    """

    def __init__(self) -> None:
        self._store: Dict[str, List[Dict[str, str]]] = {}

    # ── Public API ────────────────────────────────────────────────────────────

    def get(self, session_id: str) -> List[Dict[str, str]]:
        """Return history for a session. Returns [] if session doesn't exist."""
        return self._store.get(session_id, [])

    def exists(self, session_id: str) -> bool:
        """Check whether a session exists."""
        return session_id in self._store

    def add_user_message(self, session_id: str, content: str) -> None:
        """Append a user turn to the session."""
        self._get_or_create(session_id).append({"role": "user", "content": content})

    def add_assistant_message(self, session_id: str, content: str) -> None:
        """Append an assistant turn to the session."""
        self._get_or_create(session_id).append({"role": "assistant", "content": content})

    def clear(self, session_id: str) -> bool:
        """
        Delete a session. Returns True if the session existed, False otherwise.
        """
        if session_id in self._store:
            del self._store[session_id]
            return True
        return False

    def all_sessions(self) -> List[str]:
        """Return a list of all active session IDs."""
        return list(self._store.keys())

    # ── Private ───────────────────────────────────────────────────────────────

    def _get_or_create(self, session_id: str) -> List[Dict[str, str]]:
        """Return existing list or create an empty one for a new session."""
        if session_id not in self._store:
            self._store[session_id] = []
        return self._store[session_id]


# Singleton instance used by main.py
session_manager = SessionHistory()
