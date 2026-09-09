@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
    py HulaanBayan.py
) else (
    python HulaanBayan.py
)
if errorlevel 1 (
    echo.
    echo The game could not start. Install Python 3 with Tkinter support.
    echo You can also run: python HulaanBayan.py
    pause
)
