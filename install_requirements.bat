@echo off
python -m pip install -r "%~dp0requirements.txt"
echo.
echo Installation complete. Press any key to close the window...
pause >nul
exit /b %ERRORLEVEL%
