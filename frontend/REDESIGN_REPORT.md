# CampusAI redesign — implementation and verification report

Date: 21 October 2026 (Asia/Calcutta)

## A. Design transformation

The existing frontend now uses a navy academic workspace with restrained translucent surfaces, thin highlights, locally served Manrope/Sora typography, a compact utility header, and floating navigation. All five views and all three modals were redesigned directly in the existing application.

Chat has a department rail, a concise welcome, a multiline composer with language selection, source-grounding labels, expandable response metadata, copy and feedback controls. There are no demo or suggested queries. New conversation appears only after a conversation begins. The chat stays mounted when navigating between sections. Mobile reserves separate space for the composer and dock.

The follow-up simplification removes repeated brand/source messaging, footer slogans, and dock tooltips that duplicated visible labels. Catalog titles are the single entry to course details; the separate source action opens the original document. Comparison totals appear once per department, with the credit difference in the summary. Source page metadata appears only in the viewer header.

The catalog uses the official ReactBits SpotlightCard with low-intensity indigo illumination. Semester navigation presents eight numbered academic steps. Comparison retains exact course-code matching and adds a derived credit difference. Administration shows actual document registry and evaluation responses instead of hardcoded claims. Dialogs use the browser's native modal layer to contain focus and support nested source inspection.

## B. Brand identity

The original symbol combines an open C, two book/path strokes, and one connected node. It does not reuse the university's mark.

Assets in `public/brand/`:

- `logo-dark.svg`: primary horizontal mark and wordmark for dark backgrounds.
- `logo-light.svg`: horizontal light-background variant.
- `wordmark.svg`: horizontal lockup.
- `icon.svg`: compact indigo mark.
- `icon-light.svg`: compact light-background mark.
- `icon-mono.svg`: one-color mark.
- `app-icon-192.svg`, `app-icon-512.svg`: sized application icons.

Additional assets: `public/favicon.svg`, `public/site.webmanifest`. The rendered header uses `ui/CampusLogo.tsx` and locally served type, with a brief 650 ms path reveal.

## C. Modified existing files

- `src/App.tsx`
- `src/index.css`
- `src/components/Navbar.tsx`
- `src/components/ChatView.tsx`
- `src/components/ExploreView.tsx`
- `src/components/SemesterView.tsx`
- `src/components/CompareView.tsx`
- `src/components/AdminView.tsx`
- `src/components/CourseModal.tsx`
- `src/components/SourceModal.tsx`
- `src/components/LoginModal.tsx`
- `index.html`
- `vite.config.ts`
- `package.json`
- `package-lock.json`
- `public/favicon.svg`
- `README.md`

Added files: the brand assets above, `src/components/ui/` components below, `src/components/reactbits/SpotlightCard.tsx`, its CSS and license, `qa/verify.mjs`, `qa/contract-hashes.json`, this report, and generated QA screenshots/results.

## D. Reusable components

- `CampusLogo`: original vector identity and initial reveal.
- `FloatingDock` and its internal `DockItem`: spring magnification, adjacent icon influence, active states, arrow-key focus movement, mobile touch navigation.
- `ModalFrame`: accessible native dialog, explicit Tab/Shift+Tab wrapping, Escape, background inertness, focus restoration, backdrop dismissal, and stacked course/source viewers.
- `SpotlightCard`: official ReactBits component used for actual course cards.

## E. ReactBits integration and licensing

