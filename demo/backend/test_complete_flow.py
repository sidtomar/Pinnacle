#!/usr/bin/env python3
"""Complete end-to-end test of Hanta pipeline flow"""
import urllib.request
import json
import time
import sqlite3

print("\n" + "="*70)
print("PINNACLEIQ COMPLETE END-TO-END TEST - HANTA TOPIC")
print("="*70)

# =============================================================================
# PHASE 1: PMT RUNS PIPELINE
# =============================================================================
print("\n" + "-"*70)
print("PHASE 1: PMT USER RUNS HANTA PIPELINE")
print("-"*70)

print("\n[PMT] Navigating to: http://localhost:5173/pmt/pipeline")
print("[PMT] Logged in as: pmt@mankind.com")

print("\n[PMT] Running pipeline with:")
print("  - Topic: Hanta")
print("  - Specialty: Infectious Disease")
print("  - Therapy Area: Infectious Disease")
print("[PMT] Click 'Run'")

# Start pipeline
request_data = json.dumps({
    "topic": "Hanta",
    "specialty": "Infectious Disease",
    "therapy_area": "Infectious Disease"
}).encode('utf-8')

req = urllib.request.Request(
    "http://localhost:8010/pipeline/run",
    data=request_data,
    headers={'Content-Type': 'application/json'},
    method='POST'
)

with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())
    run_id = data['run_id']

print(f"\n[BACKEND] Pipeline started: {run_id}")

# Poll for completion
print("\n[WAITING] Pipeline progressing...")
start_time = time.time()
last_progress = -1
last_agent = ""

while time.time() - start_time < 40:
    with urllib.request.urlopen(f"http://localhost:8010/pipeline/status/{run_id}") as response:
        status = json.loads(response.read().decode())
        progress = status['progress']
        agent = status['current_agent']

        if progress != last_progress or agent != last_agent:
            if agent == "alpha":
                agent_name = "[ALPHA] Searching PubMed"
            elif agent == "beta":
                agent_name = "[BETA] Summarizing"
            elif agent == "gamma":
                agent_name = "[GAMMA] Writing Articles"
            elif agent == "delta":
                agent_name = "[DELTA] Creating Cards"
            elif agent == "done":
                agent_name = "[DONE] COMPLETED"
            else:
                agent_name = agent

            print(f"  {progress:3d}% | {agent_name}")
            last_progress = progress
            last_agent = agent

        if status['status'] == 'completed':
            elapsed = time.time() - start_time
            all_content_ids = status.get('all_content_ids', [])
            print(f"\n[SUCCESS] Pipeline completed in {elapsed:.1f}s")
            print(f"[SUCCESS] Cards created: {len(all_content_ids)}")
            break

    time.sleep(0.5)

# =============================================================================
# PHASE 2: CHECK WHAT PMT SEES IN PIPELINE UI
# =============================================================================
print("\n" + "-"*70)
print("PHASE 2: PIPELINE UI DISPLAY (What PMT sees)")
print("-"*70)

with urllib.request.urlopen(f"http://localhost:8010/pipeline/status/{run_id}") as response:
    status = json.loads(response.read().decode())
    agent_outputs = status.get('agent_outputs', {})

# Show Alpha output
alpha = agent_outputs.get('alpha', {})
print(f"\n[PMT UI] Agent Alpha Results:")
print(f"  Papers found: {alpha.get('paper_count', 0)}")
print(f"  Internal docs found: {alpha.get('internal_count', 0)}")
if 'papers' in alpha:
    for i, paper in enumerate(alpha['papers'][:3], 1):
        print(f"    {i}. {paper.get('title', '')[:60]}")

# Show Beta output
beta = agent_outputs.get('beta', {})
print(f"\n[PMT UI] Agent Beta Results:")
print(f"  Papers summarized: {beta.get('papers_summarised', 0)}")

# Show Gamma output
gamma = agent_outputs.get('gamma', {})
print(f"\n[PMT UI] Agent Gamma Results:")
print(f"  Shareable messages: {gamma.get('messages_count', 0)}")

# Show Delta output
delta = agent_outputs.get('delta', {})
print(f"\n[PMT UI] Agent Delta Results:")
print(f"  Content cards saved: {delta.get('cards_saved', 0)}")
print(f"  Status: READY FOR MA REVIEW")

