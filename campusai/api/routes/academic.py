"""
Academic exploration endpoints: departments, curricula, courses, syllabi, semesters.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from campusai.api.dependencies import get_db
from campusai.api.schemas import (
    CourseDetailOut, CourseOut, CurriculumVersionOut, DepartmentOut,
    ProgramOut, SemesterOut
)
from campusai.database.models import (
    Course, CurriculumVersion, Department, Program, Semester
)
from campusai.database.sql_retriever import SQLAcademicRetriever

router = APIRouter(tags=["Academic Curriculum"])


@router.get("/departments", response_model=List[DepartmentOut])
def get_departments(db: Session = Depends(get_db)):
    """List all official engineering departments."""
    depts = db.query(Department).order_by(Department.name).all()
    return [
        DepartmentOut(
            id=d.id,
            code=d.code,
            name=d.name,
            vision=d.vision,
            mission=d.mission
        )
        for d in depts
    ]


@router.get("/curricula", response_model=List[CurriculumVersionOut])
def get_curricula(db: Session = Depends(get_db)):
    """List registered curriculum versions."""
    versions = db.query(CurriculumVersion).filter(CurriculumVersion.is_active == True).all()
    return [
        CurriculumVersionOut(
            id=v.id,
            version_string=v.version_string,
            admission_batch=v.admission_batch,
            is_active=v.is_active
        )
        for v in versions
    ]


@router.get("/courses", response_model=List[CourseOut])
def get_courses(
    department_code: Optional[str] = Query(None, description="Filter by department code e.g. CSE, IT"),
    search: Optional[str] = Query(None, description="Search course title or code"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Catalog of courses with department filtering and search."""
    query = db.query(Course)
    if department_code:
        query = query.join(Department, Course.department_id == Department.id).filter(
            Department.code.ilike(department_code.strip())
        )
    if search:
        query = query.filter(
            (Course.code.ilike(f"%{search}%")) | (Course.title.ilike(f"%{search}%"))
        )

    courses = query.offset(skip).limit(limit).all()
    return [
        CourseOut(
            id=c.id,
            code=c.code,
            title=c.title,
            department_code=c.department.code if c.department else None,
            category=c.category,
            level=c.level,
            credits=c.credits,
            lecture_hours=c.lecture_hours,
            tutorial_hours=c.tutorial_hours,
            practical_hours=c.practical_hours,
            total_hours=c.total_hours,
            prerequisite_text=c.prerequisite_text,
            source_document_id=c.source_document_id,
            source_page=c.source_page
        )
        for c in courses
    ]


@router.get("/courses/{course_id}", response_model=CourseDetailOut)
def get_course_detail(course_id: int, db: Session = Depends(get_db)):
    """Detailed course record including units, outcomes, and textbooks."""
    c = db.query(Course).filter(Course.id == course_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Course not found")

    return CourseDetailOut(
        id=c.id,
        code=c.code,
        title=c.title,
        department_code=c.department.code if c.department else None,
        category=c.category,
        level=c.level,
        credits=c.credits,
        lecture_hours=c.lecture_hours,
        tutorial_hours=c.tutorial_hours,
        practical_hours=c.practical_hours,
        total_hours=c.total_hours,
        prerequisite_text=c.prerequisite_text,
        source_document_id=c.source_document_id,
        source_page=c.source_page,
        units=[
            {
                "unit_number": u.unit_number,
                "unit_roman": u.unit_roman,
                "title": u.title,
                "content": u.content,
                "practice_content": u.practice_content,
                "source_page": u.source_page
            }
            for u in c.units
        ],
        outcomes=[{"outcome_code": o.outcome_code, "description": o.description} for o in c.outcomes],
        textbooks=[{"book_type": b.book_type, "title": b.title, "raw_text": b.raw_text} for b in c.textbooks]
    )


@router.get("/semesters", response_model=SemesterOut)
def get_semester(
    department_code: str = Query(..., description="Department code e.g. CSE"),
    semester_number: int = Query(..., ge=1, le=8, description="Semester number 1 to 8")
):
    """Retrieve full semester curriculum table with subjects, categories, and credits."""
    retriever = SQLAcademicRetriever()
    sem_data = retriever.get_semester_courses(semester_number, department_code)
    if not sem_data:
        raise HTTPException(status_code=404, detail="Semester curriculum not found for specified parameters")

    return SemesterOut(**sem_data)
