"""
Clipboard Typer - "Raw Paste" Tool
===================================
Cross-platform utility that types clipboard contents character-by-character.
Useful for remote desktops and applications that block clipboard paste.

Runs as a menu bar icon (macOS) or system tray icon (Windows).

Hotkeys:

macOS:
  Ctrl+Shift+V  → Type clipboard contents (raw paste)
  ESC           → Stop typing immediately
  Ctrl+Shift+B  → Pause/Resume
  Ctrl+Shift+Q  → Quit

Windows:
  Ctrl+Shift+B  → Type clipboard contents (raw paste)
  ESC           → Stop typing immediately
  Ctrl+Shift+H  → Pause/Resume
  Ctrl+Shift+Q  → Quit

Platform Support:
  - Windows 10+
  - macOS 10.13+

Note: On macOS, we use Ctrl (not Cmd) to avoid conflicts with system paste.
      On Windows, we use different keys to avoid conflicting with Windows' Ctrl+Shift+V.

Options (edit below):
  - TYPING_DELAY: seconds between each keystroke (lower = faster)
"""

import time
import threading
import sys
import platform
import os
import logging

# ──────────────────────────────────────────────
# SECURITY & PRIVACY SETTINGS
# ──────────────────────────────────────────────
# DEBUG_MODE: Enable detailed logging (for troubleshooting only)
# WARNING: When enabled, logs ALL key presses to /tmp/clipboard_typer_debug.log
# This is a PRIVACY RISK - disable in production!
DEBUG_MODE = False  # Set to True only when debugging issues
# ──────────────────────────────────────────────

# Configure logging only if debug mode is enabled
if DEBUG_MODE:
    LOG_PATH = "/tmp/clipboard_typer_debug.log"
    logging.basicConfig(
        filename=LOG_PATH,
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    logging.info("=== Clipboard Typer starting (DEBUG MODE) ===")
else:
    # Disable all logging for privacy
    logging.disable(logging.CRITICAL)

try:
    from pynput import keyboard
    from pynput.keyboard import Key, Controller
    import pyperclip
    import pystray
    from PIL import Image, ImageDraw
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install them with:")
    print("  pip install pynput pyperclip pystray Pillow")
    print("\nThen run this script again.")
    try:
        input("Press Enter to exit...")
    except EOFError:
        pass
    sys.exit(1)

# Detect platform
IS_MACOS = platform.system() == "Darwin"
IS_WINDOWS = platform.system() == "Windows"

# ──────────────────────────────────────────────
# SETTINGS — adjust these to your preference
# ──────────────────────────────────────────────
TYPING_DELAY = 0.02       # Seconds between keystrokes (0.02 = fast, 0.05 = moderate)
# ──────────────────────────────────────────────

enabled = True
typing_in_progress = False
stop_typing = False
kb_controller = Controller()
tray_icon = None


# ──────────────────────────────────────────────
# ICON CREATION
# ──────────────────────────────────────────────

def create_icon_image(color):
    """Create a colored rounded-rect icon with 'CP' for the menu bar / system tray."""
    size = 64
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Draw rounded rectangle background
    margin = 2
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=12,
        fill=color
    )
    # Draw "CP" text centered
    try:
        from PIL import ImageFont
        if IS_MACOS:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22)
        elif IS_WINDOWS:
            font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 22)
        else:
            font = ImageFont.load_default()
    except Exception:
        from PIL import ImageFont
        font = ImageFont.load_default()
    draw.text((size / 2, size / 2), "CP", fill="white", font=font, anchor="mm")
    return img


def get_status_icon():
    """Return the appropriate icon based on current state."""
    if typing_in_progress:
        return create_icon_image("#F59E0B")  # Amber - typing
    elif enabled:
        return create_icon_image("#22C55E")  # Green - active
    else:
        return create_icon_image("#9CA3AF")  # Gray - paused


def update_tray():
    """Update the tray icon to reflect current state."""
    if tray_icon:
        tray_icon.icon = get_status_icon()
        tray_icon.update_menu()


# ──────────────────────────────────────────────
# CORE LOGIC
# ──────────────────────────────────────────────

def type_clipboard():
    """Read clipboard and simulate typing each character."""
    global typing_in_progress, stop_typing

    if typing_in_progress:
        return

    if not enabled:
        return

    try:
        text = pyperclip.paste()
    except Exception:
        return

    if not text:
        return

    typing_in_progress = True
    stop_typing = False
    update_tray()

    time.sleep(0.3)  # Small delay so user can release the hotkey

    for char in text:
        if stop_typing:
            break

        try:
            if char == '\n':
                kb_controller.press(Key.enter)
                kb_controller.release(Key.enter)
            elif char == '\t':
                kb_controller.press(Key.tab)
                kb_controller.release(Key.tab)
            else:
                kb_controller.type(char)
        except Exception:
            pass

        time.sleep(TYPING_DELAY)

    typing_in_progress = False
    update_tray()


