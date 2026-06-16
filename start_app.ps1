# ═══════════════════════════════════════════════════════════════
# PinnacleIQ — One-Click Startup Script
# ═══════════════════════════════════════════════════════════════
# Starts the FastAPI backend (port 8010) and opens the portal
# in your default browser.
#
# Usage:
#   Double-click start_app.bat
#   OR from PowerShell:  .\start_app.ps1
# ═══════════════════════════════════════════════════════════════

$ErrorActionPreference = "Stop"

$Port       = 8010
$BackendDir = Join-Path $PSScriptRoot "demo\backend"
$PortalUrl  = "http://127.0.0.1:$Port/app"
$HealthUrl  = "http://127.0.0.1:$Port/"

Write-Host ""
Write-Host "  ╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "  ║       PinnacleIQ — Starting Application      ║" -ForegroundColor Cyan
Write-Host "  ╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ── Step 1: Check if backend is already running ─────────────────
function Test-Backend {
    try {
        $r = Invoke-WebRequest -Uri $HealthUrl -UseBasicParsing -TimeoutSec 2
        return $r.StatusCode -eq 200
    } catch {
        return $false
    }
}

if (Test-Backend) {
    Write-Host "  [OK] Backend already running on port $Port" -ForegroundColor Green
}
else {
    # ── Step 2: Kill any stale process on port 8010 ─────────────
    Write-Host "  [..] Checking for stale process on port $Port..." -ForegroundColor DarkGray
    $stale = netstat -ano | Select-String ":$Port\s" | ForEach-Object {
        ($_ -split '\s+')[-1]
    } | Select-Object -Unique
    foreach ($pid in $stale) {
        if ($pid -match '^\d+$') {
            try {
                Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                Write-Host "  [OK] Killed stale process PID $pid on port $Port" -ForegroundColor DarkGray
            } catch {}
        }
    }

    # ── Step 3: Verify backend directory exists ──────────────────
    if (-not (Test-Path (Join-Path $BackendDir "app.py"))) {
        Write-Host "  [ERROR] app.py not found in $BackendDir" -ForegroundColor Red
        Write-Host "  Make sure you run this script from the repo root." -ForegroundColor Red
        Read-Host "  Press Enter to exit"
        exit 1
    }

    # ── Step 4: Start the backend in a new window ────────────────
    # -X utf8 forces UTF-8 stdio so print() doesn't crash on em-dash /
    # unicode characters in notification text (caused intermittent 500s
    # on first-time approve/improve-request before this fix).
    Write-Host "  [..] Starting backend server (port $Port)..." -ForegroundColor Yellow
    Start-Process -FilePath "python" `
        -ArgumentList "-X","utf8","app.py" `
        -WorkingDirectory $BackendDir `
        -WindowStyle Minimized

    # ── Step 5: Wait for the server to come up (max 30s) ─────────
    $maxWait = 30
    $waited  = 0
    while (-not (Test-Backend)) {
        Start-Sleep -Seconds 1
        $waited++
        if ($waited -ge $maxWait) {
            Write-Host "  [ERROR] Backend did not start within $maxWait seconds." -ForegroundColor Red
            Write-Host "  Check the minimized python window for errors." -ForegroundColor Red
            Read-Host "  Press Enter to exit"
            exit 1
        }
        Write-Host "  [..] Waiting for backend... ($waited s)" -ForegroundColor DarkGray
    }
    Write-Host "  [OK] Backend is up on port $Port" -ForegroundColor Green
}

# ── Step 6: Open the portal in the default browser ──────────────
Write-Host "  [..] Opening portal in browser..." -ForegroundColor Yellow
Start-Process $PortalUrl
Write-Host "  [OK] Portal launched: $PortalUrl" -ForegroundColor Green

Write-Host ""
Write-Host "  ────────────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host "  Demo accounts:" -ForegroundColor White
Write-Host "    Admin:    admin1@mankind.in / Test"
Write-Host "    BU Head:  jijo@mankind.in / Test"
Write-Host "    MA:       prashant.agarwal@mankind.in / Test"
Write-Host "  ────────────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host "  To stop the backend: close the minimized python"
Write-Host "  window, or run:  Get-Process python | Stop-Process"
Write-Host ""
