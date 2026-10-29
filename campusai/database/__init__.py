"""
Database package for CampusAI.
"""

from campusai.database.connection import Base, engine, get_db, SessionLocal, create_all_tables
from campusai.database.models import (
    Institution, Department, Program, CurriculumVersion, Course,
    Semester, CourseOffering, CourseUnit, CourseOutcome, Textbook,
    MinorStream, MinorStreamCourse, SourceDocument, ExtractionIssue,
    User, ChatSession, ChatMessage, ResponseCitation, Feedback, AuditLog
)
