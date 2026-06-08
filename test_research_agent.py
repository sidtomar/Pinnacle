#!/usr/bin/env python3
"""
Test the Research Agent with Migraine and Cardiology topics
"""

import json
import requests
import time

def test_research_agent():
    BASE_URL = "http://localhost:8010"

    # Test 1: Migraine
    print("=" * 60)
    print("TEST 1: MIGRAINE TOPIC")
    print("=" * 60)
    print()

    migraine_payload = {
        "topic": "Migraine",
        "specialty": "Neurology",
        "therapy_area": "Neurology"
    }

    print("[TEST] Starting pipeline for Migraine...")
    print(f"Payload: {json.dumps(migraine_payload, indent=2)}")
    print()

    run_id_1 = None
    try:
        resp = requests.post(
            f"{BASE_URL}/pipeline/run",
            json=migraine_payload,
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            run_id_1 = data.get('run_id')
            print(f"[SUCCESS] Pipeline started!")
            print(f"Run ID: {run_id_1}")
            print(f"Status: {data.get('status')}")
        else:
            print(f"[ERROR] Status code: {resp.status_code}")
            print(f"Response: {resp.text}")
    except Exception as e:
        print(f"[ERROR] Failed to start pipeline: {e}")

    print()

    # Test 2: Cardiology
    print("=" * 60)
    print("TEST 2: CARDIOLOGY TOPIC")
    print("=" * 60)
    print()

    cardio_payload = {
        "topic": "Hypertension",
        "specialty": "Cardiology",
        "therapy_area": "Cardiology"
    }

    print("[TEST] Starting pipeline for Cardiology (Hypertension)...")
    print(f"Payload: {json.dumps(cardio_payload, indent=2)}")
    print()

    run_id_2 = None
    try:
        resp = requests.post(
            f"{BASE_URL}/pipeline/run",
            json=cardio_payload,
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            run_id_2 = data.get('run_id')
            print(f"[SUCCESS] Pipeline started!")
            print(f"Run ID: {run_id_2}")
            print(f"Status: {data.get('status')}")
        else:
            print(f"[ERROR] Status code: {resp.status_code}")
            print(f"Response: {resp.text}")
    except Exception as e:
        print(f"[ERROR] Failed to start pipeline: {e}")

    print()
    print("=" * 60)
    print("POLLING FOR COMPLETION")
    print("=" * 60)
    print()

    # Poll both pipelines
    run_ids = {
        'Migraine': run_id_1,
        'Cardiology': run_id_2
    }

    completed = {}

    for name, run_id in run_ids.items():
        if not run_id:
            print(f"[SKIP] {name} - No run ID")
            continue

        print(f"[POLLING] {name} (Run ID: {run_id})")
        start_time = time.time()

        for attempt in range(60):  # Max 60 seconds
            try:
                resp = requests.get(
                    f"{BASE_URL}/pipeline/status/{run_id}",
                    timeout=10
                )

                if resp.status_code == 200:
                    data = resp.json()
                    progress = data.get('progress', 0)
                    status = data.get('status', 'unknown')
                    current_agent = data.get('current_agent', 'N/A')

                    elapsed = int(time.time() - start_time)
                    print(f"  [{elapsed:2d}s] Progress: {progress:3d}% | Agent: {current_agent:8s} | Status: {status}")

                    if status == 'completed':
                        print(f"[COMPLETE] {name} finished!")
                        completed[name] = data
                        break
                    elif status == 'error':
                        print(f"[ERROR] {name} failed: {data.get('error', 'Unknown error')}")
                        break
                else:
                    print(f"  [ERROR] Status code: {resp.status_code}")
                    break

            except Exception as e:
                print(f"  [ERROR] Poll failed: {e}")
                break

            time.sleep(2)  # Wait 2 seconds before next poll

        print()

    # Show results
    print()
    print("=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print()

    for name, data in completed.items():
        print(f"\n[{name.upper()}]")
        print(f"  Status: {data.get('status')}")
        print(f"  Progress: {data.get('progress')}%")

        agent_outputs = data.get('agent_outputs', {})

        # Alpha
        alpha = agent_outputs.get('alpha', {})
        sources = alpha.get('sources', [])
        print(f"  Alpha Results:")
        print(f"    - Found {len(sources)} sources from PubMed")

        # Beta
        beta = agent_outputs.get('beta', {})
        findings = beta.get('findings', [])
        print(f"  Beta Results:")
        print(f"    - Extracted {len(findings)} key findings")
        if findings:
            print(f"    - First finding: {findings[0][:80]}...")

        # Gamma
        gamma = agent_outputs.get('gamma', {})
        article_excerpt = gamma.get('article_excerpt', '')
        word_count = gamma.get('word_count', 0)
        print(f"  Gamma Results:")
        print(f"    - Article length: {word_count} words")
        if article_excerpt:
            print(f"    - Excerpt: {article_excerpt[:100]}...")

        # Delta
        delta = agent_outputs.get('delta', {})
        card_title = delta.get('card_title', 'No title')
        cards_saved = delta.get('cards_saved', 0)
        print(f"  Delta Results:")
        print(f"    - Card title: '{card_title}'")
        print(f"    - Cards saved to library: {cards_saved}")

        # Check for hashtags that should be added
        print(f"\n  Expected Hashtags:")
        print(f"    - #Migraine (topic)" if name == 'Migraine' else f"    - #Cardiology (therapy area)")
        print(f"    - #Neurology (therapy area)" if name == 'Migraine' else f"    - #Hypertension (disease)")

    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_research_agent()
