import sqlite3

conn = sqlite3.connect('pinnacleiq_demo.db')
c = conn.cursor()

print("\n=== CONTENT_ITEMS TABLE SCHEMA ===")
c.execute("PRAGMA table_info(content_items)")
for row in c.fetchall():
    col_id, name, type_, notnull, default, pk = row
    print(f"  {name}: {type_} (PK={pk})")

print("\n=== COLUMNS ===")
c.execute("SELECT * FROM content_items LIMIT 1")
cols = [description[0] for description in c.description]
for col in cols:
    print(f"  - {col}")

print("\n=== SAMPLE DATA ===")
c.execute("SELECT id, title, status FROM content_items ORDER BY created_at DESC LIMIT 3")
for row in c.fetchall():
    print(f"  {row[0][:12]}... | {row[1][:60]}... | {row[2]}")

conn.close()
print("\nDone")
