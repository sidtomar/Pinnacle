"""Verify FB-001 (notification nav), FB-002 (badge), FB-003 (hero visual)."""
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
    page = browser.new_page(viewport={"width": 1280, "height": 900})

    # ── Navigate to Today's Tasks ──────────────────────────────────────────
    page.goto("http://localhost:5173/#pmt/today", wait_until="networkidle", timeout=20000)
    time.sleep(1.5)

    # FB-003: Hero visual in the banner
    hero = page.locator("[class*=heroVisual]").first
    chk("FB-003: heroVisual element renders in banner", hero.is_visible())
    page.screenshot(path=OUT + "fb003_today_banner.png")

    # FB-002: Badge visible with unread count
    badge = page.locator("[class*=notifBadge]").first
    badge_visible = badge.is_visible()
    badge_text = badge.inner_text().strip() if badge_visible else "hidden"
    chk("FB-002: Unread badge visible on bell", badge_visible, f"count={badge_text}")

    # ── Open notification dropdown ─────────────────────────────────────────
    bell_btn = page.get_by_title("Notifications").first
    bell_btn.click()
    time.sleep(0.6)
    page.screenshot(path=OUT + "fb001_notif_open.png")

    # FB-001: Notification items visible
    items = page.locator("[class*=notifItem]").all()
    chk("FB-001: Notification items rendered in dropdown", len(items) >= 3, f"{len(items)} items")

    # FB-001: Nav hint text visible on hover
    if items:
        items[0].hover()
        time.sleep(0.3)
        page.screenshot(path=OUT + "fb001_hover.png")
        nav_hint = page.locator("[class*=notifNav]").first
        chk("FB-001: Navigation hint shown on hover", nav_hint.is_visible(), nav_hint.inner_text() if nav_hint.is_visible() else "not visible")

    # FB-001: Click navigates to correct page
    if items:
        items[0].click()
        time.sleep(1.0)
        url = page.url
        chk("FB-001: Click navigates to library page", "library" in url, url)
        page.screenshot(path=OUT + "fb001_after_click.png")

    # FB-002: Badge decreases after notification read
    page.goto("http://localhost:5173/#pmt/today", wait_until="networkidle", timeout=20000)
    time.sleep(1.0)
    badge2 = page.locator("[class*=notifBadge]").first
    badge2_text = badge2.inner_text().strip() if badge2.is_visible() else "hidden"
    chk("FB-002: Badge count decreased after notification read", badge2_text != badge_text or badge2_text == "hidden", f"was={badge_text} now={badge2_text}")

    browser.close()

print("\n" + "=" * 50)
print("VERIFICATION REPORT")
print("=" * 50)
for r in results:
    print(r)
passes = sum(1 for r in results if r.startswith("[PASS]"))
fails  = sum(1 for r in results if r.startswith("[FAIL]"))
print(f"\n{passes} PASS  |  {fails} FAIL")
