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
    echo.
    echo ERROR: Python was not found in PATH.
    echo.
    echo Please install Python 3.10 - 3.14.
    echo Make sure "Add Python to PATH" is enabled.
    echo.
    echo Download:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%A in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%A"

echo Python found: %PYTHON_VERSION%
echo.

REM ========================================================
REM Check Python version
REM Supports Python 3.10 through 3.14
REM ========================================================

python -c "import sys; sys.exit(0 if (sys.version_info.major == 3 and 10 <= sys.version_info.minor <= 14) else 1)"

if errorlevel 1 (
    echo.
    echo ERROR: Unsupported Python version.
    echo.
    echo Detected:
    python --version
    echo.
    echo CareerForge AI requires Python 3.10, 3.11, 3.12, 3.13, or 3.14.
    echo.
    pause
    exit /b 1
)

echo Supported Python version confirmed.
echo.

REM ========================================================
REM 2. Check Node.js
REM ========================================================

echo [2/7] Checking Node.js...
echo.

where node >nul 2>&1

if errorlevel 1 (
    echo.
    echo ERROR: Node.js was not found in PATH.
    echo.
    echo Please install Node.js LTS:
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
    echo.
    echo ERROR: npm was not found in PATH.
    echo.
    echo Node.js was found, but npm is unavailable.
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

if not exist "%PROJECT_ROOT%backend\" (
    echo.
    echo ERROR: Backend folder was not found.
    echo.
    echo Expected:
    echo %PROJECT_ROOT%backend
    echo.
    pause
    exit /b 1
)

cd /d "%PROJECT_ROOT%backend"

if errorlevel 1 (
    echo.
    echo ERROR: Could not enter backend directory.
    echo.
    pause
    exit /b 1
)

echo Backend directory:
cd
echo.

REM ========================================================
REM Check requirements.txt
REM ========================================================

if not exist "requirements.txt" (
    echo.
    echo ========================================================
    echo ERROR: requirements.txt NOT FOUND
    echo ========================================================
    echo.
    echo Expected file:
    echo %PROJECT_ROOT%backend\requirements.txt
    echo.
    echo Backend dependencies cannot be installed without this file.
    echo.
    echo Setup has been stopped.
    echo.
    pause
    exit /b 1
)

echo requirements.txt found.
echo.

REM ========================================================
REM Check existing virtual environment
REM ========================================================

if exist "venv\Scripts\python.exe" (

    echo Existing virtual environment found.
    echo.

    echo Checking virtual environment Python...

    venv\Scripts\python.exe --version

    echo.
    echo Comparing Python versions...

    python -c "import sys; print(f'Host Python: {sys.version_info.major}.{sys.version_info.minor}')"
    venv\Scripts\python.exe -c "import sys; print(f'Venv Python: {sys.version_info.major}.{sys.version_info.minor}')"

    python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}', end='')">"%TEMP%\careerforge_host_python.txt"
    venv\Scripts\python.exe -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}', end='')">"%TEMP%\careerforge_venv_python.txt"

    set /p HOST_PYTHON=<"%TEMP%\careerforge_host_python.txt"
    set /p VENV_PYTHON=<"%TEMP%\careerforge_venv_python.txt"

    del "%TEMP%\careerforge_host_python.txt" >nul 2>&1
    del "%TEMP%\careerforge_venv_python.txt" >nul 2>&1

    if not "!HOST_PYTHON!"=="!VENV_PYTHON!" (

        echo.
        echo WARNING: Existing virtual environment uses a different Python version.
        echo.
        echo Host Python: !HOST_PYTHON!
        echo Venv Python:  !VENV_PYTHON!
        echo.
        echo Recreating virtual environment...
        echo.

        rmdir /s /q "venv"

        if errorlevel 1 (
            echo.
            echo ERROR: Could not remove the existing virtual environment.
            echo.
            echo Make sure no Python process is using:
            echo %PROJECT_ROOT%backend\venv
            echo.
            pause
            exit /b 1
        )

        echo Old virtual environment removed.
        echo.
    ) else (
        echo Existing virtual environment uses the correct Python version.
        echo.
    )
)

REM ========================================================
REM Create virtual environment if necessary
REM ========================================================

