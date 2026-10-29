# CampusAI: Machine Learning and NLP Architecture

## 1. NLP Pipeline Stages

```
User Query
    │
    ▼
[ 1. Language Identification ]  --> Detects English, Telugu script, or Telugu-English mixed text
    │
    ▼
[ 2. Contextual Query Rewriting] --> Resolves anaphoric expressions ("What about Unit II?", "same for IT")
    │
    ▼
[ 3. Query Normalization ]      --> Expands academic abbreviations, standardizes Roman numerals, strips excess whitespace
    │
    ▼
[ 4. Academic Entity Extractor ] --> Extracts course code, course title, semester, department, unit number
    │                                (Detects ambiguity e.g. "DS" -> Data Structures vs Data Science)
    ▼
[ 5. Intent Classifier ]        --> Hierarchical intent classifier (Domain + 13 Intent Classes)
    │
    ▼
[ 6. Multi-Intent Decomposer ]  --> Identifies complex queries ("List Sem 6 courses with credits and prerequisites")
    │
    ▼
[ 7. Intelligent Orchestration ] --> Exact facts -> PostgreSQL; Complex/Syllabus -> Hybrid Vector Search
```

## 2. Model Implementations & Selection
1. **Language Identification (`campusai/nlp/language_id.py`):**
   - Unicode block detection for Telugu characters (`\u0c00-\u0c7f`).
   - Keyword lexical triggers for Romanized Telugu transliterations (`enti`, `cheppandi`, `unnayi`, `kavali`, `lo`).
   - High-speed zero-dependency inference with confidence scoring.

2. **Hierarchical Intent Recognition (`campusai/nlp/intent_classifier.py`):**
   - Word and character n-gram (1-3) TF-IDF vectorization with 5,000 features.
   - Multinomial Logistic Regression ($C=10.0$) with class-balanced weighting.
   - Evaluated Performance: **98.55% accuracy**, **89.10% Macro F1** across 13 classes.
   - Confidence thresholding ($T=0.30$) with automated clarification routing.

3. **Dense Vector Embeddings (`campusai/retrieval/dense_retriever.py`):**
   - Model: `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional dense semantic vectors).
   - Generates normalized cosine embeddings over 1,039 structured chunks with department and course metadata tags.

4. **Cross-Encoder Reranking (`campusai/retrieval/reranker.py`):**
   - Model: `cross-encoder/ms-marco-MiniLM-L-6-v2`.
   - Re-scores fused top-15 candidate passages through pairwise query-document cross-attention.
