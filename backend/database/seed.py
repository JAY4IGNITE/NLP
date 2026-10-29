"""CampusAI Academic Database Seeding & Ingestion Orchestrator.

Institution: Aditya University, Surampalem, Andhra Pradesh, India.
Domain: B.Tech Curriculum 2024, Version 3.0.

This module provides a modular, explainable, and multi-stage seeding pipeline
that extracts official academic structures from the 8 departmental curriculum PDFs
and populates the normalized PostgreSQL schema.

Workflow Architecture:
1. Institution & Department Setup: Registers Aditya University and the 8 branches.
2. Program & Curriculum Versioning: Links B.Tech programs to Regulation 2024 Version 3.0.
3. Semester Curriculum Extraction: Parses semester slots (I-VIII), course codes, L-T-P-C distributions.
4. Detailed Syllabus Parsing: Extracts unit-wise syllabi (Units I-V), practice contents, outcomes (CO1-CO5), and textbooks.
5. Cross-Department Discrepancy Audit: Identifies differences in course codes/titles and logs them as reviewable issues.
6. Administrative & Student User Initialization: Seeds secure, role-based access accounts.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple
import passlib.hash
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database.connection import SessionLocal, create_all_tables
from backend.database.crud import (
    get_or_create_institution, get_or_create_department,
    get_or_create_program, get_or_create_curriculum_version,
    upsert_course
)
from backend.database.models import (
    Course, CourseOffering, CourseOutcome, CourseUnit, ExtractionIssue,
    Institution, Program, Semester, SourceDocument, Textbook, User
)
from backend.data_ingestion.inventory import DocumentMetadata, SourceInventoryManager
from backend.data_ingestion.table_parser import CurriculumTableParser
from backend.data_ingestion.structure_parser import SyllabusStructureParser
from backend.data_ingestion.validator import AcademicRecordValidator

logger = logging.getLogger(__name__)


def seed_institution(db: Session) -> Institution:
    """Initializes the root institutional record for Aditya University."""
    inst = get_or_create_institution(
        db,
        name=settings.INSTITUTION_NAME,
        location=settings.INSTITUTION_LOCATION,
        website=settings.INSTITUTION_WEBSITE,
    )
    logger.info("Initialized Institution: %s (%s)", inst.name, inst.location)
    return inst


def seed_department_and_program(
    db: Session,
    institution_id: int,
    doc_meta: DocumentMetadata
) -> Tuple[Any, Any, Any]:
    """Creates normalized department, B.Tech program, and curriculum version records."""
    dept = get_or_create_department(
        db, institution_id, doc_meta.department_code, doc_meta.department
    )
    prog = get_or_create_program(
        db, dept.id, f"BTECH-{doc_meta.department_code}", f"B.Tech. in {doc_meta.department}"
    )
    curriculum_ver = get_or_create_curriculum_version(
        db, prog.id, doc_meta.curriculum_version, doc_meta.admission_batch
    )

    existing_doc = db.query(SourceDocument).filter(SourceDocument.doc_id == doc_meta.doc_id).first()
    if not existing_doc:
        db.add(SourceDocument(
            doc_id=doc_meta.doc_id,
            file_name=doc_meta.file_name,
            sha256=doc_meta.sha256,
            department_code=doc_meta.department_code,
            curriculum_version=doc_meta.curriculum_version,
            total_pages=doc_meta.page_count,
            file_size_bytes=doc_meta.file_size_bytes,
            extraction_status="verified"
        ))
        db.commit()

    return dept, prog, curriculum_ver


def _get_doc_path(doc_meta: DocumentMetadata) -> Path:
    p = Path(doc_meta.file_path)
    if p.exists():
        return p
    curriculum_path = settings.DOCUMENTS_DIR / doc_meta.file_name
    if curriculum_path.exists():
        return curriculum_path
    return p


def seed_semester_curriculum(
    db: Session,
    prog_id: int,
    curriculum_ver_id: int,
    dept_id: int,
    doc_meta: DocumentMetadata
) -> Tuple[int, List[Dict[str, Any]]]:
    """Parses and populates semester curriculum tables (Semesters I through VIII)."""
    table_parser = CurriculumTableParser(
        _get_doc_path(doc_meta), doc_meta.doc_id, doc_meta.department_code
    )
    parsed_sems = table_parser.extract_semester_tables()
    extracted_courses: List[Dict[str, Any]] = []
    courses_count = 0

    for p_sem in parsed_sems:
        sem_record = db.query(Semester).filter(
            Semester.program_id == prog_id,
            Semester.curriculum_version_id == curriculum_ver_id,
            Semester.semester_number == p_sem.semester_num
        ).first()

        if not sem_record:
            sem_record = Semester(
                program_id=prog_id,
                curriculum_version_id=curriculum_ver_id,
                semester_number=p_sem.semester_num,
                roman_numeral=p_sem.semester_roman,
                total_credits=p_sem.total_credits,
                total_hours=p_sem.total_hours,
                source_page=p_sem.source_page
            )
            db.add(sem_record)
            db.commit()
            db.refresh(sem_record)

        for c in p_sem.courses:
            course_obj = upsert_course(
                db=db,
                code=c.course_code,
                title=c.course_title,
                dept_id=dept_id,
                curriculum_version_id=curriculum_ver_id,
                category=c.category,
                level=c.level,
                credits=c.credits,
                l_hrs=c.lecture_hours,
                t_hrs=c.tutorial_hours,
                p_hrs=c.practical_hours,
                tot_hrs=c.total_hours,
                source_doc_id=doc_meta.doc_id,
                source_page=c.source_page
            )
            courses_count += 1
            extracted_courses.append({
                "course_code": c.course_code,
                "course_title": c.course_title,
                "credits": c.credits,
                "department_code": doc_meta.department_code,
                "source_doc_id": doc_meta.doc_id
            })

            offering = db.query(CourseOffering).filter(
                CourseOffering.semester_id == sem_record.id,
                CourseOffering.course_id == course_obj.id
            ).first()
            if not offering:
                db.add(CourseOffering(
                    semester_id=sem_record.id,
                    course_id=course_obj.id,
                    slot_type=c.category,
                    is_elective=c.is_elective
                ))
        db.commit()

    return courses_count, extracted_courses


def seed_syllabi_units_and_references(
    db: Session,
    dept_id: int,
    curriculum_ver_id: int,
    doc_meta: DocumentMetadata,
    max_pages: int
) -> Tuple[int, int, int]:
    """Parses detailed syllabus descriptions, units I-V, outcomes, and textbooks."""
    syllabus_parser = SyllabusStructureParser(
        _get_doc_path(doc_meta), doc_meta.doc_id, doc_meta.department_code, doc_meta.curriculum_version
    )
    parsed_syllabi = syllabus_parser.parse_all_syllabi(max_pages=max_pages)

    units_count = 0
    outcomes_count = 0
    textbooks_count = 0

    for syl in parsed_syllabi:
        course_obj = upsert_course(
            db=db,
            code=syl.course_code,
            title=syl.course_title,
            dept_id=dept_id,
            curriculum_version_id=curriculum_ver_id,
            credits=syl.credits,
            l_hrs=syl.lecture_hours,
            t_hrs=syl.tutorial_hours,
            p_hrs=syl.practical_hours,
            source_doc_id=doc_meta.doc_id,
            source_page=syl.source_page
        )

        for u in syl.units:
            existing_u = db.query(CourseUnit).filter(
                CourseUnit.course_id == course_obj.id,
                CourseUnit.unit_number == u.unit_number
            ).first()
            if not existing_u:
                db.add(CourseUnit(
                    course_id=course_obj.id,
                    unit_number=u.unit_number,
                    unit_roman=u.unit_roman,
                    title=u.title,
                    content=u.content,
                    practice_content=u.practice_content,
                    source_page=u.source_page,
                    source_document=doc_meta.doc_id
                ))
                units_count += 1

        for o in syl.outcomes:
            existing_o = db.query(CourseOutcome).filter(
                CourseOutcome.course_id == course_obj.id,
                CourseOutcome.outcome_code == o["code"]
            ).first()
            if not existing_o:
                db.add(CourseOutcome(
                    course_id=course_obj.id,
                    outcome_code=o["code"],
                    description=o["description"]
                ))
                outcomes_count += 1

        for b in syl.textbooks:
            existing_b = db.query(Textbook).filter(
                Textbook.course_id == course_obj.id,
                Textbook.title == b.title
            ).first()
            if not existing_b:
                db.add(Textbook(
                    course_id=course_obj.id,
                    book_type=b.book_type,
                    title=b.title,
                    raw_text=b.raw_text
                ))
                textbooks_count += 1

    db.commit()
    return units_count, outcomes_count, textbooks_count


def seed_default_users(db: Session) -> None:
    """Initializes default administrator and student credentials for authentication."""
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        hashed = passlib.hash.pbkdf2_sha256.hash("admin123")
        db.add(User(
            username="admin",
            email="admin@adityauniversity.in",
            hashed_password=hashed,
            role="admin",
            is_active=True
        ))

    student_user = db.query(User).filter(User.username == "student").first()
    if not student_user:
        hashed_s = passlib.hash.pbkdf2_sha256.hash("student123")
        db.add(User(
            username="student",
            email="student@adityauniversity.in",
            hashed_password=hashed_s,
            role="student",
            is_active=True
        ))
    db.commit()


def seed_database(max_syllabus_pages_per_doc: int = 120) -> Dict[str, Any]:
    """Master database seeding orchestration function."""
    print("=" * 65)
    print(" CampusAI Database Seeding Engine - Aditya University")
    print("=" * 65)

    create_all_tables()
    db = SessionLocal()

    try:
        inst = seed_institution(db)
        print(f"[OK] Initialized Institution: {inst.name}")

        inventory_mgr = SourceInventoryManager()
        manifest_file = inventory_mgr.manifest_path
        if not manifest_file.exists():
            docs = inventory_mgr.scan_and_inventory()
        else:
            with open(manifest_file, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
                docs = [DocumentMetadata(**d) for d in manifest_data["documents"]]

        print(f"[OK] Ingesting {len(docs)} curriculum documents...")

        all_extracted_courses: List[Dict[str, Any]] = []
        total_courses_count = 0
        total_units_count = 0
        total_outcomes_count = 0
        total_books_count = 0

        for doc_meta in docs:
            print(f"\n--> Processing [{doc_meta.department_code}] {doc_meta.department} ({doc_meta.curriculum_version})")

            dept, prog, curriculum_ver = seed_department_and_program(db, inst.id, doc_meta)

            c_count, extracted_courses = seed_semester_curriculum(
                db, prog.id, curriculum_ver.id, dept.id, doc_meta
            )
            total_courses_count += c_count
            all_extracted_courses.extend(extracted_courses)
            print(f"    Extracted {c_count} semester course offerings.")

            u_count, o_count, b_count = seed_syllabi_units_and_references(
                db, dept.id, curriculum_ver.id, doc_meta, max_pages=max_syllabus_pages_per_doc
            )
            total_units_count += u_count
            total_outcomes_count += o_count
            total_books_count += b_count
            print(f"    Parsed {u_count} units, {o_count} outcomes, {b_count} textbooks.")

        print("\n--> Running Academic Record Conflict and Validation Audit...")
        validator = AcademicRecordValidator(db_session=db)
        conflicts = validator.detect_cross_department_conflicts(all_extracted_courses)
        print(f"    Detected {len(conflicts)} cross-department observations/conflicts.")
        validator.persist_issues(conflicts)

        seed_default_users(db)
        print("    Initialized default admin and student credentials.")

        stats = {
            "total_documents": len(docs),
            "courses_registered": total_courses_count,
            "syllabus_units": total_units_count,
            "course_outcomes": total_outcomes_count,
            "textbooks": total_books_count,
            "conflicts_audited": len(conflicts)
        }

        print("\n" + "=" * 65)
        print(" DATABASE SEEDING COMPLETED SUCCESSFULLY")
        print(f" - Courses registered: {stats['courses_registered']}")
        print(f" - Syllabus Units loaded: {stats['syllabus_units']}")
        print(f" - Course Outcomes loaded: {stats['course_outcomes']}")
        print(f" - Textbooks & References cataloged: {stats['textbooks']}")
        print(f" - Cross-Department Conflicts Audited: {stats['conflicts_audited']}")
        print("=" * 65)

        return stats

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
