"""Data ingestion package for CampusAI."""
from backend.data_ingestion.inventory import SourceInventoryManager, DocumentMetadata
from backend.data_ingestion.table_parser import CurriculumTableParser, ParsedSemester, ParsedSemesterCourse
from backend.data_ingestion.structure_parser import SyllabusStructureParser, ParsedCourseSyllabus, ParsedUnit, ParsedTextbook
from backend.data_ingestion.validator import AcademicRecordValidator, ValidationReport

__all__ = [
    "SourceInventoryManager", "DocumentMetadata",
    "CurriculumTableParser", "ParsedSemester", "ParsedSemesterCourse",
    "SyllabusStructureParser", "ParsedCourseSyllabus", "ParsedUnit", "ParsedTextbook",
    "AcademicRecordValidator", "ValidationReport"
]
