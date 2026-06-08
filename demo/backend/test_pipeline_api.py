#!/usr/bin/env python3
"""Test the full pipeline via API"""
import urllib.request
import json
import time

print("\n" + "="*60)
print("TESTING HANTA PIPELINE VIA API")
print("="*60)

# Step 1: Start pipeline
print("\n[1] Starting Hanta pipeline...")
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
    print(f"    Run ID: {run_id}")
    print(f"    Status: {data['status']}")

# Step 2: Poll for completion
print("\n[2] Waiting for pipeline to complete...")
start_time = time.time()
timeout = 30  # 30 seconds max wait

while time.time() - start_time < timeout:
    with urllib.request.urlopen(f"http://localhost:8010/pipeline/status/{run_id}") as response:
        status_data = json.loads(response.read().decode())
        progress = status_data['progress']
        agent = status_data['current_agent']
        status = status_data['status']

        print(f"    Progress: {progress}% | Agent: {agent} | Status: {status}", end='\r')

        if status == 'completed':
            print(f"\n    COMPLETED in {time.time() - start_time:.1f}s")
            break

    time.sleep(1)

# Step 3: Check results
print("\n[3] Pipeline Results:")
all_content_ids = status_data.get('all_content_ids', [])
print(f"    Cards saved: {len(all_content_ids)}")

# Step 4: Verify cards in database
print("\n[4] Verifying cards...")
import sqlite3
conn = sqlite3.connect('pinnacleiq_demo.db')
c = conn.cursor()

c.execute("SELECT COUNT(*) FROM content_items WHERE topic = 'Hanta'")
total = c.fetchone()[0]

c.execute("""
    SELECT COUNT(*)
    FROM content_items
    WHERE topic = 'Hanta' AND short_article LIKE '%Read%'
""")
with_read_more = c.fetchone()[0]

c.execute("""
    SELECT COUNT(*)
    FROM content_items
    WHERE topic = 'Hanta' AND pubmed_link IS NOT NULL
""")
with_pubmed = c.fetchone()[0]

print(f"    Hanta cards in DB: {total}")
print(f"    With Read More: {with_read_more}/{total}")
print(f"    With PubMed URL: {with_pubmed}/{total}")

# Step 5: List the cards
print("\n[5] Cards generated:")
c.execute("""
    SELECT title
    FROM content_items
    WHERE topic = 'Hanta'
    ORDER BY created_at DESC
    LIMIT 7
""")

for i, (title,) in enumerate(c.fetchall(), 1):
    print(f"    {i}. {title[:60]}")

conn.close()

# Final result
print("\n" + "="*60)
if total >= 7 and with_read_more == total:
    print("SUCCESS: Hanta pipeline working! 7 cards with Read More links")
else:
    print(f"RESULT: {total} cards | {with_read_more} with Read More | {with_pubmed} with PubMed")

print("="*60 + "\n")
