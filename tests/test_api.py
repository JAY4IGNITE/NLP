"""
API test suite for FastAPI backend endpoints.
Verifies health, auth, academic listings, chat, source viewer, and admin routes.
"""

from fastapi.testclient import TestClient
from campusai.api.main import app

client = TestClient(app)


def test_health_check():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "Aditya University" in data["institution"]


def test_get_departments():
    res = client.get("/api/v1/departments")
    assert res.status_code == 200
    depts = res.json()
    assert len(depts) >= 8
    dept_codes = [d["code"] for d in depts]
    assert "CSE" in dept_codes
    assert "IT" in dept_codes


def test_get_courses_catalog():
    res = client.get("/api/v1/courses?limit=10")
    assert res.status_code == 200
    courses = res.json()
    assert len(courses) > 0
    assert "code" in courses[0]


def test_get_semester_courses():
    res = client.get("/api/v1/semesters?department_code=CSE&semester_number=1")
    assert res.status_code == 200
    sem = res.json()
    assert sem["department_code"] == "CSE"
    assert sem["semester_number"] == 1
    assert len(sem["courses"]) > 0


def test_chat_endpoint():
    res = client.post("/api/v1/chat", json={
        "query": "How many credits does Operating Systems have in CSE?",
        "department_code": "CSE"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["is_grounded"] is True
    assert "Credits" in data["answer"] or "credits" in data["answer"]
    assert len(data["citations"]) > 0


def test_auth_login():
    res = client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    assert res.status_code == 200
    token = res.json()
    assert "access_token" in token
    assert token["role"] == "admin"


def test_source_details_and_page():
    # Test details
    res = client.get("/api/v1/sources/DOC-CSE-03")
    assert res.status_code == 200
    doc_meta = res.json()
    assert doc_meta["department_code"] == "CSE"

    # Test page image rendering
    page_res = client.get("/api/v1/sources/DOC-CSE-03/page/1?format=text")
    assert page_res.status_code == 200
    page_data = page_res.json()
    assert "text" in page_data
    assert len(page_data["text"]) > 10
