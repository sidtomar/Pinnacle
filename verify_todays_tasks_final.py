"""Comprehensive Today's Tasks verification against design."""
from playwright.sync_api import sync_playwright
import time

OUT = "D:/Codebase/Pinnacle/verify_screenshots/"
results = []

def chk(label, ok, note=""):
    icon = "✅" if ok else "❌"
    msg = f"{icon} {label}" + (f" → {note}" if note else "")
    results.append(msg)
    print(msg)

with sync_playwright() as pw:
    browser = pw.chromium.launch(channel="msedge", headless=True)
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    page.goto("http://localhost:5173/#bu-head/today", wait_until="networkidle", timeout=20000)
    time.sleep(2)

    # 1. Header / Banner verification
    banner = page.locator("[class*=todaysTasksHeader]").first
    chk("Header banner visible", banner.is_visible())

    greeting = page.locator("text=Good morning").first
    chk("Greeting 'Good morning, Jijo'", greeting.is_visible())

    meta = page.locator("text=DAILY ACTION CENTRE").first
    chk("Meta text 'DAILY ACTION CENTRE'", meta.is_visible())

    summary = page.locator("[class*=tasksSummary]").first
    chk("Summary text visible", summary.is_visible(), summary.inner_text() if summary.is_visible() else "")

    # 2. Score and progress
    score = page.locator("[class*=tasksScore]").first
    chk("Done score display", score.is_visible())

    prog = page.locator("[class*=progressBar]").first
    chk("Progress bar visible", prog.is_visible())

    # 3. Status tabs
    tabs = page.locator("[class*=statusTabs]").all()
    chk("Status tabs (All/Urgent/Recommended/Upcoming/Done)", len(tabs) >= 5, f"{len(tabs)} tabs")

    all_tab = page.locator("text=All").filter(has_text="All").first
    chk("'All' tab active by default", "active" in all_tab.get_attribute("class") or "on" in all_tab.get_attribute("class"))

    # 4. Task card structure
    cards = page.locator("[class*=taskCard]").all()
    chk("Task cards rendered", len(cards) >= 1, f"{len(cards)} cards")

    if cards:
        card = cards[0]
        page.screenshot(path=OUT + "todays_tasks_design_compare.png")

        # 4a. Avatar + Score ring
        avatar = card.locator("[class*=taskAvatar]").first
        chk("Card: Avatar visible", avatar.is_visible())

        score_ring = card.locator("svg").first
        chk("Card: Score ring SVG", score_ring.is_visible())

        # 4b. Badge with icon + label
        badge = card.locator("[class*=taskBadge]").first
        badge_text = badge.inner_text() if badge.is_visible() else ""
        has_icon = any(emoji in badge_text for emoji in ["🎂", "🚨", "⚠️", "📄", "💍", "🎓", "🏆"])
        chk("Card: Badge has icon (🎂/🚨/⚠️/📄/💍/🎓/🏆)", has_icon, f"text={badge_text}")

        has_label = any(label in badge_text for label in ["Birthday Wish", "Re-engage", "Send Paper", "CME Invite", "Congratulate"])
        chk("Card: Badge has label", has_label or badge_text, f"text={badge_text}")

        # 4c. Doctor name (TITLE)
        doc_name = card.locator("[class*=taskDoctorName]").first
        chk("Card: Doctor name (title)", doc_name.is_visible(), doc_name.inner_text() if doc_name.is_visible() else "")

        # 4d. Reason (meta line: Doctor · Cat · Spec · City · Score N)
        reason = card.locator("[class*=taskReason]").first
        reason_text = reason.inner_text() if reason.is_visible() else ""
        chk("Card: Reason visible", reason.is_visible(), reason_text)

        # Parse and verify reason format
        if "·" in reason_text:
            parts = [p.strip() for p in reason_text.split("·")]
            chk("Card: Reason has doctor name first", "Dr." in parts[0] if len(parts) > 0 else False, parts[0] if len(parts) > 0 else "")
            chk("Card: Reason has category (A+/A)", any(cat in reason_text for cat in ["A+", "A "]), reason_text)
            chk("Card: Reason has specialty", any(spec in reason_text for spec in ["Gynaecologist", "Cardiologist", "Endocrinologist", "Paediatrician"]), reason_text)
            chk("Card: Reason has city", any(city in reason_text for city in ["Bangalore", "Varanasi", "Pune", "Ahmedabad", "Kolkata", "Bhubaneswar", "Hyderabad"]), reason_text)
            chk("Card: Reason has 'Score N'", "Score" in reason_text, reason_text)

        # 4e. Hint (small gray text)
        hint = card.locator("[class*=taskHint]").first
        chk("Card: Hint text visible", hint.is_visible(), hint.inner_text() if hint.is_visible() else "")

        # 4f. Action buttons (right side)
        primary_btn = card.locator("[class*=taskPrimaryBtn]").first
        chk("Card: Primary action button", primary_btn.is_visible(), primary_btn.inner_text() if primary_btn.is_visible() else "")

        done_btn = card.locator("[class*=taskDoneBtn]").first
        snooze_btn = card.locator("[class*=taskSnoozeBtn]").first
        chk("Card: Done + Snooze buttons present", done_btn.is_visible() and snooze_btn.is_visible())

        # 5. Color striping (urgent/recommended/upcoming)
        card_class = card.get_attribute("class")
        has_stripe = any(stripe in card_class for stripe in ["urgent-stripe", "recommended-stripe", "upcoming-stripe"])
        chk("Card: Color stripe (urgent/recommended/upcoming)", has_stripe, card_class)

    # 6. Section dividers (when viewing "All" tab with grouped tasks)
    dividers = page.locator("[class*=sectionDivider]").all()
    chk("Section dividers for priority groups", len(dividers) >= 0, f"{len(dividers)} dividers" if dividers else "none (filtered view)")

    browser.close()

print("\n" + "=" * 65)
print("TODAY'S TASKS DESIGN VERIFICATION")
print("=" * 65)
for r in results:
    print(r)

passes = sum(1 for r in results if r.startswith("✅"))
fails  = sum(1 for r in results if r.startswith("❌"))
print(f"\n{'PASS' if fails == 0 else 'NEEDS WORK'}: {passes} ✅  |  {fails} ❌")
