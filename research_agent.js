/**
 * PinnacleIQ Research Agent Module
 * Handles the Research Agent (formerly Research Pipeline) page functionality
 * Integrates with the 4-agent pipeline backend (Alpha→Beta→Gamma→Delta)
 */

// ═══════════════════════════════════════════════════════════════════════════
// DATA & STATE
// ═══════════════════════════════════════════════════════════════════════════

const RA_STATE = {
  selectedTherapy: null,
  selectedDisease: null,
  selectedKeywords: [],
  dateFrom: '2024-01-01',
  dateTo: '2026-06-01',
  currentRunId: null,
  pollInterval: null,
  agentStatuses: {
    alpha: { status: 'waiting', progress: 0 },
    beta: { status: 'waiting', progress: 0 },
    gamma: { status: 'waiting', progress: 0 },
    delta: { status: 'waiting', progress: 0 },
  }
};

// Therapy areas and diseases (from design)
const RA_DATA = {
  "Cardiology": {
    diseases: ["Hypertension", "Coronary Artery Disease (CAD)", "Heart Failure", "Atrial Fibrillation", "Dyslipidemia"],
    keywords: {
      "Hypertension": ["antihypertensive therapy", "blood pressure management", "hypertension treatment"],
      "Coronary Artery Disease (CAD)": ["CAD clinical trial", "statin therapy", "coronary intervention"],
      "Heart Failure": ["SGLT2 inhibitors", "HFpEF treatment", "heart failure therapy"],
      "Atrial Fibrillation": ["AF ablation", "anticoagulation therapy", "atrial fibrillation stroke prevention"],
      "Dyslipidemia": ["PCSK9 inhibitor", "LDL lowering", "lipid management"]
    }
  },
  "Diabetology": {
    diseases: ["Type 2 Diabetes", "Type 1 Diabetes", "Diabetic Nephropathy", "Diabetic Neuropathy"],
    keywords: {
      "Type 2 Diabetes": ["GLP-1 receptor agonist", "SGLT2 inhibitor", "type 2 diabetes drug"],
      "Type 1 Diabetes": ["closed loop insulin", "type 1 diabetes therapy", "artificial pancreas"],
      "Diabetic Nephropathy": ["diabetic kidney disease", "renal protection", "finerenone"],
      "Diabetic Neuropathy": ["peripheral neuropathy", "neuropathy pain management", "neuropathy treatment"]
    }
  },
  "Endocrinology": {
    diseases: ["Hypothyroidism", "Hyperthyroidism", "Osteoporosis", "PCOS"],
    keywords: {
      "Hypothyroidism": ["levothyroxine therapy", "thyroid hormone", "hypothyroidism treatment"],
      "Hyperthyroidism": ["Graves disease", "thyroid treatment", "radioiodine therapy"],
      "Osteoporosis": ["bone density treatment", "denosumab", "osteoporosis fracture prevention"],
      "PCOS": ["PCOS treatment", "inositol metformin", "PCOS therapy"]
    }
  },
  "Gynecology": {
    diseases: ["Uterine Fibroids", "Endometriosis", "Menopause", "Cervical Cancer"],
    keywords: {
      "Uterine Fibroids": ["fibroid treatment", "non-surgical treatment", "fibroid therapy"],
      "Endometriosis": ["endometriosis drug", "GnRH antagonist", "endometriosis pain"],
      "Menopause": ["HRT menopause", "vasomotor symptoms", "menopause treatment"],
      "Cervical Cancer": ["HPV vaccine", "cervical cancer screening", "immunotherapy"]
    }
  },
  "Gastroenterology": {
    diseases: ["GERD", "IBD", "NAFLD", "IBS", "Colorectal Cancer"],
    keywords: {
      "GERD": ["GERD treatment", "acid reflux", "Barrett esophagus"],
      "IBD": ["Crohns disease", "ulcerative colitis", "IBD treatment"],
      "NAFLD": ["NASH drug", "fatty liver", "MASLD treatment"],
      "IBS": ["IBS treatment", "gut microbiome", "IBS therapy"],
      "Colorectal Cancer": ["CRC treatment", "colorectal cancer", "KRAS therapy"]
    }
  },
  "Ophthalmology": {
    diseases: ["Diabetic Retinopathy", "AMD", "Glaucoma", "Dry Eye Disease"],
    keywords: {
      "Diabetic Retinopathy": ["diabetic retinopathy", "anti-VEGF", "macular edema"],
      "AMD": ["AMD treatment", "age-related macular", "geographic atrophy"],
      "Glaucoma": ["glaucoma treatment", "intraocular pressure", "glaucoma therapy"],
      "Dry Eye Disease": ["dry eye treatment", "meibomian gland", "dry eye syndrome"]
    }
  },
  "Dermatology": {
    diseases: ["Atopic Dermatitis", "Psoriasis", "Acne", "Melanoma", "Alopecia"],
    keywords: {
      "Atopic Dermatitis": ["eczema treatment", "atopic dermatitis", "JAK inhibitor"],
      "Psoriasis": ["psoriasis treatment", "IL-17 inhibitor", "psoriasis therapy"],
      "Acne": ["acne treatment", "acne vulgaris", "acne therapy"],
      "Melanoma": ["melanoma treatment", "checkpoint inhibitor", "BRAF inhibitor"],
      "Alopecia": ["alopecia treatment", "JAK inhibitor alopecia", "hair loss therapy"]
    }
  }
};

