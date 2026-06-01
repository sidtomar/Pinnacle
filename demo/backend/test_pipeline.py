#!/usr/bin/env python3
"""Test the pipeline end-to-end"""
import sys
sys.path.insert(0, "../..")
import sqlite3
import json
from mock_runner import run_mock_pipeline
from store import get_store

# Setup
run_id = "test-run-001"
topic = "Ebola"
specialty = "Infectious Disease"
therapy_area = "Infectious Disease"

# Initialize store
store = get_store()
store.setup()

# Mock run storage (simulates app.py's pipeline_runs dict)
run_store = {
    run_id: {
        "status": "running",
        "topic": topic,
        "specialty": specialty,
        "progress": 0,
    }
}

print(f"\n=== Testing Pipeline for Topic: {topic} ===\n")

# Run pipeline
print("Running mock pipeline...")
run_mock_pipeline(topic, specialty, therapy_area, run_store, run_id)

# Check results
run_data = run_store[run_id]
print(f"\nPipeline Status: {run_data['status']}")
print(f"Progress: {run_data['progress']}%")
print(f"All Cards Generated: {len(run_data.get('all_cards', []))}")

# Show agent outputs
for agent in ["alpha", "beta", "gamma", "delta"]:
    output = run_data.get("agent_outputs", {}).get(agent, {})
    summary = output.get("summary", "")
    if summary:
        print(f"\n{agent.upper()}: {summary}")

# Save cards to database
print("\n\n=== Saving to Database ===")
all_cards = run_data.get("all_cards", [])
saved_ids = []
for card in all_cards:
    try:
        cid = store.save_content_card(card)
        saved_ids.append(cid)
        print(f"✅ Saved: {card.get('title', '')[:60]}... → {cid}")
    except Exception as e:
        print(f"❌ Failed to save: {e}")

print(f"\nTotal cards saved: {len(saved_ids)}")

# Verify in database
print("\n\n=== Verifying Database ===")
conn = sqlite3.connect('pinnacleiq_demo.db')
c = conn.cursor()

c.execute("SELECT COUNT(*) FROM content_cards WHERE topic = ?", (topic,))
count = c.fetchone()[0]
print(f"Content cards for '{topic}' in database: {count}")

c.execute("SELECT id, title, pubmed_link FROM content_cards WHERE topic = ? ORDER BY created_at DESC", (topic,))
for row in c.fetchall():
    print(f"  • {row[1][:60]}...")
    print(f"    PubMed: {row[2]}")

c.execute("SELECT SUM(CASE WHEN short_article LIKE '%Read More%' THEN 1 ELSE 0 END) FROM content_cards WHERE topic = ?", (topic,))
cards_with_read_more = c.fetchone()[0] or 0
print(f"\nCards with 'Read More' link: {cards_with_read_more}/{count}")

conn.close()

print("\n✅ Test Complete")
