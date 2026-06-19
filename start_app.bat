@echo off
REM ═══════════════════════════════════════════════════════════
REM  PinnacleIQ — One-Click Startup (double-click this file)
REM  Starts backend on port 8010 + opens portal in browser
REM ═══════════════════════════════════════════════════════════
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_app.ps1"
pause
