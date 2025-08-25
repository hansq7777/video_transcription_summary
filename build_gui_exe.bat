@echo off
REM Build a standalone Video Transcription Summary GUI executable.
REM Include the .env file so environment variables are available at runtime.
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

pyinstaller --onefile --windowed src\gui.py --add-data ".env;."

