# AuPet Project Launcher
$env:PATH = $env:PATH + ";C:\Users\Parsec\AppData\Local\Programs\Python\Python312;C:\Program Files\nodejs"

$backendDir = "d:\DESK\a自建桌面\萌宠智伴\backend"
$frontendDir = "d:\DESK\a自建桌面\萌宠智伴\2026081247-萌宠智伴-前端代码\frontend"
$mysqlService = "QnSQL80"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "       AuPet Project Launcher" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services to start:"
Write-Host "  [0] MySQL    (QnSQL80)  -> localhost:3306"
Write-Host "  [1] Backend  (Flask)    -> http://localhost:8000"
Write-Host "  [2] Frontend (Vite)     -> http://localhost:3000"
Write-Host ""
Write-Host "Press any key to start..."
[Console]::ReadKey($true) | Out-Null

Write-Host ""
Write-Host "[0/3] Starting MySQL service..." -ForegroundColor Green
$svc = Get-Service -Name $mysqlService -ErrorAction SilentlyContinue
if ($svc) {
    if ($svc.Status -eq 'Running') {
        Write-Host "      MySQL is already running." -ForegroundColor DarkGray
    } else {
        try {
            Start-Service -Name $mysqlService -ErrorAction Stop
            Start-Sleep -Seconds 2
            Write-Host "      MySQL started." -ForegroundColor DarkGray
        } catch {
            Write-Host "      [Warning] Failed to start MySQL: $_" -ForegroundColor Red
            Write-Host "      Please start it manually: services.msc -> QnSQL80 -> Start" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "      [Warning] MySQL service '$mysqlService' not found!" -ForegroundColor Red
}

Write-Host ""
Write-Host "[1/3] Starting backend (hidden)..." -ForegroundColor Green
Start-Process -FilePath "python.exe" -ArgumentList "app.py" -WorkingDirectory $backendDir -WindowStyle Hidden
Write-Host "      Backend started, waiting 3s..."
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "[2/3] Starting frontend (hidden)..." -ForegroundColor Green
Start-Process -FilePath "npm.cmd" -ArgumentList "run","dev" -WorkingDirectory $frontendDir -WindowStyle Hidden
Write-Host "      Frontend started, waiting 3s..."
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  All services running in background!" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Backend:  http://localhost:8000"
Write-Host "  Frontend: http://localhost:3000"
Write-Host ""
Write-Host "  Open in browser: http://localhost:3000"
Write-Host ""
Write-Host "  Accounts:"
Write-Host "    Student (low):   20250101 / 123456"
Write-Host "    Student (high):  20260101 / 123456"
Write-Host "    Teacher:  T001 / 123456"
Write-Host "    Admin:    admin / 123456"
Write-Host ""
Write-Host "  Services run in background."
Write-Host "  Use 停止项目.bat to stop everything."
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Start-Sleep -Seconds 2
