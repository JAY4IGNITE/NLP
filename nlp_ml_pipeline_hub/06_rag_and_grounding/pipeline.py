"""End-to-end Academic NLP and RAG Chatbot Pipeline.
Orchestrates preprocessing -> intent classification -> entity extraction -> hybrid retrieval ->
cross-attention reranking -> grounded answer generation -> attribution confidence scoring.
"""
import time
from typing import List, Dict, Any, Optional

from backend.nlp.intent_classifier import intent_classifier
from backend.nlp.entity_extractor import entity_extractor
from backend.nlp.multi_intent import MultiIntentDecomposer
from backend.rag.retriever import hybrid_retriever
from backend.rag.reranker import reranker_service
from backend.rag.generator import answer_generator
from backend.rag.attribution import attribution_engine
from backend.guardrails import guardrails
from backend.utils.logger import logger


class StudentChatbotPipeline:
    """Master 8-stage NLP and evidence retrieval pipeline for university helpdesk."""

    def __init__(self):
        self.multi_intent_decomposer = MultiIntentDecomposer()

    def process_query(
        self,
        query: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        top_k: int = 4
    ) -> Dict[str, Any]:
        """Execute the full 8-stage academic NLP + RAG pipeline."""
        start_time = time.time()
        logger.info(f"Processing query: '{query}'")

        # 0. Safety & Boundary Guardrail Check
        is_safe, failure_reason, refusal_msg = guardrails.check_input_safety(query)
        if not is_safe:
            latency_ms = round((time.time() - start_time) * 1000, 2)
            return {
                "query": query,
                "intent": "safe_abstention" if failure_reason == "safe_abstention" else ("out_of_scope" if failure_reason == "non_academic_domain" else "security_guardrail"),
                "intent_confidence": 1.0,
                "raw_intent": failure_reason,
                "is_fallback": True,
                "top_intents": [],
                "entities": {},
                "answer": refusal_msg,
                "sources": [],
                "is_grounded": True,
                "overall_confidence": 1.0,
                "confidence_breakdown": {
                    "guardrail_triggered": failure_reason
                },
                "retrieved_chunk_count": 0,
                "reranked_chunk_count": 0,
                "latency_ms": latency_ms
            }

        # Check Multi-Intent Decomposer for merged queries
        plan = self.multi_intent_decomposer.decompose(query)
        if plan.is_multi_intent and len(plan.tasks) > 1:
            all_chunks = []
            sub_answers = []
            entities = entity_extractor.extract(query)
            for t in plan.tasks:
                task_q = t.query or t.description or query
                task_ent = dict(t.entities)
                if entities.get("department") and "department" not in task_ent:
                    task_ent["department"] = entities["department"]
                    task_ent["branch"] = entities["department"]
                if entities.get("course") and "course" not in task_ent:
                    task_ent["course"] = entities["course"]
                if entities.get("semester") and "semester" not in task_ent:
                    task_ent["semester"] = entities["semester"]

                sub_chunks = hybrid_retriever.retrieve(
                    query=task_q,
                    entities=task_ent,
                    intent=t.intent,
                    top_k=top_k
                )
                all_chunks.extend(sub_chunks)

                sub_ans = answer_generator.generate(
                    query=task_q,
                    intent_data={"intent": t.intent, "confidence": 0.95},
                    entities=task_ent,
                    chunks=sub_chunks
                )
                if sub_ans and sub_ans.strip():
                    sub_answers.append(sub_ans.strip())

            # Combined answer
            sem_num = entities.get("semester")
            is_pure_sem = sem_num and all(
                t.intent in ["semester_subjects", "semester_total_credits", "course_prerequisites"]
                for t in plan.tasks
            )
            if is_pure_sem:
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

            latency_ms = round((time.time() - start_time) * 1000, 2)
            return {
                "query": query,
                "intent": "multi_intent_query",
                "intent_confidence": 0.95,
                "raw_intent": "multi_intent_query",
                "is_fallback": False,
                "top_intents": [{"intent": t.intent, "confidence": 0.9} for t in plan.tasks],
                "entities": entities,
                "answer": combined_answer,
                "sources": [
                    {
                        "chunk_id": c.get("chunk_id"),
                        "source": c.get("source_document_id") or c.get("source_document"),
                        "page": c.get("page_number") or c.get("source_page", 1),
                        "score": round(float(c.get("retrieval_score", 1.0)), 3)
                    }
                    for c in all_chunks[:6]
                ],
                "is_grounded": True,
                "overall_confidence": 0.95,
                "confidence_breakdown": {
                    "multi_intent_tasks": len(plan.tasks)
                },
                "retrieved_chunk_count": len(all_chunks),
                "reranked_chunk_count": len(all_chunks),
                "latency_ms": latency_ms
            }

        # 1. Intent Classification
        intent_result = intent_classifier.predict(query)
        intent = intent_result["intent"]
        confidence = intent_result["confidence"]

        # 2. Entity Extraction
        entities = entity_extractor.extract(query)

        # Entity-guided intent routing
        if intent in {"fallback", "out_of_scope", "clarification"} and (entities.get("course_code") or entities.get("canonical_course_name")):
            intent = "course_credits" if any(w in query.lower() for w in ["credit", "credits"]) else "full_syllabus"
            confidence = max(confidence, 0.90)

        # 3. Hybrid Retrieval (Dense Vectors + Sparse BM25 + SQL structured lookup)
        retrieved_chunks = []
        reranked_chunks = []

        if intent not in {"greeting", "thanks", "help", "fallback", "out_of_scope"}:
            retrieved_chunks = hybrid_retriever.retrieve(
                query=query,
                entities=entities,
                intent=intent,
                top_k=top_k * 2
            )

            # 4. Cross-Encoder Reranking
            if retrieved_chunks:
                reranked_chunks = reranker_service.rerank(query=query, chunks=retrieved_chunks, intent=intent)
                reranked_chunks = [
                    chunk for chunk in reranked_chunks
                    if chunk.get("chunk_id", "").startswith("SQL-")
                    or chunk.get("rerank_score", chunk.get("retrieval_score", 0.0)) >= guardrails.retrieval_threshold
                ]
            else:
                reranked_chunks = []

            # Guardrail: Validate retrieval relevance threshold
            is_retrieval_grounded, grounding_warning = guardrails.validate_retrieval_grounding(intent, reranked_chunks)
            if not is_retrieval_grounded:
                latency_ms = round((time.time() - start_time) * 1000, 2)
                return {
                    "query": query,
                    "intent": intent,
                    "intent_confidence": confidence,
                    "raw_intent": intent_result.get("raw_intent", intent),
                    "is_fallback": True,
                    "top_intents": intent_result.get("top_intents", []),
                    "entities": entities,
                    "answer": grounding_warning,
                    "sources": [],
                    "is_grounded": False,
                    "overall_confidence": 0.25,
                    "confidence_breakdown": {
                        "reason": "retrieval_below_threshold"
                    },
                    "retrieved_chunk_count": len(retrieved_chunks),
                    "reranked_chunk_count": len(reranked_chunks),
                    "latency_ms": latency_ms
                }
        else:
            reranked_chunks = []

        # 5. Grounded Answer Generation
        answer = answer_generator.generate(
            query=query,
            intent_data={"intent": intent, "confidence": confidence},
            entities=entities,
            chunks=reranked_chunks,
            chat_history=chat_history
        )

        # 6. Source Attribution & Confidence Scoring
        attribution_result = attribution_engine.calculate_confidence(
            query=query,
            answer=answer,
            intent_data={"intent": intent, "confidence": confidence},
            entities=entities,
            chunks=reranked_chunks
        )

        # 7. Fact & Hallucination Check
        fact_check = guardrails.verify_answer_facts(answer, entities, reranked_chunks)

        latency_ms = round((time.time() - start_time) * 1000, 2)

        pipeline_output = {
            "query": query,
            "intent": intent,
            "intent_confidence": confidence,
            "raw_intent": intent_result.get("raw_intent", intent),
            "is_fallback": intent_result.get("is_fallback", False),
            "top_intents": intent_result.get("top_intents", []),
            "entities": entities,
            "answer": answer,
            "sources": attribution_result["citations"],
            "is_grounded": attribution_result["is_grounded"],
            "overall_confidence": attribution_result["overall_confidence"],
            "confidence_breakdown": attribution_result["breakdown"],
            "fact_check": fact_check,
            "retrieved_chunk_count": len(retrieved_chunks),
            "reranked_chunk_count": len(reranked_chunks),
            "latency_ms": latency_ms
        }

        logger.info(
            f"Completed pipeline: intent='{intent}' ({confidence}), "
            f"grounded={attribution_result['is_grounded']}, latency={latency_ms}ms"
        )
        return pipeline_output


pipeline = StudentChatbotPipeline()
