"""Table parser for academic curriculum documents.
Re-exported from backend.data_ingestion.table_parser for backward compatibility.
"""
from backend.data_ingestion.table_parser import (
    ParsedSemesterCourse,
    ParsedSemester,
    ROMAN_TO_INT,
    clean_cell,
    parse_numeric,
    CurriculumTableParser
)

__all__ = [
    "ParsedSemesterCourse",
    "ParsedSemester",
    "ROMAN_TO_INT",
    "clean_cell",
    "parse_numeric",
    "CurriculumTableParser"
]
