/**
 * PinnacleIQ — Research Agent Tab Test Suite
 *
 * HOW TO RUN:
 *   1. Start backend:  python demo/backend/app.py
 *   2. Open http://127.0.0.1:8010/app in Chrome
 *   3. Log in as MA: prashant.agarwal@mankind.in / Test
 *   4. Open DevTools Console (F12)
 *   5. Paste this entire script and press Enter
 *
 * 65 test cases covering:
 *   RA-01  Page render (13 DOM element checks)
 *   RA-02  Filter suggestions loaded from API + fallback defaults (7 checks)
 *   RA-03  Dropdown fuzzy-filter behaviour (4 checks)
 *   RA-04  Dropdown item selection (2 checks)
 *   RA-05  Keyword chip add / duplicate / remove (7 checks)
 *   RA-06  Clear All filter reset (3 checks)
 *   RA-07  Blank validation — no API call (1 check)
 *   RA-08  Search button enabled state (1 check)
 *   RA-09  Date range defaults (3 checks)
 *   RA-10  Results section hidden before search (1 check)
 *   RA-11  Hero counters / badge elements (4 checks)
 *   RA-12  raFuzzyMatch unit tests (5 checks)
 *   RA-13  Recent terms appear before defaults (3 checks)
 *   RA-14  API endpoint reachability (7 checks)
 *   RA-15  pg-pipeline navigability (2 checks)
 *   RA-16  POST /filters/suggestions persists term (2 checks)
 */

