"""
Tests for NLP language identification, normalizer, entity extractor,
multi-intent decomposer, coreference resolution, and intent classifier.
"""

from campusai.nlp.language_id import identify_language
from campusai.nlp.normalizer import normalize_query
from campusai.nlp.entity_extractor import AcademicEntityExtractor
from campusai.nlp.multi_intent import MultiIntentDecomposer
from campusai.nlp.coreference import ContextualQueryRewriter, ConversationContext
from campusai.nlp.intent_classifier import IntentClassifier


def test_language_identification():
    assert identify_language("What are the credits for Operating Systems?")[0] == "en"
    assert identify_language("ఆపరేటింగ్ సిస్టమ్స్ క్రెడిట్స్ ఎన్ని?")[0] == "te"
    assert identify_language("OS credits enni cheppandi")[0] == "te-en"


def test_query_normalization():
    norm = normalize_query("tell me 241cs001 details in sem 5 for unit-iii")
    assert "241CS001" in norm
    assert "Semester 5" in norm
    assert "Unit 3" in norm


def test_entity_extractor():
    extractor = AcademicEntityExtractor()
    ent = extractor.extract_entities("What is the syllabus of Unit 3 for Operating Systems in CSE?")
    assert ent.get("unit") == 3
    assert ent.get("department") == "CSE"
    assert ent.get("course") == "Operating Systems"

    # Ambiguity test
    ds_ent = extractor.extract_entities("Tell me about DS")
    assert ds_ent.get("is_ambiguous") is True


def test_multi_intent_decomposition():
    decomposer = MultiIntentDecomposer()
    plan = decomposer.decompose("List all sixth-semester CSE subjects with credits and prerequisites.")
    assert plan.is_multi_intent is True
    assert len(plan.tasks) >= 2
    intents = [t.intent for t in plan.tasks]
    assert "semester_subjects" in intents
    assert "course_prerequisites" in intents or "semester_total_credits" in intents


def test_coreference_rewriter():
    rewriter = ContextualQueryRewriter()
    ctx = ConversationContext(session_id="test-session", last_course="Data Structures", last_department="CSE", last_unit=1)

    rewritten, entities = rewriter.rewrite_query("What about Unit II?", ctx)
    assert "Data Structures" in rewritten
    assert entities.get("unit") == 2

    rewritten2, _ = rewriter.rewrite_query("credits enni?", ctx)
    assert "Data Structures" in rewritten2


def test_intent_classifier():
    clf = IntentClassifier()
    res = clf.predict("How many credits does Operating Systems have?")
    assert res.predicted_intent == "course_credits"
    assert res.confidence > 0.5
    assert res.domain == "curriculum"
