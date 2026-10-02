@echo off
setlocal
title CareerForge AI - Backend

echo ========================================================
echo      Starting CareerForge AI - FastAPI Backend
echo                 Port 8000
echo ========================================================
echo.

cd /d "%~dp0backend"

if not exist "venv\Scripts\python.exe" (
    echo ERROR: Python virtual environment not found.
    echo Please run setup.bat first.
    echo.
    pause
    exit /b 1
)

echo Starting FastAPI server...
echo.
venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

pause
endlocal
