"""Verify that the score display is now visible on Today's Tasks page."""
from playwright.sync_api import sync_playwright
import time
import json

results = []

def chk(label, ok, note=""):
    icon = "[PASS]" if ok else "[FAIL]"
    msg = f"{icon} {label}" + (f" => {note}" if note else "")
    results.append(msg)
    print(msg)

try:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width": 1366, "height": 768})

        # Navigate to Today's Tasks page
        page.goto("http://localhost:5174/#bu-head/today", wait_until="networkidle", timeout=20000)
        time.sleep(2)

        # Take screenshot
        page.screenshot(path="D:/Codebase/Pinnacle/verify_screenshots/todays_tasks_score_fix.png")

        # 1. Header banner visible
        banner = page.locator("[class*=todaysTasksHeader]").first
        chk("Header banner visible", banner.is_visible())

        # 2. Score display visible
        score_div = page.locator("[class*=headerScore]").first
        chk("Score container visible", score_div.is_visible())

        # 3. Score value (the big gold "0")
        score_value = page.locator("[class*=scoreValue]").first
        score_visible = score_value.is_visible()
        score_text = score_value.inner_text() if score_visible else "NOT VISIBLE"
        chk("Score value (big gold number) visible", score_visible, score_text)

        # 4. Score label
        score_label = page.locator("[class*=scoreLabel]").first
        label_visible = score_label.is_visible()
        label_text = score_label.inner_text() if label_visible else "NOT VISIBLE"
        chk("Score label (of X done) visible", label_visible, label_text)

        # 5. Check if score value is actually gold color
        if score_visible:
            style = score_value.evaluate("e => window.getComputedStyle(e).color")
            # Gold is #D4A843, which converts to rgb(212, 168, 67)
            chk("Score value color is gold", "212" in style or "gold" in style or "D4A843" in style, style)

        # 6. Check font size
        if score_visible:
            font_size = score_value.evaluate("e => window.getComputedStyle(e).fontSize")
            chk("Score value font size is large", "40" in font_size or "39" in font_size or "41" in font_size, font_size)

        # 7. Verify layout - score should be on the right side of the banner
        if score_div.is_visible():
            banner_box = banner.bounding_box()
            score_box = score_div.bounding_box()
            if banner_box and score_box:
                # Score should be on the right side (x position > half of banner width)
                banner_right = banner_box['x'] + banner_box['width']
                score_right_aligned = score_box['x'] > (banner_box['x'] + banner_box['width'] / 2)
                chk("Score positioned on right side of banner", score_right_aligned,
                    f"banner: {banner_box['width']}px wide, score at x={score_box['x']}")

        browser.close()

except Exception as e:
    print(f"Error: {e}")
    results.append(f"[FAIL] Test execution failed: {e}")

print("\n" + "=" * 70)
print("TODAY'S TASKS SCORE DISPLAY FIX VERIFICATION")
print("=" * 70)
for r in results:
    print(r)

passes = sum(1 for r in results if r.startswith("[PASS]"))
fails = sum(1 for r in results if r.startswith("[FAIL]"))
print(f"\n{'PASS' if fails == 0 else 'NEEDS WORK'}: {passes} PASS  |  {fails} FAIL")
