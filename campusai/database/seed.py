"""CampusAI Academic Database Seeding & Ingestion Orchestrator.
Re-exported from backend.database.seed for backward compatibility.
"""
from backend.database.seed import (
    seed_institution,
    seed_department_and_program,
    seed_semester_curriculum,
    seed_syllabi_units_and_references,
    seed_default_users,
    seed_database
)

__all__ = [
    "seed_institution",
    "seed_department_and_program",
    "seed_semester_curriculum",
    "seed_syllabi_units_and_references",
    "seed_default_users",
    "seed_database"
]

if __name__ == "__main__":
    seed_database()
