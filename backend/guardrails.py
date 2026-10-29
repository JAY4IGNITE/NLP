"""Academic Guardrails, Domain Boundary Enforcement, and Anti-Hallucination Engine.
Provides strict input validation, adversarial prompt injection protection,
out-of-domain rejection, retrieval confidence grounding, and hallucination verification.
"""
import re
from typing import Dict, Any, List, Optional, Tuple

ADVERSARIAL_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
    r"you\s+are\s+now\s+a",
    r"system\s+prompt",
    r"jailbreak",
    r"drop\s+table",
    r"<script.*?>",
    r"reveal\s+(your\s+)?instructions",
    r"bypass\s+restrictions",
    r"prompt\s+injection",
    r"act\s+as\s+an\s+unrestricted",
]

NON_ACADEMIC_PATTERNS = [
    r"write\s+(a\s+)?python\s+code\b",
    r"write\s+(a\s+)?code\s+for\b",
    r"implement\s+(in\s+)?(c\+\+|java|python|javascript|c#|golang)\b",
    r"debug\s+my\s+code\b",
    r"relationship\s+advice\b",
    r"crypto\b|bitcoin\b|stocks?\b",
    r"weather\s+forecast\b",
    r"recipe\s+for\b",
    r"write\s+an\s+essay\s+on\b",
    r"solve\s+this\s+leetcode\b"
]


class AcademicGuardrails:
    """Enterprise safety, boundary enforcement, and anti-hallucination controller."""

    def __init__(
        self,
        intent_threshold: float = 0.55,
        retrieval_threshold: float = 0.35
    ):
        self.intent_threshold = intent_threshold
        self.retrieval_threshold = retrieval_threshold

    def check_input_safety(self, query: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Validate student input against prompt injections and non-academic boundaries.
        Returns: (is_safe, failure_reason, refusal_message)
        """
        clean_q = query.strip().lower()

        # Check prompt injection and adversarial attacks
        for pat in ADVERSARIAL_PATTERNS:
            if re.search(pat, clean_q):
                return False, "adversarial_injection", (
                    "Security Guardrail Triggered: System instructions and academic boundaries "
                    "cannot be modified or bypassed. Please submit queries regarding the official Aditya University curriculum."
                )

        # Check out-of-scope non-academic domain
        for pat in NON_ACADEMIC_PATTERNS:
            if re.search(pat, clean_q):
                return False, "non_academic_domain", (
                    "Academic Focus Notice: I am the official Aditya University Academic Helpdesk Assistant. "
                    "I provide syllabus details, prerequisites, credits, examination rules, textbooks, and unit topics for B.Tech programs. "
                    "I do not write code implementations, solve external coding problems, or answer non-academic questions."
                )

        # Check missing official real-time information (e.g. tomorrow's exam schedule)
        if "tomorrow" in clean_q or ("exam" in clean_q and ("schedule" in clean_q or "timetable" in clean_q)):
            return False, "safe_abstention", (
                "Specific examination schedules and timetables for tomorrow are not published "
                "in the official curriculum handbooks. Please consult the Aditya University "
                "Examination Portal or your department notice board for the latest official exam notifications."
            )

        return True, None, None

    def validate_retrieval_grounding(
        self,
        intent: str,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> Tuple[bool, Optional[str]]:
        """Verify that retrieved institutional chunks meet the minimum relevance threshold."""
        if intent in {"greeting", "thanks", "help", "course_code_lookup"}:
            return True, None

        if not retrieved_chunks:
            return False, (
                "This topic does not appear in the official Aditya University B.Tech curriculum handbook (Version 3.0). "
                "Please verify the course title or consult the Department Academic Coordinator."
            )

        if any(c.get("chunk_id", "").startswith("SQL-") for c in retrieved_chunks):
            return True, None

        top_score = max((max(c.get("rerank_score", 0.0), c.get("retrieval_score", 0.0)) for c in retrieved_chunks), default=0.0)
        if top_score < self.retrieval_threshold:
            return False, (
                "The queried subject or topic could not be verified in the university curriculum records with sufficient confidence. "
                "For unlisted electives or special permissions, please contact the Office of Academic Affairs."
            )

        return True, None

    def verify_answer_facts(
        self,
        answer: str,
        entities: Dict[str, Any],
        chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Anti-hallucination verification: ensures codes, credits, and numbers are backed by context."""
        chunk_texts = " ".join([c.get("text", "") for c in chunks])
        issues = []

        # Check course codes mentioned in answer
        answer_codes = set(re.findall(r"\b([A-Z]{2,4}\d{3,4})\b", answer))
        for code in answer_codes:
            if code not in chunk_texts and code not in entities.values():
                issues.append(f"Unverified course code '{code}' in answer")

        # Check credit statements
        credit_matches = re.findall(r"(\d+)\s*credits?", answer, re.IGNORECASE)
        for cred in credit_matches:
            if cred not in chunk_texts:
                issues.append(f"Credit count '{cred}' not explicitly confirmed in retrieved context")

        return {
            "passed_fact_check": len(issues) == 0,
            "hallucination_warnings": issues
        }


guardrails = AcademicGuardrails()
