# PinnacleIQ — Project Memory File

> **Purpose:** Single source of truth for Claude sessions. Pick this up at the start of every session.
> **Last updated:** 2026-06-23 (session 3) | Active branch: `Researchagent_2306` | Main repo: `D:\Codebase\Pinnacle`

---
---

## 0. Development Workflow (ALWAYS FOLLOW)

**Rule 1 — All code changes go in `D:\Codebase\Pinnacle` only.**
Never edit the worktree or any other location unless explicitly asked.
User reviews code in VSCode from the local repo — changes elsewhere are invisible.

**Rule 2 — Update `memory.md` after every change.**

**Rule 3 — Git process: feature branch first, then main.**
- Create `feat/<name>` branch → commit work there
- Only merge to `main` when user explicitly asks to "check in the code"
- Never commit directly to `main`


## 1. What Is This Project?

**PinnacleIQ** — A multi-agent medical research portal for **Mankind Pharma**.
- Single-file HTML portal: `PinnacleIQ_Portal.html` (served at `http://127.0.0.1:8010/app`)
- FastAPI backend: `demo/backend/app.py` (port 8010)
- Real agent pipeline (unused in demo): `research_agent_system/`
- `react-app/` — **deleted** (legacy React frontend, removed 2026-06-19)

---

## 2. How to Run

```powershell
# Run from MAIN REPO (recommended — all fixes are here)
cd D:\Codebase\Pinnacle\demo\backend
python app.py

# OR use the one-click launcher from repo root:
cd D:\Codebase\Pinnacle
.\start_app.ps1

# Then open: http://127.0.0.1:8010/app
```

- Backend serves the HTML at both `/app` and `/portal`
- `start_app.ps1` handles port conflicts and UTF-8 encoding
- DB path is now **absolute** — always writes to `demo/backend/pinnacleiq_demo.db` regardless of CWD

---

## 3. Roles & Login Credentials

| Role | Email | Password | Access |
|------|-------|----------|--------|
| **Admin** | `admin@mankind.in` | Admin123 | Role switcher, all views |
| **MA (Medical Affairs)** | `prashant.agarwal@mankind.in` | Test | Research Agent, approve/reject content |
| **MA** (alt) | `anita.sharma@mankind.in` | Test | Same MA access |
| **MA** (alt) | `rohit.kumar@mankind.in` | Test | Same MA access |
| **PMT / BU Head** | `amit.verma@mankind.in` | Test | Today's Tasks, Occasion Hub, Content Library |
| **PMT** (any) | `rajesh.sharma@mankind.in` … `rahul.agarwal@mankind.in` | Test | Same PMT access |

**⚠️ Old credentials (`priya@mankind.in`, `jijo@mankind.in`) do NOT work** — those were from an earlier version. Use the emails above.

**Key mapping:** PMT == BU Head (same role). All passwords are `Test` except Admin (`Admin123`).

**Login mechanics (verified 2026-06-22):** Login is client-side against `USERS_DB` array in `PinnacleIQ_Portal.html` (~line 7442). Shared password is `const APP_PASSWORD = 'Test'`. A user can override it with a per-user `pwd:` field — the check is `password !== (user.pwd || APP_PASSWORD)`. `admin@mankind.in` carries `pwd:'Admin123'`. Other admin accounts `admin1@mankind.in`…`admin5@mankind.in` also exist (password `Test`).

---

## 4. Architecture

### Frontend (PinnacleIQ_Portal.html)
- Single-file SPA, no build step
- Hash-less routing via `showPage(id)` — renders page divs with class `on`
- All data is JS arrays (static) with some API calls for dynamic data
- CSS variables in `<style>` block; `.ov` = overlay/modal class, `.ov.on` = visible

### Backend (demo/backend/app.py)
- FastAPI on port 8010
- `mock_runner.py` — simulates LLM pipeline for demos without API keys
- `scheduler.py` — APScheduler daily jobs
- SQLite DB: `pinnacleiq_demo.db`
- Run with `python app.py` (NOT uvicorn CLI; `reload=False`)

---

## 5. Screens & Features Built

### PMT / BU Head Screens

