"""Database connection and session management for CampusAI.
Supports PostgreSQL as primary with SQLite fallback.
"""
import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from backend.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()


def get_engine():
    """Create database engine with fallback mechanism."""
    # Try PostgreSQL first if configured
    if settings.DATABASE_URL and not settings.DATABASE_URL.startswith("sqlite"):
        try:
            pg_engine = create_engine(
                settings.DATABASE_URL,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20
            )
            # Test connection
            with pg_engine.connect() as conn:
                pass
            logger.info("Connected to PostgreSQL database.")
            return pg_engine
        except Exception as e:
            logger.warning(f"Could not connect to PostgreSQL ({e}). Falling back to SQLite.")

    # SQLite fallback
    sqlite_url = settings.FALLBACK_SQLITE_URL
    sqlite_engine = create_engine(
        sqlite_url,
        connect_args={"check_same_thread": False} if sqlite_url.startswith("sqlite") else {}
    )
    logger.info(f"Using SQLite database: {sqlite_url}")
    return sqlite_engine


engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency for obtaining a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_all_tables():
    """Create all registered database tables."""
    Base.metadata.create_all(bind=engine)
