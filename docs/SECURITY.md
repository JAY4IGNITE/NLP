# CampusAI: Security, Privacy & Safety Engineering

## 1. Security Architecture Controls
1. **Evidence Isolation & Indirect Prompt Injection Defense:**
   - Retrieved PDF text is isolated inside designated Markdown data delimiters.
   - The LLM prompt explicitly instructs the model to ignore instructions inside retrieved data blocks.

2. **Source Inspection & Path Traversal Protections:**
   - Document page rendering (`/api/v1/sources/{id}/page/{num}`) strictly maps document identifiers against the verified manifest whitelist (`DOC-CSE`, `DOC-IT`, etc.).
   - Path traversal attempts (e.g., `../../etc/passwd` or `..\\..\\windows`) are rejected with `400 Bad Request`.

3. **Authentication & Authorization:**
   - JWT tokens with SHA-256 HMAC and configurable expiration.
   - Role-Based Access Control (RBAC): Public access for student query endpoints, authenticated administrator access for issue resolution (`/admin/extraction-issues/{id}`).
   - Password hashing with salted cryptographic hash functions.

4. **Privacy & Data Minimization:**
   - Chat sessions can be operated anonymously using client session IDs.
   - Personal student IDs or passwords are never stored in plain text or logged in server telemetry.
