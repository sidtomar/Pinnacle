# 🛠️ Dynamic Research Agent Implementation Plan

## Overview
Convert the Research Agent page from mock data display to dynamic user-driven article generation using the agentic pipeline.

---

## 🎯 Feature Flow

```
User fills filters:
  ✓ Therapy Area (dropdown)
  ✓ Disease (dropdown)
  ✓ Keywords (text input)
  ✓ Publication Date (from/to date)
         ↓
User clicks "Search PubMed"
         ↓
Frontend sends to backend:
  POST /pipeline/run
  {
    "topic": "user-generated from filters",
    "therapy_area": "selected value",
    "disease": "selected value",
    "keywords": "user typed keywords"
    "date_from": "01-01-2024",
    "date_to": "01-06-2026"
  }
         ↓
Backend runs agentic pipeline
(Alpha→Beta→Gamma→Delta - HIDDEN from user)
         ↓
Show LOADING SPINNER while processing
         ↓
Generate multiple content cards
         ↓
Auto-save to Content Library (Pending MA Review)
         ↓
Display results in Search Results section
         ↓
User can "Download Database"
         ↓
All articles PERSIST (accumulate, don't overwrite)
```

---

## 📁 Files to Modify

### **1. Frontend: PinnacleIQ_Portal.html**

**Sections to modify:**
- Line ~1336 (pg-research-agent page)
- The JavaScript functions for Research Agent

**Key Changes:**

#### A. Update "Search PubMed" Button
```html
CURRENT:
<button class="btn btn-navy" onclick="raRunSearch('2')">
  🔍 Search PubMed
</button>

CHANGE TO:
<button class="btn btn-navy" id="ra-search-btn" onclick="raRunDynamicSearch()">
  🔍 Search PubMed
</button>
```

#### B. Collect Therapy Area as Dropdown
```html
CURRENT (if not present):
<select id="ra-therapy-2">
  <option>Cardiology</option>
  <option>Diabetology</option>
  ...
</select>

NOTE: Make sure it has id="ra-therapy-2"
```

#### C. Collect Disease as Dropdown
```html
CURRENT (if not present):
<select id="ra-disease-2">
  <option>Hypertension</option>
  <option>Dyslipidaemia</option>
  ...
</select>

NOTE: Make sure it has id="ra-disease-2"
```

#### D. Keywords Input
```html
CURRENT (if not present):
<input type="text" id="ra-keywords-2" placeholder="Search or type, press Enter...">

NOTE: Make sure it has id="ra-keywords-2"
```

#### E. Date Range Filter
```html
CURRENT (if not present):
<input type="date" id="ra-date-from-2">
<input type="date" id="ra-date-to-2">

NOTE: Make sure it has these IDs
```

#### F. Loading Indicator
```html
Add BEFORE results section:
<div id="ra-loading-spinner" style="display:none; text-align:center; padding:20px;">
  <div style="width:40px; height:40px; border:4px solid #f3f3f3; border-top:4px solid var(--navy); border-radius:50%; animation:spin 1s linear infinite; margin:0 auto;"></div>
  <p style="margin-top:10px; color:var(--text3);">Searching articles...</p>
</div>
```

#### G. Download Button
```html
CURRENT (if not present):
<button class="btn btn-outline" onclick="raDownloadDatabase()">
  ↓ Download Database
</button>

NOTE: Add this button with results
```

#### H. Results Section
```html
Make sure results display section exists:
<div id="ra-search-results">
  <!-- Article cards will be inserted here -->
</div>
```

---

### **2. Backend: demo/backend/app.py**

**No changes needed!** The `/pipeline/run` endpoint already exists.

However, verify it accepts:
```python
{
  "topic": "user input",
  "specialty": "from user",
  "therapy_area": "from user",
  "keywords": "from user",
  "date_from": "YYYY-MM-DD",
  "date_to": "YYYY-MM-DD"
}
```

---

## 💻 JavaScript Functions to Implement

### **1. raRunDynamicSearch() - NEW FUNCTION**

```javascript
async function raRunDynamicSearch() {
  // Get filter values
  const therapyArea = document.getElementById('ra-therapy-2').value;
  const disease = document.getElementById('ra-disease-2').value;
  const keywords = document.getElementById('ra-keywords-2').value;
  const dateFrom = document.getElementById('ra-date-from-2').value;
  const dateTo = document.getElementById('ra-date-to-2').value;
  
  // Validate at least one filter is selected
  if (!therapyArea && !disease && !keywords && !dateFrom) {
    toast('⚠️', 'Please select at least one filter');
    return;
  }
  
  // Show loading spinner
  document.getElementById('ra-loading-spinner').style.display = 'block';
  document.getElementById('ra-search-results').innerHTML = '';
  
  // Disable search button
  const btn = document.getElementById('ra-search-btn');
  btn.disabled = true;
  
  try {
    // Build topic string from filters
    const topic = `${disease || 'General'} - ${therapyArea || 'General'}`;
    
    // Call backend pipeline
    const response = await fetch(PL_API + '/pipeline/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        topic: topic,
        specialty: therapyArea,
        therapy_area: therapyArea,
        keywords: keywords
      })
    });
    
    if (!response.ok) throw new Error('Pipeline failed');
    
    const data = await response.json();
    const runId = data.run_id;
    
    // Poll for results
    raPollResults(runId, btn);
    
  } catch(e) {
    document.getElementById('ra-loading-spinner').style.display = 'none';
    btn.disabled = false;
    toast('❌', 'Search failed: ' + e.message);
  }
}
```