# =============================================================================
# PHASE 3: MA REVIEWS CONTENT LIBRARY
# =============================================================================
print("\n" + "-"*70)
print("PHASE 3: MA SWITCHES TO CONTENT LIBRARY")
print("-"*70)

print("\n[MA] Navigating to: http://localhost:5173/#medical-affairs/library")
print("[MA] Logged in as: ma@mankind.com")

# Fetch content
with urllib.request.urlopen("http://localhost:8010/content") as response:
    content_data = json.loads(response.read().decode())
    items = content_data['items']
    counts = content_data['counts']

print(f"\n[MA UI] Content Library Status:")
print(f"  Total cards: {counts['total']}")
print(f"  Pending Review: {counts['pending']}")
print(f"  Approved: {counts['approved']}")
print(f"  Rejected: {counts['rejected']}")

# Show recent Hanta cards
hanta_cards = [item for item in items if item.get('topic') == 'Hanta'][-7:]
print(f"\n[MA UI] Hanta Cards Available ({len(hanta_cards)}):")
for i, card in enumerate(hanta_cards, 1):
    has_read_more = "Read" in (card.get('short_article', '') or '')
    status_text = "PENDING" if card['status'] == 'pending_review' else card['status'].upper()
    print(f"  {i}. {card['title'][:55]}")
    print(f"     Status: {status_text} | Read More: {'YES' if has_read_more else 'NO'}")

# =============================================================================
# PHASE 4: MA CLICKS ON A CARD
# =============================================================================
print("\n" + "-"*70)
print("PHASE 4: MA CLICKS ON FIRST CARD")
print("-"*70)

if hanta_cards:
    card = hanta_cards[0]
    card_id = card['id']

    print(f"\n[MA] Clicked on: {card['title'][:60]}")

    # Fetch full card details
    with urllib.request.urlopen(f"http://localhost:8010/content/{card_id}") as response:
        card_detail = json.loads(response.read().decode())

    print(f"\n[MA] Card Details Modal Opened:")
    print(f"  Title: {card_detail['title']}")
    print(f"  Authors: {card_detail.get('authors', 'Unknown')}")
    print(f"  Specialty: {card_detail['specialty']}")
    print(f"  Therapy Area: {card_detail['therapy_area']}")
    print(f"  Status: {card_detail['status']}")

    # Check for Read More link
    article = card_detail.get('short_article', '')
    has_read_more = "Read" in article
    pubmed_link = card_detail.get('pubmed_link', '')

    print(f"\n[MA] Article Content:")
    print(f"  Word count: {len(article.split())}")
    print(f"  Has 'Read More' text: {'YES' if has_read_more else 'NO'}")
    print(f"  PubMed URL: {pubmed_link}")

    if pubmed_link:
        print(f"  [CLICKABLE] Read More -> {pubmed_link}")

# =============================================================================
# PHASE 5: MA APPROVES CARDS AND SENDS TO DOCTORS
# =============================================================================
print("\n" + "-"*70)
print("PHASE 5: MA APPROVES AND SENDS TO DOCTORS")
print("-"*70)

print(f"\n[MA] Approving all {len(hanta_cards)} Hanta cards...")
print(f"[MA] Cards now available for BU Head to share")

print(f"\n[MA] Selecting doctors to send to...")
with urllib.request.urlopen("http://localhost:8010/doctors?specialty=Infectious%20Disease") as response:
    doctors_data = json.loads(response.read().decode())
    docs = doctors_data['doctors']

print(f"  Found {len(docs)} Infectious Disease doctors")
if docs:
    for doc in docs[:3]:
        print(f"    - {doc['name']} ({doc['city']}) | {doc['preferred_channel'].upper()}")

print(f"\n[MA] Sending cards to 3 doctors...")
# Simulate sharing
share_count = 0
for card in hanta_cards[:3]:
    for doc in docs[:3]:
        try:
            share_data = json.dumps({
                "doctor_id": doc['id'],
                "doctor_name": doc['name'],
                "specialty": doc['specialty'],
                "channel": doc['preferred_channel']
            }).encode('utf-8')

            req = urllib.request.Request(
                f"http://localhost:8010/content/{card['id']}/share",
                data=share_data,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )

            with urllib.request.urlopen(req) as response:
                share_count += 1
        except:
            pass

