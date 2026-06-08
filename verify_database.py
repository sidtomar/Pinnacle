#!/usr/bin/env python3
"""
Verify that content cards were saved to database with proper metadata
"""

import sqlite3

db_path = r"D:\Codebase\Pinnacle\pinnacleiq_demo.db"

try:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    print("=" * 70)
    print("DATABASE VERIFICATION - CONTENT CARDS")
    print("=" * 70)
    print()

    # Check for Migraine cards
    print("[MIGRAINE TOPIC]")
    print("-" * 70)
    c.execute("""
        SELECT id, title, topic, therapy_area, disease, short_article,
               pubmed_link, tags, status, created_at
        FROM content_items
        WHERE topic = 'Migraine'
        ORDER BY created_at DESC
        LIMIT 3
    """)

    migraine_cards = c.fetchall()
    print(f"Total Migraine cards in database: {len(migraine_cards)}")
    print()

    if migraine_cards:
        card = migraine_cards[0]
        print("Sample Card (Most Recent):")
        print(f"  ID: {card[0]}")
        print(f"  Title: {card[1]}")
        print(f"  Topic: {card[2]}")
        print(f"  Therapy Area: {card[3]}")
        print(f"  Disease: {card[4]}")
        print(f"  Article Preview: {card[5][:100]}...")
        print(f"  PubMed Link: {card[6]}")
        print(f"  Tags: {card[7]}")
        print(f"  Status: {card[8]}")
        print(f"  Created: {card[9]}")

    print()
    print()
    print("[CARDIOLOGY/HYPERTENSION TOPIC]")
    print("-" * 70)

    c.execute("""
        SELECT id, title, topic, therapy_area, disease, short_article,
               pubmed_link, tags, status, created_at
        FROM content_items
        WHERE topic = 'Hypertension'
        ORDER BY created_at DESC
        LIMIT 3
    """)

    cardio_cards = c.fetchall()
    print(f"Total Hypertension cards in database: {len(cardio_cards)}")
    print()

    if cardio_cards:
        card = cardio_cards[0]
        print("Sample Card (Most Recent):")
        print(f"  ID: {card[0]}")
        print(f"  Title: {card[1]}")
        print(f"  Topic: {card[2]}")
        print(f"  Therapy Area: {card[3]}")
        print(f"  Disease: {card[4]}")
        print(f"  Article Preview: {card[5][:100]}...")
        print(f"  PubMed Link: {card[6]}")
        print(f"  Tags: {card[7]}")
        print(f"  Status: {card[8]}")
        print(f"  Created: {card[9]}")

    print()
    print()
    print("[HASHTAG VERIFICATION]")
    print("-" * 70)
    print()

    # Check tags for hashtags
    print("Checking for hashtags in tags field...")
    print()

    if migraine_cards:
        tags = migraine_cards[0][7]
        print(f"Migraine Card Tags: {tags}")
        if tags:
            tag_list = [t.strip() for t in tags.split(',')]
            print(f"  Tag list: {tag_list}")
            has_hashtags = any(t.startswith('#') for t in tag_list)
            print(f"  Contains hashtags: {'YES' if has_hashtags else 'NO'}")

    print()

    if cardio_cards:
        tags = cardio_cards[0][7]
        print(f"Hypertension Card Tags: {tags}")
        if tags:
            tag_list = [t.strip() for t in tags.split(',')]
            print(f"  Tag list: {tag_list}")
            has_hashtags = any(t.startswith('#') for t in tag_list)
            print(f"  Contains hashtags: {'YES' if has_hashtags else 'NO'}")

    print()
    print()
    print("[READ MORE LINK VERIFICATION]")
    print("-" * 70)
    print()

    # Check for Read More links
    if migraine_cards:
        article = migraine_cards[0][5]
        has_read_more = "Read More" in article
        has_pubmed_link = migraine_cards[0][6] is not None and migraine_cards[0][6] != ''
        print(f"Migraine Card:")
        print(f"  Has 'Read More' text: {'YES' if has_read_more else 'NO'}")
        print(f"  Has PubMed link: {'YES' if has_pubmed_link else 'NO'}")
        print(f"  PubMed URL: {migraine_cards[0][6]}")

    print()

    if cardio_cards:
        article = cardio_cards[0][5]
        has_read_more = "Read More" in article
        has_pubmed_link = cardio_cards[0][6] is not None and cardio_cards[0][6] != ''
        print(f"Hypertension Card:")
        print(f"  Has 'Read More' text: {'YES' if has_read_more else 'NO'}")
        print(f"  Has PubMed link: {'YES' if has_pubmed_link else 'NO'}")
        print(f"  PubMed URL: {cardio_cards[0][6]}")

    conn.close()

    print()
    print("=" * 70)
    print("VERIFICATION COMPLETE")
    print("=" * 70)

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
