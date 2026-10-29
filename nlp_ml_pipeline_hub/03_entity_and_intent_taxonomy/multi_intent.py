"""Multi-intent query detection and decomposition planner.
Deconstructs complex student queries into discrete atomic retrieval tasks.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List
from backend.nlp.entity_extractor import AcademicEntityExtractor


@dataclass
class SubTask:
    task_id: int
    intent: str
    description: str
    entities: Dict[str, Any] = field(default_factory=dict)
    query: str = ""


@dataclass
class QueryPlan:
    original_query: str
    is_multi_intent: bool
    tasks: List[SubTask] = field(default_factory=list)


class MultiIntentDecomposer:
    """Decomposes compound questions into structured subtasks."""

    def __init__(self):
        self.extractor = AcademicEntityExtractor()

    def _split_compound_query(self, query: str) -> List[str]:
        """Split a query containing multiple merged questions or topic requests."""
        q = query.strip()

        # 1. Split on question marks, semicolons, newlines, or numbered bullets (e.g. 1. ... 2. ...)
        parts = re.split(r'[\?;]|\n|(?:\s|^)[0-9]+[\.\)]\s*', q)
        parts = [p.strip(' ,.') for p in parts if p.strip(' ,.')]
        if len(parts) > 1:
            return parts

        # 2. Split on strong discourse markers
        strong_split = re.split(
            r'\b(?:and also|also|in addition to|in addition|additionally|along with|as well as|furthermore)\b',
            q,
            flags=re.IGNORECASE
        )
        strong_split = [p.strip(' ,.') for p in strong_split if p.strip(' ,.')]
        if len(strong_split) > 1:
            return strong_split

        # 3. Split on 'and' / 'plus' when introducing a distinct question clause or topic
        split_pats = [
            r'\b(?:and\s+(?:how|what|who|which|where|when|tell|explain|give|can|could|is|are|list))\b',
            r'\b(?:and\s+(?:the\s+)?(?:rules|criteria|policy|syllabus|prerequisites|credits|passing|grading|promotion|leadership))\b'
        ]
        for pat in split_pats:
            m = re.search(pat, q, flags=re.IGNORECASE)
            if m:
                start_idx = m.start()
                left = q[:start_idx].strip(' ,.')
                right = q[start_idx:].strip()
                right = re.sub(r'^(?:and|plus)\s+', '', right, flags=re.IGNORECASE).strip(' ,.')
                if len(left.split()) >= 2 and len(right.split()) >= 2:
                    return [left, right]

        return [q]

    def decompose(self, query: str) -> QueryPlan:
        """Analyze query and produce query plan with subtasks."""
        entities = self.extractor.extract_entities(query)
        q_lower = query.lower()

        # Case 1: Semester subjects + credits + prerequisites
        has_subjects_req = any(w in q_lower for w in ["subjects", "courses", "list", "all subjects"])
        has_credits_req = any(w in q_lower for w in ["credits", "credit value", "how many credits"])
        has_prereq_req = any(w in q_lower for w in ["prerequisite", "prerequisites", "pre-requisite"])
        has_syllabus_req = any(w in q_lower for w in ["syllabus", "topics", "unit", "explain unit"])

        if has_subjects_req and (has_credits_req or has_prereq_req) and entities.get("semester"):
            tasks: List[SubTask] = []
            task_id = 1
            tasks.append(SubTask(
                task_id=task_id,
                intent="semester_subjects",
                description=f"Retrieve semester {entities.get('semester')} subject listing",
                entities=entities,
                query=f"What courses are scheduled in {entities.get('department') or 'CSE'} semester {entities.get('semester')}?"
            ))
            task_id += 1

            if has_credits_req:
                tasks.append(SubTask(
                    task_id=task_id,
                    intent="semester_total_credits",
                    description=f"Retrieve credit values for semester {entities.get('semester')} courses",
                    entities=entities,
                    query=f"What are the total credits for semester {entities.get('semester')} courses?"
                ))
                task_id += 1

            if has_prereq_req:
                tasks.append(SubTask(
                    task_id=task_id,
                    intent="course_prerequisites",
                    description="Retrieve prerequisite relationships for semester courses",
                    entities=entities,
                    query=f"What are the prerequisites for courses in semester {entities.get('semester')}?"
                ))

            return QueryPlan(
                original_query=query,
                is_multi_intent=True,
                tasks=tasks
            )

        # Case 2: Course credits + prerequisites
        if entities.get("course") and has_credits_req and has_prereq_req:
            return QueryPlan(
                original_query=query,
                is_multi_intent=True,
                tasks=[
                    SubTask(
                        task_id=1,
                        intent="course_credits",
                        description=f"Retrieve credit count for {entities.get('course')}",
                        entities=entities,
                        query=f"How many credits is {entities.get('course')}?"
                    ),
                    SubTask(
                        task_id=2,
                        intent="course_prerequisites",
                        description=f"Retrieve prerequisites for {entities.get('course')}",
                        entities=entities,
                        query=f"What are the prerequisites for {entities.get('course')}?"
                    )
                ]
            )

        # Case 3: Arbitrary Merged Queries (e.g. attendance + SGPA, Chancellor + promotion)
        candidate_clauses = self._split_compound_query(query)
        if len(candidate_clauses) > 1:
            from backend.nlp.intent_classifier import intent_classifier
            decomposed_tasks: List[SubTask] = []

            for idx, clause in enumerate(candidate_clauses, 1):
                c_clean = clause.strip(" ?;,\n\t")
                if not c_clean or len(c_clean.split()) < 2:
                    continue

                c_ent = self.extractor.extract_entities(c_clean)
                # Inherit missing contextual entities
                if "department" not in c_ent and entities.get("department"):
                    c_ent["department"] = entities["department"]
                    c_ent["branch"] = entities["department"]
                if "semester" not in c_ent and entities.get("semester"):
                    c_ent["semester"] = entities["semester"]
                if "course" not in c_ent and entities.get("course"):
                    c_ent["course"] = entities["course"]

                pred = intent_classifier.predict(c_clean)
                intent_name = str(pred["intent"])
                confidence = float(pred["confidence"])

                # Topic-specific keyword backstops
                c_lower = c_clean.lower()
                if any(w in c_lower for w in ["attendance", "condonation", "detention", "shortage"]):
                    intent_name = "attendance_policy"
                elif any(w in c_lower for w in ["grade", "sgpa", "cgpa", "grading", "pass mark", "grading system"]):
                    intent_name = "grading_system"
                elif any(w in c_lower for w in ["promotion", "detained", "promote", "progression"]):
                    intent_name = "promotion_rules"
                elif any(w in c_lower for w in ["chancellor", "principal", "vice chancellor", "head"]):
                    intent_name = "institutional_leadership"
                elif any(w in c_lower for w in ["honours", "minor", "extra credit"]):
                    intent_name = "honours_minors"
                elif any(w in c_lower for w in ["prerequisite", "prerequisites"]):
                    intent_name = "course_prerequisites"
                elif any(w in c_lower for w in ["syllabus", "units", "module"]):
                    intent_name = "full_syllabus" if not c_ent.get("unit") else "unit_syllabus"
                elif any(w in c_lower for w in ["credits", "credit value"]):
                    intent_name = "semester_total_credits" if c_ent.get("semester") else "course_credits"

                if intent_name not in ["fallback", "clarification", "greeting", "thanks"]:
                    decomposed_tasks.append(SubTask(
                        task_id=len(decomposed_tasks) + 1,
                        intent=intent_name,
                        description=f"Answer: {c_clean}",
                        entities=c_ent,
                        query=c_clean
                    ))

            # Only mark as multi-intent if tasks represent distinct intents or distinct targets
            if len(decomposed_tasks) >= 2:
                distinct_intents = set(t.intent for t in decomposed_tasks)
                distinct_courses = set(t.entities.get("course") for t in decomposed_tasks if t.entities.get("course"))
                distinct_semesters = set(t.entities.get("semester") for t in decomposed_tasks if t.entities.get("semester"))

                if len(distinct_intents) >= 2 or len(distinct_courses) >= 2 or len(distinct_semesters) >= 2:
                    return QueryPlan(
                        original_query=query,
                        is_multi_intent=True,
                        tasks=decomposed_tasks
                    )

        # Case 4: Single primary intent
        primary_intent = "unit_syllabus" if has_syllabus_req else ("course_credits" if has_credits_req else "course_search")
        tasks = [SubTask(
            task_id=1,
            intent=primary_intent,
            description=f"Execute {primary_intent} retrieval",
            entities=entities,
            query=query
        )]

        return QueryPlan(
            original_query=query,
            is_multi_intent=False,
            tasks=tasks
        )
