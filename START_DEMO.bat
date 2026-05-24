@echo off
title PinnacleIQ — Management Demo
color 0B
cls

echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║         PINNACLEIQ  ·  AI Research Pipeline Demo            ║
echo  ║                  Mankind Pharma  ·  2025                    ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

:: ── Kill any process already using port 8000 ────────────────────────────────
echo  [1/4] Clearing port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000 " 2^>nul') do (
  taskkill /PID %%a /F >nul 2>&1
)
timeout /t 1 /nobreak >nul

:: ── Activate virtual environment ─────────────────────────────────────────────
echo  [2/4] Activating virtual environment...
if exist "D:\venv\pinnacle\Scripts\activate.bat" (
  call D:\venv\pinnacle\Scripts\activate.bat
) else if exist "venv\Scripts\activate.bat" (
  call venv\Scripts\activate.bat
) else (
  echo.
  echo  NOTE: No venv found — using system Python.
  echo  To create venv: python -m venv D:\venv\pinnacle
  echo.
)

:: ── Start FastAPI backend ─────────────────────────────────────────────────────
echo  [3/4] Starting Research Pipeline API on http://localhost:8000 ...
start "PinnacleIQ API" cmd /k "cd /d "%~dp0demo\backend" && python app.py"
timeout /t 3 /nobreak >nul

:: ── Open the portal in Chrome ─────────────────────────────────────────────────
echo  [4/4] Launching PinnacleIQ Portal in Chrome...
set "HTML=%~dp0pinnacleiq_v13.html"

where chrome >nul 2>&1
if %errorlevel%==0 (
  start chrome "%HTML%"
) else (
  for %%p in (
    "%ProgramFiles%\Google\Chrome\Application\chrome.exe"
    "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
    "%LocalAppData%\Google\Chrome\Application\chrome.exe"
  ) do (
    if exist %%p ( start %%p "%HTML%" & goto :done )
  )
  :: Fallback to default browser
  start "" "%HTML%"
)

:done
echo.
echo  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo   ✅  API running at   →   http://localhost:8000
echo   ✅  API docs         →   http://localhost:8000/docs
echo   ✅  Portal open in Chrome
echo.
echo   DEMO FLOW:
echo   1. Switch to "PMT" role  →  click "Research Pipeline" in sidebar
echo   2. Select a topic (e.g. SGLT2 or GLP-1)
echo   3. Click "Run Pipeline"  →  watch 4 agents run live
echo   4. View results: Summary / Key Findings / Short Article / JSON
echo   5. Click "Review in Library →"  →  switch to MA role, approve card
echo.
echo  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo   Close this window to stop the API server.
echo  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
pause
