"""SQLAlchemy models for CampusAI academic database.
Re-exported from backend.database.models for backward compatibility.
"""
from backend.database.models import (
    utc_now, Institution, Department, Program, CurriculumVersion, Course,
    Semester, CourseOffering, CourseUnit, CourseOutcome, Textbook,
    MinorStream, MinorStreamCourse, SourceDocument, ExtractionIssue,
    User, ChatSession, ChatMessage, ResponseCitation, Feedback, AuditLog
)

__all__ = [
    "utc_now", "Institution", "Department", "Program", "CurriculumVersion", "Course",
    "Semester", "CourseOffering", "CourseUnit", "CourseOutcome", "Textbook",
    "MinorStream", "MinorStreamCourse", "SourceDocument", "ExtractionIssue",
    "User", "ChatSession", "ChatMessage", "ResponseCitation", "Feedback", "AuditLog"
]
