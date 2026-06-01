#!/usr/bin/env python3
"""Check what's in the database"""
import sqlite3

conn = sqlite3.connect('pinnacleiq_demo.db')
c = conn.cursor()

print("\n=== DATABASE TABLES ===")
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
for table in c.fetchall():
    c.execute(f"SELECT COUNT(*) FROM {table[0]}")
    count = c.fetchone()[0]
    print(f"  {table[0]}: {count} rows")

print("\n=== RECENT CONTENT CARDS ===")
c.execute("SELECT COUNT(*) FROM content_cards")
total = c.fetchone()[0]
print(f"Total cards: {total}")

c.execute("""
    SELECT id, topic, title, status, created_at
    FROM content_cards
    ORDER BY created_at DESC
    LIMIT 10
""")
rows = c.fetchall()
for row in rows:
    print(f"\nID: {row[0][:12]}...")
    print(f"  Topic: {row[1]}")
    print(f"  Title: {row[2][:70]}")
    print(f"  Status: {row[3]}")
    print(f"  Created: {row[4]}")

print("\n=== CHECKING FOR READ MORE LINKS ===")
c.execute("""
    SELECT COUNT(*) as total,
           SUM(CASE WHEN short_article LIKE '%Read%' THEN 1 ELSE 0 END) as with_read
    FROM content_cards
""")
total, with_read = c.fetchone()
print(f"Total cards: {total}")
print(f"Cards with 'Read' text: {with_read}")

c.execute("""
    SELECT COUNT(*)
    FROM content_cards
    WHERE short_article LIKE '%pubmed.ncbi.nlm.nih.gov%'
""")
with_pubmed_link = c.fetchone()[0]
print(f"Cards with PubMed URLs: {with_pubmed_link}")

print("\n=== RECENT PIPELINE RUNS ===")
c.execute("SELECT COUNT(*) FROM pipeline_runs")
run_count = c.fetchone()[0]
print(f"Total runs: {run_count}")

if run_count > 0:
    c.execute("""
        SELECT id, topic, status, created_at
        FROM pipeline_runs
        ORDER BY created_at DESC
        LIMIT 5
    """)
    for row in c.fetchall():
        print(f"\n  Run: {row[0][:12]}... | Topic: {row[1]} | Status: {row[2]} | Created: {row[3]}")

conn.close()
print("\n✅ Done")
