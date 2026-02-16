# Clipboard Typer - Raw Paste Tool

A cross-platform utility that types out your clipboard contents character-by-character, simulating keyboard input. I originally built this for remote desktop sessions where Ctrl+V kept getting blocked — so this tool simulates real typing instead. DEMO in "Tag"!

Runs silently in the background with a **menu bar icon** (macOS) or **system tray icon** (Windows) — no terminal window required.

## Features

- **Menu bar / system tray app**: Runs in the background with a status icon — no terminal window
- **Character-by-character typing**: Simulates real keyboard input instead of pasting
- **Cross-platform**: Works on both Windows and macOS
- **Status icon colors**: Green (active), amber (typing), gray (paused)
- **Customizable typing speed**: Adjust the delay between keystrokes
- **Emergency stop**: Press ESC to immediately cancel typing
- **Pause/Resume**: Toggle via hotkey or the menu bar icon

## Use Cases

- Remote Desktop connections that block clipboard paste
- Virtual machines with clipboard restrictions
- Web applications that disable paste functionality
- Any environment where you need to bypass paste restrictions

## Requirements

- Python 3.7 or higher
- Windows 10+ or macOS 10.13+

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/alivang15/clipboard-typer.git
cd clipboard-typer
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Platform-specific setup

#### macOS
On macOS, you need to grant Accessibility permissions:

1. Run the app for the first time
2. macOS will prompt you to allow accessibility access
3. Go to **System Settings** > **Privacy & Security** > **Accessibility**
4. Enable access for **Terminal** (or the built `.app`)
5. Restart the app

#### Windows
No additional setup required.

## Usage

### Option 1: Build a Standalone App (Recommended)

Build a proper `.app` or `.exe` that runs with no terminal and no Python required:

**macOS:**
```bash
./build.sh
```
Then drag `dist/Clipboard Typer.app` to your **Applications** folder. Right-click > Open the first time.