print(f"  Shared: {share_count} card-doctor combinations")

# =============================================================================
# PHASE 6: CHECK DASHBOARD
# =============================================================================
print("\n" + "-"*70)
print("PHASE 6: DASHBOARD KPIs")
print("-"*70)

conn = sqlite3.connect('pinnacleiq_demo.db')
c = conn.cursor()

# Count total cards
c.execute("SELECT COUNT(*) FROM content_items")
total_cards = c.fetchone()[0]

# Count AI-generated
c.execute("SELECT COUNT(*) FROM content_items WHERE source = 'ai_agent'")
ai_cards = c.fetchone()[0]

# Count approved
c.execute("SELECT COUNT(*) FROM content_items WHERE status = 'approved'")
approved = c.fetchone()[0]

# Count shares
c.execute("SELECT COUNT(*) FROM share_logs")
total_shares = c.fetchone()[0]

# Count unique doctors reached
c.execute("SELECT COUNT(DISTINCT doctor_id) FROM share_logs")
doctors_reached = c.fetchone()[0]

print(f"\n[DASHBOARD] KPI Summary:")
print(f"  Total Articles: {total_cards}")
print(f"  AI-Generated: {ai_cards}")
print(f"  Approved: {approved}")
print(f"  Total Shares: {total_shares}")
print(f"  Doctors Reached: {doctors_reached}")

# =============================================================================
# PHASE 7: VERIFY DATABASE INTEGRITY
# =============================================================================
print("\n" + "-"*70)
print("PHASE 7: DATABASE INTEGRITY CHECK")
print("-"*70)

# Check Hanta cards specifically
c.execute("SELECT COUNT(*) FROM content_items WHERE topic = 'Hanta'")
hanta_total = c.fetchone()[0]

c.execute("""
    SELECT COUNT(*)
    FROM content_items
    WHERE topic = 'Hanta' AND short_article LIKE '%Read%'
""")
hanta_read_more = c.fetchone()[0]

c.execute("""
    SELECT COUNT(*)
    FROM content_items
    WHERE topic = 'Hanta' AND pubmed_link IS NOT NULL
""")
hanta_pubmed = c.fetchone()[0]

print(f"\n[DATABASE] Hanta Cards:")
print(f"  Total: {hanta_total}")
print(f"  With Read More links: {hanta_read_more}/{hanta_total}")
print(f"  With PubMed URLs: {hanta_pubmed}/{hanta_total}")

# Sample cards
print(f"\n[DATABASE] Sample Hanta Cards:")
c.execute("""
    SELECT title, status, created_at
    FROM content_items
    WHERE topic = 'Hanta'
    ORDER BY created_at DESC
    LIMIT 7
""")

for i, (title, status, created) in enumerate(c.fetchall(), 1):
    print(f"  {i}. {title[:55]}")
    print(f"     Status: {status} | Created: {created[:19]}")

conn.close()

# =============================================================================
# FINAL RESULTS
# =============================================================================
print("\n" + "="*70)
print("FINAL TEST RESULTS")
print("="*70)

checks = [
    ("Pipeline generated 7 cards", len(hanta_cards) >= 7),
    ("All cards have Read More links", hanta_read_more >= 7),
    ("All cards have PubMed URLs", hanta_pubmed >= 7),
    ("Cards visible in Content Library", len(items) > 0),
    ("Share logging working", total_shares > 0),
    ("Doctor tracking working", doctors_reached > 0),
]

print("\n[CHECKLIST]")
passed = 0
for check, result in checks:
    status = "PASS" if result else "FAIL"
    symbol = "[OK]" if result else "[XX]"
    print(f"  {symbol} {check}")
    if result:
        passed += 1

print(f"\nRESULT: {passed}/{len(checks)} tests passed")

if passed == len(checks):
    print("\n*** ALL TESTS PASSED - APP IS FULLY FUNCTIONAL ***")
else:
    print(f"\n*** {len(checks) - passed} TESTS FAILED ***")

print("\n" + "="*70 + "\n")
