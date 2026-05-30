# PinnacleIQ React Application

React.js conversion of the vanilla JavaScript PinnacleIQ application with support for both web and mobile (React Native) platforms.

## 📁 Project Structure

```
src/
├── components/
│   ├── layouts/
│   │   ├── AppLayout.jsx           # Main app container
│   │   ├── Sidebar.jsx             # Left navigation
│   │   ├── Header.jsx              # Top bar with role switcher
│   │   └── MainContent.jsx         # Page router
│   ├── pages/
│   │   ├── Placeholder.jsx         # Placeholder for coming pages
│   │   ├── ContentLibrary.jsx      # Search, filter, sorting (Phase 2)
│   │   ├── Dashboard.jsx           # KPIs, sharing report (Phase 3)
│   │   ├── Pipeline.jsx            # Four-agent orchestration (Phase 4)
│   │   ├── DoctorDirectory.jsx     # Doctor list and filtering (Phase 4)
│   │   └── Analytics.jsx           # Charts and metrics (Phase 4)
│   └── shared/
│       ├── Modal.jsx               # Reusable modal (Phase 2)
│       ├── Table.jsx               # Data table component (Phase 2)
│       └── Button.jsx              # Custom button (Phase 2)
├── context/
│   ├── AuthContext.jsx             # Role & user info
│   ├── AppContext.jsx              # UI state (filters, sorting, tabs)
│   └── ContentContext.jsx          # Content library state
├── hooks/
│   ├── useRouter.js                # Hash-based routing
│   ├── useApi.js                   # API call wrapper
│   ├── useFilters.js               # Filter logic
│   ├── useAuth.js                  # Auth context hook
│   ├── useAppContext.js            # App context hook
│   └── useContent.js               # Content context hook
├── services/
│   ├── api.js                      # Axios API client
│   ├── storage.js                  # localStorage utilities (Phase 2)
│   └── excel.js                    # Excel generation (Phase 3)
├── styles/
│   ├── variables.css               # CSS variables (colors, shadows)
│   ├── index.css                   # Global base styles
│   └── components/                 # Component-scoped CSS modules
├── App.jsx                         # Root component
├── index.js                        # Entry point
└── .env.example                    # Environment variables

public/
└── index.html                      # HTML shell

Configuration:
├── package.json                    # Dependencies
├── vite.config.js                  # Vite configuration
└── .gitignore
```

## 🚀 Quick Start

### Install Dependencies
```bash
cd react-app
npm install
```

### Development Server
```bash
npm run dev
```
Starts Vite dev server on `http://localhost:5173`

### Build for Production
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

## 🏗️ Architecture

### State Management (Context API)

**AuthContext**: User role and permissions
- `role`: 'medical-affairs' | 'bu-head'
- `setRole(newRole)`: Switch roles
- `canExport`, `canRunPipeline`: Permission flags

**AppContext**: UI and navigation state
- `currentTab`: Active page
- `setCurrentTab(tab)`: Change page
- `sidebarOpen`: Mobile sidebar state
- `filters`: Active filters (specialty, therapy area, tags, date range)
- `sortField`, `sortDirection`: Current sort
- `notifications`: Toast messages

**ContentContext**: Content library data
- `papers`: All articles
- `loading`, `error`: Fetch state
- `fetchContent()`: Load articles from API
- `updateContent(id, updates)`: Update article
- `deleteContent(id)`: Remove article

### Routing (Hash-Based)

Format: `#role/page`

Examples:
- `#medical-affairs/library`
- `#medical-affairs/dashboard`
- `#bu-head/analytics`

Uses `useRouter()` hook:
```javascript
const { currentRole, currentPage, navigate } = useRouter();
navigate('medical-affairs', 'dashboard');
```

### API Client

Configured in `services/api.js` with endpoints:

```javascript
api.content.list()
api.content.get(id)
api.content.create(data)
api.content.update(id, data)
api.content.delete(id)

api.sharing.logShare(contentId, method)
api.sharing.getReport()
api.sharing.getBusinessReport()

api.pipeline.run(input)
api.pipeline.save(output)

api.doctors.list()
api.doctors.search(query)
```

## 📋 Implementation Phases

### ✅ Phase 1: Foundation (COMPLETED)
- [x] Vite + React setup
- [x] Context API (Auth, App, Content)
- [x] Custom hooks (useRouter, useApi, useFilters)
- [x] Layout components (AppLayout, Sidebar, Header)
- [x] CSS variables and global styles
- [x] API client configuration

### ⏳ Phase 2: Content Library (READY)
- [ ] ContentLibrary page component
- [ ] SearchBar component
- [ ] FilterPanel component
- [ ] ContentCard component
- [ ] Grid/List view toggle
- [ ] ShareDialog modal
- [ ] Sorting controls

### ⏳ Phase 3: Dashboard & Reports (READY)
- [ ] Dashboard page
- [ ] KPI cards
- [ ] SharingReport table
- [ ] BusinessReport generation
- [ ] Timeline component

### ⏳ Phase 4: Pipeline & Other Pages (READY)
- [ ] Pipeline page with four-agent UI
- [ ] DoctorDirectory page
- [ ] Analytics page
- [ ] Settings page

### ⏳ Phase 5: Polish & Testing (READY)
- [ ] End-to-end testing
- [ ] Performance optimization
- [ ] Mobile responsiveness
- [ ] Error boundaries
- [ ] Documentation

## 🔧 Environment Variables

Create `.env.local`:

```env
VITE_API_URL=http://localhost:8010
VITE_APP_NAME=PinnacleIQ
```

## 📱 React Native Sharing

The modular architecture allows 100% code reuse for mobile:

```
pinnacle-monorepo/
├── packages/
│   ├── shared/                # 100% shared code
│   │   ├── contexts/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── utils/
│   ├── web/                   # React app (this folder)
│   └── mobile/                # React Native app (expo)
```

## 🎨 Styling Approach

**CSS Modules** for component-scoped styles:
- No global class name conflicts
- Component CSS lives next to JSX
- Example: `ContentCard.jsx` + `ContentCard.module.css`

**CSS Variables** for theming:
- Defined in `src/styles/variables.css`
- Easy to change brand colors
- Mobile-friendly with dark mode support (future)

## 🧪 Testing

(To be implemented in Phase 5)
```bash
npm run test
```

## 📚 Learning Resources

- [React Context API](https://react.dev/reference/react/useContext)
- [Custom Hooks](https://react.dev/learn/reusing-logic-with-custom-hooks)
- [Vite](https://vitejs.dev)
- [CSS Modules](https://github.com/css-modules/css-modules)

## ⚠️ Important Notes

1. **API Base URL**: Configured in `src/services/api.js` (default: `http://localhost:8010`)
2. **Hash Routing**: Uses `window.location.hash` for persistence (browser refresh-safe)
3. **No Redux/Zustand**: Uses Context API for simplicity and React Native compatibility
4. **Git Policy**: No commits until user explicitly approves (development in local repo only)

## 🤝 Migration from Vanilla JS

Key transformations:
- Global variables → Context state
- Direct DOM manipulation → React components
- Event listeners → useEffect hooks
- localStorage → Custom storage service
- Inline styles → CSS Modules
- HTML divs/classes → React components

## 📝 Next Steps

1. Run `npm install && npm run dev`
2. Navigate to `http://localhost:5173`
3. Test role switcher and page navigation
4. Begin Phase 2: ContentLibrary implementation

---

**Version**: 1.0.0  
**Created**: 2026-05-28  
**Status**: Phase 1 Complete ✅
