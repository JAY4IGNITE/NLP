"""Academic entity extractor. Re-exported from backend.nlp.entity_extractor."""
from backend.nlp.entity_extractor import (
    AcademicEntityExtractor,
    entity_extractor,
    ROMAN_NUMERALS,
    WORD_NUMBERS,
    DEPT_PATTERNS,
    KNOWN_COURSES
)

__all__ = [
    "AcademicEntityExtractor",
    "entity_extractor",
    "ROMAN_NUMERALS",
    "WORD_NUMBERS",
    "DEPT_PATTERNS",
    "KNOWN_COURSES"
]
