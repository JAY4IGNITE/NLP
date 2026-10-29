"""Source Attribution and Groundedness Evaluation Engine.
Computes multi-factor RAG confidence scores and verifies factual citations.
"""
from typing import List, Dict, Any


class AttributionEngine:
    """Calculates multi-factor confidence breakdowns and verifies citations."""

    def __init__(self, retrieval_threshold: float = 0.35, rerank_threshold: float = 0.35):
        self.retrieval_threshold = retrieval_threshold
        self.rerank_threshold = rerank_threshold

    def calculate_confidence(
        self,
        query: str,
        answer: str,
        intent_data: Dict[str, Any],
        entities: Dict[str, Any],
        chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compute groundedness and attribution breakdown."""
        intent = intent_data.get("intent", intent_data.get("predicted_intent", "fallback"))
        intent_conf = intent_data.get("confidence", 0.0)

        # Conversational intents do not require PDF retrieval
        if intent in {"greeting", "thanks", "help"}:
            return {
                "overall_confidence": round(intent_conf, 4),
                "is_grounded": True,
                "breakdown": {
                    "intent_confidence": round(intent_conf, 4),
                    "retrieval_score": 1.0,
                    "rerank_score": 1.0,
                    "entity_match": 1.0,
                    "citation_score": 1.0
                },
                "citations": []
            }

        if intent in {"fallback", "out_of_scope"} or not chunks:
            return {
                "overall_confidence": 0.20,
                "is_grounded": False,
                "breakdown": {
                    "intent_confidence": round(intent_conf, 4),
                    "retrieval_score": 0.0,
                    "rerank_score": 0.0,
                    "entity_match": 0.0,
                    "citation_score": 0.0
                },
                "citations": []
            }

        # 1. Retrieval & Rerank Scores
        has_verified_record = any(
            c.get("chunk_id", "").startswith(("SQL-", "CHK-TBK-", "CHK-CO-", "CHK-"))
            for c in chunks
        )
        has_sql = any(c.get("chunk_id", "").startswith("SQL-") for c in chunks)
        top_retrieval_score = max((c.get("retrieval_score", c.get("score", 0.0)) for c in chunks), default=0.0)
        top_rerank_score = max((c.get("rerank_score", c.get("retrieval_score", c.get("score", 0.0))) for c in chunks), default=0.0)
        if has_sql or has_verified_record:
            top_retrieval_score = max(top_retrieval_score, 1.0)
            top_rerank_score = max(top_rerank_score, 1.0)

        # 2. Entity Alignment
        entity_score = 0.5
        course = entities.get("course") or entities.get("canonical_course_name")
        course_code = entities.get("course_code")
        unit = entities.get("unit")
        semester = entities.get("semester")

        matched_entities = 0
        total_entities = 0
        if course or course_code:
            total_entities += 1
            if any((course and course.lower() in (c.get("course_title") or c.get("course_name") or "").lower()) or
                   (course_code and course_code.upper() == (c.get("course_code") or "").upper()) for c in chunks):
                matched_entities += 1
        if unit:
            total_entities += 1
            if any(c.get("unit") == unit or f"Unit {unit}" in (c.get("content") or c.get("text") or "") for c in chunks):
                matched_entities += 1
        if semester:
            total_entities += 1
            if any(c.get("semester") == semester or f"Semester {semester}" in (c.get("content") or c.get("text") or "") for c in chunks):
                matched_entities += 1

        if total_entities > 0:
            entity_score = matched_entities / total_entities
        else:
            entity_score = 0.85

        # 3. Citation Check in Generated Answer
        citations = []
        for c in chunks:
            c_id = c.get("chunk_id", c.get("doc_id", ""))
            source_doc = c.get("source_document") or c.get("source_document_id") or c.get("title") or "Curriculum Handbook"
            page = c.get("page_number") or c.get("source_page") or c.get("page") or 1
            section = c.get("section_heading") or c.get("course_title") or c.get("course_name") or "Curriculum"
            doc_code = c.get("course_code") or ""

            is_cited = False
            if c_id and c_id in answer:
                is_cited = True
            elif doc_code and doc_code in answer:
                is_cited = True
            elif f"Page {page}" in answer or f"page {page}" in answer:
                is_cited = True
            elif source_doc in answer:
                is_cited = True

            citations.append({
                "document_id": c.get("document_id") or c.get("source_document_id") or source_doc,
                "chunk_id": c_id,
                "source_document": source_doc,
                "title": source_doc,
                "page": page,
                "section": section,
                "course_code": doc_code,
                "department": c.get("department_code") or c.get("department"),
                "relevance_score": c.get("rerank_score", c.get("retrieval_score", 0.0)),
                "is_cited": is_cited,
                "excerpt": (c.get("content") or c.get("text") or "")[:200] + "...",
                "content": c.get("content") or c.get("text", "")
            })

        citation_score = 0.9 if any(cit["is_cited"] for cit in citations) else 0.65

        # Weighted aggregate
        overall = (
            0.20 * intent_conf +
            0.30 * top_retrieval_score +
            0.30 * top_rerank_score +
            0.10 * entity_score +
            0.10 * citation_score
        )
        overall_clamped = round(max(0.0, min(1.0, overall)), 4)

        is_grounded = (
            has_sql or has_verified_record or (
                (top_rerank_score >= self.rerank_threshold or top_retrieval_score >= 0.015) and
                overall_clamped >= 0.35
            )
        )

        return {
            "overall_confidence": overall_clamped,
            "is_grounded": is_grounded,
            "breakdown": {
                "intent_confidence": round(intent_conf, 4),
                "top_retrieval_score": round(top_retrieval_score, 4),
                "top_rerank_score": round(top_rerank_score, 4),
                "entity_alignment": round(entity_score, 4),
                "citation_score": round(citation_score, 4)
            },
            "citations": citations
        }


attribution_engine = AttributionEngine()
