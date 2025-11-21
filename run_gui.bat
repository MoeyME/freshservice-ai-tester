@echo off
setlocal enabledelayedexpansion

echo ========================================
echo IT Ticket Email Generator - PySide6
echo ========================================
echo.
echo Starting application...
echo.

REM Try py launcher first (Windows Python launcher)
where py >nul 2>&1
if %ERRORLEVEL% == 0 (
    py run_pyside6_app.py
    goto :end
)

REM Try python command
where python >nul 2>&1
if %ERRORLEVEL% == 0 (
    python run_pyside6_app.py
    goto :end
)

REM Try python3 command
where python3 >nul 2>&1
if %ERRORLEVEL% == 0 (
    python3 run_pyside6_app.py
    goto :end
)

REM Check common Python installation locations
set PYTHON_FOUND=0

REM Check AppData\Local\Programs\Python
if exist "%LOCALAPPDATA%\Programs\Python\Python3*\python.exe" (
    for /f "delims=" %%i in ('dir /b /ad "%LOCALAPPDATA%\Programs\Python\Python3*" 2^>nul') do (
        set PYTHON_PATH=%LOCALAPPDATA%\Programs\Python\%%i\python.exe
        set PYTHON_FOUND=1
        goto :found
    )
)

REM Check Program Files\Python
if exist "%ProgramFiles%\Python3*\python.exe" (
    for /f "delims=" %%i in ('dir /b /ad "%ProgramFiles%\Python3*" 2^>nul') do (
        set PYTHON_PATH=%ProgramFiles%\Python3*\%%i\python.exe
        set PYTHON_FOUND=1
        goto :found
    )
)

REM Check Program Files (x86)\Python
if exist "%ProgramFiles(x86)%\Python3*\python.exe" (
    for /f "delims=" %%i in ('dir /b /ad "%ProgramFiles(x86)%\Python3*" 2^>nul') do (
        set PYTHON_PATH=%ProgramFiles(x86)%\Python3*\%%i\python.exe
        set PYTHON_FOUND=1
        goto :found
    )
)

:found
if !PYTHON_FOUND! == 1 (
    echo Found Python at: !PYTHON_PATH!
    "!PYTHON_PATH!" run_pyside6_app.py
    goto :end
)

REM Try virtual environment (if it exists)
if exist "C:\pyenv\Scripts\python.exe" (
    echo Using virtual environment at C:\pyenv
    C:\pyenv\Scripts\python.exe run_pyside6_app.py
    goto :end
)

REM Python not found - show error and instructions
echo ========================================
echo ERROR: Python not found!
echo ========================================
echo.
echo This application requires Python 3.10 or higher.
echo.
echo To install Python:
echo.
echo 1. Download Python from: https://www.python.org/downloads/
echo 2. IMPORTANT: During installation, check the box:
echo    "Add Python to PATH"
echo 3. After installation, restart this application.
echo.
echo Alternatively, you can install Python from Microsoft Store:
echo - Open Microsoft Store
echo - Search for "Python 3.12" or "Python 3.11"
echo - Click Install
echo.
echo Current working directory: %CD%
echo.
pause
exit /b 1

:end
echo.
echo Application closed.
pause
