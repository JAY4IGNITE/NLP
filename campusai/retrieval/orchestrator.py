"""Query and Retrieval Orchestrator for CampusAI."""
import logging
from typing import Any, Dict, List, Optional
from backend.config import settings
from backend.database.sql_retriever import SQLAcademicRetriever
from backend.rag.retriever import BM25Retriever, DenseRetriever, reciprocal_rank_fusion
from backend.rag.reranker import CrossEncoderReranker

logger = logging.getLogger(__name__)


class RetrievalOrchestrator:
    """Orchestrates hybrid retrieval and exact SQL routing."""

    def __init__(self):
        self.sql_retriever = SQLAcademicRetriever()
        self.bm25_retriever = BM25Retriever()
        self.dense_retriever = DenseRetriever()
        self.reranker = CrossEncoderReranker()

    def search_hybrid(
        self,
        query: str,
        dept_filter: Optional[str] = None,
        top_k: int = 5,
        enable_rerank: bool = True
    ) -> List[Dict[str, Any]]:
        """Execute hybrid search: BM25 + Dense + RRF + Cross-Encoder."""
        try:
            sparse_hits = self.bm25_retriever.search(query, top_k=20, dept_filter=dept_filter)
        except Exception as e:
            logger.warning("BM25 search error: %s", e)
            sparse_hits = []

        try:
            dense_hits = self.dense_retriever.search(query, top_k=20, dept_filter=dept_filter)
        except Exception as e:
            logger.warning("Dense search error: %s", e)
            dense_hits = []

        fused = reciprocal_rank_fusion(
            dense_results=dense_hits,
            sparse_results=sparse_hits,
            k=settings.RRF_K,
            top_k=15
        )

        if not fused:
            return []

        if enable_rerank:
            final_hits = self.reranker.rerank(query, fused, top_k=top_k)
        else:
            final_hits = fused[:top_k]

        return final_hits

    def retrieve_evidence_for_query(
        self,
        query: str,
        intent: Optional[str] = None,
        entities: Optional[Dict[str, Any]] = None,
        dept_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """High-level evidence collection selecting between SQL and Hybrid Search."""
        entities = entities or {}
        resolved_dept = dept_code or entities.get("department") or entities.get("branch")

        q_lower = query.lower()
        if (intent in ["course_credits", "course_code", "course_ltpc"] or any(k in q_lower for k in ["credit", "credits", "code of", "course code"])) and entities.get("course"):
            course_info = self.sql_retriever.get_course_credits(entities["course"], resolved_dept)
            if course_info:
                return {
                    "source_type": "sql_structured",
                    "data": course_info,
                    "citations": [{
                        "doc_id": course_info["source_document_id"] or f"DOC-{resolved_dept or 'GEN'}",
                        "title": f"Aditya University Curriculum - {course_info['course_title']}",
                        "department": resolved_dept or "University",
                        "page": course_info["source_page"] or 1,
                        "excerpt": f"Course {course_info['course_code']} ({course_info['course_title']}): {course_info['credits']} credits.",
                        "course_code": course_info["course_code"]
                    }]
                }

        if (intent in ["semester_subjects", "semester_total_credits"] or any(k in q_lower for k in ["semester", "subjects", "courses"])) and entities.get("semester") and resolved_dept:
            sem_info = self.sql_retriever.get_semester_courses(int(entities["semester"]), resolved_dept)
            if sem_info:
                return {
                    "source_type": "sql_structured",
                    "data": sem_info,
                    "citations": [{
                        "doc_id": f"DOC-{resolved_dept}",
                        "title": f"Curriculum Structure - Semester {sem_info['semester_roman']} {sem_info['department']}",
                        "department": resolved_dept,
                        "page": sem_info["source_page"],
                        "excerpt": f"Semester {sem_info['semester_roman']} total credits: {sem_info['total_credits']}.",
                        "course_code": None
                    }]
                }

        if (intent in ["course_comparison", "curriculum_comparison"] or "compare" in q_lower) and entities.get("department_b") and entities.get("semester"):
            comp_info = self.sql_retriever.compare_semester_courses(
                int(entities["semester"]), resolved_dept or "CSE", entities["department_b"]
            )
            return {
                "source_type": "sql_structured",
                "data": comp_info,
                "citations": []
            }

        if (intent in ["unit_syllabus", "full_syllabus"] or "unit" in q_lower or "syllabus" in q_lower) and entities.get("course"):
            unit_num = int(entities["unit"]) if entities.get("unit") else None
            unit_info = self.sql_retriever.get_course_units(entities["course"], unit_num)
            if unit_info and unit_info["units"]:
                u = unit_info["units"][0]
                u_text = "\n\n".join([f"{un['unit_roman']}: {un['title']}\n{un['content'][:250]}..." for un in unit_info["units"][:3]])
                return {
                    "source_type": "sql_structured",
                    "data": unit_info,
                    "citations": [{
                        "doc_id": u["source_document"] or f"DOC-{resolved_dept or 'GEN'}",
                        "title": f"{unit_info['course_title']} - Syllabus",
                        "department": resolved_dept or "University",
                        "page": u["source_page"] or 1,
                        "excerpt": u_text,
                        "course_code": unit_info["course_code"]
                    }]
                }

        hits = self.search_hybrid(query, dept_filter=resolved_dept, top_k=5)
        citations = []
        passages = []

        for h in hits:
            chunk = h["chunk"]
            passages.append(chunk["content"])
            citations.append({
                "doc_id": chunk["source_document_id"],
                "title": f"{chunk['department_name']} - {chunk.get('course_title') or chunk['chunk_type']}",
                "department": chunk["department_code"],
                "page": chunk["source_page"],
                "excerpt": chunk["content"][:200] + "...",
                "course_code": chunk.get("course_code"),
                "score": h.get("rerank_score", h.get("rrf_score", 0.0))
            })

        return {
            "source_type": "hybrid_rag",
            "passages": passages,
            "citations": citations,
            "raw_hits": hits
        }
