@echo off
:: Clipboard Typer - Windows Launcher
:: Double-click this file to run the tool

title Clipboard Typer

cd /d "%~dp0"

:: Check for Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    where python3 >nul 2>nul
    if %errorlevel% neq 0 (
        echo Python is not installed.
        echo Install it from https://www.python.org/downloads/
        echo Make sure to check "Add Python to PATH" during installation.
        echo.
        pause
        exit /b 1
    )
    set PYTHON=python3
) else (
    set PYTHON=python
)

:: Install dependencies if missing
%PYTHON% -c "import pynput, pyperclip" 2>nul
if %errorlevel% neq 0 (
    echo Installing dependencies...
    %PYTHON% -m pip install -r requirements.txt
    echo.
)

:: Run the script
%PYTHON% clipboard_typer.py
pause
