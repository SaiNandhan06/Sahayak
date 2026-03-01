"""
tests/test_api.py
-----------------
Integration tests for FastAPI endpoints in main.py.
get_rag_response is mocked — no Ollama server required.
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def reset_sessions():
    """Clear session state before each test."""
    from history import session_manager
    for sid in list(session_manager.all_sessions()):
        session_manager.clear(sid)


@pytest.fixture
def client():
    from main import app
    return TestClient(app)


# ── /health ───────────────────────────────────────────────────────────────────

def test_health_returns_200(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


# ── /chat ─────────────────────────────────────────────────────────────────────

@patch("main.get_rag_response", return_value="Use Jar or Groww to save money.")
def test_chat_returns_valid_response(mock_rag, client):
    r = client.post("/chat", json={"session_id": "s1", "message": "How to save money?"})
    assert r.status_code == 200
    data = r.json()
    assert data["session_id"] == "s1"
    assert data["message"] == "How to save money?"
    assert len(data["response"]) > 0


@patch("main.get_rag_response", return_value="Starbucks is Food & Dining.")
def test_chat_creates_session_history(mock_rag, client):
    from history import session_manager
    client.post("/chat", json={"session_id": "new", "message": "Categorize Starbucks"})
    assert session_manager.exists("new")
    history = session_manager.get("new")
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"


@patch("main.get_rag_response", side_effect=["Reply 1", "Reply 2"])
def test_chat_accumulates_history_across_turns(mock_rag, client):
    from history import session_manager
    sid = "multi"
    client.post("/chat", json={"session_id": sid, "message": "First"})
    client.post("/chat", json={"session_id": sid, "message": "Second"})
    assert len(session_manager.get(sid)) == 4  # 2 turns × 2 roles


def test_chat_rejects_empty_message(client):
    r = client.post("/chat", json={"session_id": "s1", "message": ""})
    assert r.status_code == 422  # Pydantic min_length validation


def test_chat_rejects_empty_session_id(client):
    r = client.post("/chat", json={"session_id": "", "message": "Hello"})
    assert r.status_code == 422


@patch("main.get_rag_response", side_effect=RuntimeError("Ollama down"))
def test_chat_returns_500_on_llm_error(mock_rag, client):
    r = client.post("/chat", json={"session_id": "err", "message": "Hi"})
    assert r.status_code == 500


# ── GET /history ──────────────────────────────────────────────────────────────

@patch("main.get_rag_response", return_value="Food info here.")
def test_get_history_returns_correct_messages(mock_rag, client):
    sid = "hist"
    client.post("/chat", json={"session_id": sid, "message": "Track food"})
    r = client.get(f"/history/{sid}")
    assert r.status_code == 200
    data = r.json()
    assert data["session_id"] == sid
    assert data["history"][0]["role"] == "user"
    assert data["history"][0]["content"] == "Track food"


def test_get_history_404_for_unknown_session(client):
    r = client.get("/history/does_not_exist")
    assert r.status_code == 404


# ── DELETE /history ───────────────────────────────────────────────────────────

@patch("main.get_rag_response", return_value="Sure!")
def test_delete_history_clears_session(mock_rag, client):
    sid = "del_test"
    client.post("/chat", json={"session_id": sid, "message": "Hi"})
    r = client.delete(f"/history/{sid}")
    assert r.status_code == 200
    assert "cleared" in r.json()["message"]
    assert client.get(f"/history/{sid}").status_code == 404


def test_delete_history_404_for_missing_session(client):
    r = client.delete("/history/ghost")
    assert r.status_code == 404
