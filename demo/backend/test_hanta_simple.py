#!/usr/bin/env python3
"""Simple test for Hanta pipeline - no emoji output"""
import sys
sys.path.insert(0, "../..")

import sqlite3
from mock_runner import run_mock_pipeline
from research_agent_system.store import get_store

# Setup
run_id = "test-hanta-simple"
topic = "Hanta"
specialty = "Infectious Disease"
therapy_area = "Infectious Disease"

print("\n" + "="*60)
print("HANTA PIPELINE TEST")
print("="*60)

# Run pipeline
run_store = {
    run_id: {
        "status": "running",
        "topic": topic,
        "specialty": specialty,
        "progress": 0,
        "agent_outputs": {}
    }
}

run_mock_pipeline(topic, specialty, therapy_area, run_store, run_id)
run_data = run_store[run_id]

# Check all cards
all_cards = run_data.get("all_cards", [])
print(f"\nStep 1: Agent Alpha -> Delta generated {len(all_cards)} cards")

# Check each card
for i, card in enumerate(all_cards, 1):
    has_read_more = "Read" in (card.get("short_article", "") or "")
    has_pubmed = bool(card.get("pubmed_link"))
    print(f"  Card {i}: {card.get('title', 'Unknown')[:55]}")
    print(f"    - Has Read More: {has_read_more}")
    print(f"    - Has PubMed URL: {has_pubmed}")

# Save to database
store = get_store()
store.setup()

print(f"\nStep 2: Saving {len(all_cards)} cards to database...")
saved_count = 0
for card in all_cards:
    try:
        store.save_content_card(card)
        saved_count += 1
    except Exception as e:
        print(f"  Error saving: {e}")

print(f"  Successfully saved: {saved_count}/{len(all_cards)}")

# Verify in database
conn = sqlite3.connect('pinnacleiq_demo.db')
c = conn.cursor()

c.execute("SELECT COUNT(*) FROM content_items WHERE topic = ?", (topic,))
db_count = c.fetchone()[0]

c.execute("""
    SELECT COUNT(*)
    FROM content_items
    WHERE topic = ? AND short_article LIKE '%Read%'
""", (topic,))
with_read_more = c.fetchone()[0]

c.execute("""
    SELECT COUNT(*)
    FROM content_items
    WHERE topic = ? AND pubmed_link IS NOT NULL
""", (topic,))
with_pubmed = c.fetchone()[0]

print(f"\nStep 3: Database verification")
print(f"  Total cards in DB: {db_count}")
print(f"  With Read More link: {with_read_more}")
print(f"  With PubMed URL: {with_pubmed}")

# Show card list
print(f"\nCards saved:")
c.execute("""
    SELECT title
    FROM content_items
    WHERE topic = ?
    ORDER BY created_at DESC
    LIMIT 7
""", (topic,))

for i, (title,) in enumerate(c.fetchall(), 1):
    print(f"  {i}. {title[:60]}")

conn.close()

# Results
print("\n" + "="*60)
if len(all_cards) == 7 and with_read_more == 7:
    print("SUCCESS: 7 cards generated with Read More links!")
else:
    print(f"CARDS: {len(all_cards)} | READ MORE: {with_read_more} | PUBMED: {with_pubmed}")

print("="*60 + "\n")
