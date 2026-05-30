#!/usr/bin/env python3
"""Check if database schema has new metadata columns."""
import sqlite3

conn = sqlite3.connect("pinnacleiq_demo.db")
cursor = conn.cursor()

# Get table schema
cursor.execute("PRAGMA table_info(content_items)")
columns = cursor.fetchall()

print("Database columns in content_items table:")
print("=" * 60)
col_names = []
for col in columns:
    cid, name, type_, notnull, dflt_value, pk = col
    col_names.append(name)
    print(f"  {name:<35} {type_:<10}")

# Check for new columns
new_cols = ['pmid', 'doi', 'authors', 'publication_date', 'relevant_doctor_specialties',
            'whatsapp_summary', 'pubmed_link', 'full_text_link']

print("\n" + "=" * 60)
print("NEW METADATA COLUMNS CHECK:")
print("=" * 60)
for new_col in new_cols:
    status = "PRESENT" if new_col in col_names else "MISSING"
    print(f"  {new_col:<35} {status}")

conn.close()
