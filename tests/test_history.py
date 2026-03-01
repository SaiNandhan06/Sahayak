"""
tests/test_history.py
---------------------
Unit tests for the SessionHistory class in history.py.
Pure Python — no mocking required.
"""

import pytest
from history import SessionHistory


@pytest.fixture
def manager():
    """Return a fresh SessionHistory for each test."""
    return SessionHistory()


# ── exists / get ──────────────────────────────────────────────────────────────

def test_new_session_does_not_exist(manager):
    assert not manager.exists("abc")


def test_get_nonexistent_session_returns_empty_list(manager):
    assert manager.get("xyz") == []


# ── add messages ──────────────────────────────────────────────────────────────

def test_add_user_message_creates_session(manager):
    manager.add_user_message("s1", "Hello")
    assert manager.exists("s1")


def test_add_user_message_stored_correctly(manager):
    manager.add_user_message("s1", "Hello there")
    history = manager.get("s1")
    assert len(history) == 1
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello there"


def test_add_assistant_message(manager):
    manager.add_assistant_message("s1", "How can I help?")
    history = manager.get("s1")
    assert history[0]["role"] == "assistant"
    assert history[0]["content"] == "How can I help?"


def test_add_multiple_messages_preserves_order(manager):
    manager.add_user_message("s1", "Hi")
    manager.add_assistant_message("s1", "Hello!")
    manager.add_user_message("s1", "Track my food")
    manager.add_assistant_message("s1", "Done.")

    history = manager.get("s1")
    assert len(history) == 4
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"
    assert history[2]["content"] == "Track my food"
    assert history[3]["content"] == "Done."


# ── clear ─────────────────────────────────────────────────────────────────────

def test_clear_existing_session_returns_true(manager):
    manager.add_user_message("s1", "Hi")
    assert manager.clear("s1") is True


def test_clear_removes_session(manager):
    manager.add_user_message("s1", "Hi")
    manager.clear("s1")
    assert not manager.exists("s1")
    assert manager.get("s1") == []


def test_clear_nonexistent_session_returns_false(manager):
    assert manager.clear("ghost") is False


# ── all_sessions ──────────────────────────────────────────────────────────────

def test_all_sessions_empty_initially(manager):
    assert manager.all_sessions() == []


def test_all_sessions_lists_active_sessions(manager):
    manager.add_user_message("a", "msg")
    manager.add_user_message("b", "msg")
    sessions = manager.all_sessions()
    assert set(sessions) == {"a", "b"}


def test_all_sessions_after_clear(manager):
    manager.add_user_message("a", "msg")
    manager.add_user_message("b", "msg")
    manager.clear("a")
    assert manager.all_sessions() == ["b"]


# ── session isolation ─────────────────────────────────────────────────────────

def test_sessions_are_isolated(manager):
    manager.add_user_message("s1", "Food question")
    manager.add_user_message("s2", "Travel question")
    assert manager.get("s1")[0]["content"] == "Food question"
    assert manager.get("s2")[0]["content"] == "Travel question"
