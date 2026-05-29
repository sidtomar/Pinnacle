# React Conversion - Implementation Guide

## ✅ Phase 1: Foundation - COMPLETE

### What Was Created

#### 1. **Project Structure** ✅
- Vite-based React project
- Modular component architecture
- Context-based state management
- Custom hooks for logic reuse
- CSS Modules for scoped styling

#### 2. **Context Providers** ✅

**AuthContext** (`src/context/AuthContext.jsx`)
- Manages user role (medical-affairs / bu-head)
- Persists role in localStorage
- Provides permission helpers: `canExport`, `canRunPipeline`, `isMA`, `isBUHead`
- Auto-updates browser hash on role change

**AppContext** (`src/context/AppContext.jsx`)
- Manages current tab/page
- Sidebar open/close state
- Active filters (specialty, therapy area, tags, date range, search)
- Sorting state (field, direction)
- Toast notifications system

**ContentContext** (`src/context/ContentContext.jsx`)
- Manages papers array
- Handles loading, error states
- CRUD operations: fetchContent, addContent, updateContent, deleteContent
- Current selection tracking

#### 3. **Custom Hooks** ✅

**useRouter** (`src/hooks/useRouter.js`)
```javascript
const { currentRole, currentPage, navigate, navigateTo } = useRouter();
navigate('medical-affairs', 'dashboard');  // #medical-affairs/dashboard
```

**useApi** (`src/hooks/useApi.js`)
```javascript
const { data, loading, error, refetch, mutate } = useApi('/content', 'GET', true);
```

**useFilters** (`src/hooks/useFilters.js`)
```javascript
const { filters, filteredData, setSorting, applyFilter, clearFilters } = 
  useFilters(papers, initialFilters);
```

**Context Hooks** (useAuth, useAppContext, useContent)
```javascript
const { role, setRole, canExport } = useAuth();
const { currentTab, setCurrentTab, filters } = useAppContext();
const { papers, loading, updateContent } = useContent();
```

#### 4. **Layout Components** ✅

**AppLayout** → Top-level container
- Combines Sidebar + Header + MainContent
- Manages main flex layout

**Sidebar** → Left navigation
- Logo and branding
- User info with role badge
- Navigation items (dynamic based on role)
- Version footer
- Styled with CSS Modules

**Header** → Top bar
- Breadcrumb (role / current page)
- Role switcher dropdown
- Responsive design

**MainContent** → Page router
- Routes to correct page component based on `currentPage`
- Flexible for adding new pages

#### 5. **API Client** ✅
`src/services/api.js`
- Axios-based HTTP client
- Configured for localhost:8010
- Organized endpoints:
  - content (list, get, create, update, delete)
  - sharing (logShare, getReport, getBusinessReport)
  - pipeline (run, save)
  - doctors (list, search)
- Request/response logging
- Error handling

#### 6. **Global Styles** ✅

**CSS Variables** (`src/styles/variables.css`)
- Colors (navy, gold, surface, borders, text)
- Semantic colors (green, amber, red, blue, purple, teal)
- Spacing values (--r, --rlg, --rxl)
- Shadow effects (--s1, --s2, --s3)

**Base Styles** (`src/styles/index.css`)
- Reset and normalization
- Button styles (.btn, .btn-navy, .btn-gold, etc.)
- Badge styles (.badge, .b-green, .b-amber, etc.)
- Animations (@keyframes pulse, fadeIn, spin)
- Utility classes (flex, gap, items-center, etc.)

## 🏃 Getting Started

### Step 1: Install Dependencies
```bash
cd D:\Codebase\Pinnacle\react-app
npm install
```

This installs:
- react 18.2.0
- react-dom 18.2.0
- axios 1.6.0
- vite 5.0.0 (dev)
- @vitejs/plugin-react (dev)

### Step 2: Start Development Server
```bash
npm run dev
```

Outputs:
```
  VITE v5.0.0  ready in 234 ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

Open http://localhost:5173 in your browser.

### Step 3: Test the Application

**Visual Checklist:**
- [ ] Sidebar visible on left (navy blue background)
- [ ] Logo "PinnacleIQ" with "Intelligence Platform" subtitle
- [ ] User badge showing "MA" (Medical Affairs)
- [ ] Navigation items visible (Content Library, Dashboard, Pipeline, Doctors)
- [ ] Header with breadcrumb at top
- [ ] Role switcher in top-right
- [ ] Main content area showing Placeholder page

**Functionality Test:**
- [ ] Click role switcher dropdown → See "Medical Affairs" and "BU Head" options
- [ ] Click "BU Head" → Role changes, URL hash updates to `#bu-head/library`
- [ ] Navigation items update (no Pipeline/Doctors for BU Head)
- [ ] Click "Content Library" → URL becomes `#bu-head/library`
- [ ] Refresh browser → Page persists at `#bu-head/library`
- [ ] Click "Medical Affairs" back → Full menu returns

**Console Check:**
- [ ] No errors in browser console
- [ ] API calls logged: `[API] GET /content` (if content loads)

## 📊 State Flow Example

