"""Structure parser for extracting detailed course syllabi, unit breakdowns,
course outcomes, and textbook/reference records from university curriculum documents.
Re-exported from backend.data_ingestion.structure_parser for backward compatibility.
"""
from backend.data_ingestion.structure_parser import (
    ParsedUnit,
    ParsedTextbook,
    ParsedCourseSyllabus,
    ROMAN_TO_NUM,
    SyllabusStructureParser
)

__all__ = [
    "ParsedUnit",
    "ParsedTextbook",
    "ParsedCourseSyllabus",
    "ROMAN_TO_NUM",
    "SyllabusStructureParser"
]
