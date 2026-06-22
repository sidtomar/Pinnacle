# PinnacleIQ — Session Notes (2026-06-15)

## What Was Done This Session

### 1. Fixed: Curated topic cards all identical (Critical Bug)
**Problem:** GLP-1, SGLT2, PCOS cards from `ALPHA_SOURCES` had no per-source metadata (pub_date, study_type, evidence_quality, tags, key_findings, recommendations) so every card in a curated run looked the same.

**Fix:** Added `_enrich_sources()` helper in `demo/backend/mock_runner.py`.
- Infers `study_type` from title/journal keywords (Meta-Analysis, RCT, Guideline, etc.)
- Assigns staggered `pub_date` values so each card has a distinct publication date
- Generates topic-specific `tags`, `key_findings`, `recommendations`
- Idempotent — skips sources already enriched
- Does NOT mutate global `ALPHA_SOURCES` (uses `dict(src)` copy)
- Both curated and generic pipeline paths now run through `_enrich_sources()`

---

### 2. Fixed: Card tag badges — disease name missing, specialty duplicated
**Problem:** Research Agent result cards showed e.g. "Cardiology | Cardiology | High Relevance" instead of "Cardiology | GLP-1 | High Relevance". The `therapy` field in `mapAPIItemToPaper()` was set to `item.therapy_area` which equalled `specialty` when both were "Cardiology".

**Fix:** In `PinnacleIQ_Portal.html` → `mapAPIItemToPaper()`:
```javascript
// Extract disease from topic string ("Disease - TherapyArea (keywords)")
const _topicParts = (item.topic || '').split(' - ');
const _disease = (_topicParts.length > 1 ? _topicParts[0].trim() : '') || item.therapy_area || '';
therapy: _disease,  // was: item.therapy_area (same as specialty)
tags: (item.tags && item.tags.length > 0)
  ? [...new Set(item.tags)].slice(0, 5)
  : [...new Set([item.specialty, _disease].filter(Boolean))],
// was: hardcoded [specialty, therapy_area, 'AI Pipeline']
```

---

### 3. Fixed: MA "Save Changes" giving "Approval failed — API error" toast
**Problem:** When MA edited metadata on an already-approved card and clicked Save, `doApprove()` hit the `/approve` endpoint which returned HTTP 400 ("already approved") → toast showed error.

**Two-part fix:**

**a) Backend (`demo/backend/app.py`):** Removed the hard 400 guard — `/approve` is now idempotent. BU Head notification only fires when transitioning from `pending_review` or `improvement_requested`.

**b) Frontend (`PinnacleIQ_Portal.html`) — `doApprove()` rewritten as async two-step:**
1. `PATCH /content/{id}` with edited metadata (specialty, therapy_area, sub_category, summary, tags)
2. `POST /content/{id}/approve`

Both steps are awaited with distinct error messages ("Metadata save failed" vs "Approval failed").

---

### 4. Added: PATCH /content/{id} endpoint
New endpoint to save MA metadata edits independently of approval.

**Files changed:**
- `demo/backend/app.py` — added `UpdateMetadataRequest` Pydantic model + `PATCH /content/{content_id}` route
- `research_agent_system/store/sqlite_store.py` — added `update_metadata()` method (updates specialty, therapy_area, sub_category, tags, evidence_quality, summary, relevant_doctor_specialties)

---

### 5. Fixed: `approve()` store method not saving reviewer name
**Problem:** `sqlite_store.py` `approve()` set `status='approved'` and `reviewed_at` but forgot to write `reviewer`. Field was always NULL after approve.

**Fix in `sqlite_store.py`:**
```python
# Before:
"UPDATE content_items SET status='approved', reviewed_at=? WHERE id=?"
# After:
"UPDATE content_items SET status='approved', reviewed_at=?, reviewer=? WHERE id=?"
```

---

### 6. New Test Files (both passing 100%)

#### `demo/backend/test_research_agent_cards.py` — 19 tests
Covers:
- All required fields present for generic + all 3 curated topics (GLP-1, SGLT2, PCOS)
- Unique `pub_date` per source for curated and generic
- `study_type` variation across sources
- `key_findings` populated
- `_enrich_sources` does NOT mutate `ALPHA_SOURCES`
- `ALPHA_SOURCES` has all 3 curated keys

Run: `cd demo\backend && python test_research_agent_cards.py`

#### `demo/backend/test_ma_review_workflow.py` — 38 tests
Covers:
- **Approve:** pending->approved, idempotent re-approve (no 400), 404, reviewer name stored, card visible in listing
- **Reject:** with reason, reason persisted, empty reason->400, 404
- **Improve:** pending->improvement_requested, run_id returned, allowed on rejected, empty notes->400, 404, approved card->400, notes stored
- **PATCH metadata:** specialty, therapy_area, sub_category, tags, summary, multi-field, patch-then-approve persists all fields, 404, empty body->400
- **Card meta tags:** specialty/therapy_area as separate fields, tags deserialised as list, non-empty for pipeline cards, topic not empty, disease distinguishable from specialty
- **End-to-end flows:** pending->improve->approve, pending->reject->improve->approve, edit+approve

Run: `cd demo\backend && python -X utf8 test_ma_review_workflow.py`

Both test files are also zipped at: `demo\backend\pinnacleiq_tests.zip`

---

### 7. Startup Script (INCOMPLETE — resume tomorrow)
**Status:** `start_app.ps1` update was interrupted mid-edit.

**What needs to be done:**
- Update `D:\Codebase\Pinnacle\start_app.ps1`:
  - Fix URL: `/portal` -> `/app`
  - Fix launch command: `uvicorn app:app` -> `python app.py`
  - Add port-kill step before starting
- `start_app.bat` (the double-click launcher) is fine — it just calls the PS1

**Correct startup manually (working now):**
```powershell
cd D:\Codebase\Pinnacle\demo\backend
python app.py
# Then open: http://localhost:8010/app
```

---

## Files Changed This Session

| File | Change |
|---|---|
| `demo/backend/mock_runner.py` | Added `_enrich_sources()`, routed both paths through it |
| `demo/backend/app.py` | Added `UpdateMetadataRequest`, `PATCH /content/{id}`, made `/approve` idempotent |
| `research_agent_system/store/sqlite_store.py` | Added `update_metadata()`, fixed `approve()` to save reviewer |
| `PinnacleIQ_Portal.html` | Fixed `mapAPIItemToPaper()` disease extraction, rewrote `doApprove()` as async two-step |
| `demo/backend/test_research_agent_cards.py` | NEW — 19 Research Agent tests |
| `demo/backend/test_ma_review_workflow.py` | NEW — 38 MA workflow tests |
| `demo/backend/pinnacleiq_tests.zip` | NEW — zip of both test files |
| `start_app.ps1` | INCOMPLETE — needs URL + launch command fix |

---

## How to Resume Tomorrow

1. Open `D:\Codebase\Pinnacle` in Claude Code (worktree: `epic-meninsky-846665`)
2. Start the app: `cd demo\backend && python app.py` then open `http://localhost:8010/app`
3. Complete `start_app.ps1` fix (see section 7 above)
4. Run tests to verify everything still green:

```
cd demo\backend
python test_research_agent_cards.py
python -X utf8 test_ma_review_workflow.py
```

---

## Current App State
- Server: port 8010
- DB: `demo/backend/pinnacleiq_demo.db` (SQLite, ~100+ content items)
- All MA workflow APIs working: approve, reject, improve, PATCH metadata
- Card tags display correctly: disease name distinct from specialty
