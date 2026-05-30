#!/usr/bin/env python3
"""Debug: Check actual values in new metadata columns."""
import sqlite3

conn = sqlite3.connect("pinnacleiq_demo.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get the latest content
cursor.execute("""SELECT id, title, pmid, doi, authors, publication_date,
                         whatsapp_summary, pubmed_link, full_text_link
                  FROM content_items ORDER BY created_at DESC LIMIT 1""")
row = cursor.fetchone()

if row:
    d = dict(row)
    print("Latest content record - Metadata field values:")
    print("=" * 80)
    for key, val in d.items():
        if val is None:
            print(f"  {key:<30} = NULL")
        else:
            if len(str(val)) > 60:
                print(f"  {key:<30} = {str(val)[:60]}...")
            else:
                print(f"  {key:<30} = {val}")

    # Check specific fields
    print("\n" + "=" * 80)
    print("ISSUE DIAGNOSIS:")
    print("=" * 80)

    null_fields = [k for k, v in d.items() if v is None]
    if null_fields:
        print(f"NULL fields: {', '.join(null_fields)}")
        print("\nPossible causes:")
        print("1. Fields not included in MOCK_LIBRARY entry")
        print("2. Fields not passed to save_content_card()")
        print("3. save_content_card() not including them in INSERT")
    else:
        print("All metadata fields have values!")

conn.close()
