@echo off
python -m pip install -r "%~dp0requirements.txt"
echo.
echo 操作完成，按任意键关闭窗口...
pause >nul
exit /b %ERRORLEVEL%
