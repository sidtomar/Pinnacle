# Next Steps - Phase 2: Content Library Implementation

## 🎯 Phase 2 Overview

Convert the Content Library page from vanilla JS to React component.

**Current vanilla JS file**: `D:\Codebase\Pinnacle\PinnacleIQ_Portal.html`
- Lines with `.papers-grid` (content cards)
- Lines with `.fr` and `.fsel` (filters & search)
- Lines with sorting/view toggle
- Share button functionality

**Target**: Fully functional React page with:
- Search bar
- Filter panel (specialty, therapy area, tags, date range)
- View toggle (grid ↔ list)
- Sorting controls
- Content cards with all metadata
- Share dialog modal

## 📋 To-Do List for Phase 2

### 1. Create ContentLibrary Page Component
**File**: `src/components/pages/ContentLibrary.jsx`

```javascript
export default function ContentLibrary() {
  const { papers, loading } = useContent();
  const { filters, setFilters, sorting, setSorting } = useAppContext();
  const { filteredData } = useFilters(papers, filters);

  return (
    <div>
      <SearchBar />
      <FilterPanel />
      <SortingControls />
      <ViewToggle />
      <ContentGrid data={filteredData} loading={loading} />
    </div>
  );
}
```

### 2. Create SearchBar Component
**File**: `src/components/shared/SearchBar.jsx`

Features:
- Text input for title/summary search
- Real-time filter update
- Clear button
- Styles: `.sbox` from vanilla CSS

### 3. Create FilterPanel Component
**File**: `src/components/shared/FilterPanel.jsx`

Filters to implement:
- **Specialty**: Multi-select dropdown (from papers)
- **Therapy Area**: Multi-select dropdown
- **Tags**: Tag chips with remove
- **Date Range**: From/To date pickers
- **Clear All**: Reset filters button

### 4. Create ContentCard Component
**File**: `src/components/shared/ContentCard.jsx`

Card shows:
- Status badge (approved/pending/rejected)
- Title (3-line clamp)
- Authors
- Summary (2-line clamp)
- Tags
- Publication details:
  - PMID
  - DOI
  - Publication date
  - Links (PubMed, Full Text)
- Share button

### 5. Create ContentGrid Component
**File**: `src/components/shared/ContentGrid.jsx`

Features:
- 3-column grid layout
- Loading skeletons while fetching
- Empty state message
- Hover effects on cards
- Click to open detail modal (Phase 2.5)

### 6. Create Modal Component
**File**: `src/components/shared/Modal.jsx`

Reusable modal for:
- Detail view
- Share dialog
- Edit content
- Any future modal needs

### 7. Create SortingControls
**File**: `src/components/shared/SortingControls.jsx`

Sort by:
- Date (newest first)
- Title (A-Z)
- Specialty
- Relevance

Direction: Ascending / Descending

### 8. Create ViewToggle
**File**: `src/components/shared/ViewToggle.jsx`

Toggle between:
- Grid view (3 columns)
- List view (full width rows)

Use `.vtog` and `.vb` styles from vanilla CSS

### 9. Create ShareDialog Modal
**File**: `src/components/dialogs/ShareDialog.jsx`

Share options:
- WhatsApp
- Email
- Copy Link

Log share via `api.sharing.logShare(contentId, method)`

### 10. Update MainContent Router
**File**: `src/components/layouts/MainContent.jsx`

Replace Placeholder with:
```javascript
import ContentLibrary from '../pages/ContentLibrary';

const PAGE_COMPONENTS = {
  'library': ContentLibrary,  // ← Add this
  'dashboard': Placeholder,
  // ... rest
};
```

## 🎨 CSS Modules Mapping

From vanilla CSS to CSS Modules:

| Vanilla Class | Component | Module File |
|--------------|-----------|------------|
| `.papers-grid` | ContentGrid | ContentGrid.module.css |
| `.pc` | ContentCard | ContentCard.module.css |
| `.fr` | FilterPanel | FilterPanel.module.css |
| `.sbox` | SearchBar | SearchBar.module.css |
| `.fsel` | FilterPanel select | FilterPanel.module.css |
| `.vtog` | ViewToggle | ViewToggle.module.css |
| `.ov`, `.modal` | Modal | Modal.module.css |
| `.ov.on` | Modal open state | Modal.module.css |

## 🔧 Implementation Strategy

### Step 1: Create Stub Components (1 hour)
Create all component files with placeholder JSX:
```javascript
export default function ComponentName() {
  return <div>Component Placeholder</div>;
}
```

### Step 2: Build CSS Modules (2 hours)
Extract CSS from vanilla file and convert to CSS Modules:
- Copy relevant `.css` rules
- Add module imports to components
- Test styling

### Step 3: Wire Up State (1 hour)
Connect to contexts:
- `useContent()` for papers
- `useAppContext()` for filters/sorting
- `useFilters()` for filter logic

### Step 4: Implement Components (4 hours)
Build each component logic:
- SearchBar: onChange handler
- FilterPanel: Multi-select logic
- ContentCard: Data mapping
- Modal: Show/hide state

