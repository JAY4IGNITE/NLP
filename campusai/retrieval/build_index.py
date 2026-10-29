"""
Index builder for CampusAI.
Generates knowledge chunks and constructs both BM25 sparse and dense vector indices.
"""

from campusai.ingestion.chunker import KnowledgeChunker
from campusai.retrieval.bm25_retriever import BM25Retriever
from campusai.retrieval.dense_retriever import DenseRetriever


def build_all_indices():
    print("=" * 60)
    print(" CampusAI Knowledge Index Builder")
    print("=" * 60)

    # 1. Generate chunks
    print("--> Generating structure-aware knowledge chunks from database...")
    chunker = KnowledgeChunker()
    chunks = chunker.generate_all_chunks()
    print(f"    Produced {len(chunks)} total knowledge chunks.")

    # 2. Build BM25 Sparse Index
    print("\n--> Building BM25 sparse retrieval index...")
    bm25 = BM25Retriever()
    bm25.build_index(chunks)
    print(f"    BM25 index built and saved to {bm25.index_file}")

    # 3. Build Dense Vector Index
    print("\n--> Building Dense Semantic Vector index (SentenceTransformers)...")
    dense = DenseRetriever()
    dense.build_index(chunks, batch_size=64)
    print(f"    Dense embeddings built and saved to {dense.embeddings_file}")

    print("\n[OK] All retrieval indices successfully built and ready for search!")


if __name__ == "__main__":
    build_all_indices()
