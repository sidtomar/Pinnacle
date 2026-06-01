import sqlite3

conn = sqlite3.connect('pinnacleiq_demo.db')
c = conn.cursor()

print("\n=== CHECKING EBOLA CARDS FOR READ MORE LINKS ===\n")

c.execute("""
    SELECT id, title, pubmed_link, short_article
    FROM content_items
    WHERE topic = 'Ebola'
    ORDER BY created_at DESC
    LIMIT 3
""")

for row in c.fetchall():
    card_id = row[0][:12]
    title = row[1][:70]
    pubmed_link = row[2]
    article = row[3] if row[3] else ""
    
    has_read_more = "Read" in article
    has_pubmed_url = "pubmed.ncbi.nlm.nih.gov" in article
    
    print(f"Card: {card_id}...")
    print(f"Title: {title}")
    print(f"PubMed Link (field): {pubmed_link}")
    print(f"Has 'Read More' text: {has_read_more}")
    print(f"Has PubMed URL in article: {has_pubmed_url}")
    
    if article and len(article) > 400:
        print(f"Article tail: ...{article[-400:]}\n")

conn.close()
