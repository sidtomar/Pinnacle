import sqlite3

db_path = r"D:\Codebase\Pinnacle\pinnacleiq_demo.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

print("Database Schema for content_items:")
print("=" * 50)
c.execute("PRAGMA table_info(content_items)")
columns = c.fetchall()
for col in columns:
    print(f"  {col[1]:20} ({col[2]})")

print("\n\nTotal Records in Database:")
print("=" * 50)
c.execute("SELECT COUNT(*) FROM content_items")
total = c.fetchone()[0]
print(f"Total content items: {total}")

c.execute("SELECT COUNT(DISTINCT topic) FROM content_items")
topics = c.fetchone()[0]
print(f"Unique topics: {topics}")

c.execute("SELECT DISTINCT topic FROM content_items ORDER BY topic")
topic_list = c.fetchall()
print(f"\nTopics in database:")
for t in topic_list:
    print(f"  - {t[0]}")

print("\n\nSample Data (Most Recent 4 Cards):")
print("=" * 50)
c.execute("""
    SELECT id, title, topic, therapy_area, sub_category, short_article, tags, status
    FROM content_items
    ORDER BY created_at DESC
    LIMIT 4
""")

rows = c.fetchall()
for i, row in enumerate(rows, 1):
    print(f"\n[{i}] ID: {row[0]}")
    print(f"    Title: {row[1]}")
    print(f"    Topic: {row[2]}")
    print(f"    Therapy Area: {row[3]}")
    print(f"    Sub Category: {row[4]}")
    print(f"    Tags: {row[6]}")
    print(f"    Status: {row[7]}")
    print(f"    Article: {row[5][:120]}...")

conn.close()
