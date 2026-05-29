# 🚀 Quick Start Guide

Get the React app running in 3 minutes.

## Prerequisites

- **Node.js** 18+ installed
- **npm** 9+ installed
- **Backend** running on port 8010
  ```bash
  # In another terminal, from D:\Codebase\Pinnacle\demo
  python backend/app.py --port 8010
  ```

## ⚡ 3-Minute Setup

### Step 1: Navigate to Project (30 seconds)
```bash
cd D:\Codebase\Pinnacle\react-app
```

### Step 2: Install Dependencies (1 minute)
```bash
npm install
```

Expected output:
```
added 200 packages in 45s
```

### Step 3: Start Development Server (30 seconds)
```bash
npm run dev
```

Expected output:
```
  VITE v5.0.0  ready in 234 ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

### Step 4: Open Browser (auto-opens)
Browser automatically opens at `http://localhost:5173/`

---

## ✅ Verification

After app loads, check:

- [ ] **Left sidebar visible** (navy blue)
- [ ] **Logo shows** "PinnacleIQ"
- [ ] **User badge shows** "MA" (Medical Affairs)
- [ ] **Navigation items** visible (Content Library, Dashboard, Pipeline, Doctors)
- [ ] **Top header** shows breadcrumb
- [ ] **Role switcher** in top-right corner
- [ ] **Main area** shows placeholder page
- [ ] **No red errors** in console (F12)

If all checkmarks pass ✅, you're ready!

---

## 🎮 Test the Features

### Test Role Switching
1. Click role switcher (top-right) → see dropdown
2. Select "BU Head" → page updates
3. Note: Navigation items change (no Pipeline/Doctors)
4. URL changes to `#bu-head/library`
5. Refresh browser → Stays on BU Head

### Test Navigation
1. Click "Content Library" → URL becomes `#bu-head/library`
2. Click "Analytics" → URL becomes `#bu-head/analytics`
3. Switch back to "Medical Affairs" → Full menu returns
4. Click "Dashboard" → URL becomes `#medical-affairs/dashboard`

### Test Persistence
1. Note current URL: `#medical-affairs/dashboard`
2. Refresh browser (F5)
3. App stays on same page ✓

---

## 🛠️ Common Tasks

### Open Console (DevTools)
```
Windows/Linux: F12 or Ctrl+Shift+I
Mac: Cmd+Option+I
```

Check for errors/logs related to API calls.

### Stop Dev Server
```
Press: Ctrl+C in terminal
```

### Rebuild After Changes
Changes auto-reload! No manual rebuild needed (HMR = Hot Module Reload).

### Check Backend Connection
Open browser console (F12):
```javascript
// Test API connection
fetch('http://localhost:8010/content')
  .then(r => r.json())
  .then(d => console.log('✓ Connected:', d))
  .catch(e => console.log('✗ Error:', e))
```

Expected: See `✓ Connected:` with data

---

## 📁 Project Structure (Quick Reference)

```
react-app/
├── src/
│   ├── components/        # React components
│   ├── context/           # State management
│   ├── hooks/             # Custom hooks
│   ├── services/          # API client
│   ├── styles/            # CSS variables & base
│   ├── App.jsx            # Root component
│   └── index.js           # Entry point
├── public/
│   └── index.html         # HTML shell
├── package.json           # Dependencies
├── vite.config.js         # Build config
└── README.md              # Full documentation
```

## 🔗 Important URLs

| URL | Purpose |
|-----|---------|
| http://localhost:5173 | React app |
| http://localhost:8010 | Backend API |
| http://localhost:5173/#medical-affairs/library | MA - Content Library |
| http://localhost:5173/#bu-head/analytics | BU Head - Analytics |

## 📝 Next Steps

### Option 1: Review Current App
- Explore sidebar navigation
- Test role switching
- Check browser console for any errors
- Review code in `src/components/layouts/`

### Option 2: Read Documentation
- `README.md` - Full overview
- `PHASE_1_SUMMARY.md` - What was built
- `IMPLEMENTATION_GUIDE.md` - Detailed breakdown
- `NEXT_STEPS.md` - Phase 2 planning

### Option 3: Start Phase 2
- Need ContentLibrary page? → See `NEXT_STEPS.md`
- Ready to implement? → I can start building components

## ⚠️ Troubleshooting

### Port 5173 already in use
```bash
npm run dev -- --port 5174
```

### Backend not responding
```bash
# Make sure backend is running
# In separate terminal:
cd D:\Codebase\Pinnacle\demo
python backend/app.py --port 8010
```

Check in browser console for API errors (F12).

### Changes not showing
- Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
- Close and re-open terminal
- Delete `node_modules` and `npm install` again

### Module not found error
Make sure `npm install` completed without errors.

---

## 💡 Tips

1. **Keep dev server running** - Leave terminal open while coding
2. **Use React DevTools** - Install browser extension for better debugging
3. **Check console errors** - F12 → Console tab
4. **Review network requests** - F12 → Network tab
5. **Test on mobile** - Can access from phone on same network:
   ```
   http://<your-computer-ip>:5173
   ```

---

## 🎯 Success Criteria

App is ready when:
- [x] Loads without errors
- [x] All UI elements visible
- [x] Role switcher works
- [x] Navigation works
- [x] URL persists on refresh
- [x] Console has no errors
- [x] Backend connection works

---

## 📞 Need Help?

**Check these in order:**
1. Browser console (F12) for error messages
2. Troubleshooting section above
3. IMPLEMENTATION_GUIDE.md for detailed info
4. README.md for architecture questions

---

## ✨ You're All Set!

The foundation is complete. React app is running and ready for:
- ✅ Phase 2: Content Library page
- ✅ Feature development
- ✅ React Native migration

Enjoy! 🎉

---

**Created**: 2026-05-28  
**Status**: Ready for production development
