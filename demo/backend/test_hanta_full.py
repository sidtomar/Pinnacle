#!/usr/bin/env python3
"""Full end-to-end test of Hanta pipeline"""
import sys
sys.path.insert(0, "../..")

import sqlite3
import json
from mock_runner import run_mock_pipeline

# Setup
run_id = "test-hanta-full"
topic = "Hanta"
specialty = "Infectious Disease"
therapy_area = "Infectious Disease"

print("\n" + "="*70)
print("PINNACLEIQ PIPELINE TEST: HANTA")
print("="*70)

# Mock run storage
run_store = {
    run_id: {
        "status": "running",
        "topic": topic,
        "specialty": specialty,
        "progress": 0,
        "agent_outputs": {}
    }
}

# Run pipeline
print("\n[1] Running mock pipeline...")
run_mock_pipeline(topic, specialty, therapy_area, run_store, run_id)

run_data = run_store[run_id]

# Check results
print("\n[2] Pipeline Results:")
print(f"    Status: {run_data['status']}")
print(f"    Progress: {run_data['progress']}%")

# Agent Alpha
alpha_output = run_data.get("agent_outputs", {}).get("alpha", {})
alpha_papers = len(alpha_output.get("papers", []))
print(f"\n    ALPHA Output: {alpha_output.get('summary', '')}")
print(f"    ↳ Papers found: {alpha_papers}")

# Agent Beta
beta_output = run_data.get("agent_outputs", {}).get("beta", {})
print(f"\n    BETA Output: {beta_output.get('summary', '')}")

# Agent Gamma
gamma_output = run_data.get("agent_outputs", {}).get("gamma", {})
gamma_messages = len(gamma_output.get("messages", []))
print(f"\n    GAMMA Output: {gamma_output.get('summary', '')}")
print(f"    ↳ Shareable messages: {gamma_messages}")

# Agent Delta
delta_output = run_data.get("agent_outputs", {}).get("delta", {})
delta_cards = delta_output.get("cards_saved", 0)
print(f"\n    DELTA Output: {delta_output.get('summary', '')}")
print(f"    ↳ Cards to save: {delta_cards}")

# Get all cards
all_cards = run_data.get("all_cards", [])
print(f"\n[3] Cards Generated: {len(all_cards)}")

for i, card in enumerate(all_cards, 1):
    has_read_more = "Read" in (card.get("short_article", "") or "")
    has_pubmed = card.get("pubmed_link", "")
    print(f"    Card {i}: {card.get('title', '')[:60]}...")
    print(f"      >> Read More: {'YES' if has_read_more else 'NO'}")
    print(f"      >> PubMed Link: {has_pubmed[:50]}...")

# Verify database integration
print(f"\n[4] Database Integration:")

# Import store
from research_agent_system.store import get_store

store = get_store()
store.setup()

# Save cards
saved_ids = []
for card in all_cards:
    try:
        cid = store.save_content_card(card)
        saved_ids.append(cid)
        print(f"    [OK] Saved card {len(saved_ids)}: {cid[:12]}...")
    except Exception as e:
        print(f"    [FAIL] {e}")

print(f"\n[5] Database Verification:")

conn = sqlite3.connect('pinnacleiq_demo.db')
c = conn.cursor()

# Check Hanta cards in database
c.execute("SELECT COUNT(*) FROM content_items WHERE topic = ?", (topic,))
total_hanta = c.fetchone()[0]

c.execute("""
    SELECT COUNT(*)
    FROM content_items
    WHERE topic = ? AND short_article LIKE '%Read%'
""", (topic,))
with_read_more = c.fetchone()[0]

c.execute("""
    SELECT COUNT(*)
    FROM content_items
    WHERE topic = ? AND pubmed_link IS NOT NULL AND pubmed_link != ''
""", (topic,))
with_pubmed = c.fetchone()[0]

print(f"    Total '{topic}' cards in DB: {total_hanta}")
print(f"    Cards with Read More link: {with_read_more}/{total_hanta}")
print(f"    Cards with PubMed URL: {with_pubmed}/{total_hanta}")

# List them
print(f"\n    Cards in database:")
c.execute("""
    SELECT id, title, status
    FROM content_items
    WHERE topic = ?
    ORDER BY created_at DESC
    LIMIT 7
""", (topic,))

for row in c.fetchall():
    print(f"      • {row[1][:60]}... | Status: {row[2]}")

conn.close()

# Final verdict
print("\n" + "="*70)
expected = 7
if len(all_cards) == expected and with_read_more == expected and with_pubmed == expected:
    print(f"PASS: {expected} papers --> {expected} cards with Read More links!")
else:
    print(f"PARTIAL:")
    print(f"    Generated: {len(all_cards)}/{expected} cards")
    print(f"    With Read More: {with_read_more}/{expected}")
    print(f"    With PubMed Link: {with_pubmed}/{expected}")

print("="*70 + "\n")
