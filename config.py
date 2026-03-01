"""
config.py
---------
Central configuration for the Sahayak AI Financial Assistant.
Override any value via environment variables or .env file.
"""

import os
from dotenv import load_dotenv

load_dotenv()  # Loads .env if present

# ── Vector Store ──────────────────────────────────────────────────────────────
CHROMA_DIR: str = os.getenv("CHROMA_DIR", "./chroma_db")
COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "sahayak_finance")

# ── Ollama Models ─────────────────────────────────────────────────────────────
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
LLM_MODEL: str = os.getenv("LLM_MODEL", "qwen2:0.5b")
LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.3"))

# ── RAG Settings ──────────────────────────────────────────────────────────────
RETRIEVER_K: int = int(os.getenv("RETRIEVER_K", "3"))

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_DIR: str = os.getenv("LOG_DIR", "./logs")
LOG_FILE: str = os.path.join(LOG_DIR, "app.log")
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

# ── API Settings ──────────────────────────────────────────────────────────────
API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
API_PORT: int = int(os.getenv("API_PORT", "8000"))
