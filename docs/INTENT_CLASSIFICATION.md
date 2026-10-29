# CampusAI: Intent Classification & Taxonomy

## 1. Hierarchical Intent Taxonomy
The taxonomy is structured across three levels:
- **Level 1 — Academic Domain:**
  - `curriculum`: Degree requirements, semester courses, credits, course codes, comparisons.
  - `syllabus`: Unit details, topics, course outcomes, textbook references, lab practices.
  - `electives`: Professional electives, open electives, minor streams.
  - `examinations`: Timetables, assessment regulations, academic calendars.
  - `campus_support`: General greetings, conversational thanks, out-of-scope filtering, clarifications.

- **Level 2 — Active Intent Classes:**
  1. `course_code`
  2. `course_credits`
  3. `semester_subjects`
  4. `unit_syllabus`
  5. `full_syllabus`
  6. `course_prerequisites`
  7. `course_comparison`
  8. `textbook_references`
  9. `minor_stream_list`
  10. `degree_total_credits`
  11. `academic_calendar`
  12. `greeting`
  13. `thanks`
  14. `out_of_scope`
  15. `clarification` (Abstention / Low-Confidence routing)

- **Level 3 — Slot & Entity Extraction:**
  - `department` (e.g., `CSE`, `IT`, `ECE`)
  - `course_name` (e.g., `Operating Systems`, `Data Structures`)
  - `course_code` (e.g., `241CS003`)
  - `semester` (e.g., `3`, `5`, `8`)
  - `course_unit` (e.g., `1`, `2`, `3`)
  - `credits`

## 2. Model Performance Comparison

| Model Architecture | Precision | Recall | Macro F1 | Accuracy | Latency |
|---|---|---|---|---|---|
| **TF-IDF + Multinomial Logistic Regression** (Active) | **0.912** | **0.884** | **0.891** | **98.55%** | **< 2 ms** |
| Zero-Shot Transformer Baseline | 0.820 | 0.795 | 0.805 | 87.20% | 85 ms |

## 3. Ambiguity & Low-Confidence Abstention
- If the predicted class probability falls below the calibrated threshold ($T = 0.30$), the query is routed to `clarification`.
- If an entity has multiple interpretations (e.g., "DS" can mean Data Structures or Data Science), the system returns a structured multi-choice clarification message without guessing silently.
