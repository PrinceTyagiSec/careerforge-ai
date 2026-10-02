@echo off
setlocal EnableExtensions EnableDelayedExpansion

title CareerForge AI - Setup

echo ========================================================
echo        CareerForge AI - First Time Setup
echo ========================================================
echo.

REM ========================================================
REM 1. Check Python
REM ========================================================

echo [1/7] Checking Python...

python --version >nul 2>&1
if %errorlevel% neq 0 (
echo.
echo ERROR: Python is not installed or not available in PATH.
echo.
echo Please install Python 3.10+ from:
echo https://www.python.org/downloads/
echo.
echo IMPORTANT: Enable "Add Python to PATH" during installation.
echo.
pause
exit /b 1
)

for /f "tokens=2" %%A in ('python --version 2^>^&1') do set PYTHON_VERSION=%%A
echo Python found: %PYTHON_VERSION%
echo.

REM ========================================================
REM 2. Check Node.js
REM ========================================================

echo [2/7] Checking Node.js...

node --version >nul 2>&1
if %errorlevel% neq 0 (
echo.
echo ERROR: Node.js is not installed or not available in PATH.
echo.
echo Please install Node.js LTS from:
echo https://nodejs.org/
echo.
pause
exit /b 1
)

for /f "tokens=*" %%A in ('node --version 2^>^&1') do set NODE_VERSION=%%A
echo Node.js found: %NODE_VERSION%
echo.

REM ========================================================
REM 3. Check npm
REM ========================================================

echo [3/7] Checking npm...

npm --version >nul 2>&1
if %errorlevel% neq 0 (
echo.
echo ERROR: npm is not available.
echo Please reinstall Node.js LTS.
echo.
pause
exit /b 1
)

for /f "tokens=*" %%A in ('npm --version 2^>^&1') do set NPM_VERSION=%%A
echo npm found: %NPM_VERSION%
echo.

REM ========================================================
REM 4. Setup Backend
REM ========================================================

echo [4/7] Setting up Python backend...
echo.

if not exist "%~dp0backend" (
echo ERROR: backend folder not found.
echo Expected:
echo %~dp0backend
echo.
pause
exit /b 1
)

cd /d "%~dp0backend"

if not exist "venv" (
echo Creating Python virtual environment...
python -m venv venv

```
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to create Python virtual environment.
    echo.
    pause
    exit /b 1
)
```

) else (
echo Python virtual environment already exists.
)

echo.
echo Activating virtual environment...
call "venv\Scripts\activate.bat"

if %errorlevel% neq 0 (
echo.
echo ERROR: Could not activate Python virtual environment.
echo.
pause
exit /b 1
)

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.

if exist "requirements.txt" (
echo Installing backend dependencies from requirements.txt...
python -m pip install -r requirements.txt

```
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Backend dependency installation failed.
    echo.
    pause
    exit /b 1
)
```

) else (
echo WARNING: backend\requirements.txt was not found.
echo Skipping backend dependency installation.
)

echo.
echo Backend setup complete.
echo.

REM ========================================================
REM 5. Setup Frontend
REM ========================================================

echo [5/7] Setting up React frontend...
echo.

cd /d "%~dp0frontend"

if not exist "package.json" (
echo.
echo ERROR: frontend\package.json was not found.
echo.
pause
exit /b 1
)

echo Installing frontend dependencies...
call npm install

if %errorlevel% neq 0 (
echo.
echo ERROR: Frontend dependency installation failed.
echo.
pause
exit /b 1
)

echo.
echo Frontend setup complete.
echo.

REM ========================================================
REM 6. Create run_backend.bat
REM ========================================================

echo [6/7] Creating startup scripts...
echo.

cd /d "%~dp0"

(
echo @echo off
echo title CareerForge AI - Backend
echo.
echo echo ========================================================
echo echo Starting CareerForge AI - FastAPI Backend ^(Port 8000^)...
echo echo ========================================================
echo.
echo cd /d "%%~dp0backend"
echo.
echo if not exist "venv\Scripts\python.exe" ^(
echo     echo ERROR: Python virtual environment not found.
echo     echo Please run setup.bat first.
echo     pause
echo     exit /b 1
echo ^)
echo.
echo venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
echo.
echo pause
) > "run_backend.bat"

REM ========================================================
REM 7. Create run_frontend.bat
REM ========================================================

(
echo @echo off
echo title CareerForge AI - Frontend
echo.
echo echo ========================================================
echo echo Starting CareerForge AI - Vite React Frontend ^(Port 5173^)...
echo echo ========================================================
echo.
echo cd /d "%%~dp0frontend"
echo.
echo if not exist "node_modules" ^(
echo     echo ERROR: node_modules not found.
echo     echo Please run setup.bat first.
echo     pause
echo     exit /b 1
echo ^)
echo.
echo call npm run dev -- --host 127.0.0.1 --port 5173
echo.
echo pause
) > "run_frontend.bat"

REM ========================================================
REM Create run_all.bat
REM ========================================================

(
echo @echo off
echo title CareerForge AI
echo.
echo echo ========================================================
echo echo Launching CareerForge AI Operating System...
echo echo ========================================================
echo.
echo start "CareerForge Backend" cmd /c "%%~dp0run_backend.bat"
echo timeout /t 3 /nobreak ^>nul
echo start "CareerForge Frontend" cmd /c "%%~dp0run_frontend.bat"
echo.
echo echo CareerForge AI is running!
echo echo.
echo echo Backend:
echo echo http://127.0.0.1:8000
echo echo.
echo echo Frontend:
echo echo http://127.0.0.1:5173
echo echo.
echo echo API documentation:
echo echo http://127.0.0.1:8000/docs
echo echo.
) > "run_all.bat"

echo Startup scripts created successfully.
echo.

REM ========================================================
REM Final
REM ========================================================

echo ========================================================
echo              SETUP COMPLETED SUCCESSFULLY
echo ========================================================
echo.
echo CareerForge AI has been configured on this PC.
echo.
echo To start the application:
echo.
echo     Double-click run_all.bat
echo.
echo Frontend:
echo     http://127.0.0.1:5173
echo.
echo Backend:
echo     http://127.0.0.1:8000
echo.
echo FastAPI Swagger:
echo     http://127.0.0.1:8000/docs
echo.
echo ========================================================
echo.

pause
endlocal
