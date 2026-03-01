"""
schemas.py
----------
Pydantic models for Sahayak FastAPI request and response validation.
"""

from typing import List
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(
        ...,
        min_length=1,
        description="Unique identifier for the conversation session.",
    )
    message: str = Field(
        ...,
        min_length=1,
        description="The user's query or statement.",
    )

    model_config = {"json_schema_extra": {"examples": [{"session_id": "user_123", "message": "How can I save money?"}]}}


class ChatResponse(BaseModel):
    session_id: str
    message: str
    response: str


class HistoryEntry(BaseModel):
    role: str = Field(..., description="Either 'user' or 'assistant'.")
    content: str = Field(..., description="The message content.")


class HistoryResponse(BaseModel):
    session_id: str
    history: List[HistoryEntry]


class DeleteResponse(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: str
    message: str
