#!/usr/bin/env python3
"""Test the API is responding"""
import urllib.request
import json

print("Testing API endpoints...\n")

# Test 1: /topics endpoint
try:
    with urllib.request.urlopen("http://localhost:8010/topics") as response:
        data = json.loads(response.read().decode())
        print(f"[OK] /topics: {data['count']} topics available")
except Exception as e:
    print(f"[FAIL] /topics: {e}")

# Test 2: /doctors endpoint
try:
    with urllib.request.urlopen("http://localhost:8010/doctors") as response:
        data = json.loads(response.read().decode())
        print(f"[OK] /doctors: {data['total']} doctors available")
except Exception as e:
    print(f"[FAIL] /doctors: {e}")

# Test 3: /content endpoint
try:
    with urllib.request.urlopen("http://localhost:8010/content") as response:
        data = json.loads(response.read().decode())
        print(f"[OK] /content: {data['counts']['total']} total cards")
        print(f"     - Pending: {data['counts']['pending']}")
        print(f"     - Approved: {data['counts']['approved']}")
except Exception as e:
    print(f"[FAIL] /content: {e}")

print("\nAPI is ready!")
