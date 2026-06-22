#!/usr/bin/env python3
"""
MA Review & Approval Workflow — Integration Test Suite
=======================================================
Tests the full MA lifecycle for AI-generated content cards:
  1. Approve     — pending → approved, metadata persisted
  2. Reject      — pending → rejected, reason required
  3. Improve     — pending/rejected → improvement_requested + pipeline re-run
  4. Metadata    — PATCH updates specialty/therapy/sub-category/tags
  5. Edge cases  — duplicate approve, missing reason, bad IDs, etc.
  6. Card tags   — disease badge distinct from specialty badge

All tests run against the live server at http://localhost:8010.
Run with: python test_ma_review_workflow.py
"""

import sys
import json
import time
import uuid
import requests

BASE = "http://localhost:8010"
REVIEWER = "Dr. Prashant Agarwal (MA)"

# ── Helpers ────────────────────────────────────────────────────────────────────

def _get(content_id: str) -> dict:
    r = requests.get(f"{BASE}/content/{content_id}")
    assert r.status_code == 200, f"GET /content/{content_id} returned {r.status_code}"
    return r.json()


def _approve(content_id: str) -> requests.Response:
    return requests.post(f"{BASE}/content/{content_id}/approve",
                         json={"reviewer": REVIEWER})


def _reject(content_id: str, reason: str) -> requests.Response:
    return requests.post(f"{BASE}/content/{content_id}/reject",
                         json={"reason": reason, "reviewer": REVIEWER})


def _improve(content_id: str, notes: str) -> requests.Response:
    return requests.post(f"{BASE}/content/{content_id}/request-improvement",
                         json={"notes": notes, "reviewer": REVIEWER})


def _patch(content_id: str, fields: dict) -> requests.Response:
    return requests.patch(f"{BASE}/content/{content_id}",
                          json=fields)


def _pending() -> list:
    return requests.get(f"{BASE}/content?status=pending_review").json().get("items", [])


def _approved() -> list:
    return requests.get(f"{BASE}/content?status=approved").json().get("items", [])


# ── 0. Pre-flight ──────────────────────────────────────────────────────────────

def test_server_is_up():
    """Backend must be reachable before any other test."""
    r = requests.get(f"{BASE}/app", timeout=5)
    assert r.status_code == 200, "Server not running at localhost:8010"


def test_content_list_returns_items():
    """GET /content must return at least one item for testing."""
    r = requests.get(f"{BASE}/content")
    assert r.status_code == 200
    items = r.json().get("items", [])
    assert len(items) > 0, "No content items found — run a pipeline search first"


def test_pending_items_exist():
    """At least one pending_review card must exist for MA workflow tests."""
    items = _pending()
    assert len(items) > 0, "No pending_review items — seed some via Research Agent first"


# ── 1. APPROVE FLOW ────────────────────────────────────────────────────────────

def test_approve_pending_card():
    """A pending_review card must be approvable and status must change to 'approved'."""
    items = _pending()
    assert items, "No pending_review cards to test approve"
    cid = items[0]["id"]

    r = _approve(cid)
    assert r.status_code == 200, f"Approve failed: {r.status_code} {r.text}"
    assert "approved" in r.json()["message"].lower(), f"Unexpected message: {r.json()}"

    item = _get(cid)
    assert item["status"] == "approved", f"Status not updated: {item['status']}"


def test_approve_already_approved_is_idempotent():
    """Re-approving an already-approved card must NOT return 400 — must be idempotent."""
    items = _approved()
    if not items:
        pending = _pending()
        assert pending, "Need at least one card to test idempotent approve"
        _approve(pending[0]["id"])
        items = [pending[0]]
    cid = items[0]["id"]

    r = _approve(cid)
    assert r.status_code == 200, \
        f"Re-approve should be idempotent (200), got {r.status_code}: {r.text}"


def test_approve_nonexistent_id_returns_404():
    """Approving a made-up ID must return 404."""
    r = _approve(str(uuid.uuid4()))
    assert r.status_code == 404, f"Expected 404, got {r.status_code}"


def test_approved_card_visible_in_content_list():
    """Approved card must appear in the default /content listing."""
    items = _pending()
    assert items
    cid = items[0]["id"]
    _approve(cid)
    all_items = requests.get(f"{BASE}/content").json().get("items", [])
    ids = [i["id"] for i in all_items]
    assert cid in ids, "Approved card not found in /content listing"


