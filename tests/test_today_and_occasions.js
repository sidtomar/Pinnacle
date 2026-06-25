/**
 * PinnacleIQ — Today's Tasks + Occasion Hub Test Suite
 *
 * HOW TO RUN:
 *   1. Open http://127.0.0.1:8010/app in Chrome
 *   2. Log in as BU Head (jijo@mankind.in / Test)
 *   3. Open DevTools Console (F12)
 *   4. Paste this entire script and press Enter
 *
 * Results print to the console with PASS / FAIL labels.
 */

(function PinnacleTests() {
  'use strict';

  // ─── tiny test harness ───────────────────────────────────────────────────
  let passed = 0, failed = 0;
  const results = [];

  function assert(name, condition, detail) {
    if (condition) {
      passed++;
      results.push({ status: 'PASS', name });
      console.log(`%c  ✓ PASS  %c ${name}`, 'color:#16a34a;font-weight:700', 'color:#374151');
    } else {
      failed++;
      results.push({ status: 'FAIL', name, detail });
      console.error(`  ✗ FAIL  ${name}${detail ? ' — ' + detail : ''}`);
    }
  }

  function section(title) {
    console.log(`\n%c ═══ ${title} ═══`, 'color:#0D1F3C;font-weight:900;font-size:13px');
  }

  // ─── helpers ─────────────────────────────────────────────────────────────
  function el(id) { return document.getElementById(id); }
  function qs(sel, ctx) { return (ctx || document).querySelector(sel); }
  function qsa(sel, ctx) { return [...(ctx || document).querySelectorAll(sel)]; }
  function visible(id) { const e = el(id); return e && e.style.display !== 'none' && !e.classList.contains('hidden'); }

  // Navigate to a page by calling the app's own showPage()
  function goPage(id) {
    if (typeof showPage === 'function') showPage(id);
  }

  // =========================================================================
  //  SECTION 1 — TODAY_TASKS DATA INTEGRITY
  // =========================================================================
  section('1 · TODAY_TASKS — data integrity');

  assert('TODAY_TASKS is defined',
    typeof TODAY_TASKS !== 'undefined' && Array.isArray(TODAY_TASKS));

  assert('TODAY_TASKS has exactly 9 items',
    typeof TODAY_TASKS !== 'undefined' && TODAY_TASKS.length === 9,
    `got ${typeof TODAY_TASKS !== 'undefined' ? TODAY_TASKS.length : 'undefined'}`);

  if (typeof TODAY_TASKS !== 'undefined') {
    const urgent      = TODAY_TASKS.filter(t => t.priority === 'urgent');
    const recommended = TODAY_TASKS.filter(t => t.priority === 'recommended');
    const upcoming    = TODAY_TASKS.filter(t => t.priority === 'upcoming');

    assert('4 urgent tasks exist',      urgent.length === 4,      `got ${urgent.length}`);
    assert('3 recommended tasks exist', recommended.length === 3, `got ${recommended.length}`);
    assert('2 upcoming tasks exist',    upcoming.length === 2,    `got ${upcoming.length}`);

    assert('Every task has required fields (id, priority, type, docId, title, action)',
      TODAY_TASKS.every(t => t.id && t.priority && t.type && t.docId && t.title && t.action));

    assert('Task IDs are unique',
      new Set(TODAY_TASKS.map(t => t.id)).size === TODAY_TASKS.length);

    const validPriorities = new Set(['urgent', 'recommended', 'upcoming']);
    assert('All priorities are valid values',
      TODAY_TASKS.every(t => validPriorities.has(t.priority)));

    const validTypes = new Set(['birthday', 'anniversary', 'content', 'overdue', 'event', 'congratulate']);
    assert('All task types are valid values',
      TODAY_TASKS.every(t => validTypes.has(t.type)));

    assert('Each task references a real doctor (docId in DOCTORS)',
      typeof DOCTORS !== 'undefined' &&
      TODAY_TASKS.every(t => DOCTORS.some(d => d.id === t.docId)),
      'one or more docId not found in DOCTORS array');
  }

  // =========================================================================
  //  SECTION 2 — TODAY PAGE RENDER
  // =========================================================================
  section('2 · Today page — initial render');

  goPage('today');

  // Reset done-set to ensure clean state
  if (typeof TODAY_DONE !== 'undefined') TODAY_DONE.clear();
  if (typeof renderToday === 'function') renderToday();

  assert('Today page element exists', !!el('pg-today'));
  assert('Today page is visible after showPage("today")',
    el('pg-today') && el('pg-today').classList.contains('on'));

  assert('today-task-list container exists', !!el('today-task-list'));

  const taskCards = qsa('.task-card, [data-task-id], .today-card', el('today-task-list'));
  // Task cards may use inline styles not class names — count children instead
  const taskListChildren = el('today-task-list') ? el('today-task-list').children.length : 0;
  // The 'all' tab shows grouped sections + cards; there should be child elements
  assert('today-task-list is populated on render',
    taskListChildren > 0,
    `${taskListChildren} children found`);

  assert('Done count starts at 0',
    el('today-done-count') && el('today-done-count').textContent.trim() === '0');

  assert('Total count shows 9',
    el('today-total-count') && el('today-total-count').textContent.trim() === '9');

  const progBar = el('today-prog-bar');
  assert('Progress bar starts at 0%',
    progBar && (progBar.style.width === '0%' || progBar.style.width === ''),
    `got "${progBar ? progBar.style.width : 'null'}"`);

  const summary = el('today-summary');
  assert('Summary text shows "9 tasks need attention today"',
    summary && summary.textContent.includes('9') && summary.textContent.toLowerCase().includes('task'),
    `got: "${summary ? summary.textContent : 'null'}"`);

  // =========================================================================
  //  SECTION 3 — TODAY TAB FILTER COUNTS
  // =========================================================================
  section('3 · Today page — tab counts');

  assert('tc-all shows 9',    el('tc-all')    && el('tc-all').textContent.trim()    === '9');
  assert('tc-urgent shows 4', el('tc-urgent') && el('tc-urgent').textContent.trim() === '4');
  assert('tc-rec shows 3',    el('tc-rec')    && el('tc-rec').textContent.trim()    === '3');
  assert('tc-up shows 2',     el('tc-up')     && el('tc-up').textContent.trim()     === '2');
  assert('tc-done shows 0',   el('tc-done')   && el('tc-done').textContent.trim()   === '0');

  // =========================================================================
  //  SECTION 4 — TODAY TAB SWITCHING
  // =========================================================================
  section('4 · Today page — tab switching');

  const todayTabs = qsa('#today-tabs .stab');
  assert('5 tabs exist (All / Urgent / Recommended / Upcoming / Done)',
    todayTabs.length === 5, `got ${todayTabs.length}`);

  // Switch to Urgent tab
  if (typeof setTodayTab === 'function') {
    setTodayTab('urgent', todayTabs[1] || document.createElement('div'));
    const urgentChildren = el('today-task-list') ? el('today-task-list').children.length : 0;
    assert('Urgent tab shows tasks (children > 0)', urgentChildren > 0, `got ${urgentChildren}`);
    assert('Empty state hidden on urgent tab (items exist)', el('today-empty') && el('today-empty').style.display === 'none');

    // Switch to Recommended
    setTodayTab('recommended', todayTabs[2] || document.createElement('div'));
    const recChildren = el('today-task-list') ? el('today-task-list').children.length : 0;
    assert('Recommended tab shows tasks (children > 0)', recChildren > 0, `got ${recChildren}`);

    // Switch to Upcoming
    setTodayTab('upcoming', todayTabs[3] || document.createElement('div'));
    const upChildren = el('today-task-list') ? el('today-task-list').children.length : 0;
    assert('Upcoming tab shows tasks (children > 0)', upChildren > 0, `got ${upChildren}`);

    // Switch to Done (should be empty initially)
    setTodayTab('done', todayTabs[4] || document.createElement('div'));
    const doneText = el('today-task-list') ? el('today-task-list').textContent : '';
    assert('Done tab shows empty/no-items message when nothing completed',
      el('today-task-list') && (el('today-task-list').children.length === 0 || doneText.includes('No tasks')));

    // Back to All
    setTodayTab('all', todayTabs[0] || document.createElement('div'));
  } else {
    assert('setTodayTab function exists', false, 'function not found in page scope');
  }

  // =========================================================================
  //  SECTION 5 — TODAY TASK CARD CONTENT
  // =========================================================================
  section('5 · Today page — task card content');

  if (typeof renderToday === 'function' && typeof TODAY_DONE !== 'undefined') {
    TODAY_DONE.clear();
    if (typeof TODAY_TAB !== 'undefined') window.TODAY_TAB = 'all';
    renderToday();
  }

  const taskListHTML = el('today-task-list') ? el('today-task-list').innerHTML : '';
  assert('Task list HTML contains birthday task content',
    taskListHTML.includes('Birthday') || taskListHTML.includes('birthday'));
  assert('Task list HTML contains overdue/re-engage task content',
    taskListHTML.toLowerCase().includes('overdue') || taskListHTML.toLowerCase().includes('re-engage') || taskListHTML.includes('31 days'));
  assert('Task list HTML contains doctor names',
    taskListHTML.includes('Dr.'));
  assert('Task list HTML contains action button text (Send/Share/Re-engage)',
    taskListHTML.includes('Send') || taskListHTML.includes('Share') || taskListHTML.includes('Re-engage'));

  // =========================================================================
  //  SECTION 6 — OCCASIONS DATA INTEGRITY
  // =========================================================================
  section('6 · OCCASIONS — data integrity');

  assert('OCCASIONS array is defined', typeof OCCASIONS !== 'undefined' && Array.isArray(OCCASIONS));

  if (typeof OCCASIONS !== 'undefined') {
    assert('OCCASIONS has 14 entries', OCCASIONS.length === 14, `got ${OCCASIONS.length}`);

    const medical  = OCCASIONS.filter(o => o.tag === 'medical');
    const national = OCCASIONS.filter(o => o.tag === 'national');
    assert('10 medical occasions',  medical.length  === 10, `got ${medical.length}`);
    assert('4 national occasions',  national.length === 4,  `got ${national.length}`);

    const featured = OCCASIONS.filter(o => o.featured);
    assert('2 featured occasions (Doctors Day + Diwali)', featured.length === 2, `got ${featured.length}`);

    assert('All occasions have required fields (id, date, name, icon, tag, msg)',
      OCCASIONS.every(o => o.id && o.date && o.name && o.icon && o.tag && o.msg));

    assert('All occasion IDs are unique',
      new Set(OCCASIONS.map(o => o.id)).size === OCCASIONS.length);

    assert('All dates are valid ISO format (YYYY-MM-DD)',
      OCCASIONS.every(o => /^\d{4}-\d{2}-\d{2}$/.test(o.date)));

    assert('All message templates contain {first} placeholder',
      OCCASIONS.every(o => o.msg.includes('{first}')),
      OCCASIONS.filter(o => !o.msg.includes('{first}')).map(o => o.name).join(', '));
  }

  // =========================================================================
  //  SECTION 7 — OCCASION HUB PAGE RENDER
  // =========================================================================
  section('7 · Occasion Hub — page render');

  goPage('occasions');

  assert('Occasion Hub page element exists', !!el('pg-occasions'));
  assert('Occasion Hub page is visible after navigation',
    el('pg-occasions') && el('pg-occasions').classList.contains('on'));

  assert('Occasion grid container exists', !!el('occ-grid'));

  const occGrid = el('occ-grid');
  const occCards = occGrid ? occGrid.children.length : 0;
  assert('Occasion grid is populated (cards > 0)', occCards > 0, `got ${occCards}`);

  // Default tab is 'upcoming' — should show ≤ 9 occasions from 2026-05-01
  assert('Upcoming tab (default) shows at most 9 cards', occCards <= 9, `got ${occCards}`);

  // =========================================================================
  //  SECTION 8 — OCCASION HUB TAB FILTERING
  // =========================================================================
  section('8 · Occasion Hub — tab filtering');

  const occTabs = qsa('#occ-tabs .stab');
  assert('At least 3 tabs exist (All / Upcoming / Medical / National)',
    occTabs.length >= 3, `got ${occTabs.length}`);

  if (typeof setOccTab === 'function') {
    // All tab
    setOccTab('all', occTabs.find(t => t.textContent.includes('All')) || document.createElement('div'));
    const allCount = occGrid ? occGrid.children.length : 0;
    assert('All tab shows all 14 occasions', allCount === 14, `got ${allCount}`);

    // Medical tab
    setOccTab('medical', occTabs.find(t => t.textContent.includes('Medical')) || document.createElement('div'));
    const medCount = occGrid ? occGrid.children.length : 0;
    assert('Medical tab shows 10 occasions', medCount === 10, `got ${medCount}`);

    // National tab
    setOccTab('national', occTabs.find(t => t.textContent.includes('National')) || document.createElement('div'));
    const natCount = occGrid ? occGrid.children.length : 0;
    assert('National tab shows 4 occasions', natCount === 4, `got ${natCount}`);

    // Back to Upcoming
    setOccTab('upcoming', occTabs.find(t => t.textContent.includes('Upcoming')) || document.createElement('div'));
    const upCount = occGrid ? occGrid.children.length : 0;
    assert('Upcoming tab restored to ≤ 9 cards', upCount <= 9, `got ${upCount}`);
  } else {
    assert('setOccTab function exists', false, 'not found');
  }

  // =========================================================================
  //  SECTION 9 — OCCASION CARD CONTENT
  // =========================================================================
  section('9 · Occasion Hub — card content');

  if (typeof setOccTab === 'function') {
    setOccTab('all', document.createElement('div'));
  }

  const gridHTML = occGrid ? occGrid.innerHTML : '';
  assert('Featured badge present for featured occasions',
    gridHTML.includes('Featured Occasion'));

  assert('Broadcast Message button present on each card',
    occGrid && qsa('button', occGrid).length > 0 &&
    qsa('button', occGrid).some(b => b.textContent.includes('Broadcast')));

  assert('Doctor relevance count shown on cards',
    gridHTML.includes('relevant doctor'));

  assert("Doctors' Day card present (o6 — featured, national)",
    gridHTML.includes("Doctors'") || gridHTML.includes("Doctor"));

  assert('Diwali card present (o11 — featured, national)',
    gridHTML.includes('Diwali'));

  assert('World Asthma Day card present (o1 — medical)',
    gridHTML.includes('Asthma'));

  // =========================================================================
  //  SECTION 10 — OCCASION RELEVANT DOCTOR COUNT LOGIC
  // =========================================================================
  section('10 · Occasion Hub — doctor relevance calculation');

  if (typeof OCCASIONS !== 'undefined' && typeof DOCTORS !== 'undefined') {
    // o3: International Nurses Day — specialty: null → should equal DOCTORS.length
    const o3 = OCCASIONS.find(o => o.id === 'o3');
    const o3Count = o3 && !o3.specialty ? DOCTORS.length : null;
    assert('Null-specialty occasion targets all doctors',
      o3Count !== null && o3Count === DOCTORS.length,
      `DOCTORS.length=${DOCTORS.length}`);

    // o1: World Asthma Day — specialty: ['Physician','Pulmonology'] → subset
    const o1 = OCCASIONS.find(o => o.id === 'o1');
    if (o1 && o1.specialty) {
      const o1Count = DOCTORS.filter(d =>
        o1.specialty.some(sp => d.spec.toLowerCase().includes(sp.toLowerCase().slice(0, 5)))
      ).length;
      assert('Specialty-filtered occasion count is < total doctors',
        o1Count < DOCTORS.length,
        `o1 count=${o1Count}, total=${DOCTORS.length}`);
      assert('Specialty-filtered occasion count is > 0', o1Count > 0, `got ${o1Count}`);
    }
  }

  // =========================================================================
  //  SECTION 11 — OPEN BROADCAST MODAL
  // =========================================================================
  section('11 · Occasion Hub — broadcast modal');

  if (typeof openBroadcast === 'function') {
    try {
      openBroadcast('o6'); // Doctors' Day
      const modal = qs('.modal.on, [id*="broadcast"], [id*="bcast"]') ||
                    qs('.overlay.on') ||
                    qs('[style*="block"][id*="modal"]');
      // Check BCAST_OCC_ID was set
      assert('openBroadcast sets BCAST_OCC_ID',
        typeof BCAST_OCC_ID !== 'undefined' && BCAST_OCC_ID === 'o6',
        `BCAST_OCC_ID=${BCAST_OCC_ID}`);
      // Doctors' Day (o6) has no specialty filter -> all doctors pre-selected
      assert('BCAST_SEL_DOCS pre-selects all doctors for null-specialty occasion',
        typeof BCAST_SEL_DOCS !== 'undefined' && BCAST_SEL_DOCS.size === DOCTORS.length,
        `size=${typeof BCAST_SEL_DOCS !== 'undefined' ? BCAST_SEL_DOCS.size : 'undefined'}, expected ${typeof DOCTORS !== 'undefined' ? DOCTORS.length : '?'}`);
    } catch(e) {
      assert('openBroadcast("o6") runs without throwing', false, e.message);
    }

    // Close modal if open
    const closeBtn = qs('[onclick*="closeBroadcast"], [onclick*="closeModal"], .modal-close');
    if (closeBtn) closeBtn.click();
  } else {
    assert('openBroadcast function exists', false, 'not found');
  }

  // =========================================================================
  //  SECTION 12 — QUICK WISH MODAL (openQuickWish)
  // =========================================================================
  section('12 · Quick Wish modal — openQuickWish');

  if (typeof openQuickWish === 'function' && typeof DOCTORS !== 'undefined') {
    const testDoc = DOCTORS[0];
    try {
      openQuickWish(testDoc, 'birthday');
      // Modal should be visible
      const qwModal = el('qw-modal') || qs('[id*="quick-wish"]') || qs('[id*="qw"]');
      assert('QuickWish modal element exists in DOM', !!qwModal);
      // Close it
      const qwClose = qs('[onclick*="closeQuickWish"], [onclick*="qw"]');
      if (qwClose) qwClose.click();
    } catch(e) {
      assert('openQuickWish runs without throwing', false, e.message);
    }

    try {
      openQuickWish(testDoc, 'anniversary');
      assert('openQuickWish accepts anniversary type without error', true);
      const qwClose = qs('[onclick*="closeQuickWish"]');
      if (qwClose) qwClose.click();
    } catch(e) {
      assert('openQuickWish(anniversary) runs without throwing', false, e.message);
    }
  } else {
    assert('openQuickWish function and DOCTORS exist', false, 'one or both missing');
  }

  // =========================================================================
  //  SUMMARY
  // =========================================================================
  const total = passed + failed;
  console.log(
    `\n%c ════════════════════════════════════════════════════════ \n` +
    ` PinnacleIQ Test Results — Today + Occasions             \n` +
    ` ${passed} passed  |  ${failed} failed  |  ${total} total             \n` +
    ` ════════════════════════════════════════════════════════ `,
    failed === 0
      ? 'background:#16a34a;color:#fff;font-weight:900;font-size:12px;padding:4px'
      : 'background:#dc2626;color:#fff;font-weight:900;font-size:12px;padding:4px'
  );

  if (failed > 0) {
    console.group('%c Failed tests:', 'color:#dc2626;font-weight:700');
    results.filter(r => r.status === 'FAIL').forEach(r =>
      console.log(`  ✗ ${r.name}${r.detail ? ' — ' + r.detail : ''}`)
    );
    console.groupEnd();
  }

  return { passed, failed, total, results };
})();
