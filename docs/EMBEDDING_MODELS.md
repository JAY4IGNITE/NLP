# CampusAI: Embedding Models & Semantic Representation

## 1. Dense Embedding Architecture
- **Model:** `sentence-transformers/all-MiniLM-L6-v2` (with interchangeable adapter support for `BAAI/bge-m3`).
- **Embedding Dimension:** 384 dimensions.
- **Normalization:** L2 unit norm ($||\vec{v}||_2 = 1.0$), enabling cosine similarity computation via dot product.
- **Chunking Strategy:** 1,039 structure-aware chunks. Rather than slicing arbitrary character windows, chunks are bounded by syllabus units, semester table sections, and course descriptions. Each chunk embeds structured metadata:
  ```
  [Department: CSE] [Course: 241CS009 Operating Systems] [Unit: III]
  Process Synchronization: The critical-section problem, Peterson's Solution,
  synchronization hardware, Mutex locks, Semaphores, Classic problems of synchronization.
  ```

## 2. Multi-Department Index Persistence
- Vectors are stored in `data/indices/dense_embeddings.npy` along with chunk metadata in `data/indices/dense_metadata.json`.
- Metadata filtering allows department-specific pre-filtering or unrestricted university-wide retrieval.