def test_approve_stores_reviewer_name():
    """Reviewer name must be persisted in the approved card."""
    items = _pending()
    assert items
    cid = items[0]["id"]
    _approve(cid)
    item = _get(cid)
    reviewer = item.get("reviewer") or ""
    assert reviewer, f"reviewer field empty after approve: {item}"


# ── 2. REJECT FLOW ────────────────────────────────────────────────────────────

def test_reject_pending_card_with_reason():
    """A pending card must be rejectable with a non-empty reason."""
    items = _pending()
    assert items, "No pending_review cards to test rejection"
    cid = items[0]["id"]

    r = _reject(cid, "Limited Indian population relevance — European cohort data only")
    assert r.status_code == 200, f"Reject failed: {r.status_code} {r.text}"

    item = _get(cid)
    assert item["status"] == "rejected", f"Status should be 'rejected', got: {item['status']}"


def test_rejected_card_stores_rejection_reason():
    """The rejection reason must be persisted and retrievable via GET."""
    items = _pending()
    assert items
    cid = items[0]["id"]
    reason = "Duplicate study — already covered in existing GLP-1 meta-analysis"
    _reject(cid, reason)

    item = _get(cid)
    stored = item.get("rejection_reason") or item.get("reason") or ""
    assert reason[:30] in stored, \
        f"Rejection reason not persisted. Expected substring of: {reason!r}, Got: {stored!r}"


def test_reject_without_reason_returns_400():
    """Rejecting with an empty reason must return 400."""
    items = _pending()
    assert items
    cid = items[0]["id"]
    r = _reject(cid, "")
    assert r.status_code == 400, f"Expected 400 for empty reason, got {r.status_code}"


def test_reject_nonexistent_id_returns_404():
    """Rejecting a made-up ID must return 404."""
    r = _reject(str(uuid.uuid4()), "Not relevant")
    assert r.status_code == 404, f"Expected 404, got {r.status_code}"


# ── 3. IMPROVEMENT FLOW ────────────────────────────────────────────────────────

def test_improve_pending_card_changes_status():
    """Requesting improvement on a pending card sets status to 'improvement_requested'."""
    items = _pending()
    assert items, "No pending_review cards to test improvement"
    cid = items[0]["id"]

    r = _improve(cid, "Expand Indian population data and add SGLT2 comparison section")
    assert r.status_code == 200, f"Improve request failed: {r.status_code} {r.text}"

    item = _get(cid)
    assert item["status"] == "improvement_requested", \
        f"Status should be 'improvement_requested', got: {item['status']}"


def test_improve_returns_run_id():
    """Request-improvement must return a run_id so the UI can poll progress."""
    items = _pending()
    assert items
    cid = items[0]["id"]
    r = _improve(cid, "Strengthen cardiovascular outcome data")
    body = r.json()
    assert "run_id" in body, f"run_id missing from response: {body}"
    assert body["run_id"], "run_id must be non-empty"


def test_improve_rejected_card_is_allowed():
    """Improvement must also be allowed on rejected cards."""
    items = _pending()
    assert items
    cid = items[0]["id"]
    _reject(cid, "Needs more Indian data")
    assert _get(cid)["status"] == "rejected"

    r = _improve(cid, "Add data from ICMR registry")
    assert r.status_code == 200, f"Improve on rejected card failed: {r.status_code} {r.text}"
    assert _get(cid)["status"] == "improvement_requested"


def test_improve_without_notes_returns_400():
    """Improvement with empty notes must return 400."""
    items = _pending()
    assert items
    cid = items[0]["id"]
    r = _improve(cid, "")
    assert r.status_code == 400, f"Expected 400 for empty notes, got {r.status_code}"


def test_improve_approved_card_returns_400():
    """Improvement on an already-approved card must return 400."""
    items = _pending()
    assert items
    cid = items[0]["id"]
    _approve(cid)

    r = _improve(cid, "Improve anyway")
    assert r.status_code == 400, \
        f"Expected 400 (cannot improve approved card), got {r.status_code}"


def test_improve_nonexistent_id_returns_404():
    """Improvement request on a made-up ID must return 404."""
    r = _improve(str(uuid.uuid4()), "Improve this")
    assert r.status_code == 404, f"Expected 404, got {r.status_code}"


