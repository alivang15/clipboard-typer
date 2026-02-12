#!/bin/bash
# Clipboard Typer - macOS Launcher
# Double-click this file to run the tool

# Navigate to the script directory
cd "$(dirname "$0")"

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed."
    echo "Install it from https://www.python.org/downloads/"
    echo ""
    read -p "Press Enter to close..."
    exit 1
fi

# Install dependencies if missing
python3 -c "import pynput, pyperclip" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
    echo ""
fi

# Run the script
python3 clipboard_typer.py
