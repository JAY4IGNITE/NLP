# CampusAI: Operational Limitations & Responsible AI Boundaries

## 1. Verified Boundaries
1. **Scope Restriction to Curriculum Regulation 2024 (Version 3.0):**
   - The knowledge base is strictly built from the eight official 2024 Version 3.0 B.Tech engineering curriculum documents.
   - Older regulation batches (e.g., AR20, AR22) or postgraduate degrees (M.Tech, MBA) are not currently indexed in this baseline release.

2. **Daily Assessment Schedules & Student Records:**
   - Real-time daily examination timetables, classroom room numbers, and confidential student grades are intentionally excluded from static curriculum ingestion to preserve student privacy and prevent stale schedule dissemination.
   - The system performs automated safe abstention and directs students to the live official portal.

3. **Multi-Department Cross-Catalog Conflicts:**
   - Where syllabus descriptions or prerequisite titles differ across branches for cross-listed courses, the system flags these as extraction issues (23 detected) for administrative review rather than silently picking one branch arbitrarily.

4. **Hardware & Latency Considerations:**
   - Full Cross-Encoder reranking introduces 300–800 ms of CPU inference time per query. When running on edge or low-resource hardware, Cross-Encoder reranking can be toggled via `CAMPUSAI_ENABLE_RERANK=false`, relying on fast sub-millisecond RRF fusion.
