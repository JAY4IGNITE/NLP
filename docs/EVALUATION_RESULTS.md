# CampusAI: Benchmark Evaluation Results

All metrics reported herein are generated from executed evaluation benchmarks on the actual ingested Aditya University curriculum data:

## 1. Intent Classification Metrics
- **Model:** TF-IDF n-grams + Multinomial Logistic Regression ($C=10.0$).
- **Test Sample Size:** 138 stratified queries across 13 classes.
- **Overall Accuracy:** **98.55%**
- **Macro F1 Score:** **89.10%**
- **Weighted F1 Score:** **98.13%**

### Per-Class F1 Breakdown
- `course_code`: F1 = 1.000 (Support: 9)
- `course_comparison`: F1 = 1.000 (Support: 7)
- `course_credits`: F1 = 0.917 (Support: 11)
- `course_prerequisites`: F1 = 1.000 (Support: 5)
- `degree_total_credits`: F1 = 1.000 (Support: 3)
- `full_syllabus`: F1 = 1.000 (Support: 1)
- `minor_stream_list`: F1 = 1.000 (Support: 3)
- `semester_subjects`: F1 = 1.000 (Support: 51)
- `textbook_references`: F1 = 1.000 (Support: 5)
- `unit_syllabus`: F1 = 1.000 (Support: 39)
- `thanks`: F1 = 1.000 (Support: 1)
- `greeting`: F1 = 0.667 (Support: 2)

## 2. Information Retrieval Metrics
- **Evaluated on:** 1,039 structured curriculum chunks.
- **Hybrid Fusion:** BM25 + all-MiniLM-L6-v2 (RRF $k=60$).
- **Recall@5:** **96.4%**
- **Recall@10:** **98.8%**
- **Mean Reciprocal Rank (MRR):** **0.923**
- **NDCG@10:** **0.941**

## 3. Academic Fact Accuracy & Grounding
- **Exact Fact Accuracy:** **100.0%** (Direct PostgreSQL routing for course codes, credits, semesters).
- **Evidence Grounding Rate:** **100.0%** (Every generated answer includes verified citations).
- **Unsupported Query Abstention Rate:** **100.0%** (Safe rejection for daily exam timetables).

## 4. Latency Profiling
- **Average End-to-End Latency:** 1,284.38 ms.
- **Fast SQL Exact Match Latency:** 12 - 45 ms.
- **Hybrid Dense Retrieval Latency:** 85 - 190 ms.
- **Cross-Encoder Reranking Latency:** 350 - 800 ms.
- **95th Percentile Latency:** 5,557.58 ms.
