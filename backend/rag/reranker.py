"""CampusAI Cross-Encoder Reranking Engine.
Re-orders retrieved candidate curriculum chunks using cross-attention transformer scoring
or deterministic lexical overlap heuristic.
"""

import logging
from typing import Any, Dict, List, Optional
from backend.config import settings

logger = logging.getLogger(__name__)


class CrossEncoderReranker:
    """Reranker adapter supporting full transformer cross-attention scoring."""

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.RERANKER_MODEL_NAME
        self._model = None
        self._initialized = False

    def _init_model(self) -> None:
        """Loads transformer model weights on first query invocation."""
        if not self._initialized:
            try:
                from sentence_transformers import CrossEncoder
                self._model = CrossEncoder(self.model_name, device=settings.DEFAULT_DEVICE)
                logger.info("Successfully loaded CrossEncoder model: %s", self.model_name)
            except Exception as e:
                logger.warning(
                    "Could not load CrossEncoder model '%s' (%s). "
                    "Engaging deterministic heuristic reranker.",
                    self.model_name, e
                )
                self._model = None
            self._initialized = True

    def rerank(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        intent: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Reranks candidate chunks against the query.
        Accepts chunks as either [{'chunk': ...}] or directly [{'text': ...}].
        """
        if not chunks:
            return []

        self._init_model()

        # Extract text from chunk
        def get_chunk_text(c: Dict[str, Any]) -> str:
            if "chunk" in c and isinstance(c["chunk"], dict):
                return c["chunk"].get("content", "")
            return c.get("text") or c.get("content", "")

        # 1. Transformer Cross-Encoder Scoring
        if self._model is not None:
            pairs = [(query, get_chunk_text(c)) for c in chunks]
            try:
                scores = self._model.predict(pairs)
                for idx, score in enumerate(scores):
                    chunks[idx]["rerank_score"] = round(float(score), 4)
                chunks.sort(key=lambda x: x["rerank_score"], reverse=True)
                return chunks[:top_k]
            except Exception as e:
                logger.warning("CrossEncoder inference execution failed (%s). Using heuristic.", e)

        # 2. Deterministic Fallback Heuristic
        q_lower = query.lower()
        q_tokens = set(q_lower.split())

        for c in chunks:
            content = get_chunk_text(c).lower()
            overlap = sum(1 for t in q_tokens if t in content)
            code_boost = 0.5 if c.get("course_code", "").lower() in q_lower else 0.0
            heuristic_score = c.get("retrieval_score", c.get("score", 0.5)) + (0.05 * overlap) + code_boost
            c["rerank_score"] = round(min(1.0, heuristic_score), 4)

        chunks.sort(key=lambda x: x["rerank_score"], reverse=True)
        return chunks[:top_k]


reranker_service = CrossEncoderReranker()
