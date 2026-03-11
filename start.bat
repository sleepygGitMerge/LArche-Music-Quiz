@echo off
echo ==========================================
echo Starting Music Quiz App Setup...
echo ==========================================

:: Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in your PATH.
    echo Attempting to install Python via Windows Package Manager (winget)...
    winget install -e --id Python.Python.3.11
    echo Please close this window, open a new one, and run start.bat again!
    pause
    exit
)

:: Check if Virtual Environment exists
IF NOT EXIST "venv\Scripts\activate" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate environment and install dependencies
echo Activating virtual environment...
call venv\Scripts\activate
echo Installing requirements...
pip install -r requirements.txt

:: Start the app
echo Starting the Flask server...
start http://127.0.0.1:5000
python app.py

pause