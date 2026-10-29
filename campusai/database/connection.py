"""Database connection and session management for CampusAI.
Re-exported from backend.database.connection for backward compatibility.
"""
from backend.database.connection import (
    Base, engine, SessionLocal, get_engine, get_db, create_all_tables
)

__all__ = [
    "Base", "engine", "SessionLocal", "get_engine", "get_db", "create_all_tables"
]
