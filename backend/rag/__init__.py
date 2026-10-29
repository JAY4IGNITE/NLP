"""Retrieval-Augmented Generation (RAG) package."""
from backend.rag.chunker import KnowledgeChunk, KnowledgeChunker
from backend.rag.embeddings import EmbeddingService, embedding_service
from backend.rag.retriever import HybridRetriever, hybrid_retriever, BM25Retriever, DenseRetriever, reciprocal_rank_fusion
from backend.rag.reranker import CrossEncoderReranker, reranker_service
from backend.rag.prompt_builder import build_rag_prompt, SYSTEM_DIRECTIVE
from backend.rag.llm_adapter import BaseLLMAdapter, DeterministicOfflineAdapter, get_llm_adapter
from backend.rag.citation_verifier import CitationVerifier
from backend.rag.attribution import AttributionEngine, attribution_engine
from backend.rag.generator import AnswerGenerator, answer_generator, ConversationalRAGEngine

__all__ = [
    "KnowledgeChunk", "KnowledgeChunker",
    "EmbeddingService", "embedding_service",
    "HybridRetriever", "hybrid_retriever", "BM25Retriever", "DenseRetriever", "reciprocal_rank_fusion",
    "CrossEncoderReranker", "reranker_service",
    "build_rag_prompt", "SYSTEM_DIRECTIVE",
    "BaseLLMAdapter", "DeterministicOfflineAdapter", "get_llm_adapter",
    "CitationVerifier",
    "AttributionEngine", "attribution_engine",
    "AnswerGenerator", "answer_generator", "ConversationalRAGEngine"
]
