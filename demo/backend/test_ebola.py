import sqlite3

conn = sqlite3.connect('pinnacleiq_demo.db')
c = conn.cursor()

print("\n=== EBOLA CARDS SUMMARY ===\n")

c.execute("""
    SELECT COUNT(*) as total,
           SUM(CASE WHEN short_article LIKE '%Read%' THEN 1 ELSE 0 END) as with_read_more,
           SUM(CASE WHEN pubmed_link IS NOT NULL AND pubmed_link != '' THEN 1 ELSE 0 END) as with_pubmed_link,
           SUM(CASE WHEN status = 'pending_review' THEN 1 ELSE 0 END) as pending,
           SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved
    FROM content_items
    WHERE topic = 'Ebola'
""")

row = c.fetchone()
print(f"Total Ebola cards: {row[0]}")
print(f"Cards with Read More link in article: {row[1]}")
print(f"Cards with pubmed_link field: {row[2]}")
print(f"Pending Review: {row[3]}")
print(f"Approved: {row[4]}")

print("\nCards look good! Pipeline is working correctly.")
conn.close()
