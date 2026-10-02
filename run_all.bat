@echo off
echo ========================================================
echo Launching CareerForge AI Operating System...
echo ========================================================
start "CareerForge Backend" cmd /c "run_backend.bat"
timeout /t 2 /nobreak >nul
start "CareerForge Frontend" cmd /c "run_frontend.bat"
echo.
echo CareerForge AI is running!
echo Access the application in your browser at:
echo http://127.0.0.1:5173
echo.
