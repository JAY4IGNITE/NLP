"""
Tests for sparse BM25, dense semantic retrieval, RRF fusion, and orchestrator.
"""

from campusai.retrieval.bm25_retriever import BM25Retriever
from campusai.retrieval.dense_retriever import DenseRetriever
from campusai.retrieval.hybrid_fusion import reciprocal_rank_fusion
from campusai.retrieval.orchestrator import RetrievalOrchestrator


def test_bm25_retriever_search():
    bm25 = BM25Retriever()
    results = bm25.search("Linear Algebra and Calculus", top_k=5)
    assert len(results) > 0
    top = results[0]
    assert "241MA001" in top["chunk"]["content"] or "Calculus" in top["chunk"]["content"]
    assert top["score"] > 0


def test_dense_retriever_search():
    dense = DenseRetriever()
    results = dense.search("differential equations and vector calculus", top_k=5)
    assert len(results) > 0
    assert results[0]["score"] > 0.4


def test_reciprocal_rank_fusion():
    dense = DenseRetriever()
    bm25 = BM25Retriever()

    d_hits = dense.search("Modern Physics wave optics", top_k=5)
    s_hits = bm25.search("Modern Physics wave optics", top_k=5)

    fused = reciprocal_rank_fusion(d_hits, s_hits, k=60, top_k=5)
    assert len(fused) > 0
    assert "rrf_score" in fused[0]
    assert fused[0]["rrf_score"] > 0


def test_retrieval_orchestrator_hybrid():
    orchestrator = RetrievalOrchestrator()
    res = orchestrator.retrieve_evidence_for_query(
        query="What topics are covered in wave optics and interference?",
        intent="unit_syllabus"
    )
    assert "citations" in res
    assert len(res["citations"]) > 0
    first_cit = res["citations"][0]
    assert first_cit["page"] > 0
    assert first_cit["title"] != ""
