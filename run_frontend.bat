@echo off
setlocal EnableExtensions
title CareerForge AI - Frontend

echo ========================================================
echo      Starting CareerForge AI - React Frontend
echo                 Port 5173
echo ========================================================
echo.

cd /d "%~dp0frontend"

if not exist "node_modules" (
    echo ERROR: node_modules not found.
    echo Please run setup.bat first.
    echo.
    pause
    exit /b 1
)

echo Starting Vite development server...
echo.
call npm run dev -- --host 127.0.0.1 --port 5173

if errorlevel 1 (
    echo.
    echo ========================================================
    echo ERROR: Frontend server stopped with an error.
    echo ========================================================
    echo.
)

pause
endlocal
