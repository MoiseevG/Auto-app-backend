#!/usr/bin/env powershell
Set-Location "c:\Users\Moiseev\Desktop\Moiseev_study\MEhanic\auto-app\backend"
Write-Host "Starting FastAPI server..."
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --log-level info