def toggle_enabled():
    """Toggle the tool on/off."""
    global enabled, stop_typing, typing_in_progress

    if typing_in_progress:
        stop_typing = True
        typing_in_progress = False
        update_tray()
        return

    enabled = not enabled
    update_tray()


def quit_program(icon=None, item=None):
    """Exit the program."""
    global stop_typing
    stop_typing = True
    if tray_icon:
        tray_icon.stop()
    time.sleep(0.3)
    os._exit(0)


# ──────────────────────────────────────────────
# KEYBOARD LISTENER
# ──────────────────────────────────────────────

# macOS virtual key codes (Carbon kVK_ANSI_*)
# Windows virtual key codes (same as ASCII uppercase)
VK_MAP_MACOS = {9: 'v', 11: 'b', 12: 'q'}

# Platform-specific hotkey assignments
if IS_WINDOWS:
    HOTKEY_PASTE = 'b'
    HOTKEY_TOGGLE = 'h'
    HOTKEY_QUIT = 'q'
else:
    HOTKEY_PASTE = 'v'
    HOTKEY_TOGGLE = 'b'
    HOTKEY_QUIT = 'q'


def get_key_char(key):
    """Get the letter for a key press, even when modifiers change key.char."""
    # Try char directly (works when no conflicting modifiers)
    char = getattr(key, 'char', None)
    if char and char.isalpha():
        return char.lower()

    # When Ctrl/Shift are held, key.char becomes a control code or None.
    # Fall back to virtual key code which stays consistent.
    vk = getattr(key, 'vk', None)
    if vk is not None:
        if IS_MACOS:
            return VK_MAP_MACOS.get(vk)
        elif IS_WINDOWS and 65 <= vk <= 90:
            return chr(vk).lower()

    return None


current_keys = set()


def on_press(key):
    """Handle key press events."""
    global stop_typing

    try:
        current_keys.add(key)
        logging.debug(f"Key pressed: {key}, char={getattr(key, 'char', None)}, vk={getattr(key, 'vk', None)}")

        # ESC - Stop typing immediately
        if key == Key.esc and typing_in_progress:
            stop_typing = True
            return

        # Check for Ctrl and Shift
        ctrl_pressed = (
            Key.ctrl in current_keys or
            Key.ctrl_l in current_keys or
            Key.ctrl_r in current_keys
        )

        shift_pressed = (
            Key.shift in current_keys or
            Key.shift_l in current_keys or
            Key.shift_r in current_keys
        )

        if ctrl_pressed and shift_pressed:
            char = get_key_char(key)
            logging.debug(f"Ctrl+Shift detected, resolved char={char}")

            if char == HOTKEY_PASTE:
                logging.info("Hotkey triggered: paste")
                threading.Thread(target=type_clipboard, daemon=True).start()
            elif char == HOTKEY_TOGGLE:
                logging.info("Hotkey triggered: toggle")
                toggle_enabled()
            elif char == HOTKEY_QUIT:
                logging.info("Hotkey triggered: quit")
                quit_program()

    except AttributeError:
        pass


def on_release(key):
    """Handle key release events."""
    try:
        current_keys.discard(key)
    except:
        pass


# ──────────────────────────────────────────────
# MENU BAR / SYSTEM TRAY
# ──────────────────────────────────────────────

def get_status_text(item):
    """Dynamic label showing current status."""
    if typing_in_progress:
        return "Status: Typing..."
    elif enabled:
        return "Status: Active"
    else:
        return "Status: Paused"


def get_toggle_text(item):
    """Dynamic label for the pause/resume button."""
    if typing_in_progress:
        return "Stop Typing"
    elif enabled:
        return "Pause"
    else:
        return "Resume"


def on_toggle(icon, item):
    """Menu callback for pause/resume."""
    toggle_enabled()


def create_menu():
    """Create the tray icon menu."""
    return pystray.Menu(
        pystray.MenuItem("Clipboard Typer", None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(get_status_text, None, enabled=False),
        pystray.MenuItem(
            lambda item: f"Speed: {TYPING_DELAY}s/char",
            None,
            enabled=False
        ),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Ctrl+Shift+V  Paste", None, enabled=False),
        pystray.MenuItem("ESC  Stop typing", None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(get_toggle_text, on_toggle),
        pystray.MenuItem("Quit", quit_program),
    )


def setup(icon):
    """Called when the tray icon is ready. Starts the keyboard listener."""
    icon.visible = True
    logging.info("Tray icon visible, starting keyboard listener...")
    # Start keyboard listener in a background thread
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    logging.info(f"Keyboard listener started: {listener.is_alive()}")


def main():
    global tray_icon

    tray_icon = pystray.Icon(
        "clipboard_typer",
        get_status_icon(),
        "Clipboard Typer",
        menu=create_menu()
    )

    tray_icon.run(setup=setup)


if __name__ == "__main__":
    main()
