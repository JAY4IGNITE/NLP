"""Hybrid Information Retrieval Engine for CampusAI.
Combines exact SQL structured queries, sparse lexical BM25 search,
dense semantic vector search, and Reciprocal Rank Fusion (RRF).
"""

import json
import logging
import re
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
from rank_bm25 import BM25Okapi

from backend.config import settings
from backend.database.regulations import find_regulation_match
from backend.database.sql_retriever import SQLAcademicRetriever
from backend.rag.chunker import KnowledgeChunk
from backend.rag.embeddings import embedding_service

logger = logging.getLogger(__name__)


def academic_tokenizer(text: str) -> List[str]:
    """Tokenize query and text preserving course codes, roman numerals, and academic keywords."""
    clean_text = text.lower()
    roman_map = {"i": "1", "ii": "2", "iii": "3", "iv": "4", "v": "5", "vi": "6", "vii": "7", "viii": "8"}
    for r, n in roman_map.items():
        clean_text = re.sub(rf"\bunit[\s\-]+{r}\b", f"unit_{n}", clean_text)
        clean_text = re.sub(rf"\bsem(?:ester)?[\s\-]+{r}\b", f"semester_{n}", clean_text)

    tokens = re.findall(r"\b241[a-z]{2}[0-9]{3}\b|\b[a-z0-9_\-]+\b|[\u0C00-\u0C7F]+", clean_text)
    return [t for t in tokens if len(t) > 1 or t in ["1", "2", "3", "4", "5", "6", "7", "8"]]


