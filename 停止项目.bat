@echo off
title AuPet Stopper
:: Check for admin privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)
powershell -ExecutionPolicy Bypass -File "%~dp0stop.ps1"
