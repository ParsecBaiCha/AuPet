# AuPet Project Launcher
$env:PATH = $env:PATH + ";C:\Users\Parsec\AppData\Local\Programs\Python\Python312;C:\Program Files\nodejs"

$backendDir = "d:\DESK\a自建桌面\萌宠智伴\backend"
$frontendDir = "d:\DESK\a自建桌面\萌宠智伴\2026081247-萌宠智伴-前端代码\frontend"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "       AuPet Project Launcher" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services to start:"
Write-Host "  [1] Backend  (Flask)  -> http://localhost:8000"
Write-Host "  [2] Frontend (Vite)   -> http://localhost:3000"
Write-Host ""
Write-Host "Press any key to start..."
[Console]::ReadKey($true) | Out-Null

Write-Host ""
Write-Host "[1/2] Starting backend..." -ForegroundColor Green
Start-Process -FilePath "cmd" -ArgumentList "/k", "python app.py" -WorkingDirectory $backendDir

Write-Host "      Backend window opened, waiting 3s..."
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "[2/2] Starting frontend..." -ForegroundColor Green
Start-Process -FilePath "cmd" -ArgumentList "/k", "npm run dev" -WorkingDirectory $frontendDir

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Started!" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Backend:  http://localhost:8000"
Write-Host "  Frontend: http://localhost:3000"
Write-Host ""
Write-Host "  Open in browser: http://localhost:3000"
Write-Host ""
Write-Host "  Accounts:"
Write-Host "    Student:  20250101 / 123456"
Write-Host "    Teacher:  T001 / 123456"
Write-Host "    Admin:    admin / 123456"
Write-Host ""
Write-Host "  Close the windows to stop services."
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to exit this launcher"
