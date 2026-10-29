"""
Unit tests for database models, migrations, and SQL academic retriever.
"""

from campusai.database.sql_retriever import SQLAcademicRetriever


def test_sql_retriever_course_lookup():
    retriever = SQLAcademicRetriever()
    courses = retriever.find_courses_by_name("Data Structures")
    assert len(courses) > 0
    ds = courses[0]
    assert "241" in ds["code"]
    assert ds["credits"] > 0
    assert ds["source_page"] is not None


def test_sql_retriever_semester_courses():
    retriever = SQLAcademicRetriever()
    sem_it = retriever.get_semester_courses(5, "IT")
    assert sem_it is not None
    assert sem_it["department_code"] == "IT"
    assert sem_it["semester_number"] == 5
    assert len(sem_it["courses"]) > 0
    assert sem_it["total_credits"] > 0


def test_sql_retriever_course_units():
    retriever = SQLAcademicRetriever()
    la_units = retriever.get_course_units("241MA001")
    assert la_units is not None
    assert len(la_units["units"]) >= 1
    first_unit = la_units["units"][0]
    assert "I" in first_unit["unit_roman"]
    assert len(first_unit["content"]) > 10


def test_sql_retriever_compare_departments():
    retriever = SQLAcademicRetriever()
    comp = retriever.compare_semester_courses(3, "CSE", "ECE")
    assert "common_courses" in comp
    assert "only_in_department_a" in comp
    assert "only_in_department_b" in comp


def test_sql_retriever_conflicts_review():
    retriever = SQLAcademicRetriever()
    conflicts = retriever.get_conflicts_for_review()
    assert isinstance(conflicts, list)
