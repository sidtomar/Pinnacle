# PinnacleIQ — Quick Start Guide

## Prerequisites
- Python 3.10+
- Git

---

## Step 1 — Clone the repo
```powershell
git clone https://github.com/sidtomar/Pinnacle.git
cd Pinnacle
git checkout develop
```

---

## Step 2 — Install dependencies
```powershell
cd demo/backend
pip install -r requirements-demo.txt
```

---

## Step 3 — Start the server
```powershell
python app.py
```
You should see:
```
Uvicorn running on http://0.0.0.0:8010
```

---

## Step 4 — Open the app
Open your browser and go to:
```
http://localhost:8010/app
```

---

## Login Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | `admin@mankind.in` | `Admin123` |
| Medical Affairs | `prashant.agarwal@mankind.in` | `Test` |
| PMT / BU Head | `jijo@mankind.in` | `Test` |

---

## If port 8010 is already in use
```powershell
# Find and kill the process using port 8010
netstat -ano | findstr :8010
taskkill /PID <PID_from_above> /F

# Then restart
python app.py
```

---

## Notes
- No API keys needed — runs on mock data by default
- Database resets on fresh clone (no stale data issues)
- Tested on Windows 11 / Python 3.11
