"""Structure-aware chunker for curriculum knowledge base.
Produces semantically rich, metadata-grounded chunks from the academic database.
"""

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from backend.database.connection import SessionLocal
from backend.database.models import Course, CourseUnit, Department, Semester, Textbook


@dataclass
class KnowledgeChunk:
    chunk_id: str
    chunk_type: str
    course_code: Optional[str]
    course_title: Optional[str]
    department_code: str
    department_name: str
    semester_num: Optional[int]
    unit_num: Optional[int]
    content: str
    source_document_id: str
    source_page: int
    metadata: Dict[str, Any]


class KnowledgeChunker:
    """Builds structured chunks with complete metadata provenance."""

    def __init__(self, db: Optional[Session] = None):
        self.db = db or SessionLocal()

    def generate_all_chunks(self) -> List[KnowledgeChunk]:
        """Produce all passage chunks across courses, units, and semesters."""
        chunks: List[KnowledgeChunk] = []

        courses = self.db.query(Course).all()
        for c in courses:
            dept_name = c.department.name if c.department else "General Engineering"
            dept_code = c.department.code if c.department else "GEN"

            outcomes_text = ""
            if c.outcomes:
                outcomes_text = "\nCourse Outcomes:\n" + "\n".join(
                    [f"- {o.outcome_code}: {o.description}" for o in c.outcomes]
                )

            overview_content = (
                f"Course Code: {c.code}\n"
                f"Course Title: {c.title}\n"
                f"Department: {dept_name} ({dept_code})\n"
                f"Credits: {c.credits} (Lecture: {c.lecture_hours}, Tutorial: {c.tutorial_hours}, Practical: {c.practical_hours})\n"
                f"Category: {c.category or 'MCC'}, Level: {c.level or 'FC'}\n"
                f"Total Hours: {c.total_hours}\n"
                f"Prerequisites: {c.prerequisite_text or 'None'}"
                f"{outcomes_text}"
            )

            chunks.append(KnowledgeChunk(
                chunk_id=f"CHK-CRS-{c.code}-{c.id}",
                chunk_type="course_overview",
                course_code=c.code,
                course_title=c.title,
                department_code=dept_code,
                department_name=dept_name,
                semester_num=None,
                unit_num=None,
                content=overview_content,
                source_document_id=c.source_document_id or f"DOC-{dept_code}",
                source_page=c.source_page or 1,
                metadata={
                    "credits": c.credits,
                    "category": c.category,
                    "level": c.level,
                    "prerequisites": c.prerequisite_text,
                }
            ))

            for u in c.units:
                unit_content = (
                    f"Course: {c.title} ({c.code})\n"
                    f"Department: {dept_name} ({dept_code})\n"
                    f"{u.unit_roman} Syllabus: {u.title or 'Topics'}\n"
                    f"Detailed Topics: {u.content}"
                )
                if u.practice_content:
                    unit_content += f"\nPractice / Lab Exercises: {u.practice_content}"

                chunks.append(KnowledgeChunk(
                    chunk_id=f"CHK-UNT-{c.code}-U{u.unit_number}-{u.id}",
                    chunk_type="unit_syllabus",
                    course_code=c.code,
                    course_title=c.title,
                    department_code=dept_code,
                    department_name=dept_name,
                    semester_num=None,
                    unit_num=u.unit_number,
                    content=unit_content,
                    source_document_id=u.source_document or c.source_document_id or f"DOC-{dept_code}",
                    source_page=u.source_page or c.source_page or 1,
                    metadata={
                        "unit_number": u.unit_number,
                        "unit_roman": u.unit_roman,
                        "unit_title": u.title
                    }
                ))

            if c.textbooks:
                books_lines = [f"- [{b.book_type}] {b.title}" for b in c.textbooks]
                tb_content = (
                    f"Course: {c.title} ({c.code})\n"
                    f"Recommended Textbooks and References:\n"
                    + "\n".join(books_lines)
                )
                chunks.append(KnowledgeChunk(
                    chunk_id=f"CHK-TBK-{c.code}-{c.id}",
                    chunk_type="textbooks",
                    course_code=c.code,
                    course_title=c.title,
                    department_code=dept_code,
                    department_name=dept_name,
                    semester_num=None,
                    unit_num=None,
                    content=tb_content,
                    source_document_id=c.source_document_id or f"DOC-{dept_code}",
                    source_page=c.source_page or 1,
                    metadata={"books_count": len(c.textbooks)}
                ))

        semesters = self.db.query(Semester).all()
        for s in semesters:
            dept_name = s.program.department.name if s.program and s.program.department else "Aditya University"
            dept_code = s.program.department.code if s.program and s.program.department else "GEN"

            courses_in_sem = [
                f"- {off.course.code}: {off.course.title} ({off.course.credits} credits, Category: {off.slot_type or off.course.category})"
                for off in s.offerings if off.course
            ]

            sem_content = (
                f"Aditya University B.Tech Curriculum 2024 (Version 3.0)\n"
                f"Department: {dept_name} ({dept_code})\n"
                f"Semester {s.roman_numeral} (Semester {s.semester_number})\n"
                f"Total Semester Credits: {s.total_credits}\n"
                f"Subjects Offered:\n" + "\n".join(courses_in_sem)
            )

            chunks.append(KnowledgeChunk(
                chunk_id=f"CHK-SEM-{dept_code}-S{s.semester_number}",
                chunk_type="semester_summary",
                course_code=None,
                course_title=None,
                department_code=dept_code,
                department_name=dept_name,
                semester_num=s.semester_number,
                unit_num=None,
                content=sem_content,
                source_document_id=f"DOC-{dept_code}",
                source_page=s.source_page or 1,
                metadata={
                    "semester_number": s.semester_number,
                    "semester_roman": s.roman_numeral,
                    "total_credits": s.total_credits,
                    "courses_count": len(courses_in_sem)
                }
            ))

        return chunks
