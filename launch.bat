@echo off
REM Student Engagement Tracker - Windows Launch Script

echo ============================================================
echo   STUDENT ENGAGEMENT TRACKING SYSTEM
echo ============================================================
echo.
echo Starting application...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from python.org
    echo.
    pause
    exit /b 1
)

REM Check if streamlit is installed
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo Streamlit is not installed. Installing dependencies...
    echo.
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo Error: Failed to install dependencies.
        echo Please run manually: pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
)

REM Launch the application
echo.
echo Launching Streamlit application...
echo The app will open in your default browser.
echo.
echo Press Ctrl+C to stop the server.
echo ============================================================
echo.

streamlit run app.py

echo.
echo Application stopped.
echo ============================================================
pause
