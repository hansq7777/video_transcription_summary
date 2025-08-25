@echo off
REM Launch Video Transcription Summary GUI inside its virtual environment.
REM Ensure a virtual environment exists at venv\.

SET SCRIPT_DIR=%~dp0
SET VENV_DIR=%SCRIPT_DIR%venv

IF NOT EXIST "%VENV_DIR%\Scripts\activate.bat" (
    echo Virtual environment not found in %VENV_DIR%.
    echo Create it with: python -m venv venv ^&^& pip install -r requirements.txt
    pause
    exit /b 1
)

CALL "%VENV_DIR%\Scripts\activate.bat"
cd /d "%SCRIPT_DIR%"
pythonw src\gui.py
