@echo off
REM Launch Video Transcription Summary GUI from a Python environment.

SET SCRIPT_DIR=%~dp0
SET VENV_DIR=%SCRIPT_DIR%venv
SET CONDA_ENV_NAME=VTS

REM Try running inside an active Conda environment.
IF NOT "%CONDA_PREFIX%"=="" (
    cd /d "%SCRIPT_DIR%"
    CALL :RunWithPython start_gui.pyw
    GOTO :CheckError
)

REM Try launching with conda run and a named environment.
where conda >NUL 2>&1
IF %ERRORLEVEL%==0 (
    cd /d "%SCRIPT_DIR%"
    start "" conda run -n %CONDA_ENV_NAME% pythonw start_gui.pyw
    IF %ERRORLEVEL%==0 GOTO :ExitSuccess
    start "" conda run -n %CONDA_ENV_NAME% python start_gui.pyw
    IF %ERRORLEVEL%==0 GOTO :ExitSuccess
)

REM If a local venv exists, activate it.
IF EXIST "%VENV_DIR%\Scripts\activate.bat" (
    CALL "%VENV_DIR%\Scripts\activate.bat"
    cd /d "%SCRIPT_DIR%"
    CALL :RunWithPython start_gui.pyw
    GOTO :CheckError
)

echo No Python environment found.
echo Install dependencies with Conda (conda create -n %CONDA_ENV_NAME% -f requirements.txt) or:
echo     python -m venv venv ^&^& pip install -r requirements.txt
GOTO :PauseFail

:CheckError
IF %ERRORLEVEL%==0 GOTO :ExitSuccess
GOTO :PauseFail

:ExitSuccess
exit

:PauseFail
echo.
echo GUI launch failed. See messages above.
pause
exit /b %ERRORLEVEL%

:RunWithPython
where pythonw >NUL 2>&1
IF %ERRORLEVEL%==0 (
    start "" pythonw %*
) ELSE (
    start "" python %*
)
exit /b %ERRORLEVEL%
