"""Application configuration and environment settings for CampusAI Backend."""
import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = DATA_DIR / "models"
DOCUMENTS_DIR = DATA_DIR / "institutional" / "curriculum"
REPORTS_DIR = BASE_DIR / "reports"
STRUCTURED_DIR = DATA_DIR / "structured"
INDICES_DIR = DATA_DIR / "indices"
PROCESSED_DIR = DATA_DIR / "processed"
MANIFESTS_DIR = DATA_DIR / "manifests"
EVALUATIONS_DIR = DATA_DIR / "evaluations"

# Ensure runtime directories exist
for p in [DATA_DIR, MODELS_DIR, DOCUMENTS_DIR, REPORTS_DIR, STRUCTURED_DIR, INDICES_DIR, PROCESSED_DIR, MANIFESTS_DIR, EVALUATIONS_DIR]:
    p.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    """Unified application settings with environment variable support."""
    # App Information
    APP_NAME: str = "CampusAI"
    APP_TITLE: str = "CampusAI: Aditya University Intelligent Academic Helpdesk"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    HOST: str = os.getenv("BACKEND_HOST", "127.0.0.1")
    PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    API_HOST: str = HOST
    API_PORT: int = PORT
    API_V1_STR: str = "/api/v1"

    # Institution Metadata
    INSTITUTION_NAME: str = "Aditya University"
    INSTITUTION_LOCATION: str = "Surampalem, Andhra Pradesh, India"
    INSTITUTION_WEBSITE: str = "https://www.adityauniversity.in/"
    DEFAULT_CURRICULUM_VERSION: str = "Version 3.0"
    DEFAULT_ADMISSION_BATCH: str = "2024-25"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "*"
    ]

    # Security & Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "campusai-production-super-secret-key-change-in-production-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")
    FALLBACK_SQLITE_URL: str = "sqlite:///campusai.db"
    USE_SQLITE_FALLBACK: bool = True

    # Storage Paths
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = DATA_DIR
    MODELS_DIR: Path = MODELS_DIR
    DOCUMENTS_DIR: Path = DOCUMENTS_DIR
    REPORTS_DIR: Path = REPORTS_DIR
    STRUCTURED_DIR: Path = STRUCTURED_DIR
    INDICES_DIR: Path = INDICES_DIR
    PROCESSED_DIR: Path = PROCESSED_DIR
    MANIFESTS_DIR: Path = MANIFESTS_DIR
    EVALUATIONS_DIR: Path = EVALUATIONS_DIR

    # Confidence and Retrieval Thresholds (Strict Hallucination Prevention)
    INTENT_CONFIDENCE_THRESHOLD: float = float(os.getenv("INTENT_CONFIDENCE_THRESHOLD", "0.12"))
    RETRIEVAL_SCORE_THRESHOLD: float = float(os.getenv("RETRIEVAL_SCORE_THRESHOLD", "0.35"))
    RERANKER_TOP_K: int = int(os.getenv("RERANKER_TOP_K", "4"))
    TOP_K_RETRIEVAL: int = int(os.getenv("TOP_K_RETRIEVAL", "10"))
    TOP_K_RERANK: int = int(os.getenv("TOP_K_RERANK", "5"))
    MAX_HISTORY_TURNS: int = int(os.getenv("MAX_HISTORY_TURNS", "5"))

    # Machine Learning & NLP
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    BGE_M3_MODEL_NAME: str = "BAAI/bge-m3"
    RERANKER_MODEL_NAME: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    INTENT_MODEL_TYPE: str = "tfidf_lr"
    DEFAULT_DEVICE: str = "cpu"

    # Hybrid Search Settings
    BM25_K1: float = 1.5
    BM25_B: float = 0.75
    RRF_K: int = 60

    # LLM Settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "mock")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", None)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY", None)
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "gemini-1.5-flash")
    LLM_TEMPERATURE: float = 0.1
    MAX_TOKENS: int = 1024

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def init_directories(self) -> None:
        """Ensure runtime directories exist."""
        for d in [
            self.DATA_DIR,
            self.PROCESSED_DIR,
            self.MANIFESTS_DIR,
            self.INDICES_DIR,
            self.EVALUATIONS_DIR,
            self.MODELS_DIR,
            self.STRUCTURED_DIR,
            self.REPORTS_DIR,
        ]:
            d.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.init_directories()
