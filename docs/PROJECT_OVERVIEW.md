# CampusAI: Project Overview

## 1. Institutional Context
- **Institution:** Aditya University, Surampalem, Kakinada District, Andhra Pradesh, India.
- **Campus Portal:** [https://www.adityauniversity.in/](https://www.adityauniversity.in/)
- **Academic Framework:** B.Tech Academic Regulation 2024, Version 3.0.

Aditya University offers undergraduate engineering programs across diverse specializations:
1. Computer Science and Engineering (CSE)
2. Information Technology (IT)
3. Computer Science and Engineering (Data Science) [CSE-DS]
4. Electronics and Communication Engineering (ECE)
5. Electrical and Electronics Engineering (EEE)
6. Civil Engineering (CE)
7. Mechanical / Mining Engineering (MIN)
8. Petroleum Technology (PT)

## 2. Core Problem & Mission
Each engineering department maintains voluminous curriculum PDFs spanning 750 to 850 pages per branch (totalling over 6,500 pages). Students and faculty previously had to search manually through hundreds of PDF pages to discover prerequisite chains, semester credit breakdowns, course codes, laboratory hours, or unit-wise syllabus topics.

Furthermore, general-purpose LLM interfaces frequently hallucinate critical course codes, credit allocations, and semester schedules because they treat academic records as fluid narrative text rather than verified institutional contracts.

**CampusAI's mission:**
Develop an intelligent conversational platform capable of answering academic questions accurately by retrieving evidence from university-approved documents and structured academic records with verifiable source citations down to the official PDF page.

## 3. Scope Boundaries
- **In-Scope:**
  - Curriculum structures (Semesters I through VIII).
  - Course codes, titles, L-T-P-C distributions, course categories (PC, BS, HS, ES, PE, OE).
  - Detailed syllabus units (Units I to V), laboratory/practice contents.
  - Course outcomes and textbook/reference book citations.
  - Multi-intent queries, cross-branch semester comparisons, and Telugu multilingual queries.
  - Official university calendar and examination notices via verified website ingestion.
- **Explicitly Out-of-Scope (Safe Abstention):**
  - Unverified live daily assessment timetables or personalized student grades (routed safely to the official student portal).
  - Non-academic general web queries (politely rejected with domain boundaries).
