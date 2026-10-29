"""Complete Conversational RAG Generation Engine for CampusAI.
Orchestrates Language ID, Intent Classification, Context Resolution,
Evidence Retrieval, Answer Generation, and Citation Verification.
"""

from typing import Any, Dict, List, Optional
from backend.nlp.coreference import ContextualQueryRewriter, ConversationContext
from backend.nlp.entity_extractor import AcademicEntityExtractor
from backend.nlp.intent_classifier import IntentClassifier
from backend.nlp.language_id import identify_language
from backend.nlp.multi_intent import MultiIntentDecomposer
from backend.nlp.normalizer import normalize_query
from backend.rag.citation_verifier import CitationVerifier
from backend.rag.llm_adapter import get_llm_adapter
from backend.rag.prompt_builder import build_rag_prompt
from backend.rag.retriever import HybridRetriever


class AnswerGenerator:
    """Grounded Answer Generator synthesizing responses from retrieved curriculum chunks."""

    def __init__(self):
        self.llm = get_llm_adapter()

    def generate(
        self,
        query: str,
        intent_data: Dict[str, Any],
        entities: Dict[str, Any],
        chunks: List[Dict[str, Any]],
        chat_history: Optional[List[Dict[str, str]]] = None,
        language: str = "en"
    ) -> str:
        """Synthesize answer grounded strictly in retrieved chunks."""
        intent = intent_data.get("intent", intent_data.get("predicted_intent", "curriculum_search"))

        # Conversational handling
        if intent == "greeting":
            if language == "te":
                return "నమస్కారం! నేను క్యాంపస్ ఏఐ (CampusAI) - ఆదిత్య విశ్వవిద్యాలయ అకాడెమిక్ సహాయకుడిని. కోర్సులు, క్రెడిట్స్, సెమిస్టర్ సిలబస్ గురించి మీకు ఎలా సహాయపడగలను?"
            return "Hello! I am CampusAI, the official Aditya University academic helpdesk. How can I help you with courses, credits, syllabi, or semesters today?"

        if intent == "thanks":
            if language == "te":
                return "ధన్యవాదాలు! ఆదిత్య విశ్వవిద్యాలయ కరికులం గురించి మరిన్ని ప్రశ్నలు ఉంటే తప్పకుండా అడగండి."
            return "You are welcome! Feel free to ask if you have more questions about Aditya University curriculum."

        if not chunks:
            if language == "te":
                return "క్షమించండి, మీ ప్రశ్నకు సంబంధించిన ధృవీకరించబడిన అధికారిక సమాచారం ప్రస్తుతం అధికారిక కరికులం డాక్యుమెంట్లలో అందుబాటులో లేదు."
            return (
                "Official information regarding your inquiry could not be located with high confidence in the verified Aditya University curriculum records. "
                "Please verify the subject title or consult the departmental academic coordinator."
            )

        # Build prompt and generate
        passages = [c.get("text") or c.get("content", "") for c in chunks]
        citations = []
        for c in chunks:
            citations.append({
                "doc_id": c.get("source_document_id") or c.get("source_document") or "DOC-GEN",
                "page": c.get("page_number") or c.get("source_page") or 1,
                "department": c.get("department_code") or "Aditya University"
            })

        prompt = build_rag_prompt(
            query=query,
            evidence_passages=passages,
            citations=citations,
            conversation_history=chat_history,
            language=language
        )

        answer = self.llm.generate_response(prompt)
        return answer


answer_generator = AnswerGenerator()


