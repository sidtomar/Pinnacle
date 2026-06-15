#!/usr/bin/env python3
"""
Tests for the updated Research Agent pipeline — per-source content cards.

Covers the fix that makes every generated card carry its OWN
study_type / tags / publication_date / evidence_quality / key_findings /
recommendations / clinical_insights, instead of all cards sharing the
topic-level template.

Dual-mode:
  * Run under pytest:        pytest test_research_agent_cards.py -v
  * Run standalone (no deps): python test_research_agent_cards.py

The standalone runner discovers every `test_*` function, executes it, and
prints a PASS/FAIL/SKIP summary (exit code 1 on any failure).

The full-pipeline tests call run_mock_pipeline() directly with an in-memory
store; time.sleep is disabled so they run instantly. The live-API tests at the
bottom hit http://localhost:8010 and auto-skip when the server isn't running.
"""
import json
import sys
import urllib.request
import urllib.error
from datetime import date

import mock_runner

# ── Speed: disable the pipeline's inter-agent sleeps for tests ────────────────
mock_runner.time.sleep = lambda *a, **k: None  # noqa: E731

API_BASE = "http://localhost:8010"


# ── Helpers ───────────────────────────────────────────────────────────────────
def _run(topic, specialty, therapy_area):
    """Run the mock pipeline in-process and return the completed run dict."""
    store = {}
    run_id = "test-run"
    store[run_id] = {"agent_outputs": {}}
    mock_runner.run_mock_pipeline(topic, specialty, therapy_area, store, run_id)
    return store[run_id]


def _uniq(cards, field):
    """Count distinct JSON-serialised values of `field` across cards."""
    return len({json.dumps(c.get(field), sort_keys=True, default=str) for c in cards})


def _server_up():
    try:
        with urllib.request.urlopen(f"{API_BASE}/", timeout=1.5) as r:
            return r.status == 200
    except Exception:
        return False


# Shared runs (module-level so multiple tests reuse them without re-running)
GENERIC = _run("Hypertension Management", "Cardiology", "Heart Failure")   # specialty != therapy
DEDUPE  = _run("Hypertension in Diabetology", "Diabetology", "Diabetology")  # specialty == therapy
CURATED = _run("GLP-1 in Type 2 Diabetes", "Diabetology", "Type 2 Diabetes")


# ── 1. Source-shape unit tests (pure function, no pipeline) ───────────────────
def test_generic_returns_seven_sources():
    srcs = mock_runner._generic_sources("X Therapy", "Cardiology", "Heart Failure")
    assert len(srcs) == 7, f"expected 7 generic sources, got {len(srcs)}"


def test_every_source_has_per_card_fields():
    srcs = mock_runner._generic_sources("X Therapy", "Cardiology", "Heart Failure")
    required = {"study_type", "tags", "pub_date", "evidence_quality",
                "key_findings", "recommendations"}
    for i, s in enumerate(srcs):
        missing = required - set(s)
        assert not missing, f"source {i} missing {missing}"


def test_tag_dedupe_when_specialty_equals_therapy():
    srcs = mock_runner._generic_sources("Topic", "Diabetology", "Diabetology")
    for s in srcs:
        assert s["tags"].count("Diabetology") == 1, \
            f"specialty==therapy should appear once, got {s['tags']}"


def test_tags_keep_both_when_specialty_differs():
    srcs = mock_runner._generic_sources("Topic", "Cardiology", "Heart Failure")
    for s in srcs:
        assert "Cardiology" in s["tags"] and "Heart Failure" in s["tags"], \
            f"both specialty and therapy expected in {s['tags']}"


def test_last_source_journal_has_no_literal_placeholder():
    # Regression: card 7's journal used to be a non-f-string showing "{specialty}".
    srcs = mock_runner._generic_sources("Topic", "Nephrology", "CKD")
    assert "{specialty}" not in srcs[6]["journal"], \
        f"literal placeholder leaked: {srcs[6]['journal']}"
    assert "Nephrology" in srcs[6]["journal"]


def test_evidence_quality_matches_study_design():
    srcs = mock_runner._generic_sources("Topic", "Cardiology", "Heart Failure")
    by_type = {s["study_type"]: s["evidence_quality"] for s in srcs}
    assert "High" in by_type["Randomised Controlled Trial"]
    assert "Moderate" in by_type["Expert Review"]


# ── 2. Date behaviour ─────────────────────────────────────────────────────────
def test_dates_are_unique_per_source():
    srcs = mock_runner._generic_sources("Topic", "Cardiology", "Heart Failure")
    dates = [s["pub_date"] for s in srcs]
    assert len(set(dates)) == len(dates), f"dates not unique: {dates}"


def test_dates_are_in_the_past_not_today():
    srcs = mock_runner._generic_sources("Topic", "Cardiology", "Heart Failure")
    today = date.today()
    for s in srcs:
        d = date.fromisoformat(s["pub_date"])
        assert d < today, f"publication date {d} is not in the past (today={today})"


def test_dates_are_deterministic_for_same_topic():
    a = mock_runner._generic_sources("Same Topic", "Cardiology", "Heart Failure")
    b = mock_runner._generic_sources("Same Topic", "Cardiology", "Heart Failure")
    assert [x["pub_date"] for x in a] == [x["pub_date"] for x in b]
    assert [x["tags"] for x in a] == [x["tags"] for x in b]


