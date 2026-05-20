@echo off
title PinnacleIQ Demo — Research Pipeline
color 0A

echo.
echo  ============================================================
echo   PINNACLEIQ DEMO — Research Pipeline Backend
echo   Mankind Pharma
echo  ============================================================
echo.

cd /d "%~dp0"

echo  [1/3] Activating virtual environment...
if not exist "D:\venv\pinnacle\Scripts\activate.bat" (
  echo  ERROR: venv not found at D:\venv\pinnacle
  echo  Run: python -m venv D:\venv\pinnacle
  pause & exit /b 1
)
call D:\venv\pinnacle\Scripts\activate.bat

echo  [2/3] Installing backend dependencies...
pip install -q fastapi uvicorn python-multipart

echo  [3/3] Starting API server on http://localhost:8000
echo.
echo  ----------------------------------------------------------------
echo   NEXT STEPS:
echo   1. Open  demo\pipeline_ui.html  in your browser
echo   2. Select a topic from topics.txt
echo   3. Click "Run Research Pipeline"
echo   4. Click "Open Portal" to see content in PinnacleIQ
echo  ----------------------------------------------------------------
echo.

cd backend
python app.py

pause
