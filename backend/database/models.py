"""SQLAlchemy models for CampusAI academic database.
Normalized relational schema modeling institutional, curriculum, syllabus,
evidence provenance, and conversation entities.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, JSON, Table
)
from sqlalchemy.orm import relationship
from backend.database.connection import Base


def utc_now():
    """Return timezone-aware current UTC datetime."""
    return datetime.now(timezone.utc)


class Institution(Base):
    __tablename__ = "institutions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    short_name = Column(String(50), default="Aditya")
    location = Column(String(255), nullable=False)
    website = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=utc_now)

    departments = relationship("Department", back_populates="institution")


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id"))
    code = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    vision = Column(Text, nullable=True)
    mission = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    institution = relationship("Institution", back_populates="departments")
    programs = relationship("Program", back_populates="department")
    courses = relationship("Course", back_populates="department")


class Program(Base):
    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    code = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    degree = Column(String(50), default="B.Tech.")
    total_degree_credits = Column(Integer, default=160)
    created_at = Column(DateTime, default=utc_now)

    department = relationship("Department", back_populates="programs")
    curriculum_versions = relationship("CurriculumVersion", back_populates="program")
    semesters = relationship("Semester", back_populates="program")


class CurriculumVersion(Base):
    __tablename__ = "curriculum_versions"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    version_string = Column(String(50), nullable=False)  # e.g., 'Version 3.0'
    admission_batch = Column(String(50), nullable=False)  # e.g., '2024-25'
    bos_approval_date = Column(String(100), nullable=True)
    academic_council_approval_date = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)

    program = relationship("Program", back_populates="curriculum_versions")
    courses = relationship("Course", back_populates="curriculum_version")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), index=True, nullable=False)
    title = Column(Text, index=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    curriculum_version_id = Column(Integer, ForeignKey("curriculum_versions.id"), nullable=True)
    category = Column(String(50), nullable=True)  # MCC, MDC, AEC, VAC, SEC, MC, PROJ, etc.
    level = Column(String(20), nullable=True)  # FC, IC, AC
    credits = Column(Float, nullable=False, default=3.0)
    lecture_hours = Column(Integer, default=2)
    tutorial_hours = Column(Integer, default=0)
    practical_hours = Column(Integer, default=0)
    total_hours = Column(Integer, default=3)
    prerequisite_text = Column(Text, nullable=True)
    source_document_id = Column(String(50), nullable=True)
    source_page = Column(Integer, nullable=True)
    is_verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)

    department = relationship("Department", back_populates="courses")
    curriculum_version = relationship("CurriculumVersion", back_populates="courses")
    units = relationship("CourseUnit", back_populates="course", cascade="all, delete-orphan")
    outcomes = relationship("CourseOutcome", back_populates="course", cascade="all, delete-orphan")
    textbooks = relationship("Textbook", back_populates="course", cascade="all, delete-orphan")
    offerings = relationship("CourseOffering", back_populates="course")


class Semester(Base):
    __tablename__ = "semesters"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    curriculum_version_id = Column(Integer, ForeignKey("curriculum_versions.id"), nullable=False)
    semester_number = Column(Integer, nullable=False)  # 1 to 8
    roman_numeral = Column(String(10), nullable=False)  # I to VIII
    total_credits = Column(Float, nullable=False)
    total_hours = Column(Integer, nullable=True)
    source_page = Column(Integer, nullable=True)

    program = relationship("Program", back_populates="semesters")
    offerings = relationship("CourseOffering", back_populates="semester")


class CourseOffering(Base):
    __tablename__ = "course_offerings"

    id = Column(Integer, primary_key=True, index=True)
    semester_id = Column(Integer, ForeignKey("semesters.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    slot_type = Column(String(50), default="Core")  # Core, Elective, Mandatory, Lab
    is_elective = Column(Boolean, default=False)
    elective_group_name = Column(String(100), nullable=True)

    semester = relationship("Semester", back_populates="offerings")
    course = relationship("Course", back_populates="offerings")


class CourseUnit(Base):
    __tablename__ = "course_units"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    unit_number = Column(Integer, nullable=False)  # 1 to 5
    unit_roman = Column(String(10), nullable=False)  # I, II, III, IV, V
    title = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    practice_content = Column(Text, nullable=True)
    source_page = Column(Integer, nullable=True)
    source_document = Column(String(100), nullable=True)

    course = relationship("Course", back_populates="units")


class CourseOutcome(Base):
    __tablename__ = "course_outcomes"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    outcome_code = Column(String(20), nullable=False)  # CO1, CO2, etc.
    description = Column(Text, nullable=False)

    course = relationship("Course", back_populates="outcomes")


class Textbook(Base):
    __tablename__ = "textbooks"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    book_type = Column(String(50), default="Textbook")  # Textbook, Reference
    title = Column(Text, nullable=False)
    authors = Column(Text, nullable=True)
    publisher = Column(Text, nullable=True)
    edition = Column(Text, nullable=True)
    isbn = Column(String(100), nullable=True)
    raw_text = Column(Text, nullable=True)

    course = relationship("Course", back_populates="textbooks")


class MinorStream(Base):
    __tablename__ = "minor_streams"

    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    stream_name = Column(String(255), nullable=False)
    total_credits = Column(Integer, default=20)
    description = Column(Text, nullable=True)


class MinorStreamCourse(Base):
    __tablename__ = "minor_stream_courses"

    id = Column(Integer, primary_key=True, index=True)
    minor_stream_id = Column(Integer, ForeignKey("minor_streams.id"), nullable=False)
    course_code = Column(String(20), nullable=False)
    course_title = Column(String(255), nullable=False)
    credits = Column(Float, default=3.0)
    level = Column(String(20), nullable=True)
    prerequisite = Column(String(255), nullable=True)


class SourceDocument(Base):
    __tablename__ = "source_documents"

    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String(50), unique=True, index=True, nullable=False)
    file_name = Column(String(255), nullable=False)
    sha256 = Column(String(64), nullable=False)
    department_code = Column(String(20), nullable=False)
    curriculum_version = Column(String(50), nullable=False)
    total_pages = Column(Integer, nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    extraction_status = Column(String(50), default="extracted")
    created_at = Column(DateTime, default=utc_now)


class ExtractionIssue(Base):
    __tablename__ = "extraction_issues"

    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String(50), nullable=False)
    issue_type = Column(String(100), nullable=False)  # conflicting_credits, missing_field, duplicate_code
    severity = Column(String(20), default="warning")  # info, warning, error
    course_code = Column(String(50), nullable=True)
    details = Column(JSON, nullable=True)
    status = Column(String(50), default="pending_review")  # pending_review, resolved, dismissed
    resolved_by = Column(String(100), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="student")  # student, faculty, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    department_code = Column(String(20), nullable=True)
    curriculum_version = Column(String(50), default="Version 3.0")
    language = Column(String(10), default="en")
    title = Column(String(255), default="Academic Helpdesk Inquiry")
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    intent = Column(String(100), nullable=True)
    entities = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    session = relationship("ChatSession", back_populates="messages")
    citations = relationship("ResponseCitation", back_populates="message", cascade="all, delete-orphan")


class ResponseCitation(Base):
    __tablename__ = "response_citations"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("chat_messages.id"), nullable=False)
    source_doc_id = Column(String(50), nullable=False)
    source_title = Column(String(255), nullable=False)
    department_code = Column(String(20), nullable=False)
    curriculum_version = Column(String(50), default="Version 3.0")
    source_page = Column(Integer, nullable=False)
    source_excerpt = Column(Text, nullable=False)
    course_code = Column(String(20), nullable=True)
    confidence_score = Column(Float, default=1.0)

    message = relationship("ChatMessage", back_populates="citations")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), nullable=True)
    message_id = Column(Integer, nullable=True)
    rating = Column(Integer, nullable=False)  # 1 for thumbs down, 5 for thumbs up
    category = Column(String(50), nullable=True)  # factual_error, helpful, citation_wrong, unclear
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(100), nullable=False)
    actor = Column(String(100), default="system")
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=utc_now)
