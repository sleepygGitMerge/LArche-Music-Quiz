@echo off
title Music Quiz App
echo ==========================================
echo Starting Music Quiz App Setup...
echo ==========================================

:: 1. Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Python was not found on your system!
    echo.
    echo To run this app, please install Python manually:
    echo 1. Go to https://www.python.org/downloads/
    echo 2. Download the latest installer for Windows.
    echo 3. IMPORTANT: When you run the installer, check the box at the bottom
    echo    that says "Add python.exe to PATH" before clicking Install.
    echo.
    echo After installing, run this start.bat file again.
    pause
    exit /b
)

:: 2. Check if Virtual Environment exists, create if not
IF NOT EXIST "venv\Scripts\activate" (
    echo Creating a local Python environment...
    python -m venv venv
    IF %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b
    )
)

:: 3. Activate environment and install requirements
echo Activating environment...
call venv\Scripts\activate
echo Checking dependencies...
pip install -r requirements.txt

:: 4. Start the application
echo.
echo ==========================================
echo Starting the Server! Leave this window open.
echo ==========================================
start http://127.0.0.1:5000
python app.py

pause