# ── 3. Full-pipeline card uniqueness (the core fix) ───────────────────────────
def test_pipeline_completes_with_seven_cards():
    assert GENERIC.get("status") == "completed"
    cards = GENERIC.get("all_cards", [])
    assert len(cards) == 7, f"expected 7 cards, got {len(cards)}"


def test_every_card_field_is_distinct_per_source():
    cards = GENERIC["all_cards"]
    n = len(cards)
    assert _uniq(cards, "tags") == n,             "tags should differ per card"
    assert _uniq(cards, "publication_date") == n, "dates should differ per card"
    assert _uniq(cards, "evidence_quality") == n, "evidence_quality should differ per card"
    assert _uniq(cards, "key_findings") == n,     "key_findings should differ per card"
    assert _uniq(cards, "recommendations") == n,  "recommendations should differ per card"
    assert _uniq(cards, "clinical_insights") == n, "clinical_insights should differ per card"


def test_clinical_insight_references_its_own_paper():
    # Gamma's per-paper insight is now used; each insight should mention its card title.
    for c in GENERIC["all_cards"]:
        title_head = c["title"][:40]
        assert title_head in c["clinical_insights"], \
            f"insight does not reference its own title: {title_head!r}"


def test_findings_and_recommendations_non_empty():
    for c in GENERIC["all_cards"]:
        assert len(c.get("key_findings") or []) >= 2
        assert len(c.get("recommendations") or []) >= 2


def test_pmids_and_links_well_formed():
    for c in GENERIC["all_cards"]:
        assert str(c.get("pmid", "")).isdigit(), f"bad pmid: {c.get('pmid')}"
        assert c.get("pubmed_link", "").startswith("https://pubmed.ncbi.nlm.nih.gov/")


def test_emerging_trends_is_intentionally_topic_level():
    # Documents intended behaviour: emerging_trends describes the therapy area,
    # not a single paper, so it is shared across cards (NOT a bug).
    assert _uniq(GENERIC["all_cards"], "emerging_trends") == 1


# ── 4. Edge cases & curated-path regression ───────────────────────────────────
def test_special_characters_in_topic():
    run = _run("HFpEF (>=50%) & CKD interplay", "Cardiology", "Heart Failure")
    assert run.get("status") == "completed"
    assert len(run.get("all_cards", [])) == 7


def test_curated_topic_still_works():
    # Curated topics use ALPHA_SOURCES + content fallback — must not regress.
    assert CURATED.get("status") == "completed"
    cards = CURATED.get("all_cards", [])
    assert len(cards) >= 9, f"curated GLP-1 expected >=9 cards, got {len(cards)}"


def test_dedupe_run_completes():
    assert DEDUPE.get("status") == "completed"
    assert len(DEDUPE.get("all_cards", [])) == 7


# ── 5. Live API tests (auto-skip if server not running) ───────────────────────
def _post_json(path, payload, timeout=30):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(f"{API_BASE}{path}", data=data,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, None


def _get_json(path, timeout=30):
    try:
        with urllib.request.urlopen(f"{API_BASE}{path}", timeout=timeout) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, None


def test_live_pipeline_run_and_uniqueness():
    if not _server_up():
        print("   (skipped — backend not running on :8010)")
        return
    import time
    status, run = _post_json("/pipeline/run",
                             {"topic": "Hypertension Management",
                              "specialty": "Cardiology",
                              "therapy_area": "Heart Failure"})
    assert status == 200 and run.get("run_id")
    rid = run["run_id"]
    s = {}
    for _ in range(120):
        _, s = _get_json(f"/pipeline/status/{rid}")
        if s.get("status") in ("completed", "error"):
            break
        time.sleep(0.3)
    assert s.get("status") == "completed"
    ids = s.get("all_content_ids", [])
    assert len(ids) >= 1
    cards = [_get_json(f"/content/{cid}")[1] for cid in ids]
    n = len(cards)
    assert _uniq(cards, "tags") == n
    assert _uniq(cards, "publication_date") == n


def test_live_unknown_run_id_returns_404():
    if not _server_up():
        print("   (skipped — backend not running on :8010)")
        return
    status, _ = _get_json("/pipeline/status/this-id-does-not-exist")
    assert status == 404


def test_live_missing_field_returns_422():
    if not _server_up():
        print("   (skipped — backend not running on :8010)")
        return
    status, _ = _post_json("/pipeline/run",
                          {"topic": "X", "specialty": "Cardiology"})  # therapy_area missing
    assert status == 422


# ── Standalone runner (no pytest required) ────────────────────────────────────
if __name__ == "__main__":
    tests = sorted((n, f) for n, f in globals().items()
                   if n.startswith("test_") and callable(f))
    passed = failed = 0
    print(f"Running {len(tests)} tests...\n")
    for name, fn in tests:
        try:
            fn()
            print(f"[PASS] {name}")
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] {name}: {e}")
            failed += 1
        except Exception as e:  # noqa: BLE001
            print(f"[ERROR] {name}: {type(e).__name__}: {e}")
            failed += 1
    print(f"\n{'=' * 50}\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
