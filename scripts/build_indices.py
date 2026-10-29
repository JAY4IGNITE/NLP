"""Build BM25 and Dense Retrieval Indices for Aditya University Handbooks."""
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.rag.chunker import DocumentChunker
from backend.rag.embeddings import EmbeddingModel
from backend.rag.retriever import HybridRetriever
from backend.config import settings

def main():
    print("[*] Initializing Index Building...")
    t0 = time.time()

    retriever = HybridRetriever()
    print(f"[+] BM25 Index initialized: {len(retriever.bm25_chunks)} chunks loaded.")
    print(f"[+] Dense Embedding Model initialized: {retriever.embedding_model.model_name}")
    print(f"[+] Indexing ready in {time.time() - t0:.2f}s.")

if __name__ == "__main__":
    main()
