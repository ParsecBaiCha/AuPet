# AuPet Project Launcher (robust version)
# Usage: powershell -ExecutionPolicy Bypass -File start.ps1
$ErrorActionPreference = 'Continue'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $root 'backend'
$frontendDir = Join-Path $root '2026081247-萌宠智伴-前端代码\frontend'
$mysqlService = 'QnSQL80'
$backendLog = Join-Path $root 'backend\backend.log'
$frontendLog = Join-Path $root 'backend\frontend.log'

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "       AuPet Project Launcher" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# ---- [1/3] MySQL ----
Write-Host "[1/3] Checking MySQL service ($mysqlService)..." -ForegroundColor Green
$svc = Get-Service -Name $mysqlService -ErrorAction SilentlyContinue
if ($svc -and $svc.Status -eq 'Running') {
    Write-Host "      MySQL is already running." -ForegroundColor DarkGray
} elseif ($svc) {
    try {
        Start-Service -Name $mysqlService -ErrorAction Stop
        Start-Sleep -Seconds 2
        Write-Host "      MySQL started." -ForegroundColor DarkGray
    } catch {
        Write-Host "      [ERROR] Failed to start MySQL: $_" -ForegroundColor Red
        Write-Host "      请以管理员身份运行本脚本，或手动: services.msc -> QnSQL80 -> 启动" -ForegroundColor Yellow
    }
} else {
    Write-Host "      [ERROR] MySQL service '$mysqlService' not found!" -ForegroundColor Red
}

# ---- [2/3] Backend ----
Write-Host ""
Write-Host "[2/3] Starting backend (Flask on :8000)..." -ForegroundColor Green
try {
    Start-Process -FilePath 'cmd.exe' -ArgumentList "/c", "python app.py > `"$backendLog`" 2>&1" `
        -WorkingDirectory $backendDir -WindowStyle Hidden
    Write-Host "      Backend launching, log -> $backendLog" -ForegroundColor DarkGray
} catch {
    Write-Host "      [ERROR] Failed to start backend: $_" -ForegroundColor Red
}
Start-Sleep -Seconds 3

# ---- [3/3] Frontend ----
Write-Host ""
Write-Host "[3/3] Starting frontend (Vite on :3000)..." -ForegroundColor Green
try {
    Start-Process -FilePath 'cmd.exe' -ArgumentList "/c", "npm run dev > `"$frontendLog`" 2>&1" `
        -WorkingDirectory $frontendDir -WindowStyle Hidden
    Write-Host "      Frontend launching, log -> $frontendLog" -ForegroundColor DarkGray
} catch {
    Write-Host "      [ERROR] Failed to start frontend: $_" -ForegroundColor Red
}
Start-Sleep -Seconds 4

# ---- status check ----
Write-Host ""
$bk = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
$ft = Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue
if ($bk) { Write-Host "  Backend  : OK  http://localhost:8000" -ForegroundColor Green }
else      { Write-Host "  Backend  : FAILED - 请查看 $backendLog" -ForegroundColor Red }
if ($ft) { Write-Host "  Frontend : OK  http://localhost:3000" -ForegroundColor Green }
else      { Write-Host "  Frontend : FAILED - 请查看 $frontendLog" -ForegroundColor Red }

Write-Host ""
Write-Host "  浏览器打开: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  账号: 学生 20250101/123456 | 教师 T001/123456 | 管理 admin/123456" -ForegroundColor Cyan
Write-Host ""
Write-Host "  停止服务请运行 停止项目.bat" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Start-Sleep -Seconds 8
