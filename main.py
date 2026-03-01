"""
main.py
-------
Sahayak FastAPI backend.

Endpoints:
  POST   /chat                 – Send a message and get a bot reply.
  GET    /history/{session_id} – Retrieve conversation history.
  DELETE /history/{session_id} – Clear conversation history.
  GET    /health               – Liveness check.
"""

import logging
import logging.handlers
import os
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import LOG_FILE, LOG_DIR, LOG_LEVEL
from history import session_manager
from schemas import (
    ChatRequest,
    ChatResponse,
    HistoryEntry,
    HistoryResponse,
    DeleteResponse,
    HealthResponse,
)
from rag_chain import get_rag_response

# ── Logging setup ─────────────────────────────────────────────────────────────
os.makedirs(LOG_DIR, exist_ok=True)

_handlers = [
    logging.StreamHandler(),
    logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    ),
]

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=_handlers,
)
logger = logging.getLogger("sahayak")

# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Sahayak API starting up...")
    yield
    logger.info("🛑 Sahayak API shutting down.")

# ── FastAPI App ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="Sahayak – AI Financial Assistant",
    description=(
        "Conversational AI agent for personal finance management. "
        "Parses Indian bank SMS alerts, categorizes expenses, and recommends fintech tools."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# Required so the browser-based frontend can call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # lock down to specific origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.post("/chat", response_model=ChatResponse, summary="Send a message to Sahayak")
async def chat(request: ChatRequest):
    """
    Accepts a user message and returns the AI response.

    - **session_id**: Unique ID to maintain conversation context across calls.
    - **message**: The user's finance-related query or statement.
    """
    session_id = request.session_id.strip()
    user_message = request.message.strip()

    logger.info("Chat | session=%s | user=%s", session_id, user_message[:80])

    history = session_manager.get(session_id)

    try:
        bot_response = get_rag_response(query=user_message, history=history)
    except Exception as e:
        logger.error("RAG error for session %s: %s", session_id, str(e))
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while generating the response: {str(e)}",
        )

    # Persist turn to session history
    session_manager.add_user_message(session_id, user_message)
    session_manager.add_assistant_message(session_id, bot_response)

    logger.info("Chat | session=%s | response_len=%d", session_id, len(bot_response))

    return ChatResponse(
        session_id=session_id,
        message=user_message,
        response=bot_response,
    )


@app.get(
    "/history/{session_id}",
    response_model=HistoryResponse,
    summary="Retrieve conversation history",
)
async def get_history(session_id: str):
    """Returns the full conversation history for a given session."""
    if not session_manager.exists(session_id):
        raise HTTPException(
            status_code=404,
            detail=f"No session found with id '{session_id}'.",
        )
    history = session_manager.get(session_id)
    return HistoryResponse(
        session_id=session_id,
        history=[HistoryEntry(**turn) for turn in history],
    )


@app.delete(
    "/history/{session_id}",
    response_model=DeleteResponse,
    summary="Clear conversation history",
)
async def delete_history(session_id: str):
    """Clears the conversation history for a given session."""
    deleted = session_manager.clear(session_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"No session found with id '{session_id}'.",
        )
    logger.info("Deleted session: %s", session_id)
    return DeleteResponse(message=f"History for session '{session_id}' has been cleared.")


@app.get("/health", response_model=HealthResponse, summary="Health check")
async def health():
    """Returns API liveness status."""
    return HealthResponse(status="ok", message="Sahayak is running. 🟢")

# ── Serve React Frontend (For Deployment) ────────────────────────────────────
app.mount("/assets", StaticFiles(directory="Frontend/dist/assets"), name="assets")

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """Catch-all route to serve the Single Page Application"""
    return FileResponse("Frontend/dist/index.html")
