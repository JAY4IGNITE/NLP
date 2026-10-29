"""
Application configuration for CampusAI.
Handles environment variables with Pydantic Settings.
"""

from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application Info
    APP_NAME: str = "CampusAI"
    APP_TITLE: str = "CampusAI: Aditya University Intelligent Academic Helpdesk"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Institution Metadata
    INSTITUTION_NAME: str = "Aditya University"
    INSTITUTION_LOCATION: str = "Surampalem, Andhra Pradesh, India"
    INSTITUTION_WEBSITE: str = "https://www.adityauniversity.in/"
    DEFAULT_CURRICULUM_VERSION: str = "Version 3.0"
    DEFAULT_ADMISSION_BATCH: str = "2024-25"

    # API Server Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
    ]

    # Security & Auth
    SECRET_KEY: str = "campusai-production-super-secret-key-change-in-production-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/postgres"
    FALLBACK_SQLITE_URL: str = "sqlite:///campusai.db"
    USE_SQLITE_FALLBACK: bool = True

    # Storage Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    DOCUMENTS_DIR: Path = DATA_DIR / "institutional" / "curriculum"
    PROCESSED_DIR: Path = DATA_DIR / "processed"
    MANIFESTS_DIR: Path = DATA_DIR / "manifests"
    INDICES_DIR: Path = DATA_DIR / "indices"
    EVALUATIONS_DIR: Path = DATA_DIR / "evaluations"
    MODELS_DIR: Path = DATA_DIR / "models"

    # Machine Learning & NLP
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    BGE_M3_MODEL_NAME: str = "BAAI/bge-m3"
    RERANKER_MODEL_NAME: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    INTENT_MODEL_TYPE: str = "tfidf_lr"  # 'tfidf_lr', 'sentence_transformer', 'xlm_roberta'
    DEFAULT_DEVICE: str = "cpu"

    # Hybrid Search Settings
    BM25_K1: float = 1.5
    BM25_B: float = 0.75
    RRF_K: int = 60
    TOP_K_RETRIEVAL: int = 10
    TOP_K_RERANK: int = 5

    # LLM Settings
    LLM_PROVIDER: str = "mock"  # 'gemini', 'openai', 'ollama', 'mock'
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL_NAME: str = "gemini-1.5-flash"
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
        ]:
            d.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.init_directories()
