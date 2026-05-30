#!/usr/bin/env python3
"""Direct test of save_content_card with full metadata."""
import sys
import os

# Add path to research_agent_system
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "research_agent_system"))

from store import get_store
from mock_runner import MOCK_LIBRARY

store = get_store()
store.setup()

# Test 1: Get content from MOCK_LIBRARY
print("=" * 80)
print("TEST 1: Content from MOCK_LIBRARY['GLP-1']")
print("=" * 80)

content = MOCK_LIBRARY["GLP-1"].copy()
content["topic"] = "GLP-1"
content["specialty"] = "Endocrinology"
content["therapy_area"] = "Type 2 Diabetes Management"

print(f"Keys in content dict: {len(content.keys())}")
print(f"Keys: {list(content.keys())}\n")

print("Metadata fields in content dict:")
for field in ['pmid', 'doi', 'authors', 'publication_date', 'whatsapp_summary', 'pubmed_link', 'full_text_link']:
    val = content.get(field)
    status = "PRESENT" if val else "MISSING"
    print(f"  {field:<35} [{status:<10}] {str(val)[:60] if val else 'N/A'}")

# Test 2: Call save_content_card
print("\n" + "=" * 80)
print("TEST 2: Calling save_content_card()")
print("=" * 80)

content_id = store.save_content_card(content)
print(f"\nContent saved with ID: {content_id}")

# Test 3: Query database to verify
print("\n" + "=" * 80)
print("TEST 3: Verifying in database")
print("=" * 80)

import sqlite3
conn = sqlite3.connect("pinnacleiq_demo.db")
cursor = conn.cursor()
cursor.execute("""SELECT pmid, doi, authors, publication_date, whatsapp_summary, pubmed_link, full_text_link
                 FROM content_items WHERE id=?""", (content_id,))
row = cursor.fetchone()

if row:
    print(f"Fields in database:")
    fields = ['pmid', 'doi', 'authors', 'publication_date', 'whatsapp_summary', 'pubmed_link', 'full_text_link']
    for i, field in enumerate(fields):
        val = row[i]
        status = "PRESENT" if val else "NULL"
        print(f"  {field:<35} [{status:<10}] {str(val)[:60] if val else 'NULL'}")
else:
    print("ERROR: Record not found in database!")

conn.close()
