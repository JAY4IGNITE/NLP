"""Database package for CampusAI."""
from backend.database.connection import engine, SessionLocal, get_db, create_all_tables, Base
from backend.database.models import (
    Course, CourseOffering, CourseOutcome, CourseUnit, CurriculumVersion,
    Department, ExtractionIssue, Feedback, Institution, Program,
    ResponseCitation, Semester, SourceDocument, Textbook, User, ChatSession, ChatMessage, AuditLog
)
from backend.database.sql_retriever import SQLAcademicRetriever

__all__ = [
    "engine", "SessionLocal", "get_db", "create_all_tables", "Base",
    "Course", "CourseOffering", "CourseOutcome", "CourseUnit", "CurriculumVersion",
    "Department", "ExtractionIssue", "Feedback", "Institution", "Program",
    "ResponseCitation", "Semester", "SourceDocument", "Textbook", "User",
    "ChatSession", "ChatMessage", "AuditLog", "SQLAcademicRetriever"
]
