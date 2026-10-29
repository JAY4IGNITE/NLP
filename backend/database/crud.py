"""CRUD operations and database service functions for CampusAI."""
from typing import Any, Dict, List, Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session
from backend.database.models import (
    Course, CourseOffering, CourseOutcome, CourseUnit, CurriculumVersion,
    Department, ExtractionIssue, Feedback, Institution, Program,
    ResponseCitation, Semester, SourceDocument, Textbook, User, ChatSession, ChatMessage
)


def get_or_create_institution(db: Session, name: str, location: str, website: str) -> Institution:
    inst = db.query(Institution).filter(Institution.name == name).first()
    if not inst:
        inst = Institution(name=name, location=location, website=website)
        db.add(inst)
        db.commit()
        db.refresh(inst)
    return inst


def get_or_create_department(db: Session, inst_id: int, code: str, name: str) -> Department:
    dept = db.query(Department).filter(Department.code == code).first()
    if not dept:
        dept = Department(institution_id=inst_id, code=code, name=name)
        db.add(dept)
        db.commit()
        db.refresh(dept)
    return dept


def get_or_create_program(db: Session, dept_id: int, code: str, name: str) -> Program:
    prog = db.query(Program).filter(Program.department_id == dept_id, Program.code == code).first()
    if not prog:
        prog = Program(department_id=dept_id, code=code, name=name)
        db.add(prog)
        db.commit()
        db.refresh(prog)
    return prog


def get_or_create_curriculum_version(
    db: Session, prog_id: int, version_string: str = "Version 3.0", batch: str = "2024-25"
) -> CurriculumVersion:
    cv = db.query(CurriculumVersion).filter(
        CurriculumVersion.program_id == prog_id,
        CurriculumVersion.version_string == version_string
    ).first()
    if not cv:
        cv = CurriculumVersion(
            program_id=prog_id,
            version_string=version_string,
            admission_batch=batch,
            is_active=True
        )
        db.add(cv)
        db.commit()
        db.refresh(cv)
    return cv


def upsert_course(
    db: Session,
    code: str,
    title: str,
    dept_id: Optional[int],
    curriculum_version_id: Optional[int],
    category: str = "MCC",
    level: str = "FC",
    credits: float = 3.0,
    l_hrs: int = 2,
    t_hrs: int = 0,
    p_hrs: int = 0,
    tot_hrs: int = 3,
    prerequisite_text: Optional[str] = None,
    source_doc_id: Optional[str] = None,
    source_page: Optional[int] = None
) -> Course:
    course = db.query(Course).filter(
        Course.code == code,
        Course.department_id == dept_id
    ).first()

    if not course:
        course = db.query(Course).filter(Course.code == code).first()

    if not course:
        course = Course(
            code=code,
            title=title,
            department_id=dept_id,
            curriculum_version_id=curriculum_version_id,
            category=category,
            level=level,
            credits=credits,
            lecture_hours=l_hrs,
            tutorial_hours=t_hrs,
            practical_hours=p_hrs,
            total_hours=tot_hrs,
            prerequisite_text=prerequisite_text,
            source_document_id=source_doc_id,
            source_page=source_page,
            is_verified=True
        )
        db.add(course)
        db.commit()
        db.refresh(course)
    else:
        # Update details if richer info found
        if title and len(title) > len(course.title or ""):
            course.title = title
        if credits > 0:
            course.credits = credits
        if source_page and not course.source_page:
            course.source_page = source_page
        if source_doc_id and not course.source_document_id:
            course.source_document_id = source_doc_id
        db.commit()
        db.refresh(course)
    return course
