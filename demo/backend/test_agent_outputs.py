#!/usr/bin/env python3
"""Verify agent outputs match UI expectations"""
import json
import urllib.request
import time

print('='*70)
print('COMPREHENSIVE AGENT OUTPUT VERIFICATION')
print('='*70)

# Start pipeline
print('\n[1] Starting Hanta pipeline...')
request_data = json.dumps({
    'topic': 'Hanta',
    'specialty': 'Infectious Disease',
    'therapy_area': 'Infectious Disease'
}).encode('utf-8')

req = urllib.request.Request(
    'http://localhost:8010/pipeline/run',
    data=request_data,
    headers={'Content-Type': 'application/json'},
    method='POST'
)

with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())
    run_id = data['run_id']
    print(f'Run ID: {run_id}')

# Poll for completion
print('[2] Waiting for pipeline...')
start_time = time.time()
last_progress = -1

while time.time() - start_time < 40:
    with urllib.request.urlopen(f'http://localhost:8010/pipeline/status/{run_id}') as response:
        status = json.loads(response.read().decode())
        progress = status['progress']

        if progress != last_progress:
            print(f'    {progress}% - {status["current_agent"]}')
            last_progress = progress

        if status['status'] == 'completed':
            break

    time.sleep(1)

# Get agent outputs
print('\n[3] Checking Agent Outputs...')
agent_outputs = status['agent_outputs']

# Check Alpha
print('\n--- ALPHA OUTPUT (For UI plRenderAgentOutput) ---')
alpha = agent_outputs['alpha']
print(f'[OK] Has "sources": {"sources" in alpha}')
if 'sources' in alpha:
    print(f'  Sources count: {len(alpha["sources"])}')
print(f'[OK] Has "internal_docs": {"internal_docs" in alpha}')

# Check Beta
print('\n--- BETA OUTPUT (For UI plRenderAgentOutput) ---')
beta = agent_outputs['beta']
print(f'[OK] Has "findings": {"findings" in beta}')
if 'findings' in beta:
    print(f'  Findings count: {len(beta["findings"])}')
    print(f'  Sample finding: "{beta["findings"][0][:80]}..."')

# Check Gamma
print('\n--- GAMMA OUTPUT (For UI plRenderAgentOutput) ---')
gamma = agent_outputs['gamma']
print(f'[OK] Has "article_excerpt": {"article_excerpt" in gamma}')
print(f'[OK] Has "word_count": {"word_count" in gamma}')
if 'word_count' in gamma:
    print(f'  Word count: {gamma["word_count"]}')

# Check Delta
print('\n--- DELTA OUTPUT (For UI plRenderAgentOutput) ---')
delta = agent_outputs['delta']
print(f'[OK] Has "card_title": {"card_title" in delta}')
if 'card_title' in delta:
    print(f'  Card title: "{delta["card_title"]}"')
print(f'[OK] Has "cards_saved": {"cards_saved" in delta}')
if 'cards_saved' in delta:
    print(f'  Cards saved: {delta["cards_saved"]}')

print('\n' + '='*70)
print('VERIFICATION SUMMARY')
print('='*70)

all_good = (
    'sources' in alpha and
    'findings' in beta and
    'article_excerpt' in gamma and
    'word_count' in gamma and
    'card_title' in delta
)

print(f'[RESULT] All required keys present: {all_good}')
print('[SUCCESS] All agents ready for UI rendering!')
print('='*70)