// ═══════════════════════════════════════════════════════════════════════════
// FUZZY SEARCH
// ═══════════════════════════════════════════════════════════════════════════

function raFuzzyScore(str, q) {
  str = str.toLowerCase(); q = q.toLowerCase();
  if (str.includes(q)) return 1;
  let s = 0, qi = 0;
  for (let i = 0; i < str.length && qi < q.length; i++)
    if (str[i] === q[qi]) { s++; qi++; }
  return qi === q.length ? s / str.length : 0;
}

function raHighlight(text, q) {
  if (!q) return text;
  const re = new RegExp(`(${q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
  return text.replace(re, '<mark>$1</mark>');
}

function raSetupDropdown(inputId, ddId, getOpts, onPick) {
  const inp = document.getElementById(inputId);
  const dd = document.getElementById(ddId);

  function render(q) {
    let opts = getOpts();
    if (q) opts = opts.filter(o => raFuzzyScore(o, q) > 0).sort((a, b) => raFuzzyScore(b, q) - raFuzzyScore(a, q));
    if (!opts.length) {
      dd.innerHTML = '<div class="ra-dropdown-empty">No matches found</div>';
    } else {
      dd.innerHTML = opts.map(o => `
        <div class="ra-dropdown-item" onclick="raPickItem('${inputId}','${ddId}','${o.replace(/'/g, "\\'")}')">
          ${q ? raHighlight(o, q) : o}
        </div>`).join('');
    }
    dd.classList.add('show');
    inp.classList.add('open');
  }

  inp.addEventListener('input', () => render(inp.value));
  inp.addEventListener('focus', () => render(inp.value));
  inp.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      const active = dd.querySelector('.ra-dropdown-item.active-item');
      if (active) active.click();
      else if (inputId === 'ra-keyword-input' && inp.value.trim()) raAddKeyword(inp.value.trim());
      raCloseDropdown(ddId, inputId);
    }
    if (e.key === 'Escape') raCloseDropdown(ddId, inputId);

    const items = dd.querySelectorAll('.ra-dropdown-item');
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault();
      const cur = Array.from(items).findIndex(el => el.classList.contains('active-item'));
      let next = e.key === 'ArrowDown' ? cur + 1 : cur - 1;
      next = Math.max(0, Math.min(next, items.length - 1));
      items.forEach(el => el.classList.remove('active-item'));
      if (items[next]) items[next].classList.add('active-item');
    }
  });

  document.addEventListener('click', (e) => {
    if (!inp.contains(e.target) && !dd.contains(e.target)) raCloseDropdown(ddId, inputId);
  });
}

function raCloseDropdown(ddId, inputId) {
  document.getElementById(ddId).classList.remove('show');
  document.getElementById(inputId).classList.remove('open');
}

function raPickItem(inputId, ddId, value) {
  const inp = document.getElementById(inputId);
  if (inputId === 'ra-therapy-input') {
    RA_STATE.selectedTherapy = value;
    inp.value = value;
    RA_STATE.selectedDisease = null;
    document.getElementById('ra-disease-input').value = '';
    RA_STATE.selectedKeywords = [];
    raRenderKwChips();
  } else if (inputId === 'ra-disease-input') {
    RA_STATE.selectedDisease = value;
    inp.value = value;
  } else if (inputId === 'ra-keyword-input') {
    raAddKeyword(value);
    inp.value = '';
  }
  raCloseDropdown(ddId, inputId);
}

function raAddKeyword(kw) {
  kw = kw.trim();
  if (!kw || RA_STATE.selectedKeywords.includes(kw)) return;
  RA_STATE.selectedKeywords.push(kw);
  document.getElementById('ra-keyword-input').value = '';
  raRenderKwChips();
}

function raRemoveKeyword(kw) {
  RA_STATE.selectedKeywords = RA_STATE.selectedKeywords.filter(k => k !== kw);
  raRenderKwChips();
}

function raRenderKwChips() {
  const row = document.getElementById('ra-kw-selected-row');
  const wrap = document.getElementById('ra-kw-chips');
  if (!RA_STATE.selectedKeywords.length) {
    row.style.display = 'none';
    return;
  }
  row.style.display = 'block';
  wrap.innerHTML = RA_STATE.selectedKeywords.map(kw =>
    `<span class="ra-kw-chip">${kw}<span class="ra-kw-chip-x" onclick="raRemoveKeyword('${kw.replace(/'/g, "\\'")}')">&times;</span></span>`
  ).join('');
}

