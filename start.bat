@echo off
chcp 65001 >nul 2>&1
title Twitter/X Video Downloader

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo ========================================
echo   Twitter/X Video Downloader
echo ========================================
echo.

echo [Checking Python...]
set "PYTHON_EXE="

py --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_EXE=py"
    goto found_python
)

python --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_EXE=python"
    goto found_python
)

python3 --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_EXE=python3"
    goto found_python
)

if exist "E:\python_study\python.exe" (
    set "PYTHON_EXE=E:\python_study\python.exe"
    goto found_python
)

for /d %%i in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
    if exist "%%i\python.exe" (
        set "PYTHON_EXE=%%i\python.exe"
        goto found_python
    )
)

echo.
echo ========================================
echo [ERROR] Python not found!
echo ========================================
echo.
echo Please install Python 3.8+ from:
echo https://www.python.org/downloads/
echo.
echo Make sure to check "Add Python to PATH"
echo during installation.
echo.
pause
exit /b 1

:found_python
for /f "tokens=2" %%v in ('%PYTHON_EXE% --version 2^>^&1') do set PYTHON_VERSION=%%v
echo Found Python: %PYTHON_VERSION%
echo.

echo [Checking dependencies...]
%PYTHON_EXE% -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    echo.
    %PYTHON_EXE% -m pip install --upgrade pip >nul 2>&1
    %PYTHON_EXE% -m pip install -r "%SCRIPT_DIR%requirements.txt"
    if errorlevel 1 (
        echo.
        echo [ERROR] Failed to install dependencies!
        echo Please run manually:
        echo   %PYTHON_EXE% -m pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
    echo.
    echo [Installing browser...]
    %PYTHON_EXE% -m playwright install chromium 2>nul
    echo Dependencies installed!
    echo.
)

echo [Starting...]
echo.
%PYTHON_EXE% "%SCRIPT_DIR%twitter_downloader_gui.py"

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start!
    echo Possible causes:
    echo   1. Dependencies not installed correctly
    echo   2. Python version too old (need 3.8+)
    echo   3. Script file missing
    echo.
    pause
)
