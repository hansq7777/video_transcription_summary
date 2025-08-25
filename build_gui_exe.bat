@echo off
REM Build a standalone Video Transcription Summary GUI executable.
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Ensure PyInstaller is available.
python -m pyinstaller --version >NUL 2>&1
IF ERRORLEVEL 1 (
    echo PyInstaller not found. Attempting to install...
    pip install pyinstaller || (
        echo Failed to install PyInstaller.
        pause
        exit /b 1
    )
)

python -m PyInstaller --noconfirm --onefile --windowed ^
    --add-data ".env;." ^
    src\gui.py

IF ERRORLEVEL 0 (
    echo.
    echo Build complete. Executable is located in the dist folder.
) ELSE (
    echo.
    echo Build failed. See errors above.
)

pause
