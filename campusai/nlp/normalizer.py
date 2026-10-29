"""Query normalization module. Re-exported from backend.nlp.normalizer."""
from backend.nlp.normalizer import (
    DEPARTMENT_ALIASES,
    COMMON_COURSE_ABBREVIATIONS,
    ROMAN_NUMS,
    normalize_query
)

__all__ = [
    "DEPARTMENT_ALIASES",
    "COMMON_COURSE_ABBREVIATIONS",
    "ROMAN_NUMS",
    "normalize_query"
]
