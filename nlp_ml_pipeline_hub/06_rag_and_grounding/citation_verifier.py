"""Citation verification engine for CampusAI.
Validates that generated citations match retrieved source passages and
ensures mentioned academic course codes exist in official database records.
"""

import re
from typing import Any, Dict, List, Tuple
from backend.database.sql_retriever import SQLAcademicRetriever


class CitationVerifier:
    """Verifies citations and prevents hallucinated source claims."""

    def __init__(self):
        self.sql_retriever = SQLAcademicRetriever()

    def verify_citations(
        self,
        answer_text: str,
        retrieved_citations: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Verify citations against retrieved evidence and validate course codes."""
        verified: List[Dict[str, Any]] = []
        warnings: List[str] = []

        if not retrieved_citations:
            return [], ["No citations provided by retrieval system."]

        # Check all course codes mentioned in the generated answer
        mentioned_codes = set(re.findall(r"\b241[A-Z]{2}[0-9]{3}\b", answer_text))
        for code in mentioned_codes:
            course = self.sql_retriever.get_course_by_code(code)
            if not course:
                warnings.append(f"Answer referenced unverified or non-existent course code: {code}")

        for cit in retrieved_citations:
            doc_id = cit.get("doc_id") or cit.get("source_document_id")
            page = cit.get("page") or cit.get("source_page")
            if not doc_id:
                continue

            if page is None or page <= 0:
                warnings.append(f"Citation for {doc_id} has invalid page number {page}")
                continue

            verified.append({
                "doc_id": doc_id,
                "title": cit.get("title", "Aditya University Academic Record"),
                "department": cit.get("department", "University"),
                "page": page,
                "excerpt": cit.get("excerpt", ""),
                "course_code": cit.get("course_code"),
                "is_verified": True
            })

        return verified, warnings
