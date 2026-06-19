# PinnacleIQ — Project Memory File

> **Purpose:** Single source of truth for Claude sessions. Pick this up at the start of every session.
> **Last updated:** 2026-06-19 | Worktree: `claude/quizzical-hypatia-29e4a0`

---

## 1. What Is This Project?

**PinnacleIQ** — A multi-agent medical research portal for **Mankind Pharma**.
- Single-file HTML portal: `PinnacleIQ_Portal.html` (served at `http://127.0.0.1:8010/app`)
- FastAPI backend: `demo/backend/app.py` (port 8010)
- Real agent pipeline (unused in demo): `research_agent_system/`
- **Do NOT touch** `react-app/` — legacy, unused

---

## 2. How to Run

```powershell
# From worktree root
python demo/backend/app.py
# OR use the one-click launcher:
.\start_app.ps1

# Then open: http://127.0.0.1:8010/app
```

- Backend serves the HTML at both `/app` and `/portal`
- `start_app.ps1` handles port conflicts and UTF-8 encoding

---

## 3. Roles & Login Credentials

| Role | Email | Password | Access |
|------|-------|----------|--------|
| **Admin** | admin@mankind.in | Admin123 | Role switcher, all views |
| **Medical Affairs (MA)** | priya@mankind.in | Test | Run pipeline, approve/reject content |
| **PMT / BU Head** | jijo@mankind.in | Test | Today's Tasks, Occasion Hub, Content Library, Analytics |

**Key mapping:** PMT == BU Head (same role). React-app is legacy — ignore it.

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

---

## 8. Test Coverage

### Automated Tests
| File | Tests | Status | Login |
|------|-------|--------|-------|
| `tests/test_today_and_occasions.js` | 60 cases | ✅ All pass | PMT: `amit.verma@mankind.in` / Test |
| `tests/test_research_agent.js` | 65 cases | ✅ All pass | MA: `prashant.agarwal@mankind.in` / Test |
| `tests/` (backend pytest) | 57 cases | ✅ All pass (as of 2026-06-16) | — |

**How to run JS tests:**
1. Start server: `python demo/backend/app.py`, open `http://127.0.0.1:8010/app`
2. Log in with the role shown above
3. Open DevTools Console (F12) → paste the test file content → Enter

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
| `tests/test_today_and_occasions.js` | 60-case browser console test suite (Today's Tasks + Occasion Hub) |
| `tests/test_research_agent.js` | 65-case browser console test suite (Research Agent tab) |
| `test_checklist.html` | 280-case manual checklist |
| `BRD.md` | Living business requirements document (v1.1, 13 sections) |
| `.claude/launch.json` | Preview server config (python path + port 8010) |

---

## 10. Known Issues / Pending Work

- [ ] Some card titles show mojibake em-dash (`â€"`) — double-encoded UTF-8 in DB (cosmetic, low priority)
- [ ] Fixes in worktree (`demo/backend/app.py`, `PinnacleIQ_Portal.html`) need to be propagated to main repo
- [ ] Real LLM pipeline requires `.env` with `OPENROUTER_API_KEY` and `TAVILY_API_KEY`

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
