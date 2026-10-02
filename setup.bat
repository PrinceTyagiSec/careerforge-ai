@echo off
setlocal EnableExtensions EnableDelayedExpansion

title CareerForge AI - First Time Setup

echo ========================================================
echo              CareerForge AI - First Time Setup
echo ========================================================
echo.

REM ========================================================
REM Get project root
REM ========================================================

set "PROJECT_ROOT=%~dp0"

REM ========================================================
REM 1. Check Python
REM ========================================================

echo [1/7] Checking Python...
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python was not found in PATH.
    echo.
    echo Please install Python 3.12 and enable:
    echo "Add Python to PATH"
    echo.
    echo Download:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%A in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%A"

echo Python found: %PYTHON_VERSION%

REM ========================================================
REM Check Python 3.12
REM ========================================================

python -c "import sys; sys.exit(0 if sys.version_info[:2] == (3,12) else 1)"

if errorlevel 1 (
    echo.
    echo ERROR: CareerForge AI requires Python 3.12.
    echo.
    echo Detected Python:
    python --version
    echo.
    echo Python 3.14 is NOT supported by this setup.
    echo Please install Python 3.12 and make sure it is available in PATH.
    echo.
    pause
    exit /b 1
)

echo Python 3.12 confirmed.
echo.

REM ========================================================
REM 2. Check Node.js
REM ========================================================

echo [2/7] Checking Node.js...
echo.

where node >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not available in PATH.
    echo.
    echo Please install Node.js LTS from:
    echo https://nodejs.org/
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%A in ('node --version 2^>^&1') do set "NODE_VERSION=%%A"

echo Node.js found: %NODE_VERSION%
echo.

REM ========================================================
REM 3. Check npm
REM ========================================================

echo [3/7] Checking npm...
echo.

where npm >nul 2>&1
if errorlevel 1 (
    echo ERROR: npm is not available in PATH.
    echo.
    echo Node.js was found, but npm was not found.
    echo Please reinstall Node.js LTS.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%A in ('npm --version 2^>^&1') do set "NPM_VERSION=%%A"

echo npm found: %NPM_VERSION%
echo.

REM ========================================================
REM 4. Setup Backend
REM ========================================================

echo [4/7] Setting up Python backend...
echo.

if not exist "%PROJECT_ROOT%backend" (
    echo ERROR: backend folder not found.
    echo.
    echo Expected:
    echo %PROJECT_ROOT%backend
    echo.
    pause
    exit /b 1
)

cd /d "%PROJECT_ROOT%backend"

if errorlevel 1 (
    echo ERROR: Could not enter backend directory.
    echo.
    pause
    exit /b 1
)

REM ========================================================
REM Check requirements.txt
REM ========================================================

if not exist "requirements.txt" (
    echo ERROR: requirements.txt was not found.
    echo.
    echo Expected location:
    echo %PROJECT_ROOT%backend\requirements.txt
    echo.
    echo This file is required for backend dependency installation.
    echo.
    pause
    exit /b 1
)

echo requirements.txt found.
echo.

REM ========================================================
REM Check / Create virtual environment
REM ========================================================

if exist "venv\Scripts\python.exe" (

    echo Existing virtual environment found.
    echo.

    echo Checking virtual environment Python version...

    venv\Scripts\python.exe -c "import sys; sys.exit(0 if sys.version_info[:2] == (3,12) else 1)"

    if errorlevel 1 (
        echo.
        echo ERROR: Existing virtual environment is not using Python 3.12.
        echo.
        echo Current virtual environment:
        venv\Scripts\python.exe --version
        echo.
        echo Please delete:
        echo %PROJECT_ROOT%backend\venv
        echo.
        echo Then run setup.bat again.
        echo.
        pause
        exit /b 1
    )

    echo Virtual environment uses Python 3.12.
    echo.

) else (

    echo Creating Python 3.12 virtual environment...
    echo.

    python -m venv venv

    if errorlevel 1 (
        echo.
        echo ERROR: Failed to create Python virtual environment.
        echo.
        pause
        exit /b 1
    )

    echo Python virtual environment created successfully.
    echo.
)

REM ========================================================
REM Verify virtual environment
REM ========================================================

if not exist "venv\Scripts\python.exe" (
    echo ERROR: Virtual environment Python executable was not created.
    echo.
    pause
    exit /b 1
)

echo Virtual environment verified.
echo.

REM ========================================================
REM Upgrade pip
REM ========================================================

echo Upgrading pip...
echo.

venv\Scripts\python.exe -m pip install --upgrade pip

if errorlevel 1 (
    echo.
    echo ERROR: Failed to upgrade pip.
    echo.
    pause
    exit /b 1
)

echo pip upgraded successfully.
echo.

REM ========================================================
REM Install backend dependencies
REM ========================================================

echo Installing backend dependencies...
echo.

venv\Scripts\python.exe -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Backend dependency installation failed.
    echo.
    echo The setup has been stopped.
    echo Please fix the error above and run setup.bat again.
    echo.
    pause
    exit /b 1
)

echo.
echo Backend dependencies installed successfully.
echo.

REM ========================================================
REM Verify Uvicorn
REM ========================================================

