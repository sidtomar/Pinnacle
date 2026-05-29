# 🏗️ Architecture Diagram

Visual representation of the React application structure.

---

## Component Hierarchy

```
┌─────────────────────────────────────────────────────┐
│                       App.jsx                       │
│   (Wraps all contexts: Auth, App, Content)         │
└──────────────────────┬────────────────────────────┘
                       │
        ┌──────────────┴──────────────┬──────────────┐
        │                             │              │
   ┌────▼────────────────────────────┐  ┌──────────▼─────────────┐
   │   AuthContext.Provider          │  │  AppContext.Provider   │
   │  (Role, Permissions)            │  │  (UI State, Filters)   │
   └────┬────────────────────────────┘  └──────────┬─────────────┘
        │                                           │
        └──────────────────┬──────────────────────┬─┘
                           │
                    ┌──────▼──────────┐
                    │   AppLayout     │
                    │  (Main Container)
                    └──────┬──────────┘
         ┌──────────────────┼──────────────────┐
         │                  │                  │
     ┌───▼───────┐   ┌─────▼──────┐   ┌──────▼────────┐
     │  Sidebar  │   │   Header   │   │ MainContent    │
     │(Navigation)   │(Role Switcher) │(Page Router)   │
     └───┬───────┘   └────────────┘   └──────┬────────┘
         │                                    │
         │                          ┌─────────┴──────────┐
         │                          │                    │
         │                  ┌───────▼────────┐   ┌──────▼──────┐
         │                  │ ContentLibrary │   │ Dashboard  │
         │                  │ (Phase 2)      │   │ (Phase 3)  │
         │                  └────────────────┘   └────────────┘
         │                          
         │                  ┌──────────────────┐
         │                  │   Pipeline       │
         │                  │   (Phase 4)      │
         │                  └──────────────────┘
         │
         └─► (Displays nav items based on ROLE)
```

---

## State Management Flow

```
┌─────────────────────────────────────────────────────────┐
│                    CONTEXTS (Global State)              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────┐  ┌─────────────────────────┐    │
│  │  AuthContext     │  │  AppContext             │    │
│  ├──────────────────┤  ├─────────────────────────┤    │
│  │ • role           │  │ • currentTab            │    │
│  │ • setRole()      │  │ • setCurrentTab()       │    │
│  │ • canExport      │  │ • filters               │    │
│  │ • isMA           │  │ • setFilters()          │    │
│  │ • isBUHead       │  │ • sortField             │    │
│  │                  │  │ • sortDirection         │    │
│  │                  │  │ • setSorting()          │    │
│  │                  │  │ • notifications         │    │
│  │                  │  │ • addNotification()     │    │
│  └──────────────────┘  │ • sidebarOpen           │    │
│                        │ • toggleSidebar()       │    │
│  ┌────────────────────┤─────────────────────────┤    │
│  │  ContentContext    │                         │    │
│  ├────────────────────┤                         │    │
│  │ • papers[]         │                         │    │
│  │ • loading          │                         │    │
│  │ • error            │                         │    │
│  │ • currentId        │                         │    │
│  │ • fetchContent()   │                         │    │
│  │ • addContent()     │                         │    │
│  │ • updateContent()  │                         │    │
│  │ • deleteContent()  │                         │    │
│  └────────────────────┴─────────────────────────┘    │
│                                                         │
└─────────────────────────────────────────────────────────┘
                          ▲
                          │
          Accessed via custom hooks:
          useAuth() / useAppContext() / useContent()
```

---

## Routing Architecture

```
HASH ROUTING
────────────

Format: #role/page

Examples:
┌──────────────────────────────────────────┐
│ #medical-affairs/library                 │
│ #medical-affairs/dashboard               │
│ #medical-affairs/pipeline                │
│ #medical-affairs/doctors                 │
│ #bu-head/library                         │
│ #bu-head/analytics                       │
└──────────────────────────────────────────┘

Flow:
┌─────────────────────────────────────┐
│  window.location.hash change        │
└──────────────┬──────────────────────┘
               │
       ┌───────▼────────┐
       │  hashchange    │
       │   listener     │
       └───────┬────────┘
               │
     ┌─────────▼─────────┐
     │  useRouter hook   │
     │  (reads hash)     │
     └─────────┬─────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼────────┐  ┌────────▼──┐
│ currentRole│  │currentPage │
└───┬────────┘  └────────┬───┘
    │                    │
    │                    └──► MainContent router
    │                         (mounts correct page)
    └──► AuthContext.setRole()
         (updates user role)
```

---

## Data Flow Example: Content Loading

