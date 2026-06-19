# PinnacleIQ — Project Memory File

> **Purpose:** Single source of truth for Claude sessions. Pick this up at the start of every session.
> **Last updated:** 2026-06-19 (end of day) | All fixes merged to `main` at `D:\Codebase\Pinnacle`

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
