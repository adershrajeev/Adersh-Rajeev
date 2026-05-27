@echo off
title Mobile Price Prediction System - Fuzzy Logic
echo ============================================================
echo   Mobile Price Prediction System - Fuzzy Logic
echo ============================================================

:: Set UTF-8 encoding for Python printing emoji support
set PYTHONIOENCODING=utf-8

:: Verify that the virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment 'venv' not found or incomplete.
    echo Please create the virtual environment by running:
    echo   python -m venv venv
    echo   venv\Scripts\pip.exe install -r requirements.txt
    echo   venv\Scripts\pip.exe install networkx
    pause
    exit /b 1
)

:: Start the browser in a new window/tab
echo Opening http://127.0.0.1:5000 in your browser...
start "" "http://127.0.0.1:5000"

:: Run the Flask server
echo Running Flask backend...
venv\Scripts\python.exe app.py

pause
