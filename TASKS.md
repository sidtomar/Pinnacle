# PinnacleIQ — Tasks (2026-06-15)

## In Progress
<!-- nothing in progress -->

## To Do
- [ ] Root-cause mojibake (double-encoded em-dash) in some card titles — likely in mock_runner.py topic generation

## Done This Session (2026-06-16)
- [x] Ran test_research_agent_cards.py — 19/19 pass
- [x] Ran test_ma_review_workflow.py — found 6/38 failing with 500s, root-caused to non-UTF-8 console crashing print() on em-dash in notification text (first-time approve/improve-request only)
- [x] Verified fix: restart server with `python -X utf8 app.py` → 38/38 pass
- [x] Applied -X utf8 fix to start_app.ps1
- [x] Copied start_app.ps1 + test_checklist.html to main repo and committed (2480cdb on feat/research-agent-ux-fixes)

## Done 2026-06-15
- [x] Fixed start_app.ps1: URL /portal → /app, launch uvicorn → python app.py, added port-kill step

## Carried Over From 2026-06-14
- [x] Fixed curated topic cards all identical (_enrich_sources in mock_runner.py)
- [x] Fixed card tag badges (disease distinct from specialty in mapAPIItemToPaper)
- [x] Fixed MA Save Changes "Approval failed" toast (idempotent /approve + async two-step doApprove)
- [x] Added PATCH /content/{id} endpoint
- [x] Fixed approve() not saving reviewer name in sqlite_store.py
- [x] Added test_research_agent_cards.py (19 tests) and test_ma_review_workflow.py (38 tests)
