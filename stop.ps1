# AuPet Project Stopper
$mysqlService = "QnSQL80"

Write-Host "============================================" -ForegroundColor Yellow
Write-Host "       AuPet Project Stopper" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Yellow
Write-Host ""

# Kill backend (port 8000)
$backendPid = (Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Where-Object State -eq 'Listen' | Select-Object -First 1).OwningProcess
if ($backendPid) {
    Stop-Process -Id $backendPid -Force -ErrorAction SilentlyContinue
    Write-Host "[1/3] Backend (PID $backendPid) stopped." -ForegroundColor Green
} else {
    Write-Host "[1/3] Backend was not running." -ForegroundColor DarkGray
}

# Kill frontend (port 3000)
$frontendPid = (Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue | Where-Object State -eq 'Listen' | Select-Object -First 1).OwningProcess
if ($frontendPid) {
    Stop-Process -Id $frontendPid -Force -ErrorAction SilentlyContinue
    Write-Host "[2/3] Frontend (PID $frontendPid) stopped." -ForegroundColor Green
} else {
    Write-Host "[2/3] Frontend was not running." -ForegroundColor DarkGray
}

# Stop MySQL
Write-Host "[3/3] Stopping MySQL..." -ForegroundColor Green
$svc = Get-Service -Name $mysqlService -ErrorAction SilentlyContinue
if ($svc -and $svc.Status -eq 'Running') {
    try {
        Stop-Service -Name $mysqlService -ErrorAction Stop
        Write-Host "      MySQL stopped." -ForegroundColor DarkGray
    } catch {
        Write-Host "      [Warning] Failed to stop MySQL: $_" -ForegroundColor Red
    }
} else {
    Write-Host "      MySQL was not running." -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  All services stopped." -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Start-Sleep -Seconds 2
