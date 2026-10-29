"""Embedding service and vector encoding for semantic search."""
import logging
from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from backend.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Manages transformer embedding generation with lazy model initialization."""

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL_NAME
        self._model: Optional[SentenceTransformer] = None

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(self.model_name, device=settings.DEFAULT_DEVICE)
        return self._model

    def encode(self, texts: List[str], batch_size: int = 64, normalize: bool = True) -> np.ndarray:
        """Encode list of strings into numpy float32 matrix."""
        if not texts:
            return np.empty((0, 384), dtype=np.float32)
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=False,
            normalize_embeddings=normalize
        )
        return np.array(embeddings, dtype=np.float32)

    def encode_query(self, query: str) -> np.ndarray:
        """Encode single query into 1D normalized vector."""
        return self.encode([query], normalize=True)[0]


embedding_service = EmbeddingService()
