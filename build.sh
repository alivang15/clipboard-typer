#!/bin/bash
# Build script for Clipboard Typer
# Creates a standalone .app (macOS) or .exe (Windows)

set -e

cd "$(dirname "$0")"

echo "=================================="
echo "  Building Clipboard Typer"
echo "=================================="
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required."
    echo "Install it from https://www.python.org/downloads/"
    exit 1
fi

# Install build dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt
pip3 install pyinstaller
echo ""

# Build the app
echo "Building standalone application..."

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS - build as .app bundle (onedir mode for proper macOS support)
    pyinstaller \
        --onedir \
        --windowed \
        --name "Clipboard Typer" \
        --osx-bundle-identifier "com.alivang.clipboardtyper" \
        --osx-entitlements-file entitlements.plist \
        -y \
        clipboard_typer.py

    APP_PATH="dist/Clipboard Typer.app"
    PLIST_PATH="$APP_PATH/Contents/Info.plist"

    # Add macOS-specific Info.plist entries
    /usr/libexec/PlistBuddy -c "Add :LSUIElement bool true" "$PLIST_PATH" 2>/dev/null || \
    /usr/libexec/PlistBuddy -c "Set :LSUIElement true" "$PLIST_PATH"

    /usr/libexec/PlistBuddy -c "Add :NSAccessibilityUsageDescription string 'Clipboard Typer needs accessibility access to listen for keyboard shortcuts and simulate typing.'" "$PLIST_PATH" 2>/dev/null || \
    /usr/libexec/PlistBuddy -c "Set :NSAccessibilityUsageDescription 'Clipboard Typer needs accessibility access to listen for keyboard shortcuts and simulate typing.'" "$PLIST_PATH"

    # Re-sign with entitlements so macOS trusts the modified plist
    codesign --force --deep --sign - --entitlements entitlements.plist "$APP_PATH" 2>/dev/null || true

    echo ""
    echo "============================================"
    echo "  Build complete!"
    echo "============================================"
    echo ""
    echo "  Your app: dist/Clipboard Typer.app"
    echo ""
    echo "  SETUP (one time only):"
    echo ""
    echo "  1. Right-click the .app > Open (bypass Gatekeeper)"
    echo "  2. System Settings > Privacy & Security > Accessibility"
    echo "     → Click '+', add Clipboard Typer.app, toggle ON"
    echo "  3. System Settings > Privacy & Security > Input Monitoring"
    echo "     → Click '+', add Clipboard Typer.app, toggle ON"
    echo "  4. Quit and reopen the app"
    echo ""
    echo "  NOTE: If you rebuild, you must remove and re-add"
    echo "  the app in Accessibility & Input Monitoring."
    echo "============================================"
    echo ""
else
    # Windows
    pyinstaller \
        --onefile \
        --windowed \
        --name "ClipboardTyper" \
        -y \
        clipboard_typer.py

    echo ""
    echo "============================================"
    echo "  Build complete!"
    echo "============================================"
    echo ""
    echo "  Your app: dist\\ClipboardTyper.exe"
    echo ""
    echo "  To install:"
    echo "  1. Move ClipboardTyper.exe wherever you like"
    echo "  2. Right-click > Pin to taskbar (optional)"
    echo "  3. To auto-start: Win+R > 'shell:startup'"
    echo "     then place a shortcut there"
    echo "============================================"
    echo ""
fi
