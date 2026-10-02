@echo off
setlocal
title CareerForge AI

echo ========================================================
echo       Launching CareerForge AI Operating System
echo ========================================================
echo.

start "CareerForge Backend" cmd /c ""%~dp0run_backend.bat""
timeout /t 3 /nobreak >nul
start "CareerForge Frontend" cmd /c ""%~dp0run_frontend.bat""

echo ========================================================
echo              CareerForge AI is running
echo ========================================================
echo.
echo Backend:
echo http://127.0.0.1:8000
echo.
echo Frontend:
echo http://127.0.0.1:5173
echo.
echo API documentation:
echo http://127.0.0.1:8000/docs
echo.
pause
endlocal
