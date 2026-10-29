# CampusAI: Frontend Web Application Architecture

## 1. Technology Stack
- **Framework:** React 19 + TypeScript + Vite.
- **Styling:** Vanilla CSS + Tailwind CSS (v4) with custom glassmorphism design tokens in `frontend/src/index.css`.
- **Icons:** `lucide-react`.
- **HTTP Client:** Native Fetch with typed responses in `frontend/src/api.ts`.

## 2. Component Structure
- `Navbar`: Sticky glassmorphic header with live status badge (`v3.0 Live`), brand identity, navigation tabs, and login/logout controls.
- `ChatView`: Full conversational interface with suggested prompts, branch pills, message bubbles, Markdown formatting, citation badges, source page preview triggers, and student feedback.
- `ExploreView`: Searchable course catalog with instant debounce search, department pills, and category filters.
- `SemesterView`: Semester curriculum explorer displaying official semester credit stats, course tables, and direct PDF source buttons.
- `CompareView`: Side-by-side branch curriculum comparison highlighting shared core foundations vs department-specific courses.
- `AdminView`: Academic operations dashboard with Document Inventory (8 PDFs, 6,502 pages), Discrepancy Audit Log (resolving/suppressing conflicts), and ML Benchmarks.
- `SourceModal`: Direct official PDF page image viewer rendered from PyMuPDF.
- `CourseModal`: Comprehensive course drawer showing L-T-P-C, all 5 syllabus units, lab exercises, course outcomes, and textbook lists.
- `LoginModal`: Admin authentication modal with JWT persistence in localStorage.
