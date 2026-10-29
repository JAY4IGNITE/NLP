"""
CampusAI End-to-End Scenario Test Suite (PART T Requirements).
Verifies all 10 real-world scenarios:
Scenario 1: Exact course facts
Scenario 2: Semester filtering
Scenario 3: Syllabus explanation
Scenario 4: Multi-intent request
Scenario 5: Cross-department comparison
Scenario 6: Context-aware follow-up
Scenario 7: Ambiguity detection & clarification
Scenario 8: Missing official information / Safe abstention
Scenario 9: Conflicting course information audit
Scenario 10: Multilingual query (Telugu)
"""

import pytest
from campusai.nlp.coreference import ConversationContext
from campusai.rag.generator import ConversationalRAGEngine
from campusai.database.connection import SessionLocal
from campusai.database.models import ExtractionIssue


@pytest.fixture(scope="module")
def rag_engine():
    return ConversationalRAGEngine()


def test_scenario_1_exact_course_facts(rag_engine):
    """Scenario 1: Exact course facts - What is the code and credit value of Data Structures in CSE?"""
    query = "What is the code and credit value of Data Structures in CSE?"
    result = rag_engine.process_query(query, department_hint="CSE")
    answer = result["answer"]
    assert "241CS003" in answer
    assert "4" in answer
    assert result["is_grounded"] is True
    assert len(result["citations"]) > 0


def test_scenario_2_semester_filtering(rag_engine):
    """Scenario 2: Semester filtering - List the subjects in Semester V for Information Technology."""
    query = "List the subjects in Semester V for Information Technology."
    result = rag_engine.process_query(query, department_hint="IT")
    answer = result["answer"]
    assert "Semester V" in answer or "Semester 5" in answer or "IT" in answer
    assert result["intent"] in ["semester_subjects", "course_search"]
    assert result["is_grounded"] is True


def test_scenario_3_syllabus_explanation(rag_engine):
    """Scenario 3: Syllabus explanation - Explain Unit III of Operating Systems."""
    query = "Explain Unit III of Operating Systems."
    result = rag_engine.process_query(query, department_hint="CSE")
    assert result["intent"] == "unit_syllabus"
    assert "Operating Systems" in result["answer"] or "Unit" in result["answer"]
    assert len(result["citations"]) > 0
    assert result["citations"][0]["page"] > 0


def test_scenario_4_multi_intent_request(rag_engine):
    """Scenario 4: Multi-intent request - Give Semester VI subjects, credits, and prerequisites."""
    query = "Give Semester VI subjects, credits, and prerequisites for CSE."
    result = rag_engine.process_query(query, department_hint="CSE")
    assert result["intent"] == "multi_intent_query"
    assert "Semester VI" in result["answer"] or "Semester 6" in result["answer"]
    assert result["is_grounded"] is True


def test_scenario_5_cross_department_comparison(rag_engine):
    """Scenario 5: Cross-department comparison - Compare third-semester subjects in CSE and ECE."""
    query = "Compare third-semester subjects in CSE and ECE."
    result = rag_engine.process_query(query)
    assert result["intent"] in ["course_comparison", "curriculum_comparison"]
    assert result["is_grounded"] is True


def test_scenario_6_context_aware_followup(rag_engine):
    """Scenario 6: Context-aware follow-up - 'What is the syllabus of Data Structures?' -> 'What about Unit II?'"""
    context = ConversationContext(session_id="scenario_6_session")
    # Turn 1
    res1 = rag_engine.process_query("What is the syllabus of Data Structures?", context=context, department_hint="CSE")
    assert "Data Structures" in res1["answer"]

    # Turn 2: Follow-up
    res2 = rag_engine.process_query("What about Unit II?", context=context, department_hint="CSE")
    assert res2["intent"] == "unit_syllabus"
    assert "Data Structures" in res2["answer"] or "Unit 2" in res2["answer"] or "Unit II" in res2["answer"]


def test_scenario_7_ambiguity(rag_engine):
    """Scenario 7: Ambiguity - 'What is DS?' asks for clarification."""
    result = rag_engine.process_query("What is DS?")
    assert result["intent"] == "clarification"
    assert "ambiguous" in result["answer"].lower()
    assert "Data Structures" in result["answer"]
    assert "Data Science" in result["answer"]


def test_scenario_8_missing_official_information(rag_engine):
    """Scenario 8: Missing official information - 'What is tomorrow's exam schedule?' abstains safely."""
    result = rag_engine.process_query("What is tomorrow's exam schedule?")
    assert result["source_type"] == "safe_abstention"
    assert "not published in the official curriculum" in result["answer"].lower()


def test_scenario_9_conflicting_course_information():
    """Scenario 9: Conflicting course information - audits stored conflicts."""
    db = SessionLocal()
    try:
        conflicts = db.query(ExtractionIssue).filter(ExtractionIssue.status == "pending_review").all()
        assert len(conflicts) > 0
        first_conflict = conflicts[0]
        assert first_conflict.course_code is not None
        assert first_conflict.issue_type is not None
    finally:
        db.close()


def test_scenario_10_multilingual_query(rag_engine):
    """Scenario 10: Multilingual query - Telugu curriculum query."""
    result = rag_engine.process_query("ఆపరేటింగ్ సిస్టమ్స్ క్రెడిట్స్ ఎన్ని?")
    assert result["language"] == "te"
    assert result["is_grounded"] is True
