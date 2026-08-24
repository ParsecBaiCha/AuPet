# AuPet Stop Script
Write-Host "Stopping backend and frontend..." -ForegroundColor Yellow
Get-Process -Name "python" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 1
Write-Host "All services stopped." -ForegroundColor Green
Start-Sleep -Seconds 2