def test_improve_stores_notes():
    """Improvement notes must be persisted in the card's improvement_notes field."""
    items = _pending()
    assert items
    cid = items[0]["id"]
    notes = "Add phase 3 RCT data and Indian cohort breakdown — per Dr. Prashant"
    _improve(cid, notes)
    item = _get(cid)
    stored = item.get("improvement_notes") or ""
    assert notes[:30] in stored, \
        f"improvement_notes not persisted. Expected: {notes!r}, Got: {stored!r}"


# ── 4. METADATA PATCH FLOW ────────────────────────────────────────────────────

def test_patch_updates_specialty():
    """PATCH must update specialty and the change must persist in GET."""
    items = requests.get(f"{BASE}/content").json().get("items", [])
    assert items
    cid = items[0]["id"]
    r = _patch(cid, {"specialty": "Diabetology"})
    assert r.status_code == 200, f"PATCH failed: {r.status_code} {r.text}"
    assert "specialty" in r.json().get("updated_fields", [])

    item = _get(cid)
    assert item.get("specialty") == "Diabetology", \
        f"specialty not updated: {item.get('specialty')}"


def test_patch_updates_therapy_area():
    """PATCH must update therapy_area and persist it."""
    items = requests.get(f"{BASE}/content").json().get("items", [])
    assert items
    cid = items[0]["id"]
    r = _patch(cid, {"therapy_area": "Thyroid"})
    assert r.status_code == 200, f"PATCH therapy_area failed: {r.status_code}"
    item = _get(cid)
    assert item.get("therapy_area") == "Thyroid", \
        f"therapy_area not updated: {item.get('therapy_area')}"


def test_patch_updates_sub_category():
    """PATCH must update sub_category."""
    items = requests.get(f"{BASE}/content").json().get("items", [])
    assert items
    cid = items[0]["id"]
    r = _patch(cid, {"sub_category": "Real-World Evidence"})
    assert r.status_code == 200
    item = _get(cid)
    assert item.get("sub_category") == "Real-World Evidence", \
        f"sub_category not updated: {item.get('sub_category')}"


def test_patch_updates_tags_list():
    """PATCH must update tags as a list and persist them correctly."""
    items = requests.get(f"{BASE}/content").json().get("items", [])
    assert items
    cid = items[0]["id"]
    new_tags = ["Diabetology", "Thyroid", "MA Reviewed", "Indian Population"]
    r = _patch(cid, {"tags": new_tags})
    assert r.status_code == 200

    item = _get(cid)
    stored_tags = item.get("tags") or []
    if isinstance(stored_tags, str):
        stored_tags = json.loads(stored_tags)
    assert set(new_tags) == set(stored_tags), \
        f"Tags not persisted correctly. Expected {new_tags}, got {stored_tags}"


def test_patch_updates_summary():
    """PATCH must update the clinical summary text."""
    items = requests.get(f"{BASE}/content").json().get("items", [])
    assert items
    cid = items[0]["id"]
    new_summary = "MA-edited: Updated clinical summary with focus on Indian patient outcomes."
    r = _patch(cid, {"summary": new_summary})
    assert r.status_code == 200
    item = _get(cid)
    stored = item.get("summary") or item.get("short_article") or ""
    assert new_summary[:40] in stored, \
        f"Summary not updated. Got: {stored[:80]!r}"


def test_patch_multi_field_update():
    """PATCH with multiple fields must update all of them atomically."""
    items = requests.get(f"{BASE}/content").json().get("items", [])
    assert items
    cid = items[0]["id"]
    payload = {
        "specialty": "Endocrinology",
        "therapy_area": "GLP-1 Therapy",
        "sub_category": "Clinical Trial / RCT",
        "tags": ["GLP-1", "Endocrinology", "Indian Population", "RCT"],
    }
    r = _patch(cid, payload)
    assert r.status_code == 200
    updated = r.json().get("updated_fields", [])
    for field in payload:
        assert field in updated, f"Field '{field}' not listed in updated_fields: {updated}"

    item = _get(cid)
    assert item.get("specialty") == "Endocrinology", f"specialty wrong: {item.get('specialty')}"
    assert item.get("therapy_area") == "GLP-1 Therapy", f"therapy_area wrong: {item.get('therapy_area')}"
    assert item.get("sub_category") == "Clinical Trial / RCT", f"sub_category wrong: {item.get('sub_category')}"


