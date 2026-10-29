# CampusAI: REST API Specification

Base URL: `http://localhost:8000/api/v1`  
Interactive OpenAPI Documentation: `http://localhost:8000/docs`

## 1. Core Endpoints

### Academic Endpoints
- `GET /departments`: Lists all 8 engineering departments with mission/vision.
- `GET /courses`: Searches courses with filters: `department_code`, `search`, `category`, `limit`.
- `GET /courses/{id}`: Detailed course record with units, outcomes, and textbooks.
- `GET /semesters`: Returns semester curriculum table with total credits and courses.

### Conversational AI Endpoints
- `POST /chat`:
  - Request: `{"query": string, "session_id": string, "department_code": string, "language_preference": string}`
  - Response: `{"answer": string, "intent": string, "domain": string, "citations": [...], "source_type": string, "is_grounded": bool}`
- `POST /chat/feedback`: Submits student rating (1-5 stars) and comments.

### Source Inspection Endpoint
- `GET /sources/{doc_id}/page/{page_num}?format=image`:
  - Renders physical PDF page directly as a PNG image stream (`image/png`) using PyMuPDF.

### Authentication & Admin Endpoints
- `POST /auth/login`: Issues Bearer JWT token (`{"username": string, "password": string}`).
- `GET /admin/extraction-issues`: Lists curriculum conflicts across departments.
- `PATCH /admin/extraction-issues/{id}`: Resolves or suppresses an issue (Requires Admin JWT).
- `GET /admin/evaluations`: Returns live evaluation benchmark metrics.
