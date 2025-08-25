@echo off
REM Launch Video Transcription Summary GUI from a Python environment.
REM 1) Use an active Conda environment if one is already enabled.
REM 2) Otherwise try to run via a named Conda environment.
REM 3) Finally fall back to a local venv.

SET SCRIPT_DIR=%~dp0
SET VENV_DIR=%SCRIPT_DIR%venv
SET CONDA_ENV_NAME=VTS

REM If already running inside a Conda environment, just execute the app.
IF NOT "%CONDA_PREFIX%"=="" (
    cd /d "%SCRIPT_DIR%"
    pythonw src\gui.py
    exit /b 0
)

REM Try launching with conda run and a named environment.
where conda >NUL 2>&1
IF %ERRORLEVEL%==0 (
    cd /d "%SCRIPT_DIR%"
    conda run -n %CONDA_ENV_NAME% pythonw src\gui.py
    IF %ERRORLEVEL%==0 exit /b 0
)

REM If a local venv exists, activate it.
IF EXIST "%VENV_DIR%\Scripts\activate.bat" (
    CALL "%VENV_DIR%\Scripts\activate.bat"
    cd /d "%SCRIPT_DIR%"
    pythonw src\gui.py
    exit /b 0
)

echo No Python environment found.
echo Install dependencies with Conda (conda create -n %CONDA_ENV_NAME% -f requirements.txt) or:
echo     python -m venv venv ^&^& pip install -r requirements.txt
pause
exit /b 1
