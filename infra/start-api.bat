@echo off
REM Start AdProof backend (SQLite demo mode)
cd /d %~dp0..\apps\worker
set DATABASE_URL=sqlite:///./adproof_local.db
set ADPROOF_DEMO_MODE=true
set API_BASE_URL=http://localhost:8000
if not exist .venv\Scripts\python.exe (
  echo Creating Python venv...
  "C:\Users\aagne\AppData\Local\Programs\Python\Python310\python.exe" -m venv .venv
  .venv\Scripts\pip install -r requirements.txt
)
echo Starting API on http://localhost:8000
.venv\Scripts\python.exe -m uvicorn main:app --port 8000
