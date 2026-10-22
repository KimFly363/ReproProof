@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 reproof.py %*
  exit /b %errorlevel%
)
where python >nul 2>nul
if %errorlevel%==0 (
  python reproof.py %*
  exit /b %errorlevel%
)
echo.
echo Python 3 not found. Install Python 3.9+ and try again.
pause
exit /b 2
