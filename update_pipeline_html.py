#!/usr/bin/env python3
"""
Update the Research Pipeline page HTML with the new Research Agent design.
"""

import re

html_file = r"D:\Codebase\Pinnacle\PinnacleIQ_Portal.html"

# Read the file
with open(html_file, "r", encoding="utf-8") as f:
    content = f.read()

# Find the pipeline page section boundaries
# Look for the div with id="pg-pipeline"
pipeline_start = content.find('<div class="pg" id="pg-pipeline">')
# Next page is pg-dashboard
pipeline_end = content.find('<div class="pg" id="pg-dashboard">', pipeline_start)

if pipeline_start < 0:
    print(f"[ERROR] Could not find pipeline page start (searched for pg-pipeline div)")
    exit(1)

if pipeline_end < 0:
    print(f"[ERROR] Could not find pipeline page end (searched for pg-doctors div)")
    exit(1)

print(f"[INFO] Found pipeline page from position {pipeline_start} to {pipeline_end}")

# New Research Agent page HTML
new_page_html = '''<!-- ════════════════════════ RESEARCH AGENT PAGE ════════════════════════ -->
    <div class="pg" id="pg-pipeline">
      <style>
        .ra-hero{background:linear-gradient(135deg,var(--navy) 0%,#1E3A6E 100%);border-radius:var(--rlg);padding:24px 28px;margin-bottom:24px;display:flex;align-items:center;gap:24px;position:relative;overflow:hidden;}
        .ra-hero::before{content:'';position:absolute;top:-40px;right:-40px;width:200px;height:200px;background:radial-gradient(circle,rgba(184,145,42,.12) 0%,transparent 70%);pointer-events:none;}
        .ra-hero-text{color:#fff;flex:1;position:relative;z-index:1;}
        .ra-hero-meta{font-size:10px;font-weight:600;letter-spacing:.12em;color:rgba(255,255,255,.38);text-transform:uppercase;margin-bottom:6px;}
        .ra-hero-title{font-size:24px;font-weight:700;color:#fff;letter-spacing:-.4px;margin-bottom:6px;}
        .ra-hero-desc{font-size:13px;color:rgba(255,255,255,.75);}
        .ra-hero-stats{margin-left:auto;display:flex;gap:20px;flex-shrink:0;}
        .ra-stat-item{text-align:center;}
        .ra-stat-num{font-size:22px;font-weight:700;color:var(--gold2);letter-spacing:-.5px;}
        .ra-stat-lbl{font-size:10px;color:rgba(255,255,255,.38);text-transform:uppercase;letter-spacing:.06em;margin-top:2px;}

        .ra-search-panel{background:var(--surface);border-radius:var(--rlg);border:1px solid var(--border);box-shadow:var(--s1);margin-bottom:24px;}
        .ra-panel-header{padding:18px 24px 0;display:flex;align-items:center;gap:10px;}
        .ra-panel-header h2{font-size:15px;font-weight:700;color:var(--navy);}
        .ra-ai-badge{margin-left:auto;display:flex;align-items:center;gap:5px;background:var(--gold-bg);border:1px solid var(--gold-bd);border-radius:20px;padding:3px 10px;font-size:11px;font-weight:600;color:var(--gold);}
        .ra-ai-badge::before{content:'★';font-size:10px;}
        .ra-panel-body{padding:20px 24px 24px;}

        .ra-filter-grid{display:grid;grid-template-columns:1fr 1fr 1.6fr 1.4fr;gap:16px;margin-bottom:16px;}
        .ra-filter-group{display:flex;flex-direction:column;gap:6px;position:relative;}
        .ra-filter-label{font-size:11px;font-weight:600;color:var(--text3);text-transform:uppercase;letter-spacing:.07em;}
        .ra-filter-label .req{color:var(--gold);margin-left:2px;}

        .ra-fuzzy-wrap{position:relative;}
        .ra-fuzzy-input{width:100%;height:38px;padding:0 36px 0 12px;border:1.5px solid var(--border);border-radius:var(--radius-sm);background:#f9fbfd;font-family:'DM Sans',sans-serif;font-size:13px;color:var(--text1);outline:none;transition:all .15s;cursor:pointer;}
        .ra-fuzzy-input:focus,.ra-fuzzy-input.open{border-color:var(--gold);background:var(--white);box-shadow:0 0 0 3px rgba(184,145,42,.12);}
        .ra-fuzzy-chevron{position:absolute;right:10px;top:50%;transform:translateY(-50%);pointer-events:none;color:var(--text3);font-size:11px;transition:transform .15s;}
        .ra-fuzzy-input.open~.ra-fuzzy-chevron{transform:translateY(-50%) rotate(180deg);}
        .ra-dropdown-list{display:none;position:absolute;top:calc(100% + 4px);left:0;right:0;background:var(--white);border:1.5px solid var(--border);border-radius:var(--radius-sm);box-shadow:var(--s2);z-index:200;max-height:220px;overflow-y:auto;}
        .ra-dropdown-list.show{display:block;}
        .ra-dropdown-item{padding:9px 12px;font-size:13px;cursor:pointer;color:var(--text1);display:flex;align-items:center;gap:8px;transition:background .1s;}
        .ra-dropdown-item:hover,.ra-dropdown-item.active-item{background:#f0f7ff;}
        .ra-dropdown-item mark{background:rgba(184,145,42,.25);color:inherit;border-radius:2px;padding:0 1px;}
        .ra-dropdown-empty{padding:12px;font-size:12px;color:var(--text3);text-align:center;}

        .ra-kw-selected-row{margin-bottom:14px;display:none;}
        .ra-kw-selected-label{font-size:11px;font-weight:600;color:var(--text3);text-transform:uppercase;letter-spacing:.07em;margin-bottom:6px;}
        .ra-kw-chips-wrap{display:flex;flex-wrap:wrap;gap:6px;padding:8px 10px;border:1.5px solid var(--border);border-radius:var(--radius-sm);background:#f9fbfd;min-height:38px;align-items:center;}
        .ra-kw-chip{display:inline-flex;align-items:center;gap:4px;background:var(--gold-bg);border:1px solid rgba(184,145,42,.35);color:#92600a;border-radius:4px;font-size:11px;font-weight:500;padding:3px 8px;}
        .ra-kw-chip-x{cursor:pointer;font-size:14px;line-height:1;color:#c09030;padding:0 1px;}
        .ra-kw-chip-x:hover{color:var(--red);}

        .ra-date-row{display:flex;align-items:center;gap:8px;}
        .ra-date-sep{font-size:11px;color:var(--text3);flex-shrink:0;}
        .ra-date-input{flex:1;height:38px;padding:0 10px;border:1.5px solid var(--border);border-radius:var(--radius-sm);background:#f9fbfd;font-family:'DM Sans',sans-serif;font-size:12px;color:var(--text1);outline:none;transition:all .15s;}
        .ra-date-input:focus{border-color:var(--gold);background:var(--white);box-shadow:0 0 0 3px rgba(184,145,42,.12);}

        .ra-action-row{display:flex;align-items:center;gap:10px;flex-wrap:wrap;}
        .ra-btn-search{display:flex;align-items:center;gap:8px;background:var(--navy);color:#fff;border:none;border-radius:var(--radius-sm);padding:0 22px;height:40px;font-family:'DM Sans',sans-serif;font-size:13px;font-weight:600;cursor:pointer;transition:all .15s;letter-spacing:.02em;}
        .ra-btn-search:hover{background:var(--navy2);box-shadow:var(--s2);transform:translateY(-1px);}
        .ra-result-count{margin-left:auto;font-size:12px;color:var(--text3);}
        .ra-result-count span{font-weight:700;color:var(--text1);}

        .ra-progress-section{background:var(--surface);border:1px solid var(--border);border-radius:var(--rlg);padding:18px 24px;margin-bottom:24px;display:none;}
        .ra-progress-section.show{display:block;}
        .ra-progress-header{font-size:13px;font-weight:700;color:var(--navy);margin-bottom:12px;display:flex;align-items:center;gap:10px;}
        .ra-progress-bar{height:6px;background:var(--surface3);border-radius:3px;overflow:hidden;margin-bottom:14px;}
        .ra-progress-fill{height:100%;background:linear-gradient(90deg,var(--navy),var(--navy3));border-radius:3px;transition:width .5s ease;width:0%;}
        .ra-progress-percent{font-size:12px;font-weight:700;color:var(--navy);margin-left:auto;}

        .ra-agents-row{display:flex;align-items:center;gap:14px;padding:12px 0;border-bottom:.5px solid var(--border);}
        .ra-agents-row:last-child{border-bottom:none;}
        .ra-agent-icon{width:40px;height:40px;border-radius:12px;background:var(--surface2);border:2px solid var(--border);display:flex;align-items:center;justify-content:center;flex-shrink:0;transition:all .3s;}
        .ra-agent-icon.done{background:var(--green-bg);border-color:var(--green);}
        .ra-agent-icon.running{background:var(--blue-bg);border-color:var(--blue);animation:pulse 1s infinite;}
        .ra-agent-info{flex:1;}
        .ra-agent-name{font-size:13px;font-weight:700;color:var(--navy);margin-bottom:3px;display:flex;align-items:center;gap:8px;}
        .ra-agent-status{font-size:10px;font-weight:700;padding:2px 8px;border-radius:5px;background:var(--surface3);color:var(--text4);}
        .ra-agent-status.done{background:var(--green-bg);color:var(--green);}
        .ra-agent-status.running{background:var(--blue-bg);color:var(--blue);}
        .ra-agent-desc{font-size:11.5px;color:var(--text3);}

        .ra-output-section{background:var(--surface);border:1px solid var(--border);border-radius:var(--rlg);padding:24px;margin-top:24px;display:none;}
        .ra-output-section.show{display:block;}
        .ra-output-title{font-family:'Plus Jakarta Sans',sans-serif;font-size:15px;font-weight:700;color:var(--navy);margin-bottom:12px;}
        .ra-output-badge{display:inline-flex;align-items:center;gap:6px;background:var(--green-bg);border:1px solid var(--green-bd);color:var(--green);padding:4px 10px;border-radius:6px;font-size:11px;font-weight:600;margin-bottom:16px;}
        .ra-output-badge::before{content:'✓';}

        .ra-card-preview{background:var(--surface2);border:1px solid var(--border);border-radius:var(--rlg);padding:18px;margin-bottom:16px;}
        .ra-card-title{font-family:'Plus Jakarta Sans',sans-serif;font-size:14px;font-weight:700;color:var(--navy);margin-bottom:10px;}
        .ra-card-tags{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px;}
        .ra-tag{font-size:11px;background:var(--blue-bg);color:var(--blue);border:1px solid var(--blue-bd);border-radius:4px;padding:4px 9px;font-weight:600;}
        .ra-tag-therapy{background:var(--gold-bg);color:var(--gold);border-color:var(--gold-bd);}
        .ra-tag-disease{background:var(--purple-bg);color:var(--purple);border-color:#DDD6FE;}
        .ra-card-excerpt{font-size:12px;color:var(--text1);line-height:1.6;background:var(--surface);border-radius:8px;padding:12px;border:1px solid var(--border);}
      </style>

      <!-- Hero card -->
      <div class="ra-hero">
        <div class="ra-hero-text">
          <div class="ra-hero-meta">Research Agent · AI-Powered PubMed Intelligence</div>
          <h1 class="ra-hero-title">Configure Search Filters 🔬</h1>
          <p class="ra-hero-desc">Select therapy areas, diseases, and keywords — the AI agent will scan PubMed and generate clinical content for the library.</p>
        </div>
        <div class="ra-hero-stats">
          <div class="ra-stat-item"><div class="ra-stat-num">7</div><div class="ra-stat-lbl">Therapy Areas</div></div>
          <div class="ra-stat-item"><div class="ra-stat-num">35</div><div class="ra-stat-lbl">Diseases</div></div>
          <div class="ra-stat-item"><div class="ra-stat-num">105</div><div class="ra-stat-lbl">Keywords</div></div>
        </div>
      </div>

      <!-- Search panel -->
      <div class="ra-search-panel">
        <div class="ra-panel-header">
          <h2>Search Configuration</h2>
          <span style="font-size:12px;color:var(--text3);">Set your filters below</span>
          <div class="ra-ai-badge">AI-Powered · PubMed</div>
        </div>
        <div style="height:1px;background:var(--border);margin:16px 24px 0;"></div>
        <div class="ra-panel-body">

          <!-- Filter Grid -->
          <div class="ra-filter-grid">
            <!-- Therapy -->
            <div class="ra-filter-group">
              <label class="ra-filter-label">Therapy Area <span class="req">*</span></label>
              <div class="ra-fuzzy-wrap">
                <input class="ra-fuzzy-input" id="ra-therapy-input" placeholder="Search therapy…" autocomplete="off">
                <span class="ra-fuzzy-chevron">▾</span>
                <div class="ra-dropdown-list" id="ra-therapy-dd"></div>
              </div>
            </div>

            <!-- Disease -->
            <div class="ra-filter-group">
              <label class="ra-filter-label">Disease <span class="req">*</span></label>
              <div class="ra-fuzzy-wrap">
                <input class="ra-fuzzy-input" id="ra-disease-input" placeholder="Search disease…" autocomplete="off">
                <span class="ra-fuzzy-chevron">▾</span>
                <div class="ra-dropdown-list" id="ra-disease-dd"></div>
              </div>
            </div>

            <!-- Keywords -->
            <div class="ra-filter-group">
              <label class="ra-filter-label">Keywords</label>
              <div class="ra-fuzzy-wrap">
                <input class="ra-fuzzy-input" id="ra-keyword-input" placeholder="Search or type, press Enter…" autocomplete="off">
                <span class="ra-fuzzy-chevron">▾</span>
                <div class="ra-dropdown-list" id="ra-keyword-dd"></div>
              </div>
            </div>

            <!-- Date -->
            <div class="ra-filter-group">
              <label class="ra-filter-label">Publication Date</label>
              <div class="ra-date-row">
                <input class="ra-date-input" type="date" id="ra-date-from" value="2024-01-01">
                <span class="ra-date-sep">→</span>
                <input class="ra-date-input" type="date" id="ra-date-to" value="2026-06-01">
              </div>
            </div>
          </div>

          <!-- Selected Keywords -->
          <div id="ra-kw-selected-row" class="ra-kw-selected-row">
            <div class="ra-kw-selected-label">Selected Keywords</div>
            <div class="ra-kw-chips-wrap" id="ra-kw-chips"></div>
          </div>

          <!-- Action row -->
          <div class="ra-action-row">
            <button class="ra-btn-search" onclick="raStartPipeline()">🔍 Search PubMed</button>
            <button class="btn btn-outline btn-sm" onclick="raResetForm()" style="margin-left:8px;">↺ Reset</button>
            <span class="ra-result-count" id="ra-result-label" style="display:none;">Searching <span id="ra-res-count">0</span> papers...</span>
          </div>

        </div>
      </div>

      <!-- Progress section -->
      <div id="ra-progress-section" class="ra-progress-section">
        <div class="ra-progress-header">
          <span>Pipeline Progress</span>
          <span id="ra-progress-percent" class="ra-progress-percent">0%</span>
        </div>
        <div class="ra-progress-bar">
          <div id="ra-progress-fill" class="ra-progress-fill"></div>
        </div>

        <!-- Agents -->
        <div id="ra-agents-list"></div>
      </div>

      <!-- Output section -->
      <div id="ra-output-section" class="ra-output-section">
        <div class="ra-output-badge">Content cards generated</div>
        <div class="ra-output-title">Generated Content Card</div>
        <div class="ra-card-preview">
          <div class="ra-card-title" id="ra-output-title">Loading...</div>
          <div class="ra-card-tags" id="ra-output-tags"></div>
          <div class="ra-card-excerpt" id="ra-output-excerpt"></div>
        </div>
      </div>

    </div>
    '''

# Replace
try:
    new_content = content[:pipeline_start] + new_page_html + content[pipeline_end:]
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("[SUCCESS] Research Agent page HTML updated successfully")
except Exception as e:
    print(f"[ERROR] {e}")
