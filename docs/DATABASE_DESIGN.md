# CampusAI: Academic Database Design & Schema

## 1. Relational Database Overview
The knowledge repository is modeled in PostgreSQL using SQLAlchemy declarative models across 18 normalized tables. The schema enforces foreign key constraints, composite unique indexes, and audit timestamps.

```
institutions
  └── departments
        ├── programs
        │     └── curriculum_versions
        │           ├── semesters
        │           │     └── course_offerings
        │           └── courses
        │                 ├── course_units
        │                 ├── course_outcomes
        │                 ├── course_prerequisites
        │                 ├── textbooks
        │                 └── course_references
        └── source_documents
              ├── source_pages
              ├── extraction_issues
              └── response_citations
```

## 2. Table Specifications
1. **`institutions`**: University name, official website, location, approval details.
2. **`departments`**: Code (CSE, IT, ECE, etc.), name, department vision, mission.
3. **`programs`**: Degree name (B.Tech, M.Tech), duration in years, minimum required credits.
4. **`curriculum_versions`**: Regulation year (2024), version (v3.0), effective batch (2024–2028), approval date.
5. **`semesters`**: Semester number (1 to 8), Roman numeral (I to VIII), total credits, total course slots.
6. **`courses`**: Course code (`241CS003`), title, category (`PC`, `BS`, `HS`, `ES`, `PE`, `OE`), credits, lecture hours, tutorial hours, practical hours, total contact hours, prerequisite narrative.
7. **`course_offerings`**: Association mapping a course to a semester slot within a department curriculum.
8. **`course_units`**: Unit number (1 to 5), Roman numeral (I to V), unit title, theory syllabus text, laboratory practice text, source page.
9. **`course_outcomes`**: Outcome code (`CO1` to `CO5`), descriptive competency statement.
10. **`textbooks`**: Book type (`Textbook` vs `Reference Book`), authors, title, publisher, edition, publication year.
11. **`course_prerequisites`**: Formal course-to-course prerequisite relationships.
12. **`source_documents`**: Document ID, branch, filename, SHA-256 checksum, page count, publication version.
13. **`source_pages`**: Page index, printed page number, extracted raw text, layout metadata.
14. **`extraction_issues`**: Audit log of cross-department discrepancies, status (`pending_review`, `resolved`, `suppressed`), resolution notes.
15. **`users`**: Administrative credentials, username, password hash (PBKDF2/Argon2), role (`admin`, `staff`, `student`).
16. **`chat_sessions`**: User or anonymous session ID, active department filter, language preference, created timestamp.
17. **`chat_messages`**: Role (`user`, `assistant`), message text, predicted intent, detected domain, grounded status.
18. **`response_citations`**: Verifiable citations attached to assistant answers, doc ID, page number, excerpt, relevance score.

## 3. SQL Retrieval Functions (`campusai/database/sql_retriever.py`)
- `get_course_by_code(code, dept_code)`
- `find_courses_by_name(name_query, dept_code)`
- `get_semester_courses(sem_num, dept_code)`
- `get_course_credits(course_identifier, dept_code)`
- `get_course_units(course_identifier, unit_number)`
- `compare_semester_courses(sem_num, dept_a, dept_b)`
