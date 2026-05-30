#!/usr/bin/env python3
"""Test all topics to verify word counts and metadata."""
import requests
import time
import json

topics = [
    {"topic": "GLP-1", "specialty": "Endocrinology", "therapy_area": "Type 2 Diabetes Management"},
    {"topic": "SGLT2", "specialty": "Cardiology", "therapy_area": "Heart Failure Management"},
    {"topic": "PCOS", "specialty": "Obstetrics & Gynaecology", "therapy_area": "PCOS Management"},
]

for topic_req in topics:
    print("\n" + "=" * 80)
    print(f"TESTING TOPIC: {topic_req['topic']}")
    print("=" * 80)

    url = "http://127.0.0.1:8003/pipeline/run"
    response = requests.post(url, json=topic_req)
    data = response.json()
    run_id = data.get("run_id")

    # Poll for completion
    while True:
        status_url = f"http://127.0.0.1:8003/pipeline/status/{run_id}"
        status_response = requests.get(status_url)
        status_data = status_response.json()

        if status_data.get("status") == "completed":
            break

        time.sleep(1)

    # Extract results
    content_id = status_data.get("content_id")
    word_count = status_data.get("agent_outputs", {}).get("gamma", {}).get("word_count")

    print(f"Content ID: {content_id}")
    print(f"Article Word Count: {word_count}")

    # Query database to verify metadata
    import sqlite3
    conn = sqlite3.connect("pinnacleiq_demo.db")
    cursor = conn.cursor()

    cursor.execute("""SELECT pmid, doi, authors, publication_date, whatsapp_summary
                     FROM content_items WHERE id=?""", (content_id,))
    row = cursor.fetchone()

    if row:
        print(f"PMID: {row[0]}")
        print(f"DOI: {row[1]}")
        print(f"Authors: {row[2]}")
        print(f"Publication Date: {row[3]}")
        print(f"WhatsApp Summary: {row[4][:100]}..." if row[4] and len(row[4]) > 100 else f"WhatsApp Summary: {row[4]}")

        if word_count and word_count >= 250:
            print(f"[OK] Word count requirement met ({word_count} >= 250)")
        else:
            print(f"[FAIL] Word count below 250: {word_count}")

    conn.close()

print("\n" + "=" * 80)
print("ALL TESTS COMPLETE")
print("=" * 80)
