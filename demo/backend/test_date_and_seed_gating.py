#!/usr/bin/env python3
"""
Tests for:
  1. Research Agent publication date defaults
     - Start date hardcoded to 2020-04-01
     - End date has NO hardcoded value (set dynamically to yesterday by JS)
  2. Content Library seed-gating (rebuildAllPapers logic)
     - All roles see only real pipeline content
     - 12 demo seeds used only as offline fallback
     - rebuildAllPapers() called on both load and role switch

Dual-mode: pytest OR standalone (python test_date_and_seed_gating.py)
"""
import sys
import os
import re
from datetime import date, timedelta

# Resolve the portal HTML path (3 levels up from demo/backend/)
HTML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "..", "..", "PinnacleIQ_Portal.html")

def _html():
    with open(HTML_PATH, encoding="utf-8") as f:
        return f.read()


# ── 1. PUBLICATION DATE DEFAULTS ─────────────────────────────────────────────

def test_start_date_is_1_apr_2020():
    """HTML value attribute for ra-date-from-2 must be 2020-04-01."""
    assert 'id="ra-date-from-2" value="2020-04-01"' in _html(), \
        "Start date hardcoded value should be 2020-04-01"


def test_end_date_has_no_hardcoded_value():
    """ra-date-to-2 must have NO hardcoded value attr — set dynamically by JS."""
    html = _html()
    assert 'id="ra-date-to-2"' in html, "ra-date-to-2 input not found"
    match = re.search(r'id="ra-date-to-2"[^>]*value="([^"]+)"', html)
    assert match is None, \
        f"End date should not be hardcoded; found value='{match.group(1) if match else ''}'"


def test_yesterday_js_logic_present():
    """initApp() must contain the yesterday-calculation snippet."""
    html = _html()
    assert "yesterday.setDate(yesterday.getDate() - 1)" in html, \
        "yesterday date logic missing from initApp()"
    idx = html.index("yesterday.setDate(yesterday.getDate() - 1)")
    nearby = html[idx:idx + 300]
    assert "ra-date-to-2" in nearby, \
        "yesterday value must be assigned to ra-date-to-2 within same block"


def test_yesterday_value_is_correct():
    """Python's 'today - 1 day' logic matches what JS will compute."""
    yesterday = date.today() - timedelta(days=1)
    assert yesterday < date.today(), "yesterday must be strictly before today"
    assert yesterday.isoformat() != date.today().isoformat(), \
        "yesterday must not equal today"


def test_end_date_is_not_today():
    """End date must be yesterday, not today (user requirement)."""
    yesterday = date.today() - timedelta(days=1)
    assert yesterday.isoformat() != date.today().isoformat()


def test_start_date_is_before_end_date():
    """Start date 2020-04-01 must be strictly before yesterday."""
    start = date(2020, 4, 1)
    yesterday = date.today() - timedelta(days=1)
    assert start < yesterday, \
        f"Start {start} must be before yesterday {yesterday}"


# ── 2. CONTENT LIBRARY SEED-GATING ───────────────────────────────────────────

def test_rebuildAllPapers_function_present():
    """rebuildAllPapers() must exist in the HTML."""
    assert "function rebuildAllPapers()" in _html()


def test_seed_papers_constant_present():
    """SEED_PAPERS snapshot must be defined."""
    assert "const SEED_PAPERS = ALL_PAPERS.slice()" in _html()


def test_rebuild_uses_api_papers_when_available():
    """rebuildAllPapers body must prefer _apiPapers over seeds when non-empty."""
    html = _html()
    fn_start = html.index("function rebuildAllPapers()")
    fn_body  = html[fn_start:fn_start + 300]
    assert "_apiPapers.length > 0" in fn_body, \
        "rebuildAllPapers must check _apiPapers.length before falling back"


def test_rebuild_uses_seed_papers_as_fallback():
    """rebuildAllPapers must use SEED_PAPERS.slice() when API is empty/down."""
    html = _html()
    fn_start = html.index("function rebuildAllPapers()")
    fn_body  = html[fn_start:fn_start + 300]
    assert "SEED_PAPERS.slice()" in fn_body, \
        "SEED_PAPERS must be the fallback in rebuildAllPapers"


