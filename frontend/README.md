# CampusAI frontend

A React and TypeScript academic helpdesk with an ink-black default theme, silver glass artwork, restrained blue accents, and a floating desktop dock. The landing page uses large centered typography, original material studies, image-led course and semester links, and a working academic question form. Navigation and brand marks use a consistent Lucide line style. The visual direction draws on the spacing, hierarchy, and material presentation of Apple Developer Design.

See [VISUAL-DIRECTION.md](VISUAL-DIRECTION.md) for artwork provenance, generation prompts, asset paths, and design decisions.

## Run

```sh
npm install
npm run dev -- --host 127.0.0.1 --port 5174
npm run build
npm run lint
```

The API client expects the existing FastAPI server at `http://localhost:8000/api/v1`. The landing page and navigation work independently; academic records and real assistant answers require the backend.

## Routes and components

- The default URL and `#home` open the new landing page. Its question form and suggestions send the selected question to the assistant.
- `#chat`, `#explore`, `#semesters`, `#compare`, and `#admin` support direct navigation and browser history.
- `App.tsx` coordinates navigation and modals. Chat stays mounted so conversations survive navigation. Its input resizes when the view becomes active.
- `components/LandingView.tsx` contains the introduction, working question form, academic tool links, and source-verification explanation.
- `components/Navbar.tsx` places the desktop dock at the bottom with spring magnification, click bounce, hover labels, and context-menu shortcuts. Right-click an icon or focus it and press Arrow Up to open its menu. A touch-friendly mobile menu, theme switching, and account access remain available. Main content reserves room for the dock, including the chat composer.
- `src/index.css` defines shared semantic colors and the base layout. `src/appearance.css` defines glass materials, navigation, and reduced-motion behavior. `src/landing.css` defines the editorial landing composition and responsive layouts. Components use semantic color tokens across both themes.
- `components/ui/ModalFrame.tsx` retains native dialog focus containment, Escape dismissal, and focus restoration.

Dark is the default. On first use of the graphite palette, the previous appearance resets once to dark, as requested for this redesign. Subsequent light/dark choices persist under `campusai_theme`, with `campusai_palette=graphite` marking the migration.

## Verify the redesign

```sh
npm run test:redesign
```

This Playwright suite starts and stops an isolated preview on port 5182. It uses deterministic API fixtures and does not write to the backend. It checks landing-page question submission, conversation retention, browser history, course search and details, semester and comparison controls, sign-in focus restoration, mobile navigation, and layout at 1440, 900, 768, 390, and 320 pixels in both themes. Axe audits cover desktop/mobile views and course/sign-in dialogs.

Set `CAMPUSAI_CHROMIUM` to select a browser executable, or install Playwright's default browser with `npx playwright install chromium`. Results and screenshots are written to `qa/redesign/report.json` and `qa/redesign/`.

The older `test:e2e` suite targets an earlier navigation structure and is retained for reference. Use `test:redesign` for the current UI. The fixture suite verifies frontend behavior; it does not certify backend answer accuracy or administrator mutations.

## Chat layout and motion

The assistant opens with a centered welcome, a single multiline composer, and compact suggested questions. The academic sidebar is collapsed initially and can be opened from the chat toolbar. Conversation mode keeps the composer at the bottom and presents answers without nested cards. Department selection, conversation retention, feedback, copy, and speech controls remain connected.

Motion includes staggered hero text, spring entrances and scroll reveals, restrained dock magnification and click bounce, dialog entrances, hover feedback, and a pointer-following reflection on the question panel. The reflection uses motion values so pointer movement does not render the React tree or move the form controls. There are no continuous decorative animation loops. Response details display service metadata and elapsed time; missing grounding information is treated as unconfirmed.

Reduced-motion preferences disable entrances, reflections, dock magnification, and bounce. Reduced-transparency preferences and browsers without backdrop-filter receive opaque surfaces. Both themes preserve text contrast. Glass is strongest on navigation, the composer, and dialogs. Artwork is delivered as three optimized WebP files totaling approximately 340 KB.

With the local preview running on port 5180, run `node qa/motion-check.mjs` to check pointer reflections, dock magnification and bounce, pointer/keyboard menus, scroll reveals, reduced motion, composer clearance, loading status, and response metadata. `CAMPUSAI_PREVIEW` overrides that URL. Results are saved to `qa/redesign/motion-report.json`.