### Step 5: Connect Page (1 hour)
- Wire ContentLibrary to MainContent router
- Test full page flow
- Debug issues

### Step 6: Test & Polish (2 hours)
- All filters work
- Search works
- Sorting works
- View toggle works
- Share dialog opens
- No console errors

**Total Time**: ~11 hours (1-2 days of work)

## 📌 Key Implementation Details

### SearchBar Debounce
```javascript
import { useEffect, useState } from 'react';

function SearchBar() {
  const [input, setInput] = useState('');
  const { setFilters } = useAppContext();

  useEffect(() => {
    const timer = setTimeout(() => {
      setFilters({ search: input });
    }, 300); // Debounce 300ms

    return () => clearTimeout(timer);
  }, [input, setFilters]);

  return (
    <input 
      value={input} 
      onChange={e => setInput(e.target.value)}
      placeholder="Search articles..."
    />
  );
}
```

### Multi-Select Filter
```javascript
function FilterPanel() {
  const specialties = [...new Set(papers.map(p => p.specialty))];
  const { filters, setFilters } = useAppContext();

  const toggleSpecialty = (specialty) => {
    const updated = filters.specialty.includes(specialty)
      ? filters.specialty.filter(s => s !== specialty)
      : [...filters.specialty, specialty];
    
    setFilters({ specialty: updated });
  };

  return (
    <div>
      {specialties.map(spec => (
        <label key={spec}>
          <input 
            type="checkbox"
            checked={filters.specialty.includes(spec)}
            onChange={() => toggleSpecialty(spec)}
          />
          {spec}
        </label>
      ))}
    </div>
  );
}
```

### Grid with Loading State
```javascript
function ContentGrid({ data, loading }) {
  if (loading) {
    return <div className={styles.grid}>Loading...</div>;
  }

  if (data.length === 0) {
    return <div className={styles.empty}>No articles found</div>;
  }

  return (
    <div className={styles.grid}>
      {data.map(item => (
        <ContentCard key={item.id} item={item} />
      ))}
    </div>
  );
}
```

## 🧪 Testing Checklist

After implementation, verify:

### Functionality
- [ ] Search filters papers by title
- [ ] Specialty filter works
- [ ] Therapy area filter works
- [ ] Tag filter works
- [ ] Date range filter works
- [ ] Sort by date works
- [ ] Sort by title works
- [ ] View toggle switches grid ↔ list
- [ ] Share button opens modal
- [ ] Share logs to backend
- [ ] Clear all filters resets

### Visual
- [ ] Cards display all metadata
- [ ] Links are clickable (PMID, DOI, Full Text)
- [ ] Status badges show correctly
- [ ] Tags wrap properly
- [ ] Grid is 3 columns on desktop
- [ ] List view is readable
- [ ] Responsive on mobile (2 columns grid)
- [ ] No overflow issues

### Performance
- [ ] Filtering is instant (no lag)
- [ ] Sorting is instant
- [ ] View toggle is smooth
- [ ] No unnecessary re-renders (check React DevTools)

### Integration
- [ ] Data persists after refresh
- [ ] URL hash stays correct
- [ ] Works with role switching
- [ ] Backend API calls succeed
- [ ] Error handling works

## 📝 Example File Structure After Phase 2

```
src/components/
├── layouts/
│   ├── AppLayout.jsx
│   ├── Sidebar.jsx
│   ├── Header.jsx
│   └── MainContent.jsx
├── pages/
│   ├── ContentLibrary.jsx           ← NEW
│   └── Placeholder.jsx
├── shared/                          ← NEW FOLDER
│   ├── SearchBar.jsx
│   ├── SearchBar.module.css
│   ├── FilterPanel.jsx
│   ├── FilterPanel.module.css
│   ├── ContentCard.jsx
│   ├── ContentCard.module.css
│   ├── ContentGrid.jsx
│   ├── ContentGrid.module.css
│   ├── ViewToggle.jsx
│   ├── ViewToggle.module.css
│   ├── SortingControls.jsx
│   ├── SortingControls.module.css
│   └── Modal.jsx
│       └── Modal.module.css
└── dialogs/                         ← NEW FOLDER
    ├── ShareDialog.jsx
    └── ShareDialog.module.css
```

## 🔗 References

Vanilla JS code to reference:
- Search function: `loadContent()` in original HTML
- Filter logic: `applyFilters()` in original HTML
- Sorting: `applySorting()` in original HTML
- Share logic: `shareContent()` in original HTML
- Card rendering: `.papers-grid` and `.pc` sections

## ⚡ Quick Command Reference

```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Format code (add prettier later)
npm run format

# Run tests (add vitest later)
npm run test
```

## ✅ Sign-Off

Phase 2 is complete when:
- [x] ContentLibrary page loads
- [x] All filters work
- [x] Search works
- [x] Sorting works
- [x] View toggle works
- [x] Share dialog shows
- [x] No console errors
- [x] All tests pass
- [x] Mobile responsive

---

**Estimated Effort**: 2 days  
**Difficulty**: Medium  
**Dependencies**: Phase 1 ✅ (Complete)

Ready to start? Let me know and I'll begin Phase 2 implementation!