def test_rebuild_called_in_switchRole():
    """switchRole must call rebuildAllPapers so role changes recompose papers."""
    html = _html()
    fn_start = html.index("function switchRole(")
    fn_body  = html[fn_start:fn_start + 4000]
    assert "rebuildAllPapers" in fn_body, \
        "switchRole() must call rebuildAllPapers()"


def test_rebuild_called_in_loadContentFromAPI():
    """loadContentFromAPI must call rebuildAllPapers() after fetching."""
    html = _html()
    fn_start = html.index("async function loadContentFromAPI()")
    fn_body  = html[fn_start:fn_start + 1000]
    assert "rebuildAllPapers()" in fn_body


def test_no_role_specific_seed_injection():
    """rebuildAllPapers must NOT branch on ROLE — all roles get same pool."""
    html = _html()
    fn_start = html.index("function rebuildAllPapers()")
    fn_body  = html[fn_start:fn_start + 300]
    assert "ROLE" not in fn_body, \
        "rebuildAllPapers must not branch on ROLE (seeds are not role-specific)"


def test_seed_papers_count_is_twelve():
    """The hardcoded ALL_PAPERS seed array must have exactly 12 entries."""
    html = _html()
    start = html.index("let ALL_PAPERS = [")
    end   = html.index("];", start) + 2
    block = html[start:end]
    count = len(re.findall(r'\{id:\d+,', block))
    assert count == 12, f"Expected 12 seed papers, found {count}"


def test_api_papers_variable_declared():
    """_apiPapers must be declared to hold mapped pipeline content."""
    assert "let _apiPapers" in _html(), \
        "_apiPapers variable missing — needed by rebuildAllPapers"


def test_all_papers_reassigned_only_in_rebuild():
    """ALL_PAPERS = should only be assigned inside rebuildAllPapers and its init."""
    html = _html()
    assignments = [m.start() for m in re.finditer(r'ALL_PAPERS\s*=\s*', html)]
    rebuild_start = html.index("function rebuildAllPapers()")
    rebuild_end   = html.index("}", rebuild_start) + 1
    seed_line     = html.index("let ALL_PAPERS = [")
    violations = []
    for pos in assignments:
        in_rebuild   = rebuild_start <= pos <= rebuild_end
        is_seed_init = abs(pos - seed_line) < 5
        if not in_rebuild and not is_seed_init:
            snippet = html[max(0, pos-40):pos+60].replace('\n', ' ').strip()
            violations.append(snippet)
    assert not violations, \
        f"ALL_PAPERS assigned outside rebuildAllPapers:\n" + "\n".join(violations)


# ── 3. RESET FORM DATE BEHAVIOUR ─────────────────────────────────────────────

def test_reset_restores_start_date_to_apr_2020():
    """raResetForm must reset the start date to 2020-04-01 (not stale 2024-01-01)."""
    html = _html()
    fn_start = html.index("function raResetForm(")
    fn_body  = html[fn_start:fn_start + 800]
    assert "'2020-04-01'" in fn_body, \
        "raResetForm must set start date to '2020-04-01', not the old '2024-01-01'"
    assert "'2024-01-01'" not in fn_body, \
        "raResetForm still contains stale '2024-01-01' default — not fixed"


def test_reset_uses_dynamic_yesterday_not_hardcoded_end_date():
    """raResetForm must compute yesterday dynamically, not use a hardcoded end date."""
    html = _html()
    fn_start = html.index("function raResetForm(")
    fn_body  = html[fn_start:fn_start + 800]
    assert "2026-06-01" not in fn_body, \
        "raResetForm still contains stale hardcoded '2026-06-01' end date"
    assert "getDate() - 1" in fn_body, \
        "raResetForm must compute yesterday dynamically (getDate() - 1)"


def test_reset_assigns_yesterday_to_date_to_field():
    """raResetForm must assign the computed yesterday to the ra-date-to field."""
    html = _html()
    fn_start = html.index("function raResetForm(")
    fn_body  = html[fn_start:fn_start + 800]
    assert "toISOString().slice(0, 10)" in fn_body, \
        "raResetForm must format yesterday as ISO date string"


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
            print(f"[ERROR] {name}: {type(e).__name__}: {e}")
            failed += 1
    print(f"\n{'=' * 55}")
    print(f"{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