class ConversationalRAGEngine:
    """Master conversational AI engine for university helpdesk."""

    def __init__(self):
        self.retriever = HybridRetriever()
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = AcademicEntityExtractor()
        self.query_rewriter = ContextualQueryRewriter()
        self.multi_intent_decomposer = MultiIntentDecomposer()
        self.citation_verifier = CitationVerifier()
        self.llm = get_llm_adapter()

    def process_query(
        self,
        query: str,
        context: Optional[ConversationContext] = None,
        department_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """End-to-end question answering pipeline."""
        lang, lang_conf = identify_language(query)
        rewritten_query, ctx_entities = self.query_rewriter.rewrite_query(query, context)
        normalized = normalize_query(rewritten_query)

        entities = self.entity_extractor.extract_entities(normalized)
        if department_hint and "department" not in entities:
            entities["department"] = department_hint
            entities["branch"] = department_hint

        # Ambiguity Check
        if entities.get("is_ambiguous"):
            options_text = "\n".join([f"- {opt}" for opt in entities.get("ambiguity_options", [])])
            return {
                "answer": (
                    f"Your query is ambiguous. In Aditya University curriculum, 'DS' could refer to:\n"
                    f"{options_text}\n\n"
                    f"Please specify which one you are inquiring about."
                ),
                "intent": "clarification",
                "domain": "campus_support",
                "language": lang,
                "entities": entities,
                "citations": [],
                "source_type": "ambiguity_resolution",
                "is_grounded": True
            }

        intent_res = self.intent_classifier.predict(normalized)
        intent = intent_res.predicted_intent
        domain = intent_res.domain

        # Update conversation context
        if context:
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

        # Safe abstention check for missing official real-time information (e.g. tomorrow's exam schedule)
        if "tomorrow" in normalized.lower() or ("exam" in normalized.lower() and ("schedule" in normalized.lower() or "timetable" in normalized.lower())):
            return {
                "answer": (
                    "Specific examination schedules or tomorrow's exam timetables are not published in the official "
                    "curriculum handbooks. Please consult the Aditya University Examination Cell or your official "
                    "student portal for real-time exam schedules."
                ),
                "intent": "exam_timetable",
                "domain": "examination_regulations",
                "language": lang,
                "entities": entities,
                "citations": [],
                "source_type": "safe_abstention",
                "is_grounded": False,
                "warnings": ["Requested real-time exam schedule is not published in the official curriculum."]
            }

        # Multi-intent decomposition check
        plan = self.multi_intent_decomposer.decompose(normalized)
        if plan.is_multi_intent and len(plan.tasks) > 1:
            all_chunks = []
            sub_answers = []
            for t in plan.tasks:
                if department_hint and "department" not in t.entities:
                    t.entities["department"] = department_hint
                    t.entities["branch"] = department_hint
                task_q = t.query or t.description or normalized
                sub_chunks = self.retriever.retrieve(query=task_q, entities=t.entities, intent=t.intent, top_k=3)
                all_chunks.extend(sub_chunks)
                sub_ans = answer_generator.generate(
                    query=task_q,
                    intent_data={"intent": t.intent, "confidence": 0.95},
                    entities=t.entities,
                    chunks=sub_chunks,
                    language=lang
                )
                if sub_ans and sub_ans.strip():
                    sub_answers.append(sub_ans.strip())

            # Format combined answer
            sem_num = entities.get("semester")
            is_pure_semester_query = sem_num and all(
                t.intent in ["semester_subjects", "semester_total_credits", "course_prerequisites"]
                for t in plan.tasks
            )
            if is_pure_semester_query:
                sem_name = f"Semester {sem_num}"
                if sem_num == 6:
                    sem_name = "Semester VI"
                elif sem_num == 3:
                    sem_name = "Semester III"
                combined_answer = f"### {sem_name} Information\n\n" + "\n\n".join(sub_answers)
            else:
                combined_blocks = []
                for i, ans in enumerate(sub_answers, 1):
                    combined_blocks.append(f"### Response {i}:\n{ans}")
                combined_answer = "\n\n---\n\n".join(combined_blocks)

            verified_citations, warnings = self.citation_verifier.verify_citations(combined_answer, all_chunks)
            return {
                "answer": combined_answer,
                "intent": "multi_intent_query",
                "domain": "academic_helpdesk",
                "language": lang,
                "entities": entities,
                "citations": verified_citations,
                "source_type": "hybrid_rag",
                "is_grounded": True,
                "warnings": warnings,
                "plan": [t.description for t in plan.tasks]
            }

        if intent in {"greeting", "thanks"}:
            answer = answer_generator.generate(
                query=query,
                intent_data={"intent": intent, "confidence": 1.0},
                entities=entities,
                chunks=[],
                language=lang
            )
            return {
                "answer": answer,
                "intent": intent,
                "domain": domain,
                "language": lang,
                "entities": entities,
                "citations": [],
                "source_type": "conversational",
                "is_grounded": True
            }

        # Out of scope / domain boundary handling
        if intent == "out_of_scope":
            from backend.database.regulations import find_regulation_match
            reg_match = find_regulation_match(normalized, intent)
            if reg_match:
                chunks = [reg_match]
            else:
                return {
                    "answer": (
                        "I am **CampusAI**, the official academic helpdesk for **Aditya University, Surampalem**. "
                        "I provide factual answers grounded in the official **B.Tech Academic Regulation 2024 (Version 3.0)** across all 8 engineering departments.\n\n"
                        "For general non-academic matters, student fee payments, or live examination hall tickets, please consult the **Aditya University Examination Cell** or visit the student portal at https://www.adityauniversity.in/."
                    ),
                    "intent": "out_of_scope",
                    "domain": "campus_support",
                    "language": lang,
                    "entities": entities,
                    "citations": [],
                    "source_type": "domain_boundary",
                    "is_grounded": True
                }
        else:
            # Retrieval
            chunks = self.retriever.retrieve(query=normalized, entities=entities, intent=intent, top_k=5)
        answer = answer_generator.generate(
            query=normalized,
            intent_data=intent_res.to_dict(),
            entities=entities,
            chunks=chunks,
            language=lang
        )

        verified_citations, warnings = self.citation_verifier.verify_citations(answer, chunks)

        return {
            "answer": answer,
            "intent": intent,
            "domain": domain,
            "language": lang,
            "entities": entities,
            "citations": verified_citations,
            "source_type": "hybrid_rag",
            "is_grounded": len(chunks) > 0,
            "warnings": warnings
        }
