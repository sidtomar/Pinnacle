#!/usr/bin/env python3
"""Test to verify MOCK_LIBRARY has all metadata fields."""
from mock_runner import MOCK_LIBRARY, _generic_content

print("=" * 80)
print("MOCK_LIBRARY['GLP-1'] STRUCTURE CHECK")
print("=" * 80)

glp1_content = MOCK_LIBRARY.get("GLP-1", {})

metadata_fields = [
    "pmid", "doi", "authors", "publication_date",
    "relevant_doctor_specialties", "whatsapp_summary",
    "pubmed_link", "full_text_link"
]

print(f"\nTotal keys in MOCK_LIBRARY['GLP-1']: {len(glp1_content)}")
print("Keys:", list(glp1_content.keys()))

print("\n" + "=" * 80)
print("NEW METADATA FIELDS IN MOCK_LIBRARY['GLP-1']:")
print("=" * 80)

for field in metadata_fields:
    val = glp1_content.get(field)
    if val:
        status = "PRESENT"
        preview = str(val)[:60] if len(str(val)) > 60 else str(val)
    else:
        status = "MISSING"
        preview = "N/A"

    print(f"  {field:<35} [{status:<10}] {preview}")

print("\n" + "=" * 80)
print("_generic_content() TEST:")
print("=" * 80)

generic = _generic_content("TEST TOPIC", "Endocrinology", "Test Therapy")
for field in metadata_fields:
    val = generic.get(field)
    if val:
        print(f"  {field:<35} [OK]")
    else:
        print(f"  {field:<35} [MISSING]")