```
┌──────────────────────────────────────┐
│  ContentProvider mounts              │
│  (useEffect triggered)               │
└────────────┬─────────────────────────┘
             │
    ┌────────▼────────┐
    │  fetchContent() │
    └────────┬────────┘
             │
    ┌────────▼────────────┐
    │  api.content.list() │
    │  (Axios HTTP call)  │
    └────────┬────────────┘
             │
    ┌────────▼──────────────┐
    │  localhost:8010/api/  │
    │  (Backend)           │
    └────────┬──────────────┘
             │
    ┌────────▼────────────┐
    │  Response JSON      │
    │  [papers array]     │
    └────────┬────────────┘
             │
    ┌────────▼──────────────────┐
    │  ContentContext.papers[]  │
    │  (State updated)          │
    └────────┬──────────────────┘
             │
    ┌────────▼─────────────────┐
    │  Components re-render    │
    │  (useContent hook)       │
    └────────┬─────────────────┘
             │
    ┌────────▼──────────────┐
    │  UI displays papers   │
    │  (ContentLibrary)     │
    └───────────────────────┘
```

---

## Hooks System

```
CUSTOM HOOKS (Logic Reuse)
──────────────────────────

┌─────────────────────┐
│  useRouter()        │
├─────────────────────┤
│ • currentRole       │
│ • currentPage       │
│ • navigate()        │
│ • navigateTo()      │
└────────┬────────────┘
         │
    Manages hash routing
    Re-renders on hashchange
         │
    ┌────▼────────────┐
    │ window.location │
    │     .hash       │
    └─────────────────┘


┌──────────────────┐
│  useApi()        │
├──────────────────┤
│ • data           │
│ • loading        │
│ • error          │
│ • refetch()      │
│ • mutate()       │
└────┬─────────────┘
     │
 Wraps axios
 Auto-fetches GET
     │
 ┌───▼──────────────┐
 │  axios client    │
 │ (localhost:8010) │
 └──────────────────┘


┌─────────────────────┐
│  useFilters()       │
├─────────────────────┤
│ • filters           │
│ • filteredData      │
│ • sorting           │
│ • applyFilter()     │
│ • setSorting()      │
│ • clearFilters()    │
└────┬────────────────┘
     │
 Pure data filtering
 Text search
 Multi-field filtering
 Sorting with direction
     │
 ┌───▼─────────────────┐
 │ Input: papers array │
 │ Output: filtered    │
 │         array       │
 └─────────────────────┘


┌─────────────────────┐
│  useAuth()          │
├─────────────────────┤
│ Returns AuthContext │
└─────────────────────┘

┌─────────────────────┐
│  useAppContext()    │
├─────────────────────┤
│ Returns AppContext  │
└─────────────────────┘

┌─────────────────────┐
│  useContent()       │
├─────────────────────┤
│ Returns ContentCtx  │
└─────────────────────┘
```

---

## API Integration

```
SERVICE LAYER
─────────────

┌──────────────────────────────────────┐
│  src/services/api.js                 │
│  (Axios client configured)           │
├──────────────────────────────────────┤
│                                      │
│  api.content                         │
│  ├── list()      → GET /content      │
│  ├── get(id)     → GET /content/{id} │
│  ├── create()    → POST /content     │
│  ├── update()    → PUT /content/{id} │
│  └── delete()    → DELETE /content   │
│                                      │
│  api.sharing                         │
│  ├── logShare()  → POST share        │
│  ├── getReport() → GET share-logs    │
│  └── ...getBusinessReport() → ...   │
│                                      │
│  api.pipeline                        │
│  ├── run()       → POST pipeline/run │
│  └── save()      → POST pipeline/save│
│                                      │
│  api.doctors                         │
│  ├── list()      → GET /doctors      │
│  └── search()    → GET /doctors/...  │
│                                      │
└────────────┬───────────────────────┘
             │
    ┌────────▼──────────────┐
    │   Axios HTTP Client   │
    │ Configured for:       │
    │ • Base URL: :8010     │
    │ • Timeout: 30s        │
    │ • JSON headers        │
    │ • Logging             │
    └────────┬──────────────┘
             │
    ┌────────▼──────────────────┐
    │  HTTP Requests to        │
    │  localhost:8010          │
    └────────┬──────────────────┘
             │
    ┌────────▼──────────────────┐
    │  FastAPI Backend         │
    │  (demo/backend/app.py)   │
    └────────┬──────────────────┘
             │
    ┌────────▼──────────────────┐
    │  Database Layer          │
    │  (SQLite or Databricks)  │
    └──────────────────────────┘
```

---

## Styling Architecture

```
STYLING SYSTEM
──────────────

┌────────────────────────────────────┐
│  src/styles/variables.css          │
│  (CSS Custom Properties)           │
├────────────────────────────────────┤
│ • Colors: --navy, --gold, --green │
│ • Text colors: --text1 to --text4 │
│ • Surfaces: --surface, --surface2 │
│ • Borders: --border, --border2    │
│ • Spacing: --r, --rlg, --rxl      │
│ • Shadows: --s1, --s2, --s3       │
└────────┬──────────────────────────┘
         │
    ┌────▼──────────────────┐
    │  src/styles/index.css │
    │  (Base styles)        │
    ├──────────────────────┤
    │ • Reset & normalize  │
    │ • Button styles      │
    │ • Badge styles       │
    │ • Animations         │
    │ • Utilities          │
    └────┬──────────────────┘
         │
    ┌────▼─────────────────────────────┐
    │  Component CSS Modules           │
    │  (Scoped to component)           │
    ├─────────────────────────────────┤
    │ • Sidebar.module.css            │
    │ • Header.module.css             │
    │ • ContentLibrary.module.css      │
    │ • ContentCard.module.css         │
    │ • etc.                          │
    │                                 │
    │ Benefits:                       │
    │ ✓ No global conflicts          │
    │ ✓ Component isolation          │
    │ ✓ Easy to maintain             │
    │ ✓ Can import in JSX            │
    │ ✓ Type-safe (future TS)       │
    └─────────────────────────────────┘
```

