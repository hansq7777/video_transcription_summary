@echo off
python -m pip install -r "%~dp0requirements.txt"
echo.
echo Operation complete. Press any key to close this window...
pause >nul
exit /b %ERRORLEVEL%
