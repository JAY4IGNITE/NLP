"""Typed SQL retrieval layer for CampusAI.
Implements read-only structured academic queries for exact facts:
course codes, credits, semester curriculum listings, degree totals,
prerequisites, syllabus units, and cross-department comparisons.
"""

import re
from typing import Any, Dict, List, Optional
from sqlalchemy import or_, func, and_
from sqlalchemy.orm import Session
from backend.database.connection import SessionLocal
from backend.database.models import (
    Course, CourseOffering, CourseOutcome, CourseUnit, Department,
    ExtractionIssue, Program, Semester, Textbook
)


class SQLAcademicRetriever:
    """Provides typed, exact-match structured queries over the academic database."""

    def __init__(self, db: Optional[Session] = None):
        self.db = db or SessionLocal()

    def get_course_by_code(self, code: str, dept_code: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retrieve exact course by course code, optionally filtered by department."""
        if dept_code:
            c = (
                self.db.query(Course)
                .join(Department, Course.department_id == Department.id)
                .filter(Course.code.ilike(code.strip()), Department.code.ilike(dept_code.strip()))
                .first()
            )
            if c:
                return self._format_course_dict(c)

        course = self.db.query(Course).filter(Course.code.ilike(code.strip())).first()
        return self._format_course_dict(course) if course else None

    def find_courses_by_name(self, name_query: str, dept_code: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search courses by title keywords with token matching."""
        tokens = [t for t in re.findall(r"\b[A-Za-z0-9]+\b", name_query) if len(t) > 2 and t.lower() not in ["and", "the", "for", "using"]]
        if not tokens:
            tokens = [name_query.strip()]

        conditions = [Course.title.ilike(f"%{tok}%") for tok in tokens]

        query = self.db.query(Course).filter(and_(*conditions))
        if dept_code:
            dept_matches = (
                query.join(Department, Course.department_id == Department.id)
                .filter(Department.code.ilike(dept_code.strip()))
                .limit(10)
                .all()
            )
            if dept_matches:
                return [self._format_course_dict(c) for c in dept_matches]

        courses = query.limit(10).all()
        return [self._format_course_dict(c) for c in courses]

    def get_semester_courses(
        self, semester_num: int, dept_code: str, version: str = "Version 3.0"
    ) -> Optional[Dict[str, Any]]:
        """Retrieve all subjects, categories, and credits for a specific semester and department."""
        dept = self.db.query(Department).filter(Department.code.ilike(dept_code.strip())).first()
        if not dept:
            return None

        prog = self.db.query(Program).filter(Program.department_id == dept.id).first()
        if not prog:
            return None

        sem = self.db.query(Semester).filter(
            Semester.program_id == prog.id,
            Semester.semester_number == semester_num
        ).first()

        if not sem:
            return None

        offerings = (
            self.db.query(CourseOffering, Course)
            .join(Course, CourseOffering.course_id == Course.id)
            .filter(CourseOffering.semester_id == sem.id)
            .all()
        )

        course_list = []
        for off, crs in offerings:
            course_list.append({
                "code": crs.code,
                "title": crs.title,
                "category": off.slot_type or crs.category,
                "level": crs.level,
                "credits": crs.credits,
                "lecture_hours": crs.lecture_hours,
                "tutorial_hours": crs.tutorial_hours,
                "practical_hours": crs.practical_hours,
                "total_hours": crs.total_hours,
                "is_elective": off.is_elective,
                "source_page": crs.source_page,
            })

        return {
            "department": dept.name,
            "department_code": dept.code,
            "semester_number": semester_num,
            "semester_roman": sem.roman_numeral,
            "total_credits": sem.total_credits,
            "total_courses": len(course_list),
            "courses": course_list,
            "source_page": sem.source_page
        }

    def get_course_credits(self, code_or_title: str, dept_code: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Look up credits, lecture, tutorial, practical hours for a course."""
        course_data = self.get_course_by_code(code_or_title, dept_code)
        if not course_data:
            matches = self.find_courses_by_name(code_or_title, dept_code)
            if matches:
                course_data = matches[0]

        if not course_data:
            return None

        return {
            "course_code": course_data["code"],
            "course_title": course_data["title"],
            "credits": course_data["credits"],
            "lecture_hours": course_data["lecture_hours"],
            "tutorial_hours": course_data["tutorial_hours"],
            "practical_hours": course_data["practical_hours"],
            "total_hours": course_data["total_hours"],
            "category": course_data["category"],
            "source_document_id": course_data["source_document_id"],
            "source_page": course_data["source_page"]
        }

    def get_course_prerequisites(self, code_or_title: str, dept_code: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retrieve prerequisite information for a course."""
        course = self.db.query(Course).filter(Course.code.ilike(code_or_title.strip())).first()
        if not course:
            matches = self.find_courses_by_name(code_or_title, dept_code)
            if matches:
                course = self.db.query(Course).filter(Course.id == matches[0]["id"]).first()
        if not course:
            return None
        return {
            "course_code": course.code,
            "course_title": course.title,
            "prerequisites": course.prerequisite_text or "No prior prerequisites are specified for this course in the 2024 academic regulations.",
            "source_document_id": course.source_document_id or f"DOC-{course.department.code if course.department else 'GEN'}",
            "source_page": course.source_page or 1
        }

    def get_course_textbooks(self, code_or_title: str, dept_code: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retrieve prescribed textbooks and reference materials for a course."""
        course = self.db.query(Course).filter(Course.code.ilike(code_or_title.strip())).first()
        if not course:
            matches = self.find_courses_by_name(code_or_title, dept_code)
            if matches:
                course = self.db.query(Course).filter(Course.id == matches[0]["id"]).first()
        if not course:
            return None
        books = self.db.query(Textbook).filter(Textbook.course_id == course.id).all()
        return {
            "course_code": course.code,
            "course_title": course.title,
            "textbooks": [
                {
                    "type": b.book_type or "Textbook",
                    "title": b.title,
                    "authors": b.authors or "Official Curriculum Board",
                    "publisher": b.publisher or "Aditya University Press",
                    "edition": b.edition or "Latest Edition"
                }
                for b in books
            ],
            "source_document_id": course.source_document_id or f"DOC-{course.department.code if course.department else 'GEN'}",
            "source_page": course.source_page or 1
        }

    def get_course_outcomes(self, code_or_title: str, dept_code: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retrieve course outcomes (COs) for a course."""
        course = self.db.query(Course).filter(Course.code.ilike(code_or_title.strip())).first()
        if not course:
            matches = self.find_courses_by_name(code_or_title, dept_code)
            if matches:
                course = self.db.query(Course).filter(Course.id == matches[0]["id"]).first()
        if not course:
            return None
        cos = self.db.query(CourseOutcome).filter(CourseOutcome.course_id == course.id).order_by(CourseOutcome.outcome_code).all()
        return {
            "course_code": course.code,
            "course_title": course.title,
            "outcomes": [
                {
                    "code": co.outcome_code,
                    "description": co.description
                }
                for co in cos
            ],
            "source_document_id": course.source_document_id or f"DOC-{course.department.code if course.department else 'GEN'}",
            "source_page": course.source_page or 1
        }

    def get_course_units(self, code_or_title: str, unit_num: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Retrieve syllabus units for a course."""
        course = None
        course = self.db.query(Course).filter(Course.code.ilike(code_or_title.strip())).first()
        if not course:
            matches = self.find_courses_by_name(code_or_title)
            if matches:
                course = self.db.query(Course).filter(Course.id == matches[0]["id"]).first()

        if not course:
            return None

        u_query = self.db.query(CourseUnit).filter(CourseUnit.course_id == course.id)
        if unit_num is not None:
            u_query = u_query.filter(CourseUnit.unit_number == unit_num)

        units = u_query.order_by(CourseUnit.unit_number).all()

        return {
            "course_code": course.code,
            "course_title": course.title,
            "total_units": len(course.units),
            "units": [
                {
                    "unit_number": u.unit_number,
                    "unit_roman": u.unit_roman,
                    "title": u.title,
                    "content": u.content,
                    "practice_content": u.practice_content,
                    "source_page": u.source_page,
                    "source_document": u.source_document
                }
                for u in units
            ]
        }

    def compare_semester_courses(
        self, sem_num: int, dept_code_a: str, dept_code_b: str
    ) -> Dict[str, Any]:
        """Compare courses in a given semester between two departments."""
        sem_a = self.get_semester_courses(sem_num, dept_code_a)
        sem_b = self.get_semester_courses(sem_num, dept_code_b)

        if not sem_a or not sem_b:
            return {"error": "One or both departments/semesters could not be resolved."}

        courses_a_map = {c["code"]: c for c in sem_a["courses"]}
        courses_b_map = {c["code"]: c for c in sem_b["courses"]}

        common_codes = set(courses_a_map.keys()).intersection(courses_b_map.keys())
        only_in_a = [courses_a_map[code] for code in courses_a_map if code not in common_codes]
        only_in_b = [courses_b_map[code] for code in courses_b_map if code not in common_codes]
        common = [courses_a_map[code] for code in common_codes]

        return {
            "semester_number": sem_num,
            "department_a": {"name": sem_a["department"], "code": sem_a["department_code"], "credits": sem_a["total_credits"]},
            "department_b": {"name": sem_b["department"], "code": sem_b["department_code"], "credits": sem_b["total_credits"]},
            "common_courses": common,
            "only_in_department_a": only_in_a,
            "only_in_department_b": only_in_b
        }

    def get_program_credit_requirements(self, dept_code: str) -> Optional[Dict[str, Any]]:
        """Retrieve total degree credits and breakdown for a program."""
        dept = self.db.query(Department).filter(Department.code.ilike(dept_code.strip())).first()
        if not dept:
            return None
        prog = self.db.query(Program).filter(Program.department_id == dept.id).first()
        if not prog:
            return None

        sems = self.db.query(Semester).filter(Semester.program_id == prog.id).order_by(Semester.semester_number).all()
        return {
            "department": dept.name,
            "department_code": dept.code,
            "degree": prog.degree,
            "total_degree_credits": prog.total_degree_credits,
            "semesters": [
                {"semester": s.semester_number, "roman": s.roman_numeral, "credits": s.total_credits}
                for s in sems
            ]
        }

    def get_conflicts_for_review(self) -> List[Dict[str, Any]]:
        """Fetch all extraction conflicts logged for administrative review."""
        issues = self.db.query(ExtractionIssue).filter(ExtractionIssue.status == "pending_review").all()
        return [
            {
                "id": i.id,
                "doc_id": i.doc_id,
                "course_code": i.course_code,
                "issue_type": i.issue_type,
                "severity": i.severity,
                "details": i.details,
                "status": i.status,
                "created_at": i.created_at.isoformat() if i.created_at else None
            }
            for i in issues
        ]

    def _format_course_dict(self, course: Course) -> Dict[str, Any]:
        dept_name = course.department.name if course.department else "Aditya University"
        dept_code = course.department.code if course.department else "GEN"
        return {
            "id": course.id,
            "code": course.code,
            "title": course.title,
            "department": dept_name,
            "department_code": dept_code,
            "category": course.category,
            "level": course.level,
            "credits": course.credits,
            "lecture_hours": course.lecture_hours,
            "tutorial_hours": course.tutorial_hours,
            "practical_hours": course.practical_hours,
            "total_hours": course.total_hours,
            "prerequisite_text": course.prerequisite_text,
            "source_document_id": course.source_document_id,
            "source_page": course.source_page,
            "outcomes_count": len(course.outcomes),
            "units_count": len(course.units),
            "textbooks_count": len(course.textbooks)
        }
