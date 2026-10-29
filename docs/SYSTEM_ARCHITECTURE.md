# CampusAI: System Architecture

## 1. Architectural Style
CampusAI is engineered as a **modular monolith** with decoupled service interfaces. The design avoids the operational overhead of fragmented microservices while maintaining clean boundaries between:
- Ingestion Pipeline (PyMuPDF layout extraction and schema validation).
- Knowledge Database (PostgreSQL 18-table normalized relational schema).
- Search & Retrieval Service (BM25 sparse index, Dense vector search, RRF, Cross-Encoder).
- NLP Understanding Service (Language ID, query normalization, intent classification, entity extraction, multi-intent decomposition).
- Conversational RAG Generation Service (Prompt engineering with evidence isolation, citation validation, multi-provider LLM adapters).
- Application API Service (FastAPI REST endpoints, JWT authentication, PyMuPDF PDF page streaming).
- Frontend Web Interface (React 19, TypeScript, Vite, Tailwind CSS, Glassmorphic UI).

## 2. High-Level System Architecture Diagram

```
[ Student / Administrator ]
            │
            ▼
┌────────────────────────────────────────────────────────┐
│             React / TypeScript Web Client              │
│  - Modern Glassmorphic Dark UI (Tailwind CSS)          │
│  - Real-Time Chatbot with Citations & Source Viewer    │
│  - Academic Course Catalog & Semester Explorer         │
│  - Cross-Branch Compare & Admin Conflict Audit Portal  │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP / JSON / Streams
                            ▼
┌────────────────────────────────────────────────────────┐
│             FastAPI Application Layer                  │
│  - Security & JWT Authentication (Argon2 / SHA-256)   │
│  - Academic & Course Endpoints                         │
│  - Streaming Chat Endpoint (/api/v1/chat)              │
│  - Source Page Image Streamer (PyMuPDF Page Rendering) │
│  - Extraction Issues & Conflict Resolution Controller  │
└───────────────────────────┬────────────────────────────┘
                            │
            ┌───────────────┴───────────────┐
            ▼                               ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│   PostgreSQL Engine      │    │  Information Retrieval   │
│  - 18 Normalized Tables  │    │  - BM25 Inverted Index   │
│  - 569 Courses           │    │  - all-MiniLM-L6-v2      │
│  - 583 Syllabus Units    │    │  - Reciprocal Rank Fusion│
│  - 1,273 Book Citations  │    │  - Cross-Encoder Rerank  │
│  - 23 Logged Discrepancies│    │  - 1,039 Indexed Chunks │
└──────────────────────────┘    └─────────────┬────────────┘
                                              │
                                              ▼
                                ┌──────────────────────────┐
                                │   Conversational RAG     │
                                │  - Evidence Isolation    │
                                │  - Citation Verification │
                                │  - Gemini/OpenAI/Ollama  │
                                └──────────────────────────┘
```

## 3. Communication Patterns
- **Synchronous REST:** Fast metadata discovery, course lookups, and authentication.
- **Asynchronous / Streaming Response:** Streaming question answering with real-time token emission.
- **Source Inspection:** Direct page rendering of original PDF pages via PyMuPDF rendered as PNG images directly to the client modal.