#### Today's Tasks (`showPage('today')`)
- **Status:** ✅ Fully working
- 9 static tasks: 4 Urgent, 3 Recommended, 2 Upcoming
- Demo date frozen at **4 May 2026** (`DEMO_DATE = '2026-05-04'`)
- Tab filters: All / Urgent / Recommended / Upcoming / Done
- Progress bar, done counter, summary text
- Task cards with doctor info, action buttons (Send Birthday Wish, Send First Paper, Re-engage, etc.)
- Key JS vars: `TODAY_TASKS`, `TODAY_DONE`, `TODAY_TAB`, `renderToday()`, `setTodayTab()`

#### Occasion Hub (`showPage('occasions')`)
- **Status:** ✅ Fully working (fixed in session 2026-06-19)
- 14 occasions: **10 medical** + **4 national** (Doctors' Day is `national`, NOT `medical`)
- Static array `OCCASIONS` in HTML + `GET /occasions` API endpoint in backend
- Tab filters: Upcoming / Medical Days / National & Cultural / All Occasions / May–Dec 2026
- Featured occasions: Doctors' Day (o6) + Diwali (o11)
- `openBroadcast(occId)` — opens broadcast modal for that occasion
- `openQuickWish(doctor, type)` — opens quick wish modal
- Key JS vars: `OCCASIONS`, `BCAST_OCC_ID`, `BCAST_SEL_DOCS`, `renderOccasions()`, `setOccTab()`
- Date reference: uses `new Date('2026-05-01')` as "now" (hardcoded for demo)

#### Research Agent (`showPage('research-agent')`)
- **Status:** ✅ Fully working (tested 2026-06-19)
- **Role:** MA only (login: `prashant.agarwal@mankind.in` / Test)
- Fuzzy-filter search UI: Therapy Area + Disease + Keywords (chips) + Date range
- Suggestions loaded from `GET /filters/suggestions` → `demo/filter_suggestions.txt`
- Hardcoded fallback defaults always merged when file returns empty defaults
- Calls `POST /pipeline/run` → polls `GET /pipeline/status/{runId}` until complete
- Results rendered as article cards with rank badges; approved cards show green "✓ Approved"
- "Download Database" button exports pipeline data
- Key JS vars: `RA_SUGGESTIONS_CACHE`, `raSelectedKeywords`, `RA_SEARCH_CONTEXT`
- Key JS fns: `raLoadSuggestions()`, `raShowDropdown()`, `raAddKeywordChip()`, `raRemoveKeywordChip()`, `raClearAllFilters()`, `raRunDynamicSearch()`, `raFuzzyMatch()`
- Validation: requires at least Disease OR Therapy Area before search

#### Pipeline Monitor (`showPage('pipeline')`)
- **Status:** ✅ Navigable (separate from Research Agent)
- Shows live agent log: Alpha → Beta → Gamma → Delta
- Key elements: `pl-log-alpha`, `pl-log-beta`, `pl-log-gamma`, `pl-log-delta`

#### Content Library (`showPage('library')`)
- PMT sees only MA-approved content (seed-gated)
- Shares same `GET /content` endpoint as MA view

#### Doctor 360 / Profile View
- Per-doctor detail view
- Accessible from task cards

#### Analytics
- CSV export to clipboard

### Medical Affairs (MA) Screens

#### Content Review Queue
- Lists pending content items for approve/reject/improve
- `POST /content/{id}/approve` — approve with notification
- `POST /content/{id}/reject` — reject with reason
- `POST /content/{id}/improve` — request improvement (async background task)
- `PATCH /content/{id}` — update metadata independently

#### Pipeline Runner
- Triggers `mock_runner.py` to simulate LLM pipeline
- Real pipeline: `research_agent_system/orchestrator.py`

---

## 6. Key API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/app` | Serve `PinnacleIQ_Portal.html` |
| GET | `/portal` | Alias for `/app` |
| GET | `/topics` | Research topics list |
| GET | `/occasions` | 14-occasion dataset (added 2026-06-19) |
| GET | `/content` | Content items (filtered by status) |
| POST | `/content/{id}/approve` | Approve content, send notification |
| POST | `/content/{id}/reject` | Reject content |
| POST | `/content/{id}/improve` | Request improvement (async) |
| PATCH | `/content/{id}` | Update content metadata |
| GET | `/doctors` | Doctor list |
| POST | `/admin/upload-doctors` | Upload DR Master Template Excel → replace `doctors.json` (admin only) |
| GET | `/analytics` | Analytics data |
| GET | `/pipeline/run` | Trigger mock pipeline |
| GET | `/docs` | FastAPI Swagger UI |

---

## 7. Bugs Fixed (Cumulative)

| Date | Bug | Fix |
|------|-----|-----|
| 2026-06-15 | Curated topic card enrichment created duplicates | Fixed deduplication logic |
| 2026-06-15 | Card tag badge duplicated on re-render | Fixed idempotency in badge rendering |
| 2026-06-15 | MA approval endpoint was not idempotent | Fixed state check before persisting |
| 2026-06-16 | Approve/reject endpoints returned HTTP 500 on UTF-8 emoji in notifications | Added `-X utf8` flag to Python startup; fixed stdio encoding |
| 2026-06-16 | Double-encoded UTF-8 mojibake in card titles in DB | Fixed encoding pipeline |
| 2026-06-19 | `/app` returned 404 in worktree | Added `/app` + `/portal` routes to worktree's `app.py` |
| 2026-06-19 | Occasion Hub showed empty grid | Added `GET /occasions` endpoint (was missing from worktree) |
| 2026-06-19 | Broadcast modal showed "Diwali Greetings" title for all occasions | Old stale modal `id="bcast-ov"` shadowed new modal's IDs. Renamed old modal to `bcast-ov-removed-placeholder` + `display:none` |
| 2026-06-19 | Medical/National filter counts wrong (11/3 instead of 10/4) | Doctors' Day (o6) was tagged `medical`, should be `national` — fixed in both `app.py` and HTML |
| 2026-06-19 | Holi date was 2026-03-14 (already past) | Corrected to 2027-03-14 |
| 2026-06-19 | Research Agent dropdowns blank — `filter_suggestions.txt` missing | Created seed file with 14 therapy areas, 14 diseases, 11 keywords |
| 2026-06-19 | `raLoadSuggestions()` ignored hardcoded defaults when API returned empty defaults | Fixed: always merge hardcoded defaults when API `defaults[]` is empty |
| 2026-06-19 | Research Agent Disease/Keywords dropdowns didn't open on click | Added `onfocus` handler to all 3 filter inputs (was `oninput` only) |
| 2026-06-19 | SQLite DB path relative — new empty DB created on every restart from different CWD | Fixed: `app.py` pins `SQLITE_DB_PATH` via `os.environ.setdefault` to `<script_dir>/pinnacleiq_demo.db`; `sqlite_store.py` also uses `__file__`-relative absolute path. Merged 1086-item main repo DB (91 approved) into worktree. |
| 2026-06-19 | `filter_suggestions.txt` had RECENT markers and `_test_*` entries from test runs | Reset to clean defaults — all 14 therapy/disease entries are plain defaults again |
| 2026-06-22 | Documented admin login `admin@mankind.in` / `Admin123` failed — "No account found". Only `admin1@mankind.in`…`admin5@mankind.in` existed, and password check used a single shared `APP_PASSWORD='Test'` | Added `admin@mankind.in` account (`pwd:'Admin123'`) to `USERS_DB`; changed login check to `password !== (user.pwd || APP_PASSWORD)` so per-user passwords work while everyone else stays `Test`. Committed on `feat/admin-login-credentials` → merged to `main` |
| 2026-06-23 | Duplicate specialty/therapy tag on article cards (e.g. "Endocrinology · Endocrinology") | Root cause in `raRunDynamicSearch()`: `therapy_area` was set to `therapyArea` (same as `specialty`). Fixed to `disease \|\| therapyArea \|\| 'General'`. Also added render-time guard in `clCardHTML()` and `clRowHTML()`. |
| 2026-06-23 | Alpha/Beta/Gamma/Delta agent names visible to MA users in improvement/revision modals | Removed all 4 references in `PinnacleIQ_Portal.html`; replaced with generic "AI" wording. "Beta" badge renamed "Insights". |
| 2026-06-23 | Request Improvement modal Cancel/Close button looked like plain text | Changed from `btn-ghost` (transparent, grey text) to `btn-outline` (bordered). |
| 2026-06-23 | AI Summary in detail modals was just a 220-char truncation of the article | `mapAPIItemToPaper` now uses `item.summary` (Delta's dedicated 200-300 word field). `delta.py` and `mock_runner.py` updated to produce proper summaries. |
| 2026-06-23 | Metadata tags (sub-category + keyword chips) not visible on content cards | Two-part fix: (1) `clCardHTML()` + `clRowHTML()` now render `p.sub` and `p.tags` as gray badges (dedup'd, 'AI Pipeline' filtered, capped at 4). (2) Root cause — `mapAPIItemToPaper()` hardcoded `tags` to `[specialty, therapy_area, 'AI Pipeline']`, discarding the real backend tags array; now uses `item.tags` when present. |
| 2026-06-23 | Internal `[REVISION vN]` / `MA Notes:` annotations leaking into the article body shown to users | New `stripRevisionNotes()` filters those lines (also `[MA Feedback…]`, `Reviewer Comments:`) before rendering in both `openMADetail` and `openCVModal`. |
| 2026-06-23 | Review history (reviewer/date/comments) not surfaced; date always blank | Added `buildReviewHistoryHTML()` — a "Review History" footer in both detail modals showing reviewer, date, comments (italic "NA" when none) + colour-coded status dot. `mapAPIItemToPaper()` now maps `item.reviewed_at` → `p.revDate` (backend sets it on approve/reject). |
| 2026-06-23 | Content Library search returned 0 results for partial terms like "antihyp"; only matched on Enter; no suggestions | Search now runs live (`oninput`), matches across title/journal/author/therapy/specialty/sub/summary/tags, and shows an in-app suggestion dropdown (`clBuildSuggest`) after 2+ chars with type labels (Therapy/Specialty/Tag/Article). Browser native autofill was the old "dropdown". |

---

## 8. Test Coverage

### Automated Tests — last run 2026-06-19 against `D:\Codebase\Pinnacle` (main)

| File | Cases | Result | Login |
|------|-------|--------|-------|
| `tests/test_today_and_occasions.js` | 60 | ✅ 60/60 pass | PMT: `amit.verma@mankind.in` / Test |
| `tests/test_research_agent.js` | 65 | ✅ 65/65 pass | MA: `prashant.agarwal@mankind.in` / Test |
| `tests/` (backend pytest) | 57 | ✅ All pass (as of 2026-06-16) | — |
| **Total JS** | **125** | ✅ **125/125** | |

**How to run JS tests:**
1. `cd D:\Codebase\Pinnacle\demo\backend && python app.py`
2. Open `http://127.0.0.1:8010/app`, log in with the role above
3. Open DevTools Console (F12) → paste the test file → Enter

**Note:** After running tests, `filter_suggestions.txt` may get RECENT markers. Reset with:
```powershell
git checkout demo/filter_suggestions.txt   # from D:\Codebase\Pinnacle
```

### Manual Test Checklist
- `test_checklist.html` — 280-case interactive checklist (open in browser)

---

## 9. Key Files Quick Reference

| File | Purpose |
|------|---------|
| `PinnacleIQ_Portal.html` | The entire frontend — single-file SPA |
| `demo/backend/app.py` | FastAPI REST API + HTML serving |
| `demo/backend/mock_runner.py` | Simulated LLM pipeline for demos |
| `demo/backend/scheduler.py` | APScheduler daily jobs |
| `demo/doctors.json` | 100-doctor database |
| `demo/topics.txt` | Research topics (pipe-delimited) |
| `start_app.ps1` | One-click launcher (handles port conflicts) |
| `demo/filter_suggestions.txt` | Seed file for Research Agent dropdowns (therapy, disease, keywords) |
| `demo/backend/pinnacleiq_demo.db` | **Canonical SQLite DB** — 1086 content items (91 approved). Always use this one; path pinned in `app.py` |
| `research_agent_system/store/sqlite_store.py` | SQLite store — DB path now absolute via `__file__` |
| `tests/test_today_and_occasions.js` | 60-case browser console test suite (Today's Tasks + Occasion Hub) |
| `tests/test_research_agent.js` | 65-case browser console test suite (Research Agent tab) |
| `test_checklist.html` | 280-case manual checklist |
| `BRD.md` | Living business requirements document (v1.1, 13 sections) |
| `.claude/launch.json` | Preview server config (python path + port 8010) |

---

## 10. Known Issues / Pending Work

- [ ] Some card titles show mojibake em-dash (`â€"`) — double-encoded UTF-8 in DB (cosmetic, low priority)
- [ ] Real LLM pipeline requires `.env` with `OPENROUTER_API_KEY` and `TAVILY_API_KEY`
- [ ] After running JS tests, `demo/filter_suggestions.txt` gets RECENT markers — reset with `git checkout demo/filter_suggestions.txt`
- ✅ ~~Propagate all worktree fixes to main~~ — **Done 2026-06-19** (`claude/quizzical-hypatia-29e4a0` merged → `main`)

---

## 11. BRD Status

`BRD.md` is a **living document** — update it proactively whenever code changes.
- v1.1 covers: Objectives, Scope, Roles, Functional Requirements (FR-1–FR-38), NFRs, Risks, Glossary, Open Questions, E2E Workflows, Report Formats
- Sections 7–8 added 2026-06-16 (Workflows + Report Formats)

---

## 12. Session History Summary

| Date | Key Work |
|------|----------|
| 2026-06-15 | Bug fixes: card deduplication, tag badges, MA approval idempotency. Added PATCH endpoint. 57 backend tests. Created `start_app.ps1`, `test_checklist.html` |
| 2026-06-16 | UTF-8 encoding crash fix in approval/notification flow. Created BRD.md v1.0 → v1.1 (13 sections). 38 MA workflow tests passing |
| 2026-06-19 | Occasion Hub: added `/occasions` API, fixed empty grid, fixed broadcast modal duplicate ID bug, fixed Doctors' Day tag (medical→national). 60/60 JS tests passing. Committed all files |
| 2026-06-19 | Research Agent: seeded `filter_suggestions.txt`, fixed `raLoadSuggestions()` to always merge hardcoded defaults. 65/65 JS tests passing. Login credentials corrected (prashant.agarwal@mankind.in) |
| 2026-06-19 | Research Agent onfocus fix, SQLite DB path fix, Chrome launch. DB now always resolves to `demo/backend/pinnacleiq_demo.db`. 1086-item DB (91 approved) restored from main repo. |
| 2026-06-19 | **Merged worktree → main.** All fixes in `D:\Codebase\Pinnacle` (main). Ran 125 JS tests against main — 125/125 pass. Cleaned up `filter_suggestions.txt`. App runs from `D:\Codebase\Pinnacle\demo\backend\python app.py`. |
| 2026-06-22 | Ran app (already live on 8010). Fixed admin login: `admin@mankind.in`/`Admin123` didn't exist in `USERS_DB` (only `admin1..5`). Added the account + per-user `pwd` support in `PinnacleIQ_Portal.html`. Committed on `feat/admin-login-credentials`, merged to `main`. Reset test-polluted `filter_suggestions.txt`. Documented login mechanics in §3. **Note:** `main` is ~50 commits ahead of `origin/main` — not pushed (remote: `github.com/sidtomar/Pinnacle.git`). |
| 2026-06-23 | **Branch `Researchagent_2306` created** for all work below. |
| 2026-06-23 | **DR Master Template import feature.** Added `POST /admin/upload-doctors` to `demo/backend/app.py` — accepts `.xlsx/.xls`, maps all 21 DR Master Template columns (Doctor Code, DR Name, City, Speciality, qualification, clinic address, category, DM & DMS, SOW, MR name, Division, Clinical interests, Bday, Anniversary, Spouse name, No of children, engagement score, Last engaged, Next engagement, Status, preferred channel) → writes `demo/doctors.json`. Added "Import Doctor Database" UI card in `PinnacleIQ_Portal.html` on the Research Agent page — visible to **Admin role only**. Shows colour-coded column legend (4 categories: Personal/Upload, Superman CRM, Field/Upload, PIQ Derived), drag-and-drop zone, file info display, upload button, status messages. After upload, frontend calls `loadDoctorsFromAPI()` which refreshes `DOCTORS` array so Doctor Directory + Doctor 360 reflect new data immediately. `switchRole()` updated to show/hide the card. |
| 2026-06-23 | **Dummy Excel file** `demo/3D_Mankind_DR_Master_Database.xlsx` created — 100 doctors, Division = "3D Mankind", 10 specialties × 10 doctors, realistic Indian names/hospitals/cities. 3 sheets: DR Master Database (data), Column Legend, Summary. All 26 columns including bonus fields (whatsapp, email, patients_per_day, years_experience, pinnacle_score). |
| 2026-06-23 | **Duplicate specialty/therapy tag bug fixed.** Root cause: `raRunDynamicSearch()` was sending `therapyArea` for both `specialty` and `therapy_area`, so `p.cat` and `p.therapy` were identical. Fix: `therapy_area: disease \|\| therapyArea \|\| 'General'`. Also added HTML-level guard in `clCardHTML()` and `clRowHTML()`: therapy badge only rendered if `p.therapy.toLowerCase() !== p.cat.toLowerCase()`. |
| 2026-06-23 | **Removed Alpha/Beta/Gamma/Delta agent name references from MA-facing UI.** 4 locations in `PinnacleIQ_Portal.html`: (1) Revision modal info text, (2) Revision modal step labels, (3) Request Improvement modal label, (4) "Beta" badge → renamed to "Insights". |
| 2026-06-23 | **Research Pipeline menu hidden for all roles.** Removed `research-agent` (pipeline nav item) from `PAGES_MA` and `PAGES_PMT` arrays; removed `pipeline` from `PAGES_ADMIN`. All 3 `ni-pipeline` sidebar `<div>` elements marked `style="display:none;"` across Admin, MA, PMT sidebars. Page HTML retained for potential future use. |
| 2026-06-23 | **Import Doctor Database card — collapsible + last-upload info.** Card body collapses by default; always-visible header has "Show Import Tool ▼ / Hide Import Tool ▲" toggle with animated chevron. After upload, saves record (filename, timestamp, total, specialties) to `localStorage`. Header always shows compact last-upload line ("Last updated: file.xlsx on DD MMM YYYY, HH:MM — N doctors"). Expanded panel shows green "Doctor database is up to date" banner with full details. State persists across page refreshes and re-logins. |
| 2026-06-23 | **Request Improvement modal fixes.** Cancel/Close button changed from `btn-ghost` (invisible) to `btn-outline` (bordered, clearly clickable). Footer text changes from "AI revises content" → "AI revised content" (past tense) once pipeline completes; resets to "AI revises content" when modal reopens. |
| 2026-06-23 | **Complete Article expand/collapse in detail modals.** "Abstract" section renamed "Complete Article" in both MA detail modal and PMT content view modal. Box starts collapsed (3-line preview + gradient fade). "View full article ▼" expands to full text; "View less ▲" collapses. Chevron rotates. Collapse state resets each time a modal opens. `openCVModal` now uses `mdToHtml` rendering. |
| 2026-06-23 | **AI Summary upgraded to 200-300 words.** `mapAPIItemToPaper()` now uses `item.summary` (Delta's dedicated field) instead of truncating the article to 220 chars. `delta.py` `summary` field upgraded from "2-3 sentence" to "200-300 word clinical summary" covering objective, findings with numbers, Indian practice relevance, key takeaway. `mock_runner.py` all 3 MOCK_LIBRARY entries (GLP-1, SGLT2, PCOS) and the generic fallback now have proper 200-300 word summaries with real statistics and India-specific context. |
| 2026-06-23 (session 3) | **Metadata tags now visible on content cards.** `clCardHTML()` (grid) + `clRowHTML()` (list) render `p.sub` (sub-category) and `p.tags` keyword chips as gray badges — dedup'd vs cat/therapy, internal 'AI Pipeline' tag filtered, capped at 4. Root cause also fixed: `mapAPIItemToPaper()` was discarding the backend `item.tags` array (hardcoded `[specialty, therapy_area, 'AI Pipeline']`); now uses `item.tags` when present. |
| 2026-06-23 (session 3) | **Review comments stripped from article body + Review History footer added.** New `stripRevisionNotes()` removes `[REVISION vN]`, `MA Notes:`, `[MA Feedback…]`, `Reviewer Comments:` lines before rendering the Complete Article. New `buildReviewHistoryHTML()` renders a separate "Review History" section at the bottom of both MA detail and PMT content-view modals: reviewer name (fallback "Medical Affairs"), date, comments (italic "NA" if none), colour-coded status dot (green/red/amber). `mapAPIItemToPaper()` maps `item.reviewed_at` → `p.revDate` so the first-review date shows correctly (backend writes `reviewed_at` on approve/reject in `sqlite_store.py`). |
| 2026-06-23 (session 3) | **Content Library live search + suggestions.** Search box now filters live on `oninput` (not just Enter) and matches across title/journal/author/therapy/specialty/sub-category/summary/tags — so partial queries like "antihyp" find "Antihypertensives". Added in-app suggestion dropdown (`clBuildSuggest`/`clApplySuggest`/`clHideSuggest`, CSS `.cl-suggest`/`.cl-sg-item`) showing matching therapy areas, specialties, tags and titles (type-labelled) after 2+ chars; dismisses on Esc/blur/clear. The old "dropdown" was browser native autofill. Key fns near `getCLFiltered()`. |