**Windows:**
```
build_windows.bat
```
The `.exe` will be in the `dist\` folder. Pin it to your taskbar or create a desktop shortcut.

#### Auto-start on login (optional)

**macOS:** System Settings > General > Login Items > add `Clipboard Typer.app`

**Windows:** Press `Win+R`, type `shell:startup`, and place a shortcut to `ClipboardTyper.exe` there.

### Option 2: Quick Launch Scripts

**macOS:** Double-click `run_mac.command`

**Windows:** Double-click `run_windows.bat`

These will install dependencies if needed and launch the tool.

### Option 3: Command Line

```bash
python3 clipboard_typer.py   # macOS
python clipboard_typer.py    # Windows
```

## How It Looks

Once running, a small colored circle appears in your menu bar (macOS) or system tray (Windows):

| Icon Color | Meaning |
|------------|---------|
| Green | Active — ready to type |
| Amber | Currently typing... |
| Gray | Paused |

Click the icon to see the menu with status, hotkeys, pause/resume, and quit options.

## Hotkeys

Platform-specific hotkeys are used to avoid conflicts with existing system shortcuts.

**macOS:**

| Hotkey | Action |
|--------|--------|
| **Ctrl+Shift+V** | Start typing clipboard contents |
| **ESC** | Stop typing immediately (emergency stop) |
| **Ctrl+Shift+B** | Pause/Resume the tool |
| **Ctrl+Shift+Q** | Quit the program |

**Windows:**

| Hotkey | Action |
|--------|--------|
| **Ctrl+Shift+B** | Start typing clipboard contents |
| **ESC** | Stop typing immediately (emergency stop) |
| **Ctrl+Shift+H** | Pause/Resume the tool |
| **Ctrl+Shift+Q** | Quit the program |

> **macOS note:** We use Ctrl (not Cmd) for hotkeys to avoid triggering system clipboard paste.
> **Windows note:** We use Ctrl+Shift+B for paste instead of Ctrl+Shift+V to avoid conflicts with Windows' native Ctrl+Shift+V (Emoji & Symbols panel).

## Lessons Learned: Why These Hotkeys?

### Why Ctrl+Shift+B (Windows paste)?

Originally, this tool used **Ctrl+Shift+V** on both platforms since that's the standard paste hotkey on Windows. However, when pausing the program (`enabled = False`), the keyboard listener would still capture and block the Ctrl+Shift+V keystroke, preventing Windows from handling its own **Ctrl+Shift+V** function (Emoji & Symbols panel).

**The Problem:**
- The `pynput` keyboard listener runs continuously, even when the program is paused
- You can't truly "ignore" a keystroke in `pynput` — once the listener detects it, it's consumed
- This meant pausing the tool didn't actually let Windows reclaim the hotkey

**The Solution:**
- Use a **different hotkey per platform** that doesn't conflict with OS shortcuts
- Windows: `Ctrl+Shift+B` (avoids Windows' native Ctrl+Shift+V)
- macOS: `Ctrl+Shift+V` (safe — doesn't conflict with system shortcuts)

### Why Ctrl+Shift+H (Windows pause)?

Similar reasoning: **Ctrl+Shift+B** had to be reassigned to the paste function on Windows, so we needed a different hotkey for pause/resume that wouldn't conflict with existing Windows shortcuts. **Ctrl+Shift+H** is unused by Windows, making it a safe choice.

### Key Insight

**Hotkey isolation:** When building tools that intercept keyboard input, always verify that your hotkeys don't conflict with:
1. **Operating system hotkeys** (Ctrl+Shift+V on Windows, Cmd+Space on macOS, etc.)
2. **Common application shortcuts** (especially in browsers and IDEs)
3. **Accessibility features** (screen readers, voice control, etc.)

Using platform-specific hotkeys is safer than trying to "conditionally consume" a keystroke — the listener can't unsee a key press.

## Workflow

**On Windows:**
1. **Copy** your text normally with Ctrl+C
2. **Click** where you want to type in your target application
3. **Press Ctrl+Shift+B** to start typing
4. **Press ESC** anytime to stop typing (if needed)
5. **Press Ctrl+Shift+H** to pause/resume the tool

**On macOS:**
1. **Copy** your text normally with Cmd+C
2. **Click** where you want to type in your target application
3. **Press Ctrl+Shift+V** to start typing (note: Ctrl, not Cmd)
4. **Press ESC** anytime to stop typing (if needed)
5. **Press Ctrl+Shift+B** to pause/resume the tool

## Configuration

Edit the settings in `clipboard_typer.py`:

### Typing Speed
```python
TYPING_DELAY = 0.02  # Seconds between keystrokes
```

- `0.01` = Very fast (may cause issues in some apps)
- `0.02` = Fast (default, recommended)
- `0.05` = Moderate
- `0.10` = Slow (for very sensitive applications)

### Debug Mode (Privacy & Security)
```python
DEBUG_MODE = False  # Default: disabled for privacy
```

**⚠️ Privacy Warning:** Debug mode logs ALL key presses to `/tmp/clipboard_typer_debug.log`, which is a **privacy risk**. Only enable it temporarily when troubleshooting issues, then disable it immediately.

- `False` = No logging (default, recommended for privacy)
- `True` = Enable detailed logging (troubleshooting only)

**Note:** Clipboard contents are NEVER logged or saved to disk, regardless of debug mode.

## Troubleshooting

### macOS: "Key combinations not working"
- Ensure the app has Accessibility permissions (see Installation step 3)
- Try restarting the app after granting permissions

### macOS: "Why Ctrl instead of Cmd?"
- Using Cmd+Shift+V would trigger both system paste AND raw typing
- Ctrl+Shift+V doesn't conflict with any macOS system shortcuts
- This is intentional to prevent double-pasting

### macOS: "Hotkeys stopped working after rebuilding the .app"
**Lesson learned:** Every time you rebuild the `.app` bundle (e.g., after changing the icon or code), macOS invalidates the existing Accessibility and Input Monitoring permissions because the app's code signature changes.

**Solution:**
1. **Quit** the app completely
2. **Remove** the old `Clipboard Typer.app` from:
   - System Settings > Privacy & Security > **Accessibility**
   - System Settings > Privacy & Security > **Input Monitoring**
3. Delete the old `.app` from Applications folder
4. Delete `build/` and `dist/` folders in your project
5. Run `./build.sh` to rebuild
6. **Re-add** the newly built `dist/Clipboard Typer.app` to both:
   - **Accessibility** (click `+`, navigate to the app, toggle ON)
   - **Input Monitoring** (click `+`, navigate to the app, toggle ON)
7. Restart your Mac (optional but helps clear permission caches)
8. Launch the app

**Why this happens:** macOS identifies apps by their code signature. Any rebuild creates a new signature, making macOS treat it as a different app entirely. Simply toggling the existing entry won't work — you must remove and re-add it.

**Debug tip:** Enable `DEBUG_MODE = True` in `clipboard_typer.py` to create `/tmp/clipboard_typer_debug.log`. If you see `This process is not trusted!`, permissions aren't granted correctly. **Remember to disable debug mode after troubleshooting.**

### Windows: "Module not found" error
- Make sure you installed dependencies: `pip install -r requirements.txt`
- Try using `pip3` instead of `pip`

### Typing is too fast/slow
- Adjust the `TYPING_DELAY` value in the script
- Increase the delay for applications that can't keep up with fast typing

### Special characters not typing correctly
- Some special characters may not work in all applications
- The script handles newlines and tabs specially

## How It Works

Instead of using the system clipboard paste function, this tool:

1. Reads the clipboard contents
2. Simulates individual keystrokes for each character
3. Types the text out as if you were typing it manually

This bypasses paste restrictions because applications see it as real keyboard input, not a paste operation.

## Security & Privacy

**Privacy-first design:**
- **No data collection**: This tool runs entirely locally on your machine
- **No network activity**: No internet connection required or used
- **No logging by default**: Logging is disabled in production (`DEBUG_MODE = False`)
- **Clipboard contents never saved**: Text is only read from clipboard and typed out - never written to disk or logged
- **No persistent storage**: No databases, cache files, or user data stored

**When debug mode is enabled** (`DEBUG_MODE = True`):
- Key presses are logged to `/tmp/clipboard_typer_debug.log` for troubleshooting
- This is a privacy risk and should only be enabled temporarily when debugging
- Clipboard contents are still NEVER logged, even in debug mode

**Permissions required:**
- **Accessibility**: Required to listen for hotkeys and simulate keyboard input
- **Input Monitoring**: Required to detect Ctrl+Shift+V hotkey combinations
- These permissions are standard for keyboard automation tools and are only used for the documented functionality

## Dependencies

- [pynput](https://github.com/moses-palmer/pynput) - Cross-platform keyboard control
- [pyperclip](https://github.com/asweigart/pyperclip) - Cross-platform clipboard access
- [pystray](https://github.com/moses-palmer/pystray) - Cross-platform system tray icon
- [Pillow](https://github.com/python-pillow/Pillow) - Icon image generation

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

This tool is intended for legitimate use cases where paste functionality is restricted for technical reasons. Please use responsibly and in accordance with your organization's policies.

## Author

Built by Ali Vang — a small utility I made to solve paste restrictions during remote sessions.

## Acknowledgments

- Built with [pynput](https://github.com/moses-palmer/pynput) for cross-platform keyboard control
- Clipboard access via [pyperclip](https://github.com/asweigart/pyperclip)
- System tray via [pystray](https://github.com/moses-palmer/pystray)