---

## Build & Deployment

```
DEVELOPMENT
───────────
   npm run dev
        │
        ├─► Vite dev server (:5173)
        ├─► Hot Module Reload (HMR)
        ├─► Fast refresh on save
        └─► Sourcemaps for debugging

PRODUCTION BUILD
────────────────
   npm run build
        │
        ├─► Vite bundler
        ├─► Code splitting
        ├─► Tree shaking
        ├─► Minification
        └─► dist/ folder
                │
                ├─► index.html
                ├─► js/ (chunked)
                └─► assets/


PREVIEW
───────
   npm run preview
        │
        └─► Local prod server (:4173)
```

---

## File Organization Principle

```
BY FEATURE/DOMAIN
─────────────────

src/
├── components/
│   ├── layouts/          ← Layout components (Sidebar, Header)
│   ├── pages/            ← Page-level components
│   ├── shared/           ← Reusable components (Modal, Table)
│   └── dialogs/          ← Modal dialogs
│
├── context/              ← Global state (Auth, App, Content)
│
├── hooks/                ← Custom logic (useRouter, useApi)
│
├── services/             ← External integrations (api.js)
│
└── styles/               ← Global styles & variables
```

**Benefits:**
- Easy to find code
- Component isolation
- Shared utilities clear
- Services separated
- Styles centralized

---

## React Component Pattern

```
COMPONENT TEMPLATE
──────────────────

// src/components/pages/Example.jsx
import { useAuth } from '../../hooks/useAuth';
import { useContent } from '../../hooks/useContent';
import styles from './Example.module.css';

export default function Example() {
  const { role } = useAuth();
  const { papers, loading } = useContent();

  if (loading) return <div>Loading...</div>;

  return (
    <div className={styles.container}>
      <h1>Example Page</h1>
      {/* JSX here */}
    </div>
  );
}

// src/components/pages/Example.module.css
.container {
  padding: 20px;
  max-width: 1200px;
}
```

**Pattern includes:**
✓ Hooks for state
✓ Imports from hooks/
✓ CSS Modules
✓ Conditional rendering
✓ Error boundaries (future)

---

## Lifecycle Example: Page Load

```
1. Browser loads http://localhost:5173
   │
   └─► index.html loaded
       │
       └─► App component renders

2. App.jsx mounts
   │
   ├─► AuthProvider wraps
   │   └─► Reads role from localStorage
   │
   ├─► AppProvider wraps
   │   └─► Initializes UI state
   │
   └─► ContentProvider wraps
       └─► useEffect fetchContent()
           └─► API call to localhost:8010

3. AppLayout renders
   │
   ├─► Sidebar renders
   │   └─► Shows nav for current role
   │
   ├─► Header renders
   │   └─► Shows current page
   │
   └─► MainContent renders
       └─► Reads hash (#role/page)
           └─► Routes to page component

4. Page component renders
   │
   └─► Uses hooks for data
       └─► Renders UI

5. User interacts
   │
   └─► Hooks/context update state
       └─► Components re-render (React)
```

---

## Performance Optimization Ready

```
BUILT-IN OPTIMIZATIONS
──────────────────────

✓ Code Splitting (Vite)
  └─► Separate chunks per route

✓ Tree Shaking
  └─► Remove unused code

✓ Lazy Loading (future)
  └─► Dynamic imports for routes

✓ Memoization (React)
  └─► useCallback, useMemo (added as needed)

✓ Context Optimization
  └─► Multiple contexts prevent re-render cascades

✓ CSS Modules
  └─► No runtime CSS-in-JS overhead

✓ Vite HMR
  └─► Instant refresh without full reload
```

---

## Security Architecture

```
SECURITY LAYERS
───────────────

Application Layer
├─► Environment variables (.env)
├─► No hardcoded secrets
└─► localStorage for non-sensitive data

API Layer
├─► Axios client with timeout
├─► Request/response logging
└─► Error handling

State Layer
├─► Context API (no prop drilling)
└─► Proper encapsulation

Component Layer
├─► No eval() or dangerouslySetInnerHTML
├─► XSS prevention
└─► Error boundaries (future)
```

---

This architecture is designed for:
- ✅ Scalability
- ✅ Maintainability
- ✅ Testability
- ✅ React Native portability
- ✅ Performance
- ✅ Developer experience

---

**Last Updated**: 2026-05-28  
**Status**: Phase 1 Complete ✅