def test_patch_then_approve_persists_all_fields():
    """Editing metadata then approving must keep both edits and approval status."""
    pending = _pending()
    assert pending
    cid = pending[0]["id"]

    _patch(cid, {"specialty": "Nephrology", "therapy_area": "CKD", "sub_category": "Guideline / Consensus"})
    _approve(cid)

    item = _get(cid)
    assert item["status"] == "approved", f"status wrong: {item['status']}"
    assert item.get("specialty") == "Nephrology", f"specialty lost after approve: {item.get('specialty')}"
    assert item.get("therapy_area") == "CKD", f"therapy_area lost after approve: {item.get('therapy_area')}"


def test_patch_nonexistent_id_returns_404():
    """PATCH on a made-up ID must return 404."""
    r = _patch(str(uuid.uuid4()), {"specialty": "Cardiology"})
    assert r.status_code == 404, f"Expected 404, got {r.status_code}"


def test_patch_empty_body_returns_400():
    """PATCH with no recognized fields must return 400."""
    items = requests.get(f"{BASE}/content").json().get("items", [])
    assert items
    cid = items[0]["id"]
    r = _patch(cid, {})
    assert r.status_code in (400, 422), f"Expected 400/422, got {r.status_code}"


# ── 5. CARD META TAGS ─────────────────────────────────────────────────────────

def test_card_specialty_and_therapy_area_stored_distinctly():
    """Backend must expose specialty and therapy_area as separate JSON fields."""
    items = requests.get(f"{BASE}/content").json().get("items", [])
    assert items
    item = items[0]
    assert "specialty" in item, "specialty field missing from /content response"
    assert "therapy_area" in item, "therapy_area field missing from /content response"


def test_card_tags_are_a_list():
    """tags field must be deserialized as a list in the API response (not a raw JSON string)."""
    items = requests.get(f"{BASE}/content").json().get("items", [])
    assert items
    errors = []
    for item in items[:10]:
        tags = item.get("tags", [])
        if not isinstance(tags, list):
            errors.append(f"Card {item['id'][:8]}: tags is {type(tags).__name__}: {tags!r}")
    assert not errors, "Some cards returned tags as non-list:\n" + "\n".join(errors)


def test_card_tags_non_empty_for_pipeline_cards():
    """AI-generated cards (those with a topic) must carry at least one tag."""
    items = requests.get(f"{BASE}/content").json().get("items", [])
    pipeline_cards = [i for i in items if i.get("topic")]
    assert pipeline_cards, "No pipeline-generated cards found"
    errors = []
    for card in pipeline_cards[:10]:
        tags = card.get("tags") or []
        if isinstance(tags, str):
            try:
                tags = json.loads(tags)
            except Exception:
                tags = []
        if len(tags) < 1:
            errors.append(f"Card '{card.get('title', '')[:40]}' has empty tags")
    assert not errors, "Cards with empty tags:\n" + "\n".join(errors)


def test_card_topic_field_not_empty():
    """All pipeline-generated cards must have a non-empty topic field."""
    items = requests.get(f"{BASE}/content").json().get("items", [])
    pipeline_cards = [i for i in items if i.get("source") == "ai_agent"]
    assert pipeline_cards, "No ai_agent cards found"
    errors = [f"Card {c['id'][:8]} has empty topic" for c in pipeline_cards[:10] if not c.get("topic")]
    assert not errors, "\n".join(errors)


def test_card_disease_distinguishable_from_specialty():
    """Cards where specialty != therapy_area must have distinct values stored."""
    items = requests.get(f"{BASE}/content").json().get("items", [])
    # Find cards where topic is in "Disease - TherapyArea" format
    split_topic_cards = [i for i in items if " - " in (i.get("topic") or "")]
    if not split_topic_cards:
        # No curated topic cards — skip (not a failure)
        return
    for card in split_topic_cards[:5]:
        topic = card.get("topic", "")
        disease = topic.split(" - ")[0].strip()
        therapy = card.get("therapy_area") or ""
        # disease should NOT equal specialty when topic carries explicit disease name
        specialty = card.get("specialty") or ""
        if disease and specialty:
            assert disease != specialty or therapy != specialty, \
                f"Card '{card['id'][:8]}': disease=specialty=therapy='{specialty}' — no distinction"