echo Verifying Uvicorn installation...
echo.

venv\Scripts\python.exe -m uvicorn --version

if errorlevel 1 (
    echo.
    echo ERROR: Uvicorn is not installed correctly.
    echo.
    pause
    exit /b 1
)

echo.
echo Uvicorn verified successfully.
echo.

REM ========================================================
REM Verify FastAPI application import
REM ========================================================

echo Checking FastAPI application...
echo.

venv\Scripts\python.exe -c "from app.main import app; print('FastAPI application loaded successfully.')"

if errorlevel 1 (
    echo.
    echo ERROR: FastAPI application could not be loaded.
    echo.
    echo There may be a Python syntax error or missing dependency.
    echo.
    pause
    exit /b 1
)

echo.

REM ========================================================
REM 5. Setup Frontend
REM ========================================================

echo [5/7] Setting up React frontend...
echo.

if not exist "%PROJECT_ROOT%frontend" (
    echo ERROR: frontend folder not found.
    echo.
    echo Expected:
    echo %PROJECT_ROOT%frontend
    echo.
    pause
    exit /b 1
)

cd /d "%PROJECT_ROOT%frontend"

if errorlevel 1 (
    echo ERROR: Could not enter frontend directory.
    echo.
    pause
    exit /b 1
)

if not exist "package.json" (
    echo ERROR: frontend\package.json was not found.
    echo.
    pause
    exit /b 1
)

echo package.json found.
echo.
echo Installing frontend dependencies...
echo.

call npm install

if errorlevel 1 (
    echo.
    echo ERROR: Frontend dependency installation failed.
    echo.
    pause
    exit /b 1
)

echo.
echo Frontend dependencies installed successfully.
echo.

REM ========================================================
REM 6. Create run_backend.bat
REM ========================================================

echo [6/7] Creating startup scripts...
echo.

cd /d "%PROJECT_ROOT%"

if errorlevel 1 (
    echo ERROR: Could not return to project root.
    echo.
    pause
    exit /b 1
)

(
echo @echo off
echo setlocal
echo title CareerForge AI - Backend
echo.
echo echo ========================================================
echo echo      Starting CareerForge AI - FastAPI Backend
echo echo                 Port 8000
echo echo ========================================================
echo echo.
echo cd /d "%%~dp0backend"
echo.
echo if not exist "venv\Scripts\python.exe" ^(
echo     echo ERROR: Python virtual environment not found.
echo     echo Please run setup.bat first.
echo     echo pause
echo     exit /b 1
echo ^)
echo.
echo venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
echo.
echo if errorlevel 1 ^(
echo     echo.
echo     echo ERROR: Backend server stopped with an error.
echo     echo.
echo ^)
echo.
echo pause
echo endlocal
) > "%PROJECT_ROOT%run_backend.bat"

if errorlevel 1 (
    echo ERROR: Failed to create run_backend.bat
    echo.
    pause
    exit /b 1
)

if not exist "%PROJECT_ROOT%run_backend.bat" (
    echo ERROR: run_backend.bat was not created.
    echo.
    pause
    exit /b 1
)

REM ========================================================
REM 7. Create run_frontend.bat
REM ========================================================

(
echo @echo off
echo setlocal
echo title CareerForge AI - Frontend
echo.
echo echo ========================================================
echo echo      Starting CareerForge AI - React Frontend
echo echo                 Port 5173
echo echo ========================================================
echo echo.
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
echo if errorlevel 1 ^(
echo     echo.
echo     echo ERROR: Frontend server stopped with an error.
echo     echo.
echo ^)
echo.
echo pause
echo endlocal
) > "%PROJECT_ROOT%run_frontend.bat"

if errorlevel 1 (
    echo ERROR: Failed to create run_frontend.bat
    echo.
    pause
    exit /b 1
)

if not exist "%PROJECT_ROOT%run_frontend.bat" (
    echo ERROR: run_frontend.bat was not created.
    echo.
    pause
    exit /b 1
)

REM ========================================================
REM Create run_all.bat
REM ========================================================

(
echo @echo off
echo setlocal
echo title CareerForge AI
echo.
echo echo ========================================================
echo echo       Launching CareerForge AI Operating System
echo echo ========================================================
echo echo.
echo start "CareerForge Backend" cmd /c ""%%~dp0run_backend.bat""
echo timeout /t 3 /nobreak ^>nul
echo start "CareerForge Frontend" cmd /c ""%%~dp0run_frontend.bat""
echo.
echo echo ========================================================
echo echo              CareerForge AI is running!
echo echo ========================================================
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
echo pause
echo endlocal
) > "%PROJECT_ROOT%run_all.bat"

if errorlevel 1 (
    echo ERROR: Failed to create run_all.bat
    echo.
    pause
    exit /b 1
)

if not exist "%PROJECT_ROOT%run_all.bat" (
    echo ERROR: run_all.bat was not created.
    echo.
    pause
    exit /b 1
)

echo.
echo Startup scripts created successfully.
echo.

REM ========================================================
REM Final
REM ========================================================

echo ========================================================
echo          SETUP COMPLETED SUCCESSFULLY
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
exit /b 0