// ═══════════════════════════════════════════════════════════════════════════
// INITIALIZATION
// ═══════════════════════════════════════════════════════════════════════════

function raInitialize() {
  // Setup dropdowns
  raSetupDropdown('ra-therapy-input', 'ra-therapy-dd', () => Object.keys(RA_DATA));
  raSetupDropdown('ra-disease-input', 'ra-disease-dd', () =>
    RA_STATE.selectedTherapy && RA_DATA[RA_STATE.selectedTherapy] ?
    RA_DATA[RA_STATE.selectedTherapy].diseases :
    Object.values(RA_DATA).flatMap(d => d.diseases)
  );
  raSetupDropdown('ra-keyword-input', 'ra-keyword-dd', () => {
    let kws = [];
    if (RA_STATE.selectedTherapy && RA_STATE.selectedDisease && RA_DATA[RA_STATE.selectedTherapy]?.keywords[RA_STATE.selectedDisease])
      kws = RA_DATA[RA_STATE.selectedTherapy].keywords[RA_STATE.selectedDisease];
    else if (RA_STATE.selectedTherapy)
      kws = Object.values(RA_DATA[RA_STATE.selectedTherapy].keywords).flat();
    else
      kws = Object.values(RA_DATA).flatMap(d => Object.values(d.keywords).flat());
    return [...new Set(kws)].filter(k => !RA_STATE.selectedKeywords.includes(k));
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// PIPELINE EXECUTION
// ═══════════════════════════════════════════════════════════════════════════

async function raStartPipeline() {
  const therapy = RA_STATE.selectedTherapy;
  const disease = RA_STATE.selectedDisease;
  const keywords = RA_STATE.selectedKeywords;

  if (!therapy && !disease && !keywords.length) {
    toast('⚠️', 'Please select at least a Therapy Area or Disease.');
    return;
  }

  // Show progress section
  const progressSection = document.getElementById('ra-progress-section');
  const outputSection = document.getElementById('ra-output-section');
  progressSection.classList.add('show');
  outputSection.classList.remove('show');

  try {
    // Start pipeline
    const response = await fetch('http://localhost:8010/pipeline/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        topic: disease || therapy || 'Custom Research',
        specialty: therapy || 'General Medicine',
        therapy_area: therapy || 'General'
      })
    });

    const data = await response.json();
    RA_STATE.currentRunId = data.run_id;

    // Start polling
    raPollPipeline();
  } catch (e) {
    console.error('Pipeline error:', e);
    toast('❌', 'Failed to start pipeline');
  }
}

async function raPollPipeline() {
  if (!RA_STATE.currentRunId) return;

  try {
    const response = await fetch(`http://localhost:8010/pipeline/status/${RA_STATE.currentRunId}`);
    const status = await response.json();

    // Update progress
    const percent = status.progress || 0;
    document.getElementById('ra-progress-fill').style.width = percent + '%';
    document.getElementById('ra-progress-percent').textContent = percent + '%';

    // Update agent statuses
    raUpdateAgentStatus(status.current_agent || '', percent);

    if (status.status === 'completed') {
      // Show output
      raDisplayOutput(status.agent_outputs);
      clearInterval(RA_STATE.pollInterval);
    } else if (status.status === 'error') {
      toast('❌', 'Pipeline error: ' + (status.error || 'Unknown error'));
      clearInterval(RA_STATE.pollInterval);
    } else {
      // Continue polling
      RA_STATE.pollInterval = setTimeout(raPollPipeline, 1000);
    }
  } catch (e) {
    console.error('Poll error:', e);
    RA_STATE.pollInterval = setTimeout(raPollPipeline, 2000);
  }
}

