"""Academic record validator and conflict detection engine.
Re-exported from backend.data_ingestion.validator for backward compatibility.
"""
from backend.data_ingestion.validator import (
    ValidationReport,
    COURSE_CODE_PATTERN,
    AcademicRecordValidator
)

__all__ = [
    "ValidationReport",
    "COURSE_CODE_PATTERN",
    "AcademicRecordValidator"
]