def test_patch_tags_stored_as_list_not_string():
    """After PATCH, GET must return tags as a Python list (not a raw JSON string)."""
    items = requests.get(f"{BASE}/content").json().get("items", [])
    assert items
    cid = items[0]["id"]
    _patch(cid, {"tags": ["Cardiology", "RCT", "Indian Population"]})

    item = _get(cid)
    tags = item.get("tags", [])
    assert isinstance(tags, list), \
        f"Tags should be list after PATCH, got {type(tags).__name__}: {tags!r}"
    assert len(tags) > 0, "Tags should not be empty after PATCH"


# ── 6. END-TO-END STATE MACHINE ───────────────────────────────────────────────

def test_reject_overrides_approved_status():
    """MA can reject an already-approved card (override scenario)."""
    items = _pending()
    assert items
    cid = items[0]["id"]
    _approve(cid)
    assert _get(cid)["status"] == "approved"

    r = _reject(cid, "MA changed decision after peer review discussion")
    assert r.status_code == 200, \
        f"Reject of approved card should succeed as MA override, got {r.status_code}: {r.text}"
    assert _get(cid)["status"] == "rejected"


def test_full_workflow_pending_improve_approve():
    """End-to-end: pending → improvement_requested → approved."""
    items = _pending()
    assert items
    cid = items[0]["id"]

    r1 = _improve(cid, "Add phase 3 RCT data and Indian cohort breakdown")
    assert r1.status_code == 200
    assert _get(cid)["status"] == "improvement_requested"

    r2 = _approve(cid)
    assert r2.status_code == 200
    assert _get(cid)["status"] == "approved"


def test_full_workflow_pending_reject_improve_approve():
    """End-to-end: pending → rejected → improvement_requested → approved."""
    items = _pending()
    assert items
    cid = items[0]["id"]

    _reject(cid, "Insufficient Indian data")
    assert _get(cid)["status"] == "rejected"

    _improve(cid, "Add ICMR registry data and South Asian cohort analysis")
    assert _get(cid)["status"] == "improvement_requested"

    _approve(cid)
    assert _get(cid)["status"] == "approved"


def test_full_workflow_edit_metadata_then_approve():
    """End-to-end: MA edits specialty+tags then approves — both changes persist."""
    items = _pending()
    assert items
    cid = items[0]["id"]

    patch_payload = {
        "specialty": "Endocrinology",
        "therapy_area": "GLP-1",
        "tags": ["GLP-1", "Indian Population", "MA Reviewed"],
    }
    r_patch = _patch(cid, patch_payload)
    assert r_patch.status_code == 200

    r_approve = _approve(cid)
    assert r_approve.status_code == 200

    item = _get(cid)
    assert item["status"] == "approved"
    assert item.get("specialty") == "Endocrinology"
    assert item.get("therapy_area") == "GLP-1"

    tags = item.get("tags") or []
    if isinstance(tags, str):
        tags = json.loads(tags)
    assert "MA Reviewed" in tags, f"tag 'MA Reviewed' lost after approve: {tags}"


# ── Standalone runner ──────────────────────────────────────────────────────────
def _safe_print(text: str):
    """Print text with ASCII fallback for terminals that can't handle Unicode."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("ascii", errors="replace").decode("ascii"))


if __name__ == "__main__":
    # Force UTF-8 output so error messages containing emoji don't crash the runner.
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    tests = sorted((n, f) for n, f in globals().items()
                   if n.startswith("test_") and callable(f))
    passed = failed = skipped = 0
    _safe_print(f"\nRunning {len(tests)} MA workflow tests against {BASE}\n{'-' * 65}")

    for name, fn in tests:
        try:
            fn()
            _safe_print(f"  [PASS]  {name}")
            passed += 1
        except AssertionError as e:
            _safe_print(f"  [FAIL]  {name}")
            # Truncate very long assertion messages (e.g. full card dumps)
            msg = str(e)
            if len(msg) > 300:
                msg = msg[:300] + " ... [truncated]"
            _safe_print(f"          {msg}")
            failed += 1
        except requests.exceptions.ConnectionError:
            _safe_print(f"  [SKIP]  {name} -- server unreachable at {BASE}")
            skipped += 1
        except Exception as e:
            _safe_print(f"  [ERROR] {name}: {type(e).__name__}: {e}")
            failed += 1

    _safe_print(f"\n{'=' * 65}")
    _safe_print(f"  {passed} passed  |  {failed} failed  |  {skipped} skipped")
    sys.exit(1 if failed else 0)
