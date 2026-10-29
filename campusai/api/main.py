"""FastAPI Application entrypoint. Re-exported from backend.main."""
from backend.main import (
    app,
    QueryRequest,
    ChatRequest,
    FeedbackRequest,
    query_endpoint,
    chat_endpoint,
    health_check,
    submit_feedback,
    root
)

__all__ = [
    "app",
    "QueryRequest",
    "ChatRequest",
    "FeedbackRequest",
    "query_endpoint",
    "chat_endpoint",
    "health_check",
    "submit_feedback",
    "root"
]
