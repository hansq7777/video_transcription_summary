@echo off
REM Update the repository by pulling the latest changes.

SET SCRIPT_DIR=%~dp0
SET VENV_DIR=%SCRIPT_DIR%venv
SET CONDA_ENV_NAME=VTS

REM Try running inside an active Conda environment.
IF NOT "%CONDA_PREFIX%"=="" (
    cd /d "%SCRIPT_DIR%"
    git pull
    GOTO :CheckError
)

REM Try launching with conda run and a named environment.
where conda >NUL 2>&1
IF %ERRORLEVEL%==0 (
    cd /d "%SCRIPT_DIR%"
    CALL conda run -n %CONDA_ENV_NAME% git pull
    IF %ERRORLEVEL%==0 GOTO :End
)

REM If a local venv exists, activate it.
IF EXIST "%VENV_DIR%\Scripts\activate.bat" (
    CALL "%VENV_DIR%\Scripts\activate.bat"
    cd /d "%SCRIPT_DIR%"
    git pull
    GOTO :CheckError
)

echo No Python environment found.
echo Install dependencies with Conda (conda create -n %CONDA_ENV_NAME% -f requirements.txt) or:
echo     python -m venv venv ^&^& pip install -r requirements.txt
GOTO :PauseFail

:CheckError
IF %ERRORLEVEL%==0 GOTO :End

:PauseFail
echo.
echo Git pull failed. See messages above.
GOTO :End

:End
echo.
echo 操作完成，按任意键关闭窗口...
pause >nul
exit /b %ERRORLEVEL%
