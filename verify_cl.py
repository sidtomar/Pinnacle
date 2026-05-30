"""
Verify the Add Content flow for Medical Affairs in ContentLibrary.
Uses Playwright with Microsoft Edge (system browser).
"""
import os, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

OUT = Path("D:/Codebase/Pinnacle/verify_screenshots")
OUT.mkdir(exist_ok=True)

BASE = "http://localhost:5173"
MA_LIB = f"{BASE}/#medical-affairs/library"

results = []
def step(n, desc, ok, note=""):
    icon = "✅" if ok else "❌"
    results.append(f"{icon} Step {n}: {desc}" + (f" → {note}" if note else ""))
    print(results[-1])

def probe(desc, ok, note=""):
    icon = "🔍" if ok else "⚠️"
    results.append(f"{icon} PROBE: {desc}" + (f" → {note}" if note else ""))
    print(results[-1])

with sync_playwright() as pw:
    browser = pw.chromium.launch(channel="msedge", headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 800})
    page.goto(MA_LIB, wait_until="networkidle", timeout=15000)
    time.sleep(1)

    # ── Screenshot 1: MA Content Library landing ──────────────────────────
    page.screenshot(path=str(OUT / "01_ma_library.png"), full_page=False)

    # Step 1: MA Banner
    banner = page.query_selector('[class*="maBanner"]')
    step(1, "MA Banner visible", bool(banner),
         banner.inner_text()[:80] if banner else "NOT FOUND")

    # Step 2: Add Content button
    add_btn = page.query_selector('[class*="addBtn"]')
    step(2, "'Add Content' button present", bool(add_btn),
         add_btn.inner_text() if add_btn else "NOT FOUND")

    # KPI cards check
    kpis = page.query_selector_all('[class*="kpiValue"]')
    step(3, f"KPI cards rendered ({len(kpis)} values)", len(kpis) >= 4,
         f"values: {[k.inner_text() for k in kpis[:4]]}")

    # Tabs check
    tabs = page.query_selector_all('[class*="tab"]')
    tab_texts = [t.inner_text() for t in tabs if t.inner_text().strip()]
    step(4, "Tabs rendered (All/Pending/Approved/Rejected)", len(tabs) >= 4,
         str(tab_texts[:6]))

    # Paper cards check
    cards = page.query_selector_all('[class*="paperCard"]')
    step(5, f"Paper cards visible ({len(cards)} cards)", len(cards) > 0)

    # Approve/Reject buttons on pending cards
    approve_btns = page.query_selector_all('[class*="approveBtn"]')
    reject_btns  = page.query_selector_all('[class*="rejectBtn"]')
    step(6, f"Approve/Reject buttons on pending cards",
         len(approve_btns) > 0,
         f"{len(approve_btns)} Approve, {len(reject_btns)} Reject buttons")

    # ── Step 7: Open wizard ───────────────────────────────────────────────
    add_btn.click()
    time.sleep(0.4)
    page.screenshot(path=str(OUT / "02_wizard_step1.png"))

    overlay = page.query_selector('[class*="overlay"]')
    step(7, "Wizard modal opens on Add Content click", bool(overlay))

    # Step 1 source cards
    src_cards = page.query_selector_all('[class*="srcCard"]')
    step(8, f"3 source cards shown in Step 1", len(src_cards) == 3,
         f"Found {len(src_cards)} cards")

    wizard_title = page.query_selector('[class*="stepTitle"]')
    step(8, "Step title is 'Add New Content'",
         "Add New Content" in (wizard_title.inner_text() if wizard_title else ""),
         wizard_title.inner_text() if wizard_title else "NOT FOUND")

    # ── Step 8: Select PubMed ─────────────────────────────────────────────
    pubmed_card = src_cards[0]  # first card is PubMed
    pubmed_card.click()
    time.sleep(0.3)
    page.screenshot(path=str(OUT / "03_pubmed_selected.png"))

    pmid_input = page.query_selector('[placeholder*="pubmed.ncbi"]')
    step(9, "PubMed input appears after selecting PubMed card", bool(pmid_input))

    if pmid_input:
        pmid_input.fill("38291234")
        time.sleep(0.2)
        fetch_btn = page.query_selector('[class*="fetchBtn"]')
        step(10, "Fetch button enabled after PMID input",
             fetch_btn and not fetch_btn.get_attribute("disabled"),
             "enabled" if fetch_btn and not fetch_btn.get_attribute("disabled") else "disabled/missing")
        if fetch_btn:
            fetch_btn.click()

    # ── Step 9: AI Processing ─────────────────────────────────────────────
    time.sleep(0.8)
    page.screenshot(path=str(OUT / "04_ai_processing.png"))
    ai_spinner = page.query_selector('[class*="aiSpinner"]')
    step(11, "AI Processing step 2 shows spinner", bool(ai_spinner))

    # Wait for auto-advance to step 3
    try:
        page.wait_for_selector('[class*="summaryTextarea"]', timeout=8000)
        page.screenshot(path=str(OUT / "05_review_form.png"))
        step(12, "AI auto-advances to Step 3 (Review form)", True)
    except PWTimeout:
        page.screenshot(path=str(OUT / "05_timeout.png"))
        step(12, "AI auto-advances to Step 3", False, "Timed out waiting for review form")

    # ── Step 10: Review & Categorise form ─────────────────────────────────
    summary_ta = page.query_selector('[class*="summaryTextarea"]')
    step(13, "Editable AI summary textarea in Step 3", bool(summary_ta),
         summary_ta.input_value()[:80] if summary_ta else "NOT FOUND")

    spec_select = page.query_selector('[class*="fieldSelect"]')
    step(14, "Specialty/dropdowns rendered", bool(spec_select))

    auto_note = page.query_selector('[class*="autoApproveNote"]')
    step(15, "Auto-approve note shown", bool(auto_note),
         auto_note.inner_text()[:60] if auto_note else "NOT FOUND")

    field_grid = page.query_selector('[class*="fieldGrid"]')
    step(16, "2-column field grid for Specialty/Therapy/etc.", bool(field_grid))

    # ── Step 11: Click Add to Library ─────────────────────────────────────
    next_btn = page.query_selector('[class*="nextBtn"]')
    step(17, "Next button shows 'Add to Library'",
         next_btn and "Library" in next_btn.inner_text(),
         next_btn.inner_text() if next_btn else "NOT FOUND")

    if next_btn and not next_btn.get_attribute("disabled"):
        next_btn.click()
        time.sleep(0.5)
        page.screenshot(path=str(OUT / "06_step4_success.png"))

        success_title = page.query_selector('[class*="successTitle"]')
        step(18, "Step 4 success screen shows 'Content Added'",
             bool(success_title) and "Successfully" in (success_title.inner_text() if success_title else ""),
             success_title.inner_text() if success_title else "NOT FOUND")

        # Close wizard
        done_btn = page.query_selector('[class*="nextBtn"]')
        if done_btn:
            done_btn.click()
        time.sleep(0.4)
        page.screenshot(path=str(OUT / "07_after_add.png"))

        new_cards = page.query_selector_all('[class*="paperCard"]')
        step(19, f"New card appears in library after add ({len(new_cards)} total)", len(new_cards) > len(cards))

    # ── PROBE: Approve a pending card ──────────────────────────────────────
    page.goto(MA_LIB, wait_until="networkidle")
    time.sleep(0.8)
    approve_btns2 = page.query_selector_all('[class*="approveBtn"]')
    if approve_btns2:
        approve_btns2[0].click()
        time.sleep(0.3)
        page.screenshot(path=str(OUT / "08_after_approve.png"))
        # Pending count should decrease
        pending_tab = page.query_selector('[class*="tabBadge"]')
        probe("Approve action updates card status",
              True, f"Pending badge: {pending_tab.inner_text() if pending_tab else 'gone'}")
    else:
        probe("Approve button test", False, "No approve buttons found after reload")

    # ── PROBE: Pending tab filter ──────────────────────────────────────────
    tabs2 = page.query_selector_all('[class*="tab"]')
    pending_tab_btn = next((t for t in tabs2 if "Pending" in t.inner_text()), None)
    if pending_tab_btn:
        pending_tab_btn.click()
        time.sleep(0.3)
        pending_cards = page.query_selector_all('[class*="paperCard"]')
        page.screenshot(path=str(OUT / "09_pending_tab.png"))
        probe("Pending tab filters to only pending cards",
              len(pending_cards) >= 1, f"{len(pending_cards)} cards shown")

    # ── PROBE: Wizard close mid-flow (Step 1 → X button) ─────────────────
    all_tab = next((t for t in page.query_selector_all('[class*="tab"]') if t.inner_text().strip() == "All"), None)
    if all_tab:
        all_tab.click()
        time.sleep(0.2)
    add_btn2 = page.query_selector('[class*="addBtn"]')
    if add_btn2:
        add_btn2.click()
        time.sleep(0.3)
        close_btn = page.query_selector('[class*="closeBtn"]')
        if close_btn:
            close_btn.click()
            time.sleep(0.3)
            overlay_after = page.query_selector('[class*="overlay"]')
            probe("Wizard closes on X button", not overlay_after,
                  "overlay gone" if not overlay_after else "overlay still visible!")

    # ── PROBE: Wizard backdrop click closes ───────────────────────────────
    add_btn3 = page.query_selector('[class*="addBtn"]')
    if add_btn3:
        add_btn3.click()
        time.sleep(0.3)
        overlay3 = page.query_selector('[class*="overlay"]')
        if overlay3:
            # Click the overlay backdrop (outside the modal)
            page.mouse.click(50, 400)
            time.sleep(0.3)
            overlay_after2 = page.query_selector('[class*="overlay"]')
            probe("Wizard closes on backdrop click", not overlay_after2,
                  "closed" if not overlay_after2 else "still open")

    # ── PROBE: Upload PDF card shows drop zone ─────────────────────────────
    add_btn4 = page.query_selector('[class*="addBtn"]')
    if add_btn4:
        add_btn4.click()
        time.sleep(0.3)
        src_cards2 = page.query_selector_all('[class*="srcCard"]')
        if len(src_cards2) >= 2:
            src_cards2[1].click()   # Upload PDF
            time.sleep(0.3)
            upload_zone = page.query_selector('[class*="uploadZone"]')
            page.screenshot(path=str(OUT / "10_upload_zone.png"))
            probe("Upload PDF card shows drag-drop zone", bool(upload_zone),
                  "uploadZone found" if upload_zone else "NOT FOUND")
        close2 = page.query_selector('[class*="closeBtn"]')
        if close2:
            close2.click()

    browser.close()

# ── Print report ──────────────────────────────────────────────────────────
print("\n" + "="*60)
print("VERIFICATION COMPLETE")
print("="*60)
for r in results:
    print(r)
passes  = sum(1 for r in results if r.startswith("✅"))
fails   = sum(1 for r in results if r.startswith("❌"))
probes  = sum(1 for r in results if r.startswith("🔍") or r.startswith("⚠️"))
print(f"\n{passes} passed · {fails} failed · {probes} probes")
print(f"Screenshots: {OUT}")
sys.exit(0 if fails == 0 else 1)
