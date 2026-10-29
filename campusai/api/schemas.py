"""
Pydantic v2 schemas for CampusAI API requests and responses.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, EmailStr, Field


# Auth Schemas
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    role: str


class LoginRequest(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: str


# Academic Schemas
class DepartmentOut(BaseModel):
    id: int
    code: str
    name: str
    vision: Optional[str] = None
    mission: Optional[str] = None


class ProgramOut(BaseModel):
    id: int
    code: str
    name: str
    degree: str
    total_degree_credits: int


class CurriculumVersionOut(BaseModel):
    id: int
    version_string: str
    admission_batch: str
    is_active: bool


class CourseUnitOut(BaseModel):
    unit_number: int
    unit_roman: str
    title: Optional[str] = None
    content: str
    practice_content: Optional[str] = None
    source_page: Optional[int] = None


class CourseOutcomeOut(BaseModel):
    outcome_code: str
    description: str


class TextbookOut(BaseModel):
    book_type: str
    title: str
    raw_text: Optional[str] = None


class CourseOut(BaseModel):
    id: int
    code: str
    title: str
    department_code: Optional[str] = None
    category: Optional[str] = None
    level: Optional[str] = None
    credits: float
    lecture_hours: int
    tutorial_hours: int
    practical_hours: int
    total_hours: int
    prerequisite_text: Optional[str] = None
    source_document_id: Optional[str] = None
    source_page: Optional[int] = None


class CourseDetailOut(CourseOut):
    units: List[CourseUnitOut] = []
    outcomes: List[CourseOutcomeOut] = []
    textbooks: List[TextbookOut] = []


class SemesterCourseOut(BaseModel):
    code: str
    title: str
    category: str
    credits: float
    level: Optional[str] = None
    lecture_hours: int
    tutorial_hours: int
    practical_hours: int
    total_hours: int
    is_elective: bool
    source_page: Optional[int] = None


class SemesterOut(BaseModel):
    department: str
    department_code: str
    semester_number: int
    semester_roman: str
    total_credits: float
    total_courses: int
    courses: List[SemesterCourseOut] = []
    source_page: Optional[int] = None


# Chat Schemas
class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    department_code: Optional[str] = None
    curriculum_version: str = "Version 3.0"
    language_preference: Optional[str] = None


class CitationOut(BaseModel):
    doc_id: str
    title: str
    department: str
    page: int
    excerpt: str
    course_code: Optional[str] = None
    score: Optional[float] = None


class ChatResponse(BaseModel):
    answer: str
    intent: str
    domain: str
    language: str
    session_id: str
    entities: Dict[str, Any] = {}
    citations: List[CitationOut] = []
    source_type: str
    is_grounded: bool
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FeedbackRequest(BaseModel):
    session_id: Optional[str] = None
    message_id: Optional[int] = None
    rating: int  # 1 to 5
    category: Optional[str] = None
    comments: Optional[str] = None


# Admin Schemas
class ExtractionIssueOut(BaseModel):
    id: int
    doc_id: str
    course_code: Optional[str] = None
    issue_type: str
    severity: str
    details: Optional[Dict[str, Any]] = None
    status: str
    created_at: Optional[datetime] = None


class IssueUpdate(BaseModel):
    status: str
    resolution_notes: Optional[str] = None
