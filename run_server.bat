@echo off
cd /d "c:\Users\Moiseev\Desktop\Moiseev_study\MEhanic\auto-app\backend"
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --log-level info
pause
