#!/usr/bin/env python3
"""Test pipeline with enhanced logging output."""
import requests
import time
import json

url = "http://127.0.0.1:8002/pipeline/run"
payload = {
    "topic": "GLP-1",
    "specialty": "Endocrinology",
    "therapy_area": "Type 2 Diabetes Management"
}

print("=" * 80)
print("TRIGGERING PIPELINE RUN")
print("=" * 80)
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, json=payload)
    data = response.json()
    run_id = data.get("run_id")
    print(f"\nRun ID: {run_id}")
    print(f"Response: {json.dumps(data, indent=2)}")

    # Poll for completion
    print("\n" + "=" * 80)
    print("POLLING FOR COMPLETION...")
    print("=" * 80)

    while True:
        status_url = f"http://127.0.0.1:8002/pipeline/status/{run_id}"
        status_response = requests.get(status_url)
        status_data = status_response.json()

        status = status_data.get("status")
        progress = status_data.get("progress")
        print(f"Status: {status} | Progress: {progress}%")

        if status == "completed":
            print("\n" + "=" * 80)
            print("PIPELINE COMPLETED")
            print("=" * 80)
            print(json.dumps(status_data, indent=2))
            break

        time.sleep(1)

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