class BM25Retriever:
    """BM25 sparse indexer and searcher."""

    def __init__(self, index_file: Optional[Path] = None):
        self.index_file = index_file or (settings.INDICES_DIR / "bm25_index.json")
        self.bm25: Optional[BM25Okapi] = None
        self.chunks: List[Dict[str, Any]] = []

    def build_index(self, chunks: List[KnowledgeChunk]) -> None:
        """Build BM25 index from knowledge chunks and save to disk."""
        self.chunks = [asdict(c) for c in chunks]
        tokenized_corpus = [academic_tokenizer(c["content"]) for c in self.chunks]
        self.bm25 = BM25Okapi(tokenized_corpus, k1=settings.BM25_K1, b=settings.BM25_B)
        self.save_index()

    def save_index(self) -> None:
        """Persist BM25 index and chunks metadata to disk."""
        settings.INDICES_DIR.mkdir(parents=True, exist_ok=True)
        data = {
            "total_chunks": len(self.chunks),
            "chunks": self.chunks,
        }
        with open(self.index_file, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def load_index(self) -> bool:
        """Load index from disk if available."""
        if not self.index_file.exists():
            return False
        with open(self.index_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.chunks = data.get("chunks", [])
            tokenized_corpus = [academic_tokenizer(c["content"]) for c in self.chunks]
            self.bm25 = BM25Okapi(tokenized_corpus, k1=settings.BM25_K1, b=settings.BM25_B)
            return True

    def search(
        self, query: str, top_k: int = 10, dept_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search BM25 index using tokenized query."""
        if self.bm25 is None:
            if not self.load_index():
                return []

        tokens = academic_tokenizer(query)
        if not tokens:
            return []

        scores = self.bm25.get_scores(tokens)
        ranked = []
        for idx, score in enumerate(scores):
            chunk = self.chunks[idx]
            if dept_filter and chunk.get("department_code") != dept_filter:
                continue
            if score > 0.0:
                ranked.append({
                    "chunk_id": chunk["chunk_id"],
                    "score": float(score),
                    "chunk": chunk
                })

        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked[:top_k]


class DenseRetriever:
    """Dense vector retriever using embedding models."""

    def __init__(
        self,
        embeddings_file: Optional[Path] = None,
        metadata_file: Optional[Path] = None,
    ):
        self.embeddings_file = embeddings_file or (settings.INDICES_DIR / "dense_embeddings.npy")
        self.metadata_file = metadata_file or (settings.INDICES_DIR / "chunks_metadata.json")
        self.embeddings: Optional[np.ndarray] = None
        self.chunks: List[Dict[str, Any]] = []

    def load_index(self) -> bool:
        """Load precomputed embeddings and metadata."""
        if not self.embeddings_file.exists() or not self.metadata_file.exists():
            return False
        try:
            self.embeddings = np.load(self.embeddings_file)
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.chunks = data.get("chunks", [])
            return True
        except Exception:
            return False

    def search(
        self, query: str, top_k: int = 10, dept_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Dense semantic search using cosine similarity."""
        if self.embeddings is None:
            if not self.load_index():
                return []

        query_emb = embedding_service.encode_query(query)
        sims = np.dot(self.embeddings, query_emb)

        ranked = []
        for idx, score in enumerate(sims):
            chunk = self.chunks[idx]
            if dept_filter and chunk.get("department_code") != dept_filter:
                continue
            ranked.append({
                "chunk_id": chunk["chunk_id"],
                "score": float(score),
                "chunk": chunk
            })

        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked[:top_k]


def reciprocal_rank_fusion(
    dense_results: List[Dict[str, Any]],
    sparse_results: List[Dict[str, Any]],
    k: int = 60,
    dense_weight: float = 1.0,
    sparse_weight: float = 1.0,
    top_k: int = 10,
) -> List[Dict[str, Any]]:
    """Fuses ranked candidate lists from dense semantic search and sparse lexical BM25 search."""
    fused_scores: Dict[str, float] = {}
    item_map: Dict[str, Dict[str, Any]] = {}
    provenance: Dict[str, Dict[str, Any]] = {}

    for rank, item in enumerate(dense_results, 1):
        cid = item["chunk_id"]
        item_map[cid] = item["chunk"]
        fused_scores[cid] = fused_scores.get(cid, 0.0) + (dense_weight / (k + rank))
        provenance.setdefault(cid, {})["dense_rank"] = rank
        provenance[cid]["dense_score"] = item["score"]

    for rank, item in enumerate(sparse_results, 1):
        cid = item["chunk_id"]
        item_map[cid] = item["chunk"]
        fused_scores[cid] = fused_scores.get(cid, 0.0) + (sparse_weight / (k + rank))
        provenance.setdefault(cid, {})["sparse_rank"] = rank
        provenance[cid]["sparse_score"] = item["score"]

    merged: List[Dict[str, Any]] = []
    for cid, rrf_score in sorted(fused_scores.items(), key=lambda x: x[1], reverse=True):
        merged.append({
            "chunk_id": cid,
            "rrf_score": round(rrf_score, 6),
            "provenance": provenance[cid],
            "chunk": item_map[cid]
        })

    return merged[:top_k]


class HybridRetriever:
    """Master hybrid retrieval orchestrator combining SQL, BM25, and Dense embeddings."""

    def __init__(self):
        self.sql_retriever = SQLAcademicRetriever()
        self.bm25_retriever = BM25Retriever()
        self.dense_retriever = DenseRetriever()

    def retrieve(
        self,
        query: str,
        entities: Optional[Dict[str, Any]] = None,
        intent: Optional[str] = None,
        top_k: int = 4
    ) -> List[Dict[str, Any]]:
        """Unified retrieval method returning standardized chunks matching NLP-cornerstone specification."""
        entities = entities or {}
        resolved_dept = entities.get("branch") or entities.get("department")
        q_lower = query.lower()

        # 0. Check verified academic regulations knowledge base (Attendance, Grading, Promotion, Honours, Leadership, etc.)
        reg_chunk = find_regulation_match(query, intent, entities)
        if reg_chunk:
            return [reg_chunk]

        # 1. Check exact SQL routing for fast structured responses
        if (intent in ["course_credits", "course_code", "course_ltpc"] or any(k in q_lower for k in ["credit", "credits", "code of", "course code"])) and entities.get("course"):
            course_info = self.sql_retriever.get_course_credits(entities["course"], resolved_dept)
            if course_info:
                text = (
                    f"Course: {course_info['course_title']} ({course_info['course_code']})\n"
                    f"Credits: {course_info['credits']}\n"
                    f"Lecture Hours: {course_info['lecture_hours']}, Tutorial Hours: {course_info['tutorial_hours']}, Practical Hours: {course_info['practical_hours']}\n"
                    f"Total Contact Hours: {course_info['total_hours']}, Category: {course_info['category']}"
                )
                return [{
                    "chunk_id": f"SQL-CRS-{course_info['course_code']}",
                    "text": text,
                    "content": text,
                    "course_code": course_info["course_code"],
                    "course_name": course_info["course_title"],
                    "course_title": course_info["course_title"],
                    "source_document": course_info["source_document_id"] or f"DOC-{resolved_dept or 'GEN'}",
                    "source_document_id": course_info["source_document_id"] or f"DOC-{resolved_dept or 'GEN'}",
                    "page_number": course_info["source_page"] or 1,
                    "source_page": course_info["source_page"] or 1,
                    "retrieval_score": 1.0,
                    "department_code": resolved_dept or "GEN"
                }]

        # Check structured semester queries
        sem_candidate = entities.get("semester")
        if sem_candidate is None:
            m = re.search(r"\b(?:semester|sem)\s*[-]?\s*([1-8])\b", q_lower)
            if m:
                sem_candidate = int(m.group(1))
            else:
                ord_m = re.search(r"\b(1st|2nd|3rd|4th|5th|6th|7th|8th)\s+(?:semester|sem)\b", q_lower)
                if ord_m:
                    sem_candidate = int(ord_m.group(1)[0])

        target_dept = resolved_dept or "CSE"
        if (intent in ["semester_subjects", "semester_total_credits"] or any(k in q_lower for k in ["semester", "sem ", "subjects", "courses"])) and sem_candidate is not None:
            sem_info = self.sql_retriever.get_semester_courses(int(sem_candidate), target_dept)
            if sem_info:
                courses_text = "\n".join([f"- {c['code']}: {c['title']} ({c['credits']} credits, Category: {c['category']})" for c in sem_info["courses"]])
                # Calculate accurate sum of credits
                summed_credits = sum(float(c.get("credits", 0.0)) for c in sem_info["courses"])
                credits_display = f"{summed_credits:.1f}" if summed_credits > 0 else str(sem_info['total_credits'])
                text = (
                    f"Aditya University B.Tech Curriculum - Semester {sem_info['semester_roman']} ({sem_info['department']})\n"
                    f"Total Semester Credits: {credits_display}\n\n"
                    f"Subjects & Laboratories Scheduled:\n{courses_text}"
                )
                return [{
                    "chunk_id": f"SQL-SEM-{target_dept}-S{sem_info['semester_number']}",
                    "text": text,
                    "content": text,
                    "course_code": None,
                    "course_name": f"Semester {sem_info['semester_roman']} Curriculum",
                    "course_title": f"Semester {sem_info['semester_roman']} Curriculum",
                    "source_document": f"DOC-{target_dept}",
                    "source_document_id": f"DOC-{target_dept}",
                    "page_number": sem_info["source_page"] or 1,
                    "source_page": sem_info["source_page"] or 1,
                    "retrieval_score": 1.0,
                    "department_code": target_dept
                }]

        if (intent in ["unit_syllabus", "full_syllabus"] or "unit" in q_lower or "syllabus" in q_lower) and entities.get("course"):
            unit_num = int(entities["unit"]) if entities.get("unit") else None
            unit_info = self.sql_retriever.get_course_units(entities["course"], unit_num)
            if unit_info and unit_info["units"]:
                if unit_num is not None:
                    u = unit_info["units"][0]
                    text = f"Course: {unit_info['course_title']} ({unit_info['course_code']})\n{u['unit_roman']}: {u['title']}\nTopics: {u['content']}"
                    if u.get("practice_content"):
                        text += f"\nPractice / Exercises: {u['practice_content']}"
                else:
                    # Comprehensive Multi-Unit Syllabus
                    unit_blocks = [f"**{unit_info['course_title']}** (`{unit_info['course_code']}`) Syllabus:\n"]
                    for u in unit_info["units"]:
                        unit_blocks.append(
                            f"### {u['unit_roman']}: {u['title'] or 'Topics'}\n"
                            f"- **Topics:** {u['content']}"
                        )
                        if u.get("practice_content"):
                            unit_blocks.append(f"- **Lab / Practical Exercises:** {u['practice_content']}")

                    # If query asks about textbooks or full syllabus, attach prescribed textbooks
                    if any(w in q_lower for w in ["textbook", "book", "reference", "author", "full", "5 unit", "all unit"]) or intent == "full_syllabus":
                        tb_info = self.sql_retriever.get_course_textbooks(entities["course"], resolved_dept)
                        if tb_info and tb_info.get("textbooks"):
                            unit_blocks.append("### Recommended Textbooks & Reference Books:")
                            for b in tb_info["textbooks"]:
                                unit_blocks.append(f"- [{b['type']}] **{b['title']}** by {b['authors']} ({b['publisher']}, {b['edition']})")

                    text = "\n\n".join(unit_blocks)

                return [{
                    "chunk_id": f"SQL-UNT-{unit_info['course_code']}-ALL" if unit_num is None else f"SQL-UNT-{unit_info['course_code']}-U{unit_num}",
                    "text": text,
                    "content": text,
                    "course_code": unit_info["course_code"],
                    "course_name": unit_info["course_title"],
                    "course_title": unit_info["course_title"],
                    "source_document": unit_info["units"][0]["source_document"] or f"DOC-{resolved_dept or 'GEN'}",
                    "source_document_id": unit_info["units"][0]["source_document"] or f"DOC-{resolved_dept or 'GEN'}",
                    "page_number": unit_info["units"][0]["source_page"] or 1,
                    "source_page": unit_info["units"][0]["source_page"] or 1,
                    "retrieval_score": 1.0,
                    "department_code": resolved_dept or "GEN",
                    "unit": unit_num
                }]

        if (intent in ["prerequisites", "course_prerequisites"] or any(k in q_lower for k in ["prerequisite", "prerequisites", "pre-requisite"])) and entities.get("course"):
            prereq_info = self.sql_retriever.get_course_prerequisites(entities["course"], resolved_dept)
            if prereq_info:
                text = (
                    f"Course: {prereq_info['course_title']} ({prereq_info['course_code']})\n"
                    f"Prerequisites: {prereq_info['prerequisites']}"
                )
                return [{
                    "chunk_id": f"SQL-PRE-{prereq_info['course_code']}",
                    "text": text,
                    "content": text,
                    "course_code": prereq_info["course_code"],
                    "course_name": prereq_info["course_title"],
                    "course_title": prereq_info["course_title"],
                    "source_document": prereq_info["source_document_id"] or f"DOC-{resolved_dept or 'GEN'}",
                    "source_document_id": prereq_info["source_document_id"] or f"DOC-{resolved_dept or 'GEN'}",
                    "page_number": prereq_info["source_page"] or 1,
                    "source_page": prereq_info["source_page"] or 1,
                    "retrieval_score": 1.0,
                    "department_code": resolved_dept or "GEN"
                }]

        if (intent in ["textbooks", "course_textbooks"] or any(k in q_lower for k in ["textbook", "textbooks", "reference book", "prescribed book", "recommended book"])) and entities.get("course"):
            tb_info = self.sql_retriever.get_course_textbooks(entities["course"], resolved_dept)
            if tb_info and tb_info["textbooks"]:
                b_lines = [f"- [{b['type']}] {b['title']} by {b['authors']} ({b['publisher']}, {b['edition']})" for b in tb_info["textbooks"]]
                text = (
                    f"Course: {tb_info['course_title']} ({tb_info['course_code']})\n"
                    f"Prescribed Textbooks & References:\n" + "\n".join(b_lines)
                )
                return [{
                    "chunk_id": f"SQL-TBK-{tb_info['course_code']}",
                    "text": text,
                    "content": text,
                    "course_code": tb_info["course_code"],
                    "course_name": tb_info["course_title"],
                    "course_title": tb_info["course_title"],
                    "source_document": tb_info["source_document_id"] or f"DOC-{resolved_dept or 'GEN'}",
                    "source_document_id": tb_info["source_document_id"] or f"DOC-{resolved_dept or 'GEN'}",
                    "page_number": tb_info["source_page"] or 1,
                    "source_page": tb_info["source_page"] or 1,
                    "retrieval_score": 1.0,
                    "department_code": resolved_dept or "GEN"
                }]

        if (intent in ["outcomes", "course_outcomes"] or any(k in q_lower for k in ["outcome", "outcomes", "co1", "cos", "course outcome"])) and entities.get("course"):
            co_info = self.sql_retriever.get_course_outcomes(entities["course"], resolved_dept)
            if co_info and co_info["outcomes"]:
                co_lines = [f"- **{co['code']}**: {co['description']}" for co in co_info["outcomes"]]
                text = (
                    f"Course: {co_info['course_title']} ({co_info['course_code']})\n"
                    f"Course Outcomes:\n" + "\n".join(co_lines)
                )
                return [{
                    "chunk_id": f"SQL-CO-{co_info['course_code']}",
                    "text": text,
                    "content": text,
                    "course_code": co_info["course_code"],
                    "course_name": co_info["course_title"],
                    "course_title": co_info["course_title"],
                    "source_document": co_info["source_document_id"] or f"DOC-{resolved_dept or 'GEN'}",
                    "source_document_id": co_info["source_document_id"] or f"DOC-{resolved_dept or 'GEN'}",
                    "page_number": co_info["source_page"] or 1,
                    "source_page": co_info["source_page"] or 1,
                    "retrieval_score": 1.0,
                    "department_code": resolved_dept or "GEN"
                }]

        # 2. Hybrid search: BM25 + Dense + RRF
        sparse_hits = self.bm25_retriever.search(query, top_k=20, dept_filter=resolved_dept)
        dense_hits = self.dense_retriever.search(query, top_k=20, dept_filter=resolved_dept)

        fused = reciprocal_rank_fusion(
            dense_results=dense_hits,
            sparse_results=sparse_hits,
            k=settings.RRF_K,
            top_k=top_k * 2
        )

        formatted_chunks = []
        for item in fused:
            c = item["chunk"]
            formatted_chunks.append({
                "chunk_id": item["chunk_id"],
                "text": c.get("content", ""),
                "content": c.get("content", ""),
                "course_code": c.get("course_code"),
                "course_name": c.get("course_title"),
                "course_title": c.get("course_title"),
                "source_document": c.get("source_document_id") or f"DOC-{c.get('department_code', 'GEN')}",
                "source_document_id": c.get("source_document_id") or f"DOC-{c.get('department_code', 'GEN')}",
                "page_number": c.get("source_page") or 1,
                "source_page": c.get("source_page") or 1,
                "retrieval_score": item["rrf_score"],
                "department_code": c.get("department_code"),
                "semester": c.get("semester_num"),
                "unit": c.get("unit_num"),
            })

        return formatted_chunks[:top_k]


hybrid_retriever = HybridRetriever()
