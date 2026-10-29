"""Enterprise FastAPI Application for CampusAI and CampusNLP.
Aditya University Intelligent Academic Helpdesk and Query Understanding System.
Exposes both deterministic /api/query and full 8-stage /api/chat pipelines,
along with normalized academic catalog endpoints and audit logging.
"""

import json
import logging
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Annotated, Dict, Any, List, Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, StringConstraints

from backend.config import settings
from backend.pipeline import pipeline
from backend.utils.logger import logger
from campusai.api.routes import academic, admin, auth, chat, sources

FEEDBACK_FILE = settings.DATA_DIR / "feedback_log.json"
_log_lock = Lock()

app = FastAPI(
    title=settings.APP_TITLE,
    description="Enterprise-grade AI-powered academic helpdesk for Aditya University, Surampalem.",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    try:
        from backend.database.connection import create_all_tables
        create_all_tables()
        logger.info("Database tables verified.")
    except Exception as e:
        logger.warning("Could not auto-create database tables on startup: %s", e)


@app.middleware("http")
async def add_security_headers_and_tracing(request: Request, call_next):
    """Adds request correlation ID, latency tracking, and security headers."""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start_time = time.time()

    response = await call_next(request)

    latency_ms = (time.time() - start_time) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time-MS"] = f"{latency_ms:.2f}"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"

    return response


class QueryRequest(BaseModel):
    query: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]


class ChatRequest(BaseModel):
    query: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)]
    chat_history: Optional[List[Dict[str, str]]] = Field(default_factory=list)
    top_k: Optional[int] = Field(default=4, ge=1, le=10)


class FeedbackRequest(BaseModel):
    query: str
    answer: str
    intent: str
    feedback: str = Field(pattern="^(thumbs_up|thumbs_down)$")
    comments: Optional[str] = None


@app.post("/api/query", tags=["Core NLP"])
def query_endpoint(req: QueryRequest):
    """Deterministic demonstration and quick curriculum query understanding."""
    result = pipeline.process_query(req.query)
    return {
        "query": result["query"],
        "intent": result["intent"],
        "confidence": round(result["intent_confidence"], 2),
        "answer": result["answer"],
        "sources": result["sources"],
    }


@app.post("/api/chat", tags=["Core NLP"])
def chat_endpoint(req: ChatRequest):
    """Full 8-stage academic NLP + RAG student chatbot pipeline."""
    return pipeline.process_query(query=req.query, chat_history=req.chat_history, top_k=req.top_k or 4)


@app.get("/api/health", tags=["Health"])
def api_health_check():
    """Health check endpoint matching NLP-cornerstone contract."""
    return {
        "status": "healthy",
        "service": "CampusAI",
        "institution": settings.INSTITUTION_NAME,
        "mode": "full_hybrid_rag",
        "curriculum_version": settings.DEFAULT_CURRICULUM_VERSION
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Container probe health check."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "institution": settings.INSTITUTION_NAME,
        "environment": settings.ENVIRONMENT
    }


def _append_feedback_log(file_path: Path, entry: dict) -> bool:
    try:
        with _log_lock:
            data = json.loads(file_path.read_text(encoding="utf-8")) if file_path.exists() else []
            if not isinstance(data, list):
                return False
            data.append(entry)
            temporary = file_path.with_suffix(".tmp")
            temporary.write_text(json.dumps(data[-500:], indent=2), encoding="utf-8")
            temporary.replace(file_path)
        return True
    except (OSError, ValueError):
        logger.warning("Could not save feedback")
        return False


@app.post("/api/feedback", tags=["Feedback"])
def submit_feedback(feedback: FeedbackRequest):
    """Log student feedback for continuous model and citation evaluation."""
    entry = {"timestamp": datetime.now(timezone.utc).isoformat(), **feedback.model_dump()}
    if not _append_feedback_log(FEEDBACK_FILE, entry):
        raise HTTPException(status_code=503, detail="Feedback could not be saved. Please try again.")
    return {"status": "success", "message": "Feedback logged successfully"}


@app.get("/", tags=["Root"])
def root():
    frontend_index = settings.BASE_DIR / "frontend" / "dist" / "index.html"
    if frontend_index.is_file():
        return FileResponse(str(frontend_index))
    return {
        "message": f"Welcome to {settings.APP_TITLE}",
        "institution": settings.INSTITUTION_NAME,
        "location": settings.INSTITUTION_LOCATION,
        "version": settings.APP_VERSION,
        "documentation": "/docs"
    }


# Include Routers with /api/v1 prefix
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(academic.router, prefix=settings.API_V1_STR)
app.include_router(chat.router, prefix=settings.API_V1_STR)
app.include_router(sources.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)

# Mount Static Frontend Assets & SPA Fallback if frontend/dist exists
frontend_dist = settings.BASE_DIR / "frontend" / "dist"
if frontend_dist.is_dir() and (frontend_dist / "index.html").exists():
    assets_dir = frontend_dist / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="frontend-assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa_frontend(full_path: str):
        # Do not intercept API, docs, or OpenAPI schemas
        if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
            raise HTTPException(status_code=404, detail="API route not found")
        target_file = frontend_dist / full_path
        if full_path and target_file.is_file():
            return FileResponse(str(target_file))
        return FileResponse(str(frontend_dist / "index.html"))