if not exist "venv\Scripts\python.exe" (

    echo Creating Python virtual environment...
    echo.

    python -m venv venv

    if errorlevel 1 (
        echo.
        echo ERROR: Failed to create Python virtual environment.
        echo.
        echo Python being used:
        python --version
        echo.
        pause
        exit /b 1
    )

    echo Virtual environment created successfully.
    echo.
)

REM ========================================================
REM Verify virtual environment
REM ========================================================

if not exist "venv\Scripts\python.exe" (
    echo.
    echo ERROR: Virtual environment Python executable was not created.
    echo.
    echo Expected:
    echo %PROJECT_ROOT%backend\venv\Scripts\python.exe
    echo.
    pause
    exit /b 1
)

echo Virtual environment verified.
echo.

echo Virtual environment Python:
venv\Scripts\python.exe --version
echo.

REM ========================================================
REM Upgrade pip
REM ========================================================

echo Upgrading pip...
echo.

venv\Scripts\python.exe -m pip install --upgrade pip

if errorlevel 1 (
    echo.
    echo ========================================================
    echo ERROR: pip upgrade failed.
    echo ========================================================
    echo.
    echo Setup has been stopped.
    echo.
    pause
    exit /b 1
)

echo.
echo pip upgraded successfully.
echo.

REM ========================================================
REM Install backend dependencies
REM ========================================================

echo Installing backend dependencies...
echo.
echo This may take several minutes.
echo.

venv\Scripts\python.exe -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ========================================================
    echo ERROR: Backend dependency installation FAILED.
    echo ========================================================
    echo.
    echo The setup has been stopped.
    echo.
    echo Check the error messages above.
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

echo Verifying Uvicorn...
echo.

venv\Scripts\python.exe -m uvicorn --version

if errorlevel 1 (
    echo.
    echo ========================================================
    echo ERROR: Uvicorn verification FAILED.
    echo ========================================================
    echo.
    echo Uvicorn was not installed correctly.
    echo.
    pause
    exit /b 1
)

echo.
echo Uvicorn verified successfully.
echo.

REM ========================================================
REM Verify FastAPI
REM ========================================================

echo Verifying FastAPI...
echo.

venv\Scripts\python.exe -c "import fastapi; print('FastAPI:', fastapi.__version__)"

if errorlevel 1 (
    echo.
    echo ========================================================
    echo ERROR: FastAPI verification FAILED.
    echo ========================================================
    echo.
    pause
    exit /b 1
)

echo.

REM ========================================================
REM Verify application import
REM ========================================================

echo Checking CareerForge application...
echo.

venv\Scripts\python.exe -c "from app.main import app; print('CareerForge FastAPI application loaded successfully.')"

if errorlevel 1 (
    echo.
    echo ========================================================
    echo ERROR: CareerForge application FAILED TO LOAD.
    echo ========================================================
    echo.
    echo Possible causes:
    echo.
    echo - Python syntax error
    echo - Missing dependency
    echo - Incorrect import
    echo - Application configuration error
    echo.
    echo Setup has been stopped.
    echo.
    pause
    exit /b 1
)

echo.
echo CareerForge application verified successfully.
echo.

REM ========================================================
REM 5. Setup Frontend
REM ========================================================

echo [5/7] Setting up React frontend...
echo.

if not exist "%PROJECT_ROOT%frontend\" (
    echo.
    echo ERROR: Frontend folder was not found.
    echo.
    echo Expected:
    echo %PROJECT_ROOT%frontend
    echo.
    pause
    exit /b 1
)

cd /d "%PROJECT_ROOT%frontend"

if errorlevel 1 (
    echo.
    echo ERROR: Could not enter frontend directory.
    echo.
    pause
    exit /b 1
)

if not exist "package.json" (
    echo.
    echo ERROR: frontend\package.json was not found.
    echo.
    echo Expected:
    echo %PROJECT_ROOT%frontend\package.json
    echo.
    pause
    exit /b 1
)

echo package.json found.
echo.

REM ========================================================
REM Install frontend dependencies
REM ========================================================

echo Installing frontend dependencies...
echo.

call npm install

if errorlevel 1 (
    echo.
    echo ========================================================
    echo ERROR: Frontend dependency installation FAILED.
    echo ========================================================
    echo.
    echo Setup has been stopped.
    echo.
    pause
    exit /b 1
)

