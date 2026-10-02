@echo off
echo ========================================================
echo Starting CareerForge AI - Vite React Frontend (Port 5173)...
echo ========================================================
cd /d "%~dp0frontend"
npm run dev -- --host 127.0.0.1 --port 5173
pause