### User Switches Role
```
User clicks role dropdown
→ onClick handler calls setRole('bu-head')
→ AuthContext updates state
→ window.location.hash set to '#bu-head/library'
→ hashchange event fires
→ useRouter() hook updates currentRole/currentPage
→ Sidebar and MainContent re-render with new role
→ Navigation items filtered to BU Head subset
```

### User Navigates to Page
```
User clicks "Dashboard" in sidebar
→ onClick calls setCurrentTab('dashboard') + navigate(role, 'dashboard')
→ AppContext.currentTab updates
→ window.location.hash → '#medical-affairs/dashboard'
→ useRouter() detects hash change
→ MainContent switches from Placeholder(library) → Placeholder(dashboard)
```

### Content Loads
```
App mounts
→ ContentProvider useEffect triggers
→ fetchContent() called
→ api.content.list() hits localhost:8010
→ Response data stored in ContentContext.papers
→ Pages can access via useContent().papers
```

## 🗂️ File Organization Summary

```
react-app/
├── src/
│   ├── components/
│   │   ├── layouts/
│   │   │   ├── AppLayout.jsx          ← Main container
│   │   │   ├── AppLayout.module.css
│   │   │   ├── Sidebar.jsx            ← Navigation
│   │   │   ├── Sidebar.module.css
│   │   │   ├── Header.jsx             ← Top bar
│   │   │   ├── Header.module.css
│   │   │   ├── MainContent.jsx        ← Page router
│   │   │   └── MainContent.module.css
│   │   └── pages/
│   │       ├── Placeholder.jsx        ← Temp page
│   │       └── Placeholder.module.css
│   ├── context/
│   │   ├── AuthContext.jsx            ← Role mgmt
│   │   ├── AppContext.jsx             ← UI state
│   │   └── ContentContext.jsx         ← Data mgmt
│   ├── hooks/
│   │   ├── useRouter.js               ← Hash routing
│   │   ├── useApi.js                  ← API wrapper
│   │   ├── useFilters.js              ← Filter logic
│   │   ├── useAuth.js                 ← Auth hook
│   │   ├── useAppContext.js
│   │   ├── useContent.js
│   │   └── index.js                   ← Exports
│   ├── services/
│   │   └── api.js                     ← Axios client
│   ├── styles/
│   │   ├── variables.css              ← CSS vars
│   │   └── index.css                  ← Global styles
│   ├── App.jsx                        ← Root component
│   └── index.js                       ← Entry point
├── public/
│   └── index.html                     ← HTML shell
├── package.json                       ← Dependencies
├── vite.config.js                     ← Build config
├── .env.example
├── .gitignore
├── README.md
├── IMPLEMENTATION_GUIDE.md            ← YOU ARE HERE
└── NEXT_STEPS.md
```

## 🔗 Migration Mapping (Vanilla JS → React)

| Vanilla JS | React | Location |
|-----------|-------|----------|
| `ROLE` global | `useAuth().role` | AuthContext |
| `ALL_PAPERS` global | `useContent().papers` | ContentContext |
| `CL_TAB` global | `useAppContext().currentTab` | AppContext |
| `SORT_F`, `SORT_D` | `useAppContext().sortField/Direction` | AppContext |
| localStorage | Context + localStorage sync | Each context |
| Hash routing logic | `useRouter()` hook | hooks/useRouter.js |
| API calls | `api.content.list()` | services/api.js |
| DOM manipulation | React re-renders | Components |
| Event listeners | useEffect + cleanup | Hooks |

## 🚀 Next Phase: Content Library (Phase 2)

Ready to convert the ContentLibrary page. Create:

1. **ContentLibrary.jsx** page component
2. **SearchBar.jsx** component
3. **FilterPanel.jsx** component
4. **ContentCard.jsx** component
5. **Modal.jsx** reusable modal
6. **Sorting controls** in header area
7. **Grid/List view toggle**

Would you like to proceed with Phase 2 now?

## 🐛 Troubleshooting

**Port 5173 already in use:**
```bash
npm run dev -- --port 5174
```

**API not responding:**
- Ensure backend running on port 8010
- Check `VITE_API_URL` in .env.local
- Look at browser Network tab for 404/500 errors

**Changes not reflecting:**
- Vite has HMR (hot module reload)
- Save file again if needed
- Hard refresh (Ctrl+Shift+R / Cmd+Shift+R)

**TypeScript errors (future):**
- This project uses JavaScript
- To add TypeScript: rename .jsx → .tsx, add tsconfig.json

## 📝 Notes for Implementation

- **No breaking changes**: Each phase builds on previous
- **Easy rollback**: Each component is isolated
- **Testing ready**: Structure supports unit tests
- **Mobile ready**: All code can be shared to React Native
- **Git safety**: Not committing until you review

## ✅ Verification Checklist

Before proceeding to Phase 2, confirm:

- [ ] `npm install` completed without errors
- [ ] `npm run dev` starts successfully
- [ ] App loads at localhost:5173
- [ ] Sidebar visible with correct styling
- [ ] Role switcher works
- [ ] Navigation changes URL hash
- [ ] Browser refresh persists URL
- [ ] No console errors
- [ ] All files created in correct locations
- [ ] Backend running on port 8010

---

**Phase 1 Status**: ✅ COMPLETE  
**Ready for Phase 2**: ✅ YES

Next: Implement ContentLibrary page component
