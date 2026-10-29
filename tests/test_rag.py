"""
Tests for Conversational RAG Engine, prompt builder, citations, and groundings.
"""

from campusai.nlp.coreference import ConversationContext
from campusai.rag.generator import ConversationalRAGEngine


def test_rag_exact_course_fact():
    rag = ConversationalRAGEngine()
    res = rag.process_query("What is the code and credit value of Data Structures in CSE?")
    assert res["is_grounded"] is True
    assert "241CS003" in res["answer"]
    assert "4" in res["answer"]
    assert len(res["citations"]) > 0


def test_rag_semester_listing():
    rag = ConversationalRAGEngine()
    res = rag.process_query("List the subjects in Semester 5 for Information Technology.")
    assert res["is_grounded"] is True
    assert "Semester" in res["answer"]
    assert len(res["citations"]) > 0


def test_rag_ambiguity_handling():
    rag = ConversationalRAGEngine()
    res = rag.process_query("Tell me about DS")
    assert res["intent"] == "clarification"
    assert "ambiguous" in res["answer"].lower()
    assert "Data Structures" in res["answer"]


def test_rag_multi_turn_coreference():
    rag = ConversationalRAGEngine()
    ctx = ConversationContext(session_id="multi-turn-test")

    # Turn 1
    res1 = rag.process_query("What is the syllabus of Linear algebra & Calculus?", context=ctx)
    assert ctx.last_course is not None

    # Turn 2
    res2 = rag.process_query("What about Unit II?", context=ctx)
    assert res2["is_grounded"] is True
    assert "unit" in res2["answer"].lower()


def test_rag_safe_abstention():
    rag = ConversationalRAGEngine()
    res = rag.process_query("What is tomorrow's exam schedule for CSE?")
    assert res["source_type"] in ["safe_abstention", "hybrid_rag"]
    assert ("not published" in res["answer"].lower() or "unavailable" in res["answer"].lower())
