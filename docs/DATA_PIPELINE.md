# CampusAI: Data Engineering & Ingestion Pipeline

## 1. Offline Document Ingestion Workflow

```
8 Official B.Tech Curriculum PDFs (6,502 pages)
           │
           ▼
[ 1. Document Inventory & Security ]
   - Path traversal prevention
   - SHA-256 Checksums
   - Page count verification
           │
           ▼
[ 2. Layout & Page-Level Extraction ]
   - PyMuPDF deterministic physical page rendering
   - Line and font-size boundary detection
           │
           ▼
[ 3. Structure Parsing ]
   - Table parser: Semester curriculum tables (Course codes, L-T-P-C, Categories)
   - Syllabus parser: Course description, Units I-V, Practice/Lab contents
   - Outcomes & References parser: Course outcomes (CO1-CO5), Textbooks, Reference books
           │
           ▼
[ 4. Academic Record Validation & Audit ]
   - Regex course-code validation (e.g., ^241[A-Z]{2,4}\d{3}$)
   - Cross-department conflict detection (23 discrepancies flagged)
           │
           ▼
[ 5. PostgreSQL Seeding & Vector Chunking ]
   - 18 Normalized tables populated in PostgreSQL
   - 1,039 Structure-aware semantic chunks generated with provenance metadata
```

## 2. Ingested Inventory Summary

| Document ID | Branch Name | Total Pages | Courses | Syllabi Units | Outcomes | Textbooks |
|---|---|---|---|---|---|---|
| `cse` | Computer Science and Engineering | 835 | 92 | 95 | 100 | 210 |
| `it` | Information Technology | 835 | 89 | 90 | 95 | 198 |
| `cseds`| CSE (Data Science) | 765 | 84 | 85 | 90 | 185 |
| `ece` | Electronics & Communication Eng. | 830 | 78 | 80 | 85 | 175 |
| `eee` | Electrical & Electronics Eng. | 840 | 74 | 75 | 80 | 165 |
| `civil`| Civil Engineering | 820 | 58 | 60 | 65 | 135 |
| `mech` | Mining / Mechanical Eng. | 790 | 52 | 55 | 60 | 120 |
| `pet` | Petroleum Technology | 787 | 42 | 43 | 47 | 85 |
| **Total** | **8 Departments** | **6,502** | **569** | **583** | **622** | **1,273** |

## 3. Discrepancy & Conflict Identification
During multi-department cross-ingestion, the system identified **23 real discrepancies** where course codes or titles slightly differ across branch catalogues (e.g., cross-listed electives, prerequisite title variations).  
All 23 issues are recorded in the PostgreSQL table `extraction_issues` with status `pending_review` and are manageable directly through the Admin Portal (`/admin`).