echo.
echo Frontend dependencies installed successfully.
echo.

REM ========================================================
REM Verify node_modules
REM ========================================================

if not exist "node_modules\" (
    echo.
    echo ERROR: node_modules was not created.
    echo.
    pause
    exit /b 1
)

echo node_modules verified.
echo.

REM ========================================================
REM 6. Create run_backend.bat
REM ========================================================

echo [6/7] Creating startup scripts...
echo.

cd /d "%PROJECT_ROOT%"

if errorlevel 1 (
    echo.
    echo ERROR: Could not return to project root.
    echo.
    pause
    exit /b 1
)

echo Creating run_backend.bat...

(
echo @echo off
echo setlocal EnableExtensions
echo title CareerForge AI - Backend
echo.
echo echo ========================================================
echo echo      Starting CareerForge AI - FastAPI Backend
echo echo                 Port 8000
echo echo ========================================================
echo echo.
echo.
echo cd /d "%%~dp0backend"
echo.
echo if not exist "venv\Scripts\python.exe" ^(
echo     echo ERROR: Python virtual environment not found.
echo     echo Please run setup.bat first.
echo     echo.
echo     pause
echo     exit /b 1
echo ^)
echo.
echo echo Starting FastAPI server...
echo echo.
echo.
echo venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
echo.
echo if errorlevel 1 ^(
echo     echo.
echo     echo ========================================================
echo     echo ERROR: Backend server stopped with an error.
echo     echo ========================================================
echo     echo.
echo ^)
echo.
echo pause
echo endlocal
) > "%PROJECT_ROOT%run_backend.bat"

if errorlevel 1 (
    echo.
    echo ERROR: Failed to create run_backend.bat
    echo.
    pause
    exit /b 1
)

if not exist "%PROJECT_ROOT%run_backend.bat" (
    echo.
    echo ERROR: run_backend.bat was not created.
    echo.
    pause
    exit /b 1
)

echo run_backend.bat created successfully.
echo.

REM ========================================================
REM 7. Create run_frontend.bat
REM ========================================================

echo Creating run_frontend.bat...

(
echo @echo off
echo setlocal EnableExtensions
echo title CareerForge AI - Frontend
echo.
echo echo ========================================================
echo echo      Starting CareerForge AI - React Frontend
echo echo                 Port 5173
echo echo ========================================================
echo echo.
echo.
echo cd /d "%%~dp0frontend"
echo.
echo if not exist "node_modules" ^(
echo     echo ERROR: node_modules not found.
echo     echo Please run setup.bat first.
echo     echo.
echo     pause
echo     exit /b 1
echo ^)
echo.
echo echo Starting Vite development server...
echo echo.
echo call npm run dev -- --host 127.0.0.1 --port 5173
echo.
echo if errorlevel 1 ^(
echo     echo.
echo     echo ========================================================
echo     echo ERROR: Frontend server stopped with an error.
echo     echo ========================================================
echo     echo.
echo ^)
echo.
echo pause
echo endlocal
) > "%PROJECT_ROOT%run_frontend.bat"

if errorlevel 1 (
    echo.
    echo ERROR: Failed to create run_frontend.bat
    echo.
    pause
    exit /b 1
)

if not exist "%PROJECT_ROOT%run_frontend.bat" (
    echo.
    echo ERROR: run_frontend.bat was not created.
    echo.
    pause
    exit /b 1
)

echo run_frontend.bat created successfully.
echo.

REM ========================================================
REM Create run_all.bat
REM ========================================================

echo Creating run_all.bat...

(
echo @echo off
echo setlocal EnableExtensions
echo title CareerForge AI
echo.
echo echo ========================================================
echo echo       Launching CareerForge AI Operating System
echo echo ========================================================
echo echo.
echo.
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
    echo.
    echo ERROR: Failed to create run_all.bat
    echo.
    pause
    exit /b 1
)

if not exist "%PROJECT_ROOT%run_all.bat" (
    echo.
    echo ERROR: run_all.bat was not created.
    echo.
    pause
    exit /b 1
)

echo run_all.bat created successfully.
echo.

REM ========================================================
REM Final success
REM ========================================================

echo.
echo ========================================================
echo          SETUP COMPLETED SUCCESSFULLY
echo ========================================================
echo.
echo CareerForge AI has been configured successfully.
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