### **2. raPollResults() - NEW FUNCTION**

```javascript
async function raPollResults(runId, btn) {
  try {
    const response = await fetch(PL_API + '/pipeline/status/' + runId);
    if (!response.ok) return;
    
    const data = await response.json();
    
    if (data.status === 'completed') {
      // Hide spinner
      document.getElementById('ra-loading-spinner').style.display = 'none';
      btn.disabled = false;
      
      // Fetch and display content cards
      if (data.all_content_ids && data.all_content_ids.length > 0) {
        raDisplayResults(data.all_content_ids);
      }
    } else if (data.status === 'error') {
      document.getElementById('ra-loading-spinner').style.display = 'none';
      btn.disabled = false;
      toast('❌', 'Pipeline failed');
    } else {
      // Still running, poll again
      setTimeout(() => raPollResults(runId, btn), 2000);
    }
  } catch(e) {
    console.error('Poll error:', e);
    setTimeout(() => raPollResults(runId, btn), 2000);
  }
}
```

### **3. raDisplayResults() - NEW FUNCTION**

```javascript
async function raDisplayResults(contentIds) {
  const resultsDiv = document.getElementById('ra-search-results');
  resultsDiv.innerHTML = '';
  
  for (const contentId of contentIds) {
    try {
      const res = await fetch(PL_API + '/content/' + contentId);
      if (!res.ok) continue;
      
      const card = await res.json();
      
      // Create article card HTML
      const html = `
        <div class="ra-article-card">
          <div style="display:flex; justify-content:space-between; align-items:start;">
            <div style="flex:1;">
              <h3 style="margin:0 0 8px; font-size:15px; font-weight:700; color:var(--navy);">
                ${card.title || 'Article'}
              </h3>
              <div style="font-size:12px; color:var(--text3); margin-bottom:8px;">
                ${card.authors || 'Unknown Authors'} • ${card.published_date || 'N/A'}
              </div>
              <p style="margin:0; font-size:13px; color:var(--text1); line-height:1.5;">
                ${card.summary || card.description || 'No summary available'}
              </p>
            </div>
            <span style="background:var(--green); color:#fff; padding:4px 8px; border-radius:4px; font-size:11px; font-weight:600; white-space:nowrap; margin-left:10px;">
              ✓ Approved
            </span>
          </div>
          <div style="margin-top:10px; padding-top:10px; border-top:1px solid var(--border); display:flex; gap:8px;">
            <a href="${card.pubmed_link || '#'}" target="_blank" style="font-size:12px; color:var(--blue); text-decoration:none; cursor:pointer;">
              View on PubMed →
            </a>
          </div>
        </div>
      `;
      
      resultsDiv.innerHTML += html;
      
    } catch(e) {
      console.error('Error fetching card:', contentId);
    }
  }
  
  // Show count
  document.querySelector('#ra-search-results').insertAdjacentHTML('beforebegin', 
    `<div style="font-size:13px; color:var(--text2); margin-bottom:12px;">
      Showing ${contentIds.length} article(s)
    </div>`
  );
}
```

### **4. raDownloadDatabase() - NEW FUNCTION**

```javascript
async function raDownloadDatabase() {
  try {
    const response = await fetch(PL_API + '/content');
    const data = await response.json();
    
    if (!data.items || data.items.length === 0) {
      toast('⚠️', 'No articles to download');
      return;
    }
    
    // Create CSV
    const headers = ['Title', 'Authors', 'Date', 'Therapy Area', 'Disease', 'PubMed Link', 'Status'];
    const rows = data.items.map(item => [
      item.title || '',
      item.authors || '',
      item.published_date || '',
      item.therapy_area || '',
      item.disease || '',
      item.pubmed_link || '',
      item.status || 'Approved'
    ]);
    
    let csv = headers.join(',') + '\n';
    rows.forEach(row => {
      csv += row.map(cell => `"${(cell || '').replace(/"/g, '""')}"`).join(',') + '\n';
    });
    
    // Download
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `research-articles-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
    
    toast('✓', 'Database downloaded');
  } catch(e) {
    toast('❌', 'Download failed: ' + e.message);
  }
}
```

---

## 🧪 Testing Checklist

- [ ] Fill Therapy Area dropdown
- [ ] Fill Disease dropdown
- [ ] Enter keywords
- [ ] Select date range
- [ ] Click "Search PubMed"
- [ ] Loading spinner appears
- [ ] Wait for results
- [ ] Articles display in Search Results
- [ ] Articles saved to Content Library
- [ ] Click "Download Database"
- [ ] CSV file downloads
- [ ] Perform another search
- [ ] Previous results still visible (accumulated)
- [ ] Backend shows articles in database

---

## 📝 Implementation Steps

1. **Add HTML elements** (filter dropdowns, inputs, buttons)
2. **Add CSS** for loading spinner
3. **Implement raRunDynamicSearch()** function
4. **Implement raPollResults()** function
5. **Implement raDisplayResults()** function
6. **Implement raDownloadDatabase()** function
7. **Test** the complete flow
8. **Commit** to git

---

## 🚀 Ready to Code?

All the code snippets above are ready to use. Next step:
1. Open PinnacleIQ_Portal.html
2. Find the Research Agent page (pg-research-agent)
3. Add/update the HTML elements
4. Add the JavaScript functions
5. Test in browser

**Questions? Ask before coding!** ✅
