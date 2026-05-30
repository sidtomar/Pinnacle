"""Verify sidebar nav structure and Share Doctor Picker 2-step modal."""
from playwright.sync_api import sync_playwright
import time

OUT = "D:/Codebase/Pinnacle/verify_screenshots/"
results = []

def chk(label, ok, note=""):
    icon = "PASS" if ok else "FAIL"
    msg = f"[{icon}] {label}" + (f" => {note}" if note else "")
    results.append(msg)
    print(msg)

with sync_playwright() as pw:
    browser = pw.chromium.launch(channel="msedge", headless=True)

    # ── PMT sidebar (fresh page) ─────────────────────────────
    pmt = browser.new_page(viewport={"width": 1280, "height": 900})
    pmt.goto("http://localhost:5173/#bu-head/today", wait_until="networkidle", timeout=20000)
    time.sleep(1.5)
    pmt.screenshot(path=OUT + "sidebar_pmt_final.png")
    nav_pmt = pmt.locator("aside nav").inner_text()
    chk("PMT: Research Pipeline removed", "Research Pipeline" not in nav_pmt)
    chk("PMT: Dashboard present", "Dashboard" in nav_pmt)
    chk("PMT: Today's Tasks present", "Today" in nav_pmt)
    chk("PMT: Analytics present", "Analytics" in nav_pmt)
    chk("PMT: Doctor Directory present", "Doctor Directory" in nav_pmt)
    pmt.close()

    # ── MA sidebar (fresh page loads as MA from hash) ─────────
    ma = browser.new_page(viewport={"width": 1280, "height": 900})
    ma.goto("http://localhost:5173/#medical-affairs/library", wait_until="networkidle", timeout=20000)
    time.sleep(1.5)
    ma.screenshot(path=OUT + "sidebar_ma_final.png")
    nav_ma = ma.locator("aside nav").inner_text()
    chk("MA: Content Library present", "Content Library" in nav_ma)
    chk("MA: Doctor Directory absent", "Doctor Directory" not in nav_ma)
    chk("MA: Analytics absent", "Analytics" not in nav_ma)
    chk("MA: Research Pipeline absent", "Research Pipeline" not in nav_ma)
    chk("MA: Dashboard absent", "Dashboard" not in nav_ma)
    chk("MA: Access Level panel present", "ACCESS LEVEL" in nav_ma.upper())
    chk("MA: Review & Approve permission shown", "Review" in nav_ma)
    ma.close()

    # ── Share Doctor Picker (PMT library) ─────────────────────
    sh = browser.new_page(viewport={"width": 1280, "height": 900})
    sh.goto("http://localhost:5173/#bu-head/library", wait_until="networkidle", timeout=20000)
    time.sleep(1.5)

    share_btn = sh.locator("text=Share with Doctor").first
    chk("Share button on approved card", share_btn.is_visible())
    share_btn.click()
    time.sleep(0.7)
    sh.screenshot(path=OUT + "share_step1.png")

    modal_title = sh.locator("text=Share Content").first
    chk("Modal: Share Content title", modal_title.is_visible())
    ai_tab = sh.locator("text=AI Recommended").first
    chk("Modal: AI Recommended tab", ai_tab.is_visible())

    doc_cards = sh.locator("[class*=recDocCard]").all()
    chk("Modal: AI doctor cards rendered", len(doc_cards) >= 1, f"{len(doc_cards)} cards")

    # Select 2 doctors from AI recs
    if len(doc_cards) >= 2:
        doc_cards[0].click()
        time.sleep(0.2)
        doc_cards[1].click()
        time.sleep(0.2)
    sel_summary = sh.locator("[class*=selSummary]").first
    chk("Modal: Selection summary shows count", sel_summary.is_visible(),
        sel_summary.inner_text() if sel_summary.is_visible() else "not visible")

    # Switch to All Doctors tab
    all_tab = sh.locator("text=All Doctors").first
    all_tab.click()
    time.sleep(0.3)
    rows = sh.locator("[class*=miniDt] tbody tr").all()
    chk("Modal: All Doctors table populated", len(rows) >= 5, f"{len(rows)} rows")
    sh.screenshot(path=OUT + "share_step1_all.png")

    # Go to step 2
    next_btn = sh.locator("button").filter(has_text="Select Doctors").first
    chk("Modal: Next button shows Select Doctors text", next_btn.is_visible())
    next_btn.click()
    time.sleep(0.6)
    sh.screenshot(path=OUT + "share_step2.png")

    wa_bubble = sh.locator("[class*=waBubble]").first
    chk("Step 2: WhatsApp preview bubble", wa_bubble.is_visible())
    msg_ta = sh.locator("[class*=msgTextarea]").first
    chk("Step 2: Edit message textarea", msg_ta.is_visible())

    # Channel buttons individually
    wa_ch = sh.locator("[class*=channelBtn]").filter(has_text="WhatsApp").first
    em_ch = sh.locator("[class*=channelBtn]").filter(has_text="Email").first
    bt_ch = sh.locator("[class*=channelBtn]").filter(has_text="Both").first
    chk("Step 2: WhatsApp channel button", wa_ch.is_visible())
    chk("Step 2: Email channel button", em_ch.is_visible())
    chk("Step 2: Both channel button", bt_ch.is_visible())

    # Send button
    send_btn = sh.locator("[class*=nextBtnSend]").first
    chk("Step 2: Green Send button", send_btn.is_visible())

    # Back button
    back_btn = sh.locator("[class*=backBtn]").first
    chk("Step 2: Back button present", back_btn.is_visible())
    back_btn.click()
    time.sleep(0.3)
    chk("Back to step 1: AI Recommended tab visible", sh.locator("text=AI Recommended").first.is_visible())

    sh.close()
    browser.close()

print("\n" + "=" * 55)
print("SIDEBAR & SHARE MODAL VERIFICATION")
print("=" * 55)
for r in results:
    print(r)
passes = sum(1 for r in results if r.startswith("[PASS]"))
fails  = sum(1 for r in results if r.startswith("[FAIL]"))
print(f"\n{passes} PASS  |  {fails} FAIL")
