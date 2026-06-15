#!/usr/bin/env python3
"""
Tests for Research-Agent pipeline card metadata.

Covers:
  1. Generic topics  — cards produced via _generic_sources()
  2. Curated topics  — GLP-1, SGLT2, PCOS produced via ALPHA_SOURCES + _enrich_sources()

Both groups assert that per-card metadata fields are unique and populated,
ensuring the code-review finding (Critical Issue #1 & #2) is regression-tested.

Dual-mode: pytest OR standalone (python test_research_agent_cards.py)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mock_runner import (
    _generic_sources,
    _enrich_sources,
    ALPHA_SOURCES,
)


# ── Helpers ────────────────────────────────────────────────────────────────────

CURATED_TOPICS = ["GLP-1", "SGLT2", "PCOS"]
GENERIC_TOPICS = [
    ("Metformin", "Endocrinology", "Diabetes"),
    ("Statins", "Cardiology", "Cardiovascular"),
    ("Telmisartan", "Nephrology", "Hypertension"),
]

REQUIRED_FIELDS = ["pub_date", "study_type", "evidence_quality", "tags",
                   "key_findings", "recommendations"]


def _curated_enriched(curated_key: str):
    """Return enriched sources for a curated ALPHA_SOURCES key."""
    raw = ALPHA_SOURCES[curated_key]
    return _enrich_sources(raw, curated_key, "Endocrinology", "Metabolic Disease")


def _generic_enriched(topic, specialty, therapy_area):
    raw = _generic_sources(topic, specialty, therapy_area)
    return _enrich_sources(raw, topic, specialty, therapy_area)


# ── 1. ALL REQUIRED FIELDS PRESENT ────────────────────────────────────────────

def test_generic_sources_have_required_fields():
    """Every generic source must have all required metadata fields."""
    sources = _generic_enriched("Metformin", "Endocrinology", "Diabetes")
    for i, src in enumerate(sources):
        for field in REQUIRED_FIELDS:
            assert field in src and src[field], \
                f"Generic source[{i}] missing or empty field '{field}'"


def test_curated_glp1_sources_have_required_fields():
    """Every GLP-1 source must have all required metadata after enrichment."""
    sources = _curated_enriched("GLP-1")
    for i, src in enumerate(sources):
        for field in REQUIRED_FIELDS:
            assert field in src and src[field], \
                f"GLP-1 source[{i}] missing or empty field '{field}'"


def test_curated_sglt2_sources_have_required_fields():
    """Every SGLT2 source must have all required metadata after enrichment."""
    sources = _curated_enriched("SGLT2")
    for i, src in enumerate(sources):
        for field in REQUIRED_FIELDS:
            assert field in src and src[field], \
                f"SGLT2 source[{i}] missing or empty field '{field}'"


def test_curated_pcos_sources_have_required_fields():
    """Every PCOS source must have all required metadata after enrichment."""
    sources = _curated_enriched("PCOS")
    for i, src in enumerate(sources):
        for field in REQUIRED_FIELDS:
            assert field in src and src[field], \
                f"PCOS source[{i}] missing or empty field '{field}'"


# ── 2. UNIQUE PUB_DATE PER SOURCE ─────────────────────────────────────────────

def test_generic_pub_dates_are_unique():
    """Generic sources must not all share the same publication date."""
    sources = _generic_enriched("Metformin", "Endocrinology", "Diabetes")
    dates = [s["pub_date"] for s in sources]
    assert len(set(dates)) > 1, \
        f"All generic sources have identical pub_date={dates[0]!r}"


def test_curated_glp1_pub_dates_are_unique():
    """GLP-1 curated sources must have distinct publication dates."""
    sources = _curated_enriched("GLP-1")
    dates = [s["pub_date"] for s in sources]
    unique = set(dates)
    assert len(unique) > 1, \
        f"GLP-1 sources all share the same pub_date={dates[0]!r}. Dates: {dates}"


def test_curated_sglt2_pub_dates_are_unique():
    """SGLT2 curated sources must have distinct publication dates."""
    sources = _curated_enriched("SGLT2")
    dates = [s["pub_date"] for s in sources]
    assert len(set(dates)) > 1, \
        f"SGLT2 sources all share the same pub_date={dates[0]!r}"


def test_curated_pcos_pub_dates_are_unique():
    """PCOS curated sources must have distinct publication dates."""
    sources = _curated_enriched("PCOS")
    dates = [s["pub_date"] for s in sources]
    assert len(set(dates)) > 1, \
        f"PCOS sources all share the same pub_date={dates[0]!r}"


# ── 3. UNIQUE EVIDENCE_QUALITY / STUDY_TYPE (not all identical) ───────────────

def test_generic_evidence_quality_varies():
    """Generic sources should have at least two different evidence quality levels."""
    sources = _generic_enriched("Metformin", "Endocrinology", "Diabetes")
    qualities = [s["evidence_quality"] for s in sources]
    assert len(set(qualities)) > 1, \
        "All generic sources have identical evidence_quality"


def test_curated_glp1_study_types_vary():
    """GLP-1 curated sources must include more than one study type."""
    sources = _curated_enriched("GLP-1")
    types = [s["study_type"] for s in sources]
    assert len(set(types)) > 1, \
        f"All GLP-1 sources have identical study_type={types[0]!r}"


def test_curated_sglt2_study_types_vary():
    """SGLT2 curated sources must include more than one study type."""
    sources = _curated_enriched("SGLT2")
    types = [s["study_type"] for s in sources]
    assert len(set(types)) > 1, \
        f"All SGLT2 sources have identical study_type={types[0]!r}"


def test_curated_pcos_study_types_vary():
    """PCOS curated sources must include more than one study type."""
    sources = _curated_enriched("PCOS")
    types = [s["study_type"] for s in sources]
    assert len(set(types)) > 1, \
        f"All PCOS sources have identical study_type={types[0]!r}"


# ── 4. KEY FINDINGS ARE NON-EMPTY LISTS ───────────────────────────────────────

def test_curated_glp1_key_findings_populated():
    """GLP-1 sources must each have at least one key finding."""
    for i, src in enumerate(_curated_enriched("GLP-1")):
        assert src.get("key_findings") and len(src["key_findings"]) >= 1, \
            f"GLP-1 source[{i}] has empty key_findings"


def test_curated_sglt2_key_findings_populated():
    for i, src in enumerate(_curated_enriched("SGLT2")):
        assert src.get("key_findings") and len(src["key_findings"]) >= 1, \
            f"SGLT2 source[{i}] has empty key_findings"


def test_curated_pcos_key_findings_populated():
    for i, src in enumerate(_curated_enriched("PCOS")):
        assert src.get("key_findings") and len(src["key_findings"]) >= 1, \
            f"PCOS source[{i}] has empty key_findings"


# ── 5. ENRICH DOES NOT MUTATE ALPHA_SOURCES ────────────────────────────────────

def test_enrich_does_not_mutate_alpha_sources():
    """_enrich_sources must not modify the ALPHA_SOURCES entries in-place."""
    key = "GLP-1"
    original_keys = set(ALPHA_SOURCES[key][0].keys())
    _curated_enriched(key)
    after_keys = set(ALPHA_SOURCES[key][0].keys())
    new_keys = after_keys - original_keys
    assert not new_keys, \
        f"_enrich_sources mutated ALPHA_SOURCES — added keys: {new_keys}"


# ── 6. ALPHA_SOURCES KEY PRESENCE ─────────────────────────────────────────────

def test_alpha_sources_has_glp1():
    assert "GLP-1" in ALPHA_SOURCES, "ALPHA_SOURCES missing 'GLP-1' key"


def test_alpha_sources_has_sglt2():
    assert "SGLT2" in ALPHA_SOURCES, "ALPHA_SOURCES missing 'SGLT2' key"


def test_alpha_sources_has_pcos():
    assert "PCOS" in ALPHA_SOURCES, "ALPHA_SOURCES missing 'PCOS' key"


# ── Standalone runner ──────────────────────────────────────────────────────────
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
        except Exception as e:
            import traceback
            print(f"[ERROR] {name}: {type(e).__name__}: {e}")
            traceback.print_exc()
            failed += 1
    print(f"\n{'=' * 60}")
    print(f"{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
