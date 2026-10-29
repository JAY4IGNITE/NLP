"""CRUD operations and database service functions for CampusAI.
Re-exported from backend.database.crud for backward compatibility.
"""
from backend.database.crud import (
    get_or_create_institution,
    get_or_create_department,
    get_or_create_program,
    get_or_create_curriculum_version,
    upsert_course
)

__all__ = [
    "get_or_create_institution",
    "get_or_create_department",
    "get_or_create_program",
    "get_or_create_curriculum_version",
    "upsert_course"
]
