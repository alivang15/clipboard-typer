@echo off
:: Build script for Clipboard Typer (Windows)
:: Creates a standalone .exe

cd /d "%~dp0"

echo ==================================
echo   Building Clipboard Typer
echo ==================================
echo.

:: Check for Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Python 3 is required.
    echo Install it from https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Install dependencies
echo Installing dependencies...
python -m pip install -r requirements.txt
python -m pip install pyinstaller
echo.

:: Build
echo Building standalone application...
python -m PyInstaller --onefile --windowed --name "ClipboardTyper" clipboard_typer.py

echo.
echo Build complete!
echo.
echo Your app is at: dist\ClipboardTyper.exe
echo.
echo To install:
echo   1. Move ClipboardTyper.exe wherever you like
echo   2. Right-click ^> Pin to taskbar (optional)
echo   3. To auto-start: press Win+R, type 'shell:startup',
echo      then place a shortcut to ClipboardTyper.exe there
echo.
pause