Used **SpotlightCard**, TypeScript + plain CSS, downloaded from the [official repository](https://github.com/DavidHDev/react-bits/tree/main/src/ts-default/Components/SpotlightCard). Its [MIT + Commons Clause license](https://github.com/DavidHDev/react-bits/blob/main/LICENSE.md) is retained verbatim in `src/components/reactbits/LICENSE.md`.

Local adaptations: synchronize settings refs after render, disable pointer effects for reduced motion/coarse pointers, skip hidden-document frame work, and apply CampusAI surface tokens. Intensity is 0.06, proximity 0, ambient animation off, click flare off. There are no WebGL canvases.

The [official Dock](https://reactbits.dev/components/dock) was inspected. The shipped dock is a smaller custom Motion equivalent tailored to the existing tab callbacks, not a claim to have vendored ReactBits Dock. No invented ReactBits npm package or component import is used.

## F. Motion system

- Dock: transform-only springs, stiffness 280, damping 24, mass 0.6; 22 px baseline icons with restrained magnification and neighbor influence.
- Logo: initial path drawing and scale/fade settling, approximately 650 ms.
- Views/messages: short opacity and 7 px vertical entrances, 250–300 ms.
- Dialogs: 240 ms opacity/scale/translation entrance; immediate native close and focus restoration.
- Cards: restrained hover elevation and border changes.
- Loading: existing skeleton pulses and a small thinking indicator; no artificial response delays.
- Reduced motion: CSS cancels decorative transforms/animations, including a dock icon already enlarged when the preference changes. Pointer spotlight is disabled. The ambient background is static.

## G. Compatibility

Verified installed versions before implementation and preserved them:

| Dependency | Version |
|---|---|
| React / React DOM | 19.3.1 |
| TypeScript | 6.0.3 |
| Vite | 8.3.4 |
| Tailwind CSS | 4.3.3 |
| Lucide React | 1.60.0 |
| Oxlint | 1.89.0 installed; original package range remains ^1.88.0 |

Added Motion 14.5.0, Fontsource Manrope/Sora 5.3.0, and the matching `@tailwindcss/vite` 4.3.3 plugin. Browser QA uses Playwright 1.64.1 and axe-core Playwright 4.14.0. No existing framework dependency was downgraded.

The initial build exposed unprocessed `@theme`/`@tailwind` directives. Adding the [documented Tailwind Vite plugin](https://tailwindcss.com/docs/installation/using-vite) corrected the existing styling pipeline. Motion was installed using its [official React integration](https://motion.dev/docs/react-installation).

## H. Identifier preservation checklist

Existing application identifiers renamed: **zero**.

Preserved component names and exports: `App`, `Navbar`, `ChatView`, `ExploreView`, `SemesterView`, `CompareView`, `AdminView`, `CourseModal`, `SourceModal`, `LoginModal`.

Preserved existing state/setter names, including `activeTab`, `selectedCourseId`, `sourceModal`, `isLoginOpen`, `user`, `messages`, `input`, `selectedDept`, `loading`, `sessionId`, `departments`, `searchQuery`, `selectedCategory`, `courses`, `selectedSem`, `semesterData`, `dept1`, `dept2`, `semesterNum`, `data1`, `data2`, `activeSubTab`, `issues`, `metrics`, `_loading`, `resolvingId`, `resolutionNotes`, `actionSuccess`, `course`, `username`, `password`, and `error`.

Preserved existing callback/function identifiers and props, including `handleSend`, `handleFeedback`, `scrollToBottom`, `handleViewSource`, `handleLoginSuccess`, `handleLogout`, `loadData`, `handleResolveIssue`, `handleSubmit`, `onViewSource`, `onSelectCourse`, `onClose`, `onOpenLogin`, and `onLoginSuccess`.

Preserved domain constants and comparison variables: `DEPARTMENTS`, `categories`, `filteredCourses`, `semesters`, `codes1`, `codes2`, `commonCodes`, `uniqueToDept1`, `uniqueToDept2`, `documents`, and `imageUrl`. New state is limited to presentation/feedback/loading controls and consuming the existing document registry. Following the user's explicit request to remove demo queries, the obsolete `SUGGESTED_PROMPTS` constant and its rendering/styles were removed; no identifier was renamed.

## I. Backend and data compatibility

`src/api.ts` and `src/types.ts` were not edited. All existing method names, endpoints, HTTP verbs, request/response shapes, exported interfaces, and fields remain intact. Recorded SHA-256 values are in `qa/contract-hashes.json`.

- Catalog keeps its 250 ms debounce, existing limit, department query, and category filter logic.
- Comparison still matches exact course codes, not titles.
- PDF URLs still come from `api.getSourcePageImageUrl(docId, pageNum)` with the original parameters.
- Login still uses the same callback and the same `campusai_user` / `campusai_token` keys.
- Chat still uses `api.sendChat`; the existing optional language parameter now has a visible selector.
- Feedback still uses the same method and rating values, with added success/error presentation.
- The admin document registry consumes the already-existing `GET /api/v1/admin/documents`. Its records are mapped to the existing presentation property names `id`, `name`, `file`, `pages`, and `status`.
- No backend source files were changed. No fake application data was introduced.

## J. Verification

Initial baseline: `npm run build` succeeded but reported unprocessed Tailwind directives. `npm run lint` exited successfully with nine warnings. No frontend test script existed initially.

Final verification:

- `npm run build`: passed (TypeScript project build and Vite production bundling).
- `npm run lint`: exit code 0, zero errors, nine warnings in the existing state/effect/catch patterns noted below.
- `npm run test:e2e`: **37 passed, 0 failed**.
- axe scans: **15 scanned states, 0 violations** for the selected WCAG A/AA rules.
- Browser uncaught runtime errors: **0**.
- Existing API tests: **7 passed**.
- SVG XML parsing: passed for all SVG assets.
- API/type file hash check: passed; neither public-contract file was edited.

Machine-readable results are in `qa/verification.json`. Commands:

```sh
npm run build
npm run lint
npm run test:e2e
```

Existing API suite from the repository root:

```powershell
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
python -m pytest tests/test_api.py -q
```

The API suite passed all seven tests. An earlier attempt combining API and website tests stalled during initialization in the restricted environment and was stopped; the website suite is not claimed as passing. The API suite then passed outside the isolated sandbox using local model caches.

Browser verification uses the actual local API for successful flows. It checks chat payloads, responses, citations, feedback, clear chat, state retention, title/code search, department/category filtering, all course tabs, nested source dialogs, semester switching, comparison selectors, actual login, registry/metrics rendering, mobile layouts, keyboard containment, error states, source retry, and reduced motion. Request failures are deliberately simulated only inside the isolated test browser.

The simplified production build includes approximately 438.24 kB JavaScript (135.15 kB gzip) and 59.62 kB CSS (15.14 kB gzip), plus locally served font subsets. No Core Web Vitals or physical-device battery claim is made.

## K. Visual verification

Rendered screenshots were captured in Chromium and visually inspected. Desktop checks covered Chat, Explore, Semesters, Compare, Admin documents/issues/metrics, Course units/outcomes/books, Source, and Login. Responsive captures covered all five views at:

- 1440 × 1000
- 1280 × 800
- 768 × 1024
- 390 × 844
- 320 × 740

Course, Source, and Login dialogs also have 390 × 844 captures. Empty/error states were captured for the catalog, course details, source viewer, and login. Screenshots live in `qa/screenshots/`. The automated layout checks assert no horizontal document overflow and no chat composer/dock intersection.

## L. Known limitations and separate follow-ups

1. **Existing admin integration mismatches:** all 23 live issue records use `pending_review`, while the existing UI counts and exposes resolution controls only for `pending`. Login also returns `access_token`, while `handleResolveIssue` expects `user.token`. These domain values and authentication semantics were preserved under the brief. Real resolve/suppress mutations were not exercised. A separate correction should reconcile issue statuses and the token field, alongside logout token clearing and prefilled development credentials.
2. **Existing data quality:** some extracted courses contain fragmented textbook references; some cross-department semester results contain identical course sets. The UI shows those values faithfully. The title search returned Operating Systems under CSE-DS, not CSE, and tests were adjusted to the actual data.
3. **Existing category list:** the PC/BS/ES/etc. filter constants are preserved even though some current records use MCC/AEC/SEC categories. Broadening the domain filter vocabulary is a separate data/UI behavior change.
4. **Lint warnings:** nine warnings remain around existing state-in-effect patterns, unused catch variables, and the semester effect dependency. No lint errors; no broad state refactoring was done.
5. **Deployment unchanged:** the API URL is still hardcoded to localhost in the original client. This is a local implementation, not a production deployment.
6. **Browser coverage:** Chromium desktop/mobile emulation only; no physical iOS/Android, Safari, Firefox, or screen-reader hardware certification.
7. **Git:** work is on `codex/campusai-glass-redesign`. The repository began without a commit and with all project files untracked; unrelated files were not staged or committed.
