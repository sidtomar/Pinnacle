#!/usr/bin/env python3
"""Test script to verify all 15 metadata fields are in the database."""
import sqlite3
import json

conn = sqlite3.connect("pinnacleiq_demo.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get the latest content added
cursor.execute("SELECT * FROM content_items ORDER BY created_at DESC LIMIT 1")
row = cursor.fetchone()

if row:
    print("=" * 80)
    print("LATEST CONTENT RECORD FROM DATABASE")
    print("=" * 80)

    d = dict(row)

    # Display key fields
    print(f"\nTitle: {d.get('title', 'N/A')}")
    print(f"Topic: {d.get('topic', 'N/A')}")
    print(f"Specialty: {d.get('specialty', 'N/A')}")
    print(f"Therapy Area: {d.get('therapy_area', 'N/A')}")
    print(f"Status: {d.get('status', 'N/A')}")

    print("\n" + "=" * 80)
    print("METADATA FIELDS VALIDATION (15-Field Template):")
    print("=" * 80)

    metadata_fields = {
        "pmid": "PMID",
        "doi": "DOI",
        "authors": "Authors",
        "publication_date": "Publication Date",
        "relevant_doctor_specialties": "Relevant Doctor Specialties",
        "whatsapp_summary": "WhatsApp Summary",
        "pubmed_link": "PubMed Link",
        "full_text_link": "Full Text Link",
        "tags": "Tags",
        "sub_category": "Sub-category",
        "source_journals": "Source Journals",
        "specialty": "Specialty",
        "therapy_area": "Therapy Area",
        "summary": "Summary/Abstract",
        "title": "Title"
    }

    print(f"\n{'Field':<35} {'Status':<15} {'Value (Preview)':<50}")
    print("-" * 100)

    populated_count = 0
    for db_field, label in metadata_fields.items():
        val = d.get(db_field)
        if val:
            status = "[OK]"
            populated_count += 1
        else:
            status = "[MISSING]"

        # Truncate long values
        if val:
            val_str = str(val)[:50]
        else:
            val_str = ""

        print(f"{label:<35} {status:<15} {val_str:<50}")

    print("-" * 100)
    print(f"\nTOTAL: {populated_count}/15 fields populated")

    # Check article length
    short_article = d.get('short_article', '')
    word_count = len(short_article.split())
    print(f"\nArticle Word Count: {word_count} words")
    print(f"Minimum Required: 250 words")
    status_msg = "MEETS REQUIREMENT" if word_count >= 250 else "BELOW REQUIREMENT"
    print(f"Status: {status_msg}")

    # Show WhatsApp summary
    if d.get('whatsapp_summary'):
        summary_words = len(d['whatsapp_summary'].split())
        print(f"\nWhatsApp Summary Word Count: {summary_words} words")
        print(f"Preview: {d['whatsapp_summary'][:100]}...")

else:
    print("ERROR: No content found in database")

conn.close()
