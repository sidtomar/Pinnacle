import sys
sys.path.insert(0, "../..")
from mock_runner import _generic_sources

print("\n=== Testing _generic_sources for Hanta ===\n")

sources = _generic_sources("Hanta", "Infectious Disease", "Infectious Disease")

print(f"Number of papers generated: {len(sources)}\n")

for i, src in enumerate(sources, 1):
    print(f"{i}. {src['title'][:70]}")
    print(f"   URL: {src['url']}\n")

print(f"Total: {len(sources)} papers")