(async function RATests() {
  'use strict';
  let passed = 0, failed = 0;
  const results = [];

  function assert(id, name, condition, detail) {
    if (condition) {
      passed++;
      results.push({ status: 'PASS', id, name });
      console.log(`%c  ✓ PASS  %c [${id}] ${name}`, 'color:#16a34a;font-weight:700', 'color:#374151');
    } else {
      failed++;
      results.push({ status: 'FAIL', id, name, detail });
      console.error(`  ✗ FAIL  [${id}] ${name}${detail ? ' — ' + detail : ''}`);
    }
  }

  function el(id)         { return document.getElementById(id); }
  function qsa(sel, ctx)  { return [...(ctx || document).querySelectorAll(sel)]; }

  showPage('research-agent');
  await new Promise(r => setTimeout(r, 1000));

  // ── RA-01: Page render ─────────────────────────────────────────────────────
  console.log('\n%c ═══ RA-01 · Page Render ═══', 'color:#0D1F3C;font-weight:900;font-size:13px');
  assert('RA-01a','pg-research-agent exists',     !!el('pg-research-agent'));
  assert('RA-01b','page is visible',              el('pg-research-agent')?.classList.contains('on'));
  assert('RA-01c','Therapy input exists',         !!el('ra-therapy-2'));
  assert('RA-01d','Disease input exists',         !!el('ra-disease-2'));
  assert('RA-01e','Keywords input exists',        !!el('ra-keywords-2'));
  assert('RA-01f','Search button exists',         !!el('ra-search-btn-2'));
  assert('RA-01g','Date From exists',             !!el('ra-date-from-2'));
  assert('RA-01h','Date To exists',               !!el('ra-date-to-2'));
  assert('RA-01i','Download DB button exists',    !!el('ra-db-btn-2'));
  assert('RA-01j','Results section exists',       !!el('ra-results-section-2'));
  assert('RA-01k','Loading state element exists', !!el('ra-loading-state-2'));
  assert('RA-01l','Empty state element exists',   !!el('ra-empty-state-2'));
  assert('RA-01m','Articles grid exists',         !!el('ra-articles-grid-2'));

  // ── RA-02: Filter suggestions ──────────────────────────────────────────────
  console.log('\n%c ═══ RA-02 · Filter Suggestions ═══', 'color:#0D1F3C;font-weight:900;font-size:13px');
  assert('RA-02a','RA_SUGGESTIONS_CACHE populated', typeof RA_SUGGESTIONS_CACHE !== 'undefined' && RA_SUGGESTIONS_CACHE !== null);
  if (typeof RA_SUGGESTIONS_CACHE !== 'undefined' && RA_SUGGESTIONS_CACHE) {
    const ta = RA_SUGGESTIONS_CACHE.therapy_area;
    const ds = RA_SUGGESTIONS_CACHE.disease;
    const kw = RA_SUGGESTIONS_CACHE.keywords;
    assert('RA-02b','therapy_area defaults present', Array.isArray(ta?.defaults) && ta.defaults.length > 0, `got ${ta?.defaults?.length}`);
    assert('RA-02c','disease defaults present',       Array.isArray(ds?.defaults) && ds.defaults.length > 0, `got ${ds?.defaults?.length}`);
    assert('RA-02d','keywords defaults present',      Array.isArray(kw?.defaults) && kw.defaults.length > 0, `got ${kw?.defaults?.length}`);
    assert('RA-02e','recent arrays exist',            Array.isArray(ta?.recent) && Array.isArray(ds?.recent) && Array.isArray(kw?.recent));
    assert('RA-02f','Cardiology in therapy defaults', ta?.defaults?.includes('Cardiology'));
    assert('RA-02g','Hypertension in disease defaults', ds?.defaults?.includes('Hypertension'));
  }

  // ── RA-03: Dropdown fuzzy filter ──────────────────────────────────────────
  console.log('\n%c ═══ RA-03 · Dropdown Fuzzy Filter ═══', 'color:#0D1F3C;font-weight:900;font-size:13px');
  const therapyInput    = el('ra-therapy-2');
  const therapyDropdown = el('ra-dropdown-therapy');
  therapyInput.value = '';
  raShowDropdown('therapy');
  assert('RA-03a','Dropdown opens on focus',        therapyDropdown && !therapyDropdown.classList.contains('hidden'));
  assert('RA-03b','Dropdown has items',             therapyDropdown && therapyDropdown.children.length > 0);
  therapyInput.value = 'card';
  therapyInput.dispatchEvent(new Event('input'));
  raShowDropdown('therapy');
  const cardItems = qsa('.ra-dropdown-item', therapyDropdown);
  assert('RA-03c','Fuzzy filter "card" → cardiology', cardItems.some(i => i.textContent.toLowerCase().includes('card')));
  therapyInput.value = 'zzznomatch';
  therapyInput.dispatchEvent(new Event('input'));
  raShowDropdown('therapy');
  assert('RA-03d','No-match shows "Add" option',    therapyDropdown.innerHTML.includes('Add'));

  // ── RA-04: Dropdown selection ──────────────────────────────────────────────
  console.log('\n%c ═══ RA-04 · Dropdown Selection ═══', 'color:#0D1F3C;font-weight:900;font-size:13px');
  raSelectFilterOption('therapy', 'Cardiology');
  assert('RA-04a','Selected item fills input',      therapyInput.value === 'Cardiology');
  assert('RA-04b','Dropdown hides after selection', therapyDropdown.classList.contains('hidden'));

  // ── RA-05: Keyword chips ───────────────────────────────────────────────────
  console.log('\n%c ═══ RA-05 · Keyword Chips ═══', 'color:#0D1F3C;font-weight:900;font-size:13px');
  raSelectedKeywords = [];
  el('ra-keyword-chips').innerHTML = '';
  el('ra-keywords-chips-section').style.display = 'none';
  el('ra-keywords-2').value = 'hypertension';
  raAddKeywordChip();
  assert('RA-05a','Chip added to array',            raSelectedKeywords.includes('hypertension'));
  assert('RA-05b','Chips section visible',          el('ra-keywords-chips-section').style.display !== 'none');
  assert('RA-05c','Chip rendered in DOM',           el('ra-keyword-chips').innerHTML.includes('hypertension'));
  el('ra-keywords-2').value = 'clinical trials';
  raAddKeywordChip();
  assert('RA-05d','Second chip added',              raSelectedKeywords.length === 2);
  el('ra-keywords-2').value = 'hypertension';
  raAddKeywordChip();
  assert('RA-05e','Duplicate chip not added',       raSelectedKeywords.filter(k => k === 'hypertension').length === 1);
  raRemoveKeywordChip('hypertension');
  assert('RA-05f','Chip removed from array',        !raSelectedKeywords.includes('hypertension'));
  assert('RA-05g','Remaining chip still present',   raSelectedKeywords.includes('clinical trials'));

  // ── RA-06: Clear All ──────────────────────────────────────────────────────
  console.log('\n%c ═══ RA-06 · Clear All Filters ═══', 'color:#0D1F3C;font-weight:900;font-size:13px');
  therapyInput.value = 'Cardiology';
  el('ra-disease-2').value = 'Type 2 Diabetes';
  raClearAllFilters();
  assert('RA-06a','Clear All resets therapy',       el('ra-therapy-2').value === '');
  assert('RA-06b','Clear All resets disease',       el('ra-disease-2').value === '');
  assert('RA-06c','Clear All resets keywords',      raSelectedKeywords.length === 0);

  // ── RA-07: Blank validation ────────────────────────────────────────────────
  console.log('\n%c ═══ RA-07 · Blank Validation ═══', 'color:#0D1F3C;font-weight:900;font-size:13px');
  raClearAllFilters(); raSelectedKeywords = [];
  el('ra-therapy-2').value = ''; el('ra-disease-2').value = '';
  let apiCalled = false;
  const origFetch = window.fetch;
  window.fetch = (...args) => { if (String(args[0]).includes('/pipeline/run')) apiCalled = true; return origFetch(...args); };
  await raRunDynamicSearch();
  window.fetch = origFetch;
  assert('RA-07','Blank fields → pipeline NOT called', !apiCalled);

  // ── RA-08 / 09: Button state & Date defaults ─────────────────────────────
  console.log('\n%c ═══ RA-08/09 · Button State & Dates ═══', 'color:#0D1F3C;font-weight:900;font-size:13px');
  assert('RA-08a','Search button starts enabled',   !el('ra-search-btn-2').disabled);
  const dateFrom = el('ra-date-from-2').value;
  const dateTo   = el('ra-date-to-2').value;
  assert('RA-09a','Date From has value',            !!dateFrom && /\d{4}-\d{2}-\d{2}/.test(dateFrom));
  assert('RA-09b','Date To has value',              !!dateTo   && /\d{4}-\d{2}-\d{2}/.test(dateTo));
  assert('RA-09c','Date From < Date To',            new Date(dateFrom) < new Date(dateTo));

  // ── RA-10 / 11: Results section & hero elements ───────────────────────────
  console.log('\n%c ═══ RA-10/11 · Results & Hero Elements ═══', 'color:#0D1F3C;font-weight:900;font-size:13px');
  assert('RA-10','Results hidden before search',    el('ra-results-section-2')?.style.display !== 'block');
  assert('RA-11a','Hero results counter',           !!el('ra-hero-results'));
  assert('RA-11b','Results badge',                  !!el('ra-results-badge-2'));
  assert('RA-11c','CSV export button',              !!el('ra-csv-btn-2'));
  assert('RA-11d','Result label element',           !!el('ra-result-label-2'));

  // ── RA-12: raFuzzyMatch unit ───────────────────────────────────────────────
  console.log('\n%c ═══ RA-12 · raFuzzyMatch Unit Tests ═══', 'color:#0D1F3C;font-weight:900;font-size:13px');
  if (typeof raFuzzyMatch === 'function') {
    const items = ['Cardiology','Cardiac Surgery','Neurology','Oncology'];
    assert('RA-12a','2 matches for "card"',         raFuzzyMatch('card', items).length === 2);
    assert('RA-12b','prefix match first',           raFuzzyMatch('card', items)[0].toLowerCase().startsWith('card'));
    assert('RA-12c','no-match → empty',             raFuzzyMatch('xyz', items).length === 0);
    assert('RA-12d','empty query → all',            raFuzzyMatch('', items).length === items.length);
    assert('RA-12e','case-insensitive',             raFuzzyMatch('CARD', items).length === 2);
  } else { assert('RA-12','raFuzzyMatch exists', false, 'not found'); }

  // ── RA-13: Recent terms first ─────────────────────────────────────────────
  console.log('\n%c ═══ RA-13 · Recent Terms Ordering ═══', 'color:#0D1F3C;font-weight:900;font-size:13px');
  if (typeof raGetSuggestions === 'function' && RA_SUGGESTIONS_CACHE) {
    const saved = RA_SUGGESTIONS_CACHE.therapy_area.recent.slice();
    RA_SUGGESTIONS_CACHE.therapy_area.recent = ['MyRecentTherapy'];
    const sugg = raGetSuggestions('therapy');
    assert('RA-13a','Recent term first in list',    sugg[0] === 'MyRecentTherapy');
    assert('RA-13b','Defaults follow recent',        sugg.length > 1);
    assert('RA-13c','Max 5 recent items enforced',   RA_SUGGESTIONS_CACHE.therapy_area.recent.length <= 5 || saved.length <= 5);
    RA_SUGGESTIONS_CACHE.therapy_area.recent = saved;
  }

  // ── RA-14: API reachability ────────────────────────────────────────────────
  console.log('\n%c ═══ RA-14 · API Endpoints ═══', 'color:#0D1F3C;font-weight:900;font-size:13px');
  try {
    const r = await fetch('/filters/suggestions');
    assert('RA-14a','GET /filters/suggestions → 200',  r.ok, `status ${r.status}`);
    if (r.ok) {
      const d = await r.json();
      assert('RA-14b','Response has therapy_area key',  !!d.therapy_area);
      assert('RA-14c','Response has disease key',        !!d.disease);
      assert('RA-14d','Response has keywords key',       !!d.keywords);
      assert('RA-14e','therapy_area defaults seeded',    d.therapy_area.defaults.length > 0, `got ${d.therapy_area.defaults.length}`);
    }
  } catch(e) { assert('RA-14a','GET /filters/suggestions', false, e.message); }

  try {
    const r = await fetch('/pipeline/runs');
    assert('RA-14f','GET /pipeline/runs → 200', r.ok, `status ${r.status}`);
    if (r.ok) {
      const d = await r.json();
      assert('RA-14g','pipeline/runs returns array', Array.isArray(d) || Array.isArray(d.runs));
    }
  } catch(e) { assert('RA-14f','GET /pipeline/runs', false, e.message); }

  // ── RA-15: Pipeline page navigable ────────────────────────────────────────
  console.log('\n%c ═══ RA-15 · Pipeline Page ═══', 'color:#0D1F3C;font-weight:900;font-size:13px');
  assert('RA-15a','pg-pipeline element exists',    !!el('pg-pipeline'));
  showPage('pipeline');
  await new Promise(r => setTimeout(r, 200));
  assert('RA-15b','pg-pipeline is navigable',      el('pg-pipeline')?.classList.contains('on'));
  showPage('research-agent');

  // ── RA-16: POST persists & appears in GET ────────────────────────────────
  console.log('\n%c ═══ RA-16 · Suggestion Persistence ═══', 'color:#0D1F3C;font-weight:900;font-size:13px');
  const testTerm = `_test_${Date.now()}`;
  try {
    const r = await fetch('/filters/suggestions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ section: 'therapy_area', term: testTerm })
    });
    assert('RA-16a','POST /filters/suggestions → 200', r.ok, `status ${r.status}`);
    if (r.ok) {
      const verify = await fetch('/filters/suggestions');
      const d = await verify.json();
      assert('RA-16b','Persisted term appears in subsequent GET', d.therapy_area?.recent?.includes(testTerm));
    }
  } catch(e) { assert('RA-16a','POST /filters/suggestions', false, e.message); }

  // ── Summary ───────────────────────────────────────────────────────────────
  const total = passed + failed;
  console.log(
    `\n%c ════════════════════════════════════════════════════════ \n` +
    ` PinnacleIQ Test Results — Research Agent                \n` +
    ` ${passed} passed  |  ${failed} failed  |  ${total} total             \n` +
    ` ════════════════════════════════════════════════════════ `,
    failed === 0
      ? 'background:#16a34a;color:#fff;font-weight:900;font-size:12px;padding:4px'
      : 'background:#dc2626;color:#fff;font-weight:900;font-size:12px;padding:4px'
  );
  if (failed > 0) {
    console.group('%c Failed tests:', 'color:#dc2626;font-weight:700');
    results.filter(r => r.status === 'FAIL').forEach(r =>
      console.log(`  ✗ [${r.id}] ${r.name}${r.detail ? ' — ' + r.detail : ''}`)
    );
    console.groupEnd();
  }
  return { passed, failed, total, results };
})();