function raUpdateAgentStatus(agent, progress) {
  const agentsList = document.getElementById('ra-agents-list');
  if (!agentsList) return;

  // Map agent names
  const agentNames = {
    'alpha': { name: 'Alpha · Search Agent', desc: 'Searching PubMed for evidence...' },
    'beta': { name: 'Beta · Insights Agent', desc: 'Synthesizing key findings...' },
    'gamma': { name: 'Gamma · Content Agent', desc: 'Writing article...' },
    'delta': { name: 'Delta · Publisher Agent', desc: 'Building content card...' }
  };

  // Create or update agents display
  if (!agentsList.innerHTML.trim()) {
    agentsList.innerHTML = ['alpha', 'beta', 'gamma', 'delta'].map(a => `
      <div class="ra-agents-row" id="ra-agent-${a}">
        <div class="ra-agent-icon" id="ra-icon-${a}">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
            ${a === 'alpha' ? '<circle cx="8" cy="8" r="6"/><line x1="8" y1="4" x2="8" y2="12"/><line x1="4" y1="8" x2="12" y2="8"/>' : ''}
            ${a === 'beta' ? '<path d="M4 2l4 8-4 8h8L8 10l4-8"/>' : ''}
            ${a === 'gamma' ? '<path d="M2 3h12M2 8h12M2 13h6"/>' : ''}
            ${a === 'delta' ? '<path d="M3 2h10l2 3v8H1v-8l2-3z"/>' : ''}
          </svg>
        </div>
        <div class="ra-agent-info">
          <div class="ra-agent-name">${agentNames[a].name}</div>
          <div class="ra-agent-desc">${agentNames[a].desc}</div>
        </div>
        <span class="ra-agent-status" id="ra-status-${a}">Waiting</span>
      </div>
    `).join('');
  }

  // Update current agent
  ['alpha', 'beta', 'gamma', 'delta'].forEach(a => {
    const icon = document.getElementById(`ra-icon-${a}`);
    const status = document.getElementById(`ra-status-${a}`);
    if (a === agent) {
      icon?.classList.add('running');
      status.classList.add('running');
      status.textContent = 'Running...';
    } else if (['alpha', 'beta', 'gamma', 'delta'].indexOf(a) < ['alpha', 'beta', 'gamma', 'delta'].indexOf(agent)) {
      icon?.classList.add('done');
      status.classList.add('done');
      status.textContent = 'Done';
    }
  });
}

function raDisplayOutput(agentOutputs) {
  const outputSection = document.getElementById('ra-output-section');
  const delta = agentOutputs.delta || {};

  // Display title
  document.getElementById('ra-output-title').textContent = delta.card_title || 'Generated Content';

  // Display tags with hashtags
  const tags = [];
  if (RA_STATE.selectedTherapy) tags.push({ label: RA_STATE.selectedTherapy, class: 'ra-tag-therapy' });
  if (RA_STATE.selectedDisease) tags.push({ label: RA_STATE.selectedDisease, class: 'ra-tag-disease' });
  if (RA_STATE.selectedKeywords.length) {
    RA_STATE.selectedKeywords.slice(0, 2).forEach(kw => tags.push({ label: kw, class: 'ra-tag' }));
  }

  document.getElementById('ra-output-tags').innerHTML = tags.map(t =>
    `<span class="ra-tag ${t.class}">#${t.label.replace(/\s+/g, '')}</span>`
  ).join('');

  // Display excerpt
  const gamma = agentOutputs.gamma || {};
  document.getElementById('ra-output-excerpt').textContent = gamma.article_excerpt || 'Content preview...';

  outputSection.classList.add('show');
}

function raResetForm() {
  RA_STATE.selectedTherapy = null;
  RA_STATE.selectedDisease = null;
  RA_STATE.selectedKeywords = [];
  ['ra-therapy-input', 'ra-disease-input', 'ra-keyword-input'].forEach(id =>
    document.getElementById(id).value = ''
  );
  raRenderKwChips();
  document.getElementById('ra-progress-section').classList.remove('show');
  document.getElementById('ra-output-section').classList.remove('show');
}

// ═══════════════════════════════════════════════════════════════════════════
// ON PAGE LOAD
// ═══════════════════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', raInitialize);
