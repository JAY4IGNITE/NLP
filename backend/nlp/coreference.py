"""Conversational coreference resolution and contextual query rewriting engine.
Maintains dialogue state and resolves anaphoric references across conversation turns.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from backend.nlp.entity_extractor import AcademicEntityExtractor
from backend.nlp.normalizer import ROMAN_NUMS


@dataclass
class ConversationContext:
    session_id: str
    last_course: Optional[str] = None
    last_course_code: Optional[str] = None
    last_department: Optional[str] = None
    last_semester: Optional[int] = None
    last_unit: Optional[int] = None
    last_intent: Optional[str] = None
    language: str = "en"
    turn_history: List[Dict[str, str]] = field(default_factory=list)


class ContextualQueryRewriter:
    """Resolves elliptical and coreferent student queries using conversation memory."""

    def __init__(self):
        self.extractor = AcademicEntityExtractor()

    def rewrite_query(self, query: str, context: Optional[ConversationContext]) -> Tuple[str, Dict[str, Any]]:
        """Rewrite ambiguous or follow-up query by injecting missing context entities."""
        entities = self.extractor.extract_entities(query)

        if not context:
            return query, entities

        q_lower = query.lower().strip()
        rewritten = query

        # 1. Resolve "Unit II" or "next unit" or "What about Unit 3?"
        unit_match = re.search(r"\b(?:what about|and|tell me about)?\s*(?:the\s+)?(?:next\s+unit|unit\s*(\d+|[ivx]+))\b", q_lower)
        if unit_match and context.last_course:
            target_unit = None
            if "next unit" in q_lower:
                target_unit = (context.last_unit or 1) + 1
            elif unit_match.group(1):
                val = unit_match.group(1).lower()
                target_unit = int(ROMAN_NUMS.get(val, val if val.isdigit() else 1))

            if target_unit:
                entities["unit"] = target_unit
                entities["course"] = context.last_course
                entities["department"] = context.last_department
                rewritten = f"Explain Unit {target_unit} of {context.last_course} in {context.last_department or 'curriculum'}"

        # 2. Resolve "What about its credits?" / "credits enni?"
        elif any(phrase in q_lower for phrase in ["its credits", "how many credits for it", "what about credits", "credits enni"]):
            if context.last_course:
                entities["course"] = context.last_course
                entities["department"] = context.last_department
                rewritten = f"How many credits does {context.last_course} have in {context.last_department or 'curriculum'}?"

        # 3. Resolve "Same for IT" / "What about in ECE?"
        elif re.search(r"\b(?:same for|what about in|for)\s+([a-zA-Z\s]+)\b", q_lower):
            dept_m = re.search(r"\b(?:same for|what about in|for)\s+([a-zA-Z\s]+)\b", q_lower)
            candidate_dept = dept_m.group(1).strip()
            resolved = self.extractor._resolve_dept(candidate_dept)
            if resolved and context.last_course:
                entities["department"] = resolved
                entities["course"] = context.last_course
                rewritten = f"What is {context.last_course} in {resolved}?"

        # 4. Resolve "Explain it in Telugu" / "in telugu"
        elif "telugu" in q_lower and ("explain it" in q_lower or "in telugu" in q_lower):
            course = context.last_course or "the subject"
            unit_str = f"Unit {context.last_unit} of " if context.last_unit else ""
            rewritten = f"Explain {unit_str}{course} in Telugu"
            entities["language"] = "te"

        # Update context state with newly extracted non-null entities
        if entities.get("course"):
            context.last_course = entities["course"]
        if entities.get("course_code"):
            context.last_course_code = entities["course_code"]
        if entities.get("department"):
            context.last_department = entities["department"]
        if entities.get("semester"):
            context.last_semester = entities["semester"]
        if entities.get("unit"):
            context.last_unit = entities["unit"]

        return rewritten, entities
