# -*- coding: utf-8 -*-
"""
TruTops DWG to GEO Converter
A GUI automation tool for batch converting DWG files to GEO format.
Press ESC at any time to abort automation.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import threading
import time
import copy
import re
from pathlib import Path
import ctypes
import sys

APP_VERSION = "1.2.0"

HOTKEY_COMMANDS = {
    "1": "load",
    "2": "save",
    "3": "retry",
    "4": "skip",
    "5": "full",
}

GEO_POLICY_LABELS = {
    "Skip existing GEO": "skip_existing",
    "Replace existing GEO": "replace_existing",
    "Only process changed DWGs": "newer_only",
}

GEO_POLICY_NAMES = {value: key for key, value in GEO_POLICY_LABELS.items()}

from dwg_filter import DwgProjectFilter, FilterError

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)


# Enable High DPI Awareness on Windows to fix blurry UI
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass


import pyautogui
from PIL import Image, ImageGrab, ImageDraw, ImageTk
from pynput import mouse, keyboard

# Safety: Move mouse to top-left corner to abort
pyautogui.FAILSAFE = True

# Default configuration
# Default configuration
DEFAULT_CONFIG = {
    "import_delay": 3.0,
    "save_delay": 2.0,
    "smart_wait_timeout": 12.0,
    "screen_settle_time": 0.7,
    "trutops_window_title": "TruTops",  # Window title to focus
    "mode": "auto",                     # auto or manual
    "auto_delay": 3,                    # Seconds to wait in auto mode
    "manual_hotkey": "f2",              # Hotkey for manual trigger
    "existing_geo_policy": "skip_existing",
    "oda_converter_path": "",
    "project_root": "",
    "click_locations": {
        "open_drawing": [549, 114],          # Open Drawing button (not Ctrl+O)
        "no_save": [3009, 672],              # "No" button - don't save modifications
        "save_selected": [680, 126],         # Save Selected to GEO button
        "select_top_left": [75, 209],        # Top-left corner of selection box
        "select_bottom_right": [3350, 1867], # Bottom-right corner of selection box
        "delete_selection": None,
        "cleanup_delete": None,
    },
    "relative_click_locations": {},
    "buttons": {
        "open_drawing": {
            "image": "ScreenShots/Opendrawings.png",
            "fallback_coords": None,
        },
        "save_selected": {
            "image": "ScreenShots/Save Selection.png",
            "fallback_coords": None,
        },
    },
    "last_processed_index": 0
}

CONFIG_FILE = "config.json"
SCREENSHOTS_DIR = "ScreenShots"


def find_trutops_window(partial_title="TruTops"):
    """Return the largest visible external TruTops window, if available."""
    title_filter = (partial_title or "TruTops").strip().lower()

    try:
        import win32gui

        matches = []

        def callback(hwnd, _):
            if not win32gui.IsWindowVisible(hwnd):
                return

            title = win32gui.GetWindowText(hwnd)
            if not title or title_filter not in title.lower():
                return

            # Do not mistake this D2G window for TruTops.
            if "dwg to geo" in title.lower() or "d2g" == title.lower().strip():
                return

            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            area = max(0, right - left) * max(0, bottom - top)
            if area:
                matches.append({
                    "hwnd": hwnd,
                    "title": title,
                    "rect": (left, top, right, bottom),
                    "area": area,
                })

        win32gui.EnumWindows(callback, None)
        if matches:
            return max(matches, key=lambda item: item["area"])
    except Exception as exc:
        print("[WINDOW] TruTops lookup unavailable: {}".format(exc))

    return None


def to_relative_position(x, y, rect):
    """Convert a screen coordinate to a normalized position inside a window."""
    if not rect:
        return None
    left, top, right, bottom = rect
    width = right - left
    height = bottom - top
    if width <= 0 or height <= 0:
        return None
    return [
        round((x - left) / float(width), 6),
        round((y - top) / float(height), 6),
    ]


def from_relative_position(position, rect):
    """Convert a normalized window position back to screen coordinates."""
    if not position or not rect:
        return None
    left, top, right, bottom = rect
    return (
        int(round(left + float(position[0]) * (right - left))),
        int(round(top + float(position[1]) * (bottom - top))),
    )


class ImagePreviewWindow(tk.Toplevel):
    """Window to display the part preview on a second screen."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Part Preview")
        
        # Center window on screen
        win_width = 800
        win_height = 800
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - win_width) // 2
        y = (screen_height - win_height) // 2
        self.geometry(f"{win_width}x{win_height}+{x}+{y}")
        
        self.configure(bg="black")
        
        # Make it persistent (don't destroy on close, just hide)
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        
        self.image_label = tk.Label(self, bg="black")
        self.image_label.pack(fill="both", expand=True)
        
        self.current_image = None
        
        # Initial overlay text
        self.status_label = tk.Label(
            self, text="Waiting for automation...", 
            bg="black", fg="white", font=("Arial", 14)
        )
        self.status_label.place(relx=0.5, rely=0.5, anchor="center")
        
        self.raw_image = None
        self.bind("<Configure>", self._on_resize)
        self.resize_timer = None

    def _on_resize(self, event):
        """Handle window resize events."""
        if self.raw_image:
            # Debounce resize to avoid lag
            if self.resize_timer:
                self.after_cancel(self.resize_timer)
            self.resize_timer = self.after(100, self._refresh_image)

    def show_image(self, image_path):
        """Load and scale image to fit window."""
        self.deiconify()
        
        if not os.path.exists(image_path):
            self.status_label.config(text="Image not found:\n" + os.path.basename(image_path))
            self.status_label.place(relx=0.5, rely=0.5, anchor="center")
            self.image_label.configure(image='')
            return

        try:
            # Load and convert to RGB (Fixes over-exposed/CMYK issues)
            self.raw_image = Image.open(image_path).convert('RGB')
            self._refresh_image()
            self.status_label.place_forget()
            
        except Exception as e:
            print("Image ID 10T Error: {}".format(e))
            self.status_label.config(text="Error loading image")
            self.status_label.place(relx=0.5, rely=0.5, anchor="center")

    def _refresh_image(self):
        """Resize current raw image to fit window."""
        if not self.raw_image:
            return

        # Get window size
        win_width = self.winfo_width()
        win_height = self.winfo_height()
        
        if win_width < 50 or win_height < 50: 
            return
        
        # Calculate input aspect ratio
        img_ratio = self.raw_image.width / self.raw_image.height
        win_ratio = win_width / win_height
        
        if img_ratio > win_ratio:
            # limited by width
            target_width = win_width
            target_height = int(win_width / img_ratio)
        else:
            # limited by height
            target_height = win_height
            target_width = int(win_height * img_ratio)
            
        # Use High Quality Downsampling
        img = self.raw_image.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        self.current_image = ImageTk.PhotoImage(img)
        self.image_label.configure(image=self.current_image)
            


    def clear(self):
        """Clear the current image."""
        self.image_label.configure(image='')
        self.status_label.config(text="Waiting...")
        self.status_label.place(relx=0.5, rely=0.5, anchor="center")


class Config:
    """Handles loading and saving configuration."""

    def __init__(self):
        self.data = copy.deepcopy(DEFAULT_CONFIG)
        self.load()
        print("[CONFIG] Loaded. click_locations: {}".format(self.data.get("click_locations")))

    def load(self):
        """Load configuration from file."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    saved = json.load(f)
                    self._deep_update(self.data, saved)
                
                # Migration: Update F1 to F2
                if self.data.get("manual_hotkey") == "f1":
                    print("[CONFIG] Migrating hotkey from F1 to F2")
                    self.data["manual_hotkey"] = "f2"
                    self.save()

            except (json.JSONDecodeError, IOError):
                pass

    def save(self):
        """Save configuration to file."""
        full_path = os.path.abspath(CONFIG_FILE)
        print("[CONFIG] Saving to: {}".format(full_path))
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
        print("[CONFIG] Saved! click_locations: {}".format(self.data.get("click_locations")))

    def _deep_update(self, base, update):
        """Recursively update nested dictionaries."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value

    def get(self, *keys):
        """Get a nested config value."""
        value = self.data
        for key in keys:
            if value is None:
                return None
            value = value.get(key) if isinstance(value, dict) else None
        return value

    def set(self, *keys_and_value):
        """Set a nested config value."""
        keys = keys_and_value[:-1]
        value = keys_and_value[-1]
        target = self.data
        for key in keys[:-1]:
            target = target.setdefault(key, {})
        target[keys[-1]] = value
        self.save()


class ButtonDetector:
    """Handles finding buttons on screen with multiple strategies."""

    @staticmethod
    def find_button(image_path, fallback_coords=None, region=None, allow_fallback=True):
        """Find a button on screen using image detection."""
        if image_path and not os.path.isabs(image_path):
            image_path = resource_path(image_path)

        if not image_path or not os.path.exists(image_path):
            if allow_fallback and fallback_coords:
                return tuple(fallback_coords), "Saved coordinates (no image)"
            return None, "Not found (no image file)"

        strategies = [
            ("High confidence", {"confidence": 0.8}),
            ("Medium confidence", {"confidence": 0.7}),
        ]

        for name, params in strategies:
            try:
                location = pyautogui.locateOnScreen(image_path, region=region, **params)
                if location:
                    return pyautogui.center(location), name
            except Exception:
                continue

        # Try grayscale
        try:
            location = pyautogui.locateOnScreen(
                image_path, confidence=0.7, grayscale=True, region=region
            )
            if location:
                return pyautogui.center(location), "Grayscale match"
        except Exception:
            pass

        if allow_fallback and fallback_coords:
            return tuple(fallback_coords), "Saved coordinates"

        return None, "Not found"


class ClickIndicator:
    """Shows a visual indicator where clicks happen using a simple approach."""

    def __init__(self, app):
        self.app = app
        self.indicator_window = None

    def show_click(self, x, y, persistent=False):
        """Show a yellow circle at click position."""
        self._show_overlay(x, y, "click", persistent)

    def show_highlight(self, x, y, duration=500):
        """Show a blue target/highlight at position."""
        self._show_overlay(x, y, "highlight", False, duration)

    def _show_overlay(self, x, y, type_="click", persistent=False, duration=200):
        try:
            # Create indicator window
            window = tk.Toplevel(self.app)
            window.overrideredirect(True)
            window.attributes('-topmost', True)

            # Try to make transparent (Windows)
            try:
                window.attributes('-transparentcolor', 'black')
            except:
                pass

            size = 60 if type_ == "click" else 100
            window.geometry("{}x{}+{}+{}".format(
                size, size, int(x - size // 2), int(y - size // 2)
            ))
            window.configure(bg='black')

            # Draw
            canvas = tk.Canvas(
                window,
                width=size, height=size,
                bg='black', highlightthickness=0
            )
            canvas.pack()

            if type_ == "click":
                # Yellow circle for click
                canvas.create_oval(5, 5, size-5, size-5, outline='#ffff00', width=4)
                canvas.create_oval(15, 15, size-15, size-15, fill='', outline='#ffff00', width=2)
                # Just outline is fine as per original, maybe thicker
                canvas.create_oval(20, 20, size-20, size-20, outline='#ffff00', width=2)
            else:
                # Blue corners/box for highlight
                color = '#00a8ff'  # Bright blue
                # Draw corners to look like a target sight
                l = 20 # line length
                w = 3  # width
                # Top-left
                canvas.create_line(0, 0, l, 0, fill=color, width=w)
                canvas.create_line(0, 0, 0, l, fill=color, width=w)
                # Top-right
                canvas.create_line(size, 0, size-l, 0, fill=color, width=w)
                canvas.create_line(size, 0, size, l, fill=color, width=w)
                # Bottom-left
                canvas.create_line(0, size, 0, size-l, fill=color, width=w)
                canvas.create_line(0, size, l, size, fill=color, width=w)
                # Bottom-right
                canvas.create_line(size, size, size-l, size, fill=color, width=w)
                canvas.create_line(size, size, size, size-l, fill=color, width=w)

            # Keep reference to avoid GC if needed, but for now just let it float?
            # We need to track it to close it if persistent=False
            
            if not persistent:
                window.after(duration, window.destroy)
            else:
                # If persistent, we might want to store it in self.indicator_window to close later manually
                # But original code had logic for that. Let's keep it simple for now.
                self.indicator_window = window

        except Exception as e:
            print("Indicator error: {}".format(e))

    def _close_indicator(self):
        """Close the persistent indicator window."""
        if self.indicator_window:
            try:
                self.indicator_window.destroy()
            except:
                pass
            self.indicator_window = None

    def show_keypress(self, key):
        """Show a key press indicator."""
        try:
            self.indicator_window = tk.Toplevel(self.app)
            self.indicator_window.overrideredirect(True)
            self.indicator_window.attributes('-topmost', True)

            # Position at top-center of screen
            screen_width = self.app.winfo_screenwidth()
            self.indicator_window.geometry("+{}+50".format(screen_width // 2 - 50))
            self.indicator_window.configure(bg='yellow')

            label = tk.Label(
                self.indicator_window,
                text="[{}]".format(key.upper()),
                font=("Arial", 16, "bold"),
                bg='yellow', fg='black',
                padx=10, pady=5
            )
            label.pack()

            self.indicator_window.after(200, self._close_indicator)

        except Exception as e:
            print("Indicator error: {}".format(e))



class StatusOverlay:
    """Persistent overlay to show current automation status/step."""
    
    def __init__(self, root):
        self.root = root
        self.window = None
        self.label = None
        
    def show(self, text, mode="AUTO"):
        """Show or update the overlay."""
        try:
            if not self.window:
                self.window = tk.Toplevel(self.root)
                self.window.overrideredirect(True)
                self.window.attributes('-topmost', True)
                self.window.attributes('-alpha', 0.85) # Slight transparency
                self.window.configure(bg='black')
                
                # Position bottom-left
                screen_h = self.root.winfo_screenheight()
                self.window.geometry("+30+{}".format(screen_h - 120))
                
                self.label = tk.Label(
                    self.window, 
                    text="", 
                    font=("Consolas", 12, "bold"),
                    bg='black', fg='#00ff00', # Hacker green
                    padx=15, pady=8,
                    relief="raised", borderwidth=1
                )
                self.label.pack()

            # Format: [MODE] Step Description
            display_text = "[{}] {}".format(mode.upper(), text)
            self.label.config(text=display_text)
            self.window.deiconify()
            self.window.lift()
            
        except Exception as e:
            print("Overlay error: {}".format(e))

    def hide(self):
        """Hide the overlay."""
        if self.window:
            self.window.withdraw()

    def destroy(self):
        """Clean up."""
        if self.window:
            self.window.destroy()
            self.window = None


class LocationSetupDialog(tk.Toplevel):
    """Dialog for capturing click locations."""

    def __init__(self, parent, config):
        super().__init__(parent)
        self.parent = parent
        self.config = config
        self.title("Setup Window-Relative Click Locations")
        self.geometry("650x780")
        self.minsize(650, 700)
        self.transient(parent)
        self.grab_set()

        # Use parent's colors
        self.colors = parent.colors
        self.configure(bg=self.colors["bg"])

        self.locations = {
            "open_drawing": "Open Drawing button",
            "no_save": "No button (save dialog)",
            "save_selected": "Save Selected to GEO",
            "select_top_left": "Selection TOP-LEFT",
            "select_bottom_right": "Selection BOTTOM-RIGHT",
            "delete_selection": "Delete Selection button",
            "cleanup_delete": "OK button in cleanup dialog",
        }

        self.captured = {}
        self._create_widgets()
        self._update_status()

    def _create_widgets(self):
        """Create dialog widgets."""
        # Instructions
        instr = tk.Label(
            self,
            text=(
                "Click CAPTURE, then click the location in TruTops. "
                "D2G stores it relative to the TruTops window so the window can move."
            ),
            font=("Segoe UI", 10),
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            wraplength=450
        )
        instr.pack(pady=15)

        # Location captures
        self.status_labels = {}
        self.capture_buttons = {}

        for key, name in self.locations.items():
            frame = tk.Frame(self, bg=self.colors["bg_light"], padx=10, pady=8)
            frame.pack(fill="x", padx=15, pady=4)

            tk.Label(
                frame, text=name, font=("Segoe UI", 10),
                bg=self.colors["bg_light"], fg=self.colors["fg"], anchor="w"
            ).pack(side="left")

            # Buttons on right side
            btn = tk.Button(
                frame, text="CAPTURE", font=("Segoe UI", 9),
                bg=self.colors["accent"], fg=self.colors["fg"],
                activebackground=self.colors["highlight"],
                bd=0, padx=10, pady=4,
                command=lambda k=key: self._start_capture(k)
            )
            btn.pack(side="right", padx=(5, 0))
            self.capture_buttons[key] = btn

            edit_btn = tk.Button(
                frame, text="EDIT", font=("Segoe UI", 9),
                bg=self.colors["bg"], fg=self.colors["fg"],
                activebackground=self.colors["highlight"],
                bd=0, padx=10, pady=4,
                command=lambda k=key: self._edit_coords(k)
            )
            edit_btn.pack(side="right", padx=(5, 0))

            status = tk.Label(
                frame, text="Not set", font=("Consolas", 9),
                bg=self.colors["bg_light"], fg=self.colors["accent"],
                width=14, anchor="e"
            )
            status.pack(side="right", padx=(10, 0))
            self.status_labels[key] = status

        # Countdown label
        self.countdown_label = tk.Label(
            self, text="", font=("Segoe UI", 14, "bold"),
            bg=self.colors["bg"], fg=self.colors["highlight"]
        )
        self.countdown_label.pack(pady=15)

        # Buttons
        btn_frame = tk.Frame(self, bg=self.colors["bg"])
        btn_frame.pack(fill="x", padx=15, pady=15)

        tk.Button(
            btn_frame, text="Save & Close", font=("Segoe UI", 10),
            bg=self.colors["success"], fg="#ffffff",
            activebackground=self.colors["highlight"],
            bd=0, padx=20, pady=8,
            command=self._save
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame, text="Cancel", font=("Segoe UI", 10),
            bg=self.colors["accent"], fg=self.colors["fg"],
            activebackground=self.colors["highlight"],
            bd=0, padx=20, pady=8,
            command=self.destroy
        ).pack(side="left", padx=5)

    def _update_status(self):
        """Update status labels."""
        for key in self.locations:
            coords = self.config.get("click_locations", key)
            relative = self.config.get("relative_click_locations", key)
            if coords:
                self.status_labels[key].config(
                    text=("Relative" if relative else "({}, {})".format(coords[0], coords[1])),
                    fg=self.colors["success"]
                )
                self.captured[key] = True
            else:
                self.status_labels[key].config(
                    text="Not set",
                    fg=self.colors["accent"]
                )
                self.captured[key] = False

    def _start_capture(self, location_key):
        """Start capture countdown."""
        for btn in self.capture_buttons.values():
            btn.config(state="disabled")

        self.withdraw()

        threading.Thread(
            target=self._capture_countdown,
            args=(location_key,),
            daemon=True
        ).start()

    def _capture_countdown(self, location_key):
        """Countdown and wait for click."""
        for i in range(5, 0, -1):
            self.after(0, lambda i=i: self.countdown_label.config(
                text="Click in {}...".format(i)
            ))
            time.sleep(1)

        self.after(0, lambda: self.countdown_label.config(text="Click now!"))

        click_pos = [None]

        def on_click(x, y, button, pressed):
            if pressed:
                click_pos[0] = (x, y)
                return False

        listener = mouse.Listener(on_click=on_click)
        listener.start()
        listener.join(timeout=10)

        if click_pos[0]:
            x, y = click_pos[0]
            print("[CAPTURE] Got click at ({}, {}) for {}".format(x, y, location_key))
            self._store_location(location_key, x, y)
            self.captured[location_key] = True
            self.after(0, lambda: self._capture_complete(location_key, x, y))
        else:
            print("[CAPTURE] No click detected for {}".format(location_key))
            self.after(0, lambda: self._capture_complete(location_key, None, None))

    def _capture_complete(self, location_key, x, y):
        """Handle capture completion."""
        self.deiconify()
        self.countdown_label.config(text="")

        for btn in self.capture_buttons.values():
            btn.config(state="normal")

        if x is not None:
            relative = self.config.get("relative_click_locations", location_key)
            self.status_labels[location_key].config(
                text=("Relative" if relative else "({}, {})".format(x, y)),
                fg=self.colors["success"]
            )

    def _store_location(self, location_key, x, y):
        """Store both a legacy absolute point and a window-relative point."""
        self.config.set("click_locations", location_key, [x, y])

        title = self.config.get("trutops_window_title") or "TruTops"
        window = find_trutops_window(title)
        relative = to_relative_position(x, y, window["rect"]) if window else None
        if relative:
            self.config.set("relative_click_locations", location_key, relative)
            print("[CAPTURE] Stored relative position {} for {}".format(relative, location_key))
        else:
            self.config.set("relative_click_locations", location_key, None)
            print("[CAPTURE] TruTops window not found; kept absolute position")

    def _edit_coords(self, location_key):
        """Manually edit coordinates."""
        from tkinter import simpledialog

        current = self.config.get("click_locations", location_key)
        current_str = "{}, {}".format(current[0], current[1]) if current else ""

        result = simpledialog.askstring(
            "Edit Coordinates",
            "Enter X, Y coordinates for {}:".format(self.locations[location_key]),
            initialvalue=current_str,
            parent=self
        )

        if result:
            try:
                parts = result.replace(" ", "").split(",")
                x, y = int(parts[0]), int(parts[1])
                self._store_location(location_key, x, y)
                relative = self.config.get("relative_click_locations", location_key)
                self.status_labels[location_key].config(
                    text=("Relative" if relative else "({}, {})".format(x, y)),
                    fg=self.colors["success"]
                )
                print("[EDIT] {} set to ({}, {})".format(location_key, x, y))
            except (ValueError, IndexError):
                from tkinter import messagebox
                messagebox.showerror("Invalid", "Enter coordinates as: X, Y")

    def _save(self):
        """Save and close."""
        self.config.save()
        self.destroy()


class AutomationRunner:
    """Handles the automation process."""

    def __init__(self, app):
        self.app = app
        self.config = app.config
        self.running = False
        self.current_index = 0
        self.indicator = ClickIndicator(app)
        self.overlay = StatusOverlay(app)
        self.escape_pressed = False
        self.keyboard_listener = None
        self.manual_trigger = False
        self.dry_run = False
        self.step_by_step = False
        self.ctrl_down = False
        self.pressed_hotkeys = set()
        self.command_event = threading.Event()
        self.command_lock = threading.Lock()
        self.pending_command = None
        self.accepting_commands = False
        self.current_group = None
        self.current_file_path = None
        self.trutops_window = None

    def start(self, files, mode="auto", delay=3.0, manual_hotkey="f1"):
        """Start processing files."""
        self.running = True
        self.escape_pressed = False
        self.files = files # List of dicts: {"dwg": path, "image": path}
        self.mode = mode
        self.delay = delay
        self.manual_hotkey = manual_hotkey
        self.pending_command = None
        self.command_event.clear()
        self.accepting_commands = False
        
        self.current_index = self.config.get("last_processed_index") or 0
        self.manual_trigger = False

        # Ask if resuming
        if self.current_index > 0 and self.current_index < len(files):
            if not messagebox.askyesno(
                "Resume?",
                "Resume from file {}?".format(self.current_index + 1)
            ):
                self.current_index = 0
        else:
            self.current_index = 0

        # Start Global Listener (ESC and Hotkey)
        self._start_listeners()

        threading.Thread(target=self._run, daemon=True).start()

    def stop(self):
        """Stop processing."""
        self.running = False
        self.command_event.set()
        self._stop_listeners()
        self.app.after(0, self.overlay.hide)
        self.app.update_status("Stopped")

    def _start_listeners(self):
        """Start listening for keyboard events."""
        def on_press(key):
            # Check ESC
            if key == keyboard.Key.esc:
                print("\n[ESC PRESSED] Aborting automation...")
                self.escape_pressed = True
                self.running = False
                self.command_event.set()
                return False

            try:
                ctrl_keys = {keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r}
                if key in ctrl_keys:
                    self.ctrl_down = True
                    return

                if self.ctrl_down and isinstance(key, keyboard.KeyCode):
                    number = str(key.char or "").lower()
                    if number not in HOTKEY_COMMANDS and getattr(key, "vk", None) in range(48, 58):
                        number = chr(key.vk)
                    if number in HOTKEY_COMMANDS and number not in self.pressed_hotkeys:
                        self.pressed_hotkeys.add(number)
                        self._queue_command(HOTKEY_COMMANDS[number], number)
            except Exception as exc:
                print("[HOTKEY] Listener error: {}".format(exc))

        def on_release(key):
            ctrl_keys = {keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r}
            if key in ctrl_keys:
                self.ctrl_down = False
                self.pressed_hotkeys.clear()
            elif isinstance(key, keyboard.KeyCode):
                self.pressed_hotkeys.discard(str(key.char or "").lower())

        self.keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.keyboard_listener.start()

    def _queue_command(self, command, number):
        """Queue a grouped shortcut while D2G is waiting for help."""
        if not self.accepting_commands:
            print("[HOTKEY] Ctrl+{} ignored while automation is busy".format(number))
            return

        with self.command_lock:
            self.pending_command = command
            self.command_event.set()
        print("[HOTKEY] Ctrl+{} -> {}".format(number, command))

    def _stop_listeners(self):
        """Stop listeners."""
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None

    def _wait_for_command(self, message):
        """Pause safely until one grouped Ctrl shortcut is pressed."""
        instructions = (
            "Ctrl+1 Load | Ctrl+2 Create GEO | Ctrl+3 Retry | "
            "Ctrl+4 Skip File | Ctrl+5 Full File | Esc Stop"
        )
        print("[RECOVERY] {}".format(message))
        print("[RECOVERY] {}".format(instructions))

        with self.command_lock:
            self.pending_command = None
            self.command_event.clear()
            self.accepting_commands = True

        self.app.after(0, lambda: self.overlay.show(
            "{}\n{}".format(message, instructions), "PAUSED"
        ))
        self.app.after(0, lambda: self.app.update_status(
            "{} - {}".format(message, instructions)
        ))

        while self.running and not self.escape_pressed:
            if self.command_event.wait(0.1):
                break

        with self.command_lock:
            command = self.pending_command
            self.pending_command = None
            self.command_event.clear()
            self.accepting_commands = False

        return command

    def _wait_for_trigger(self):
        """Retained compatibility wrapper for the configurable auto pause."""
        return self._interruptible_delay(self.delay)

    def _interruptible_delay(self, seconds):
        """Wait without preventing ESC from stopping the runner."""
        deadline = time.monotonic() + max(0.0, float(seconds))
        while time.monotonic() < deadline:
            if not self.running or self.escape_pressed:
                return False
            time.sleep(min(0.1, max(0.0, deadline - time.monotonic())))
        return self.running and not self.escape_pressed

    def _focus_trutops(self):
        """Try to focus TrueTops window."""
        try:
            import win32con
            import win32gui

            title = self.config.get("trutops_window_title") or "TruTops"
            self.trutops_window = find_trutops_window(title)
            if not self.trutops_window:
                print("[FOCUS] Window '{}' not found".format(title))
                return False

            hwnd = self.trutops_window["hwnd"]
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            self.app.after(0, self._restore_app_if_minimized)
            self._interruptible_delay(0.25)
            print("[FOCUS] Activated: {}".format(self.trutops_window["title"]))
            return True

        except Exception as e:
            print("[FOCUS] Error: {}".format(e))
            return False

    def _restore_app_if_minimized(self):
        """Keep D2G open behind TruTops while TruTops receives input focus."""
        if self.app.state() == "iconic":
            self.app.deiconify()

    def _window_rect(self):
        """Return the current TruTops rectangle, refreshing it after moves/resizes."""
        title = self.config.get("trutops_window_title") or "TruTops"
        window = find_trutops_window(title)
        if window:
            self.trutops_window = window
            return window["rect"]
        return self.trutops_window["rect"] if self.trutops_window else None

    def _window_region(self):
        rect = self._window_rect()
        if not rect:
            return None
        left, top, right, bottom = rect
        if left < 0 or top < 0:
            return None
        return (left, top, right - left, bottom - top)

    def _resolve_location(self, location_key, prefer_image=False):
        """Resolve an image match, relative point, or legacy absolute point."""
        rect = self._window_rect()

        if prefer_image:
            image_path = self.config.get("buttons", location_key, "image")
            pos, strategy = ButtonDetector.find_button(
                image_path,
                region=self._window_region(),
                allow_fallback=False,
            )
            if pos:
                print("[LOCATION] {} found via {}".format(location_key, strategy))
                return tuple(pos)

        relative = self.config.get("relative_click_locations", location_key)
        position = from_relative_position(relative, rect)
        if position:
            print("[LOCATION] {} resolved relative to TruTops".format(location_key))
            return position

        absolute = self.config.get("click_locations", location_key)
        if absolute:
            print("[LOCATION] {} using legacy absolute coordinates".format(location_key))
            return tuple(absolute)

        return None

    def _capture_signature(self):
        """Capture a small grayscale signature of the TruTops window."""
        try:
            rect = self._window_rect()
            image = ImageGrab.grab(bbox=rect, all_screens=True) if rect else ImageGrab.grab(all_screens=True)
            image = image.convert("L").resize((96, 54), Image.Resampling.BILINEAR)
            return bytes(image.tobytes())
        except Exception as exc:
            print("[WAIT] Screen capture unavailable: {}".format(exc))
            return None

    @staticmethod
    def _signature_difference(first, second):
        if not first or not second or len(first) != len(second):
            return 0.0
        total = sum(abs(a - b) for a, b in zip(first, second))
        return total / float(len(first) * 255)

    def _wait_for_ui_transition(self, before, description, timeout=None, require_change=True):
        """Wait for a screen change to finish instead of sleeping a fixed amount."""
        if self.dry_run:
            return True
        if before is None:
            return self._interruptible_delay(0.8)

        timeout = float(timeout or self.config.get("smart_wait_timeout") or 12.0)
        settle_time = float(self.config.get("screen_settle_time") or 0.7)
        deadline = time.monotonic() + timeout
        previous = before
        changed = not require_change
        stable_since = None

        while time.monotonic() < deadline:
            if not self.running or self.escape_pressed:
                return False

            current = self._capture_signature()
            if current is None:
                return self._interruptible_delay(0.8)

            if self._signature_difference(before, current) >= 0.0025:
                changed = True

            frame_change = self._signature_difference(previous, current)
            if changed and frame_change <= 0.0015:
                if stable_since is None:
                    stable_since = time.monotonic()
                elif time.monotonic() - stable_since >= settle_time:
                    print("[WAIT] {} ready".format(description))
                    return True
            else:
                stable_since = None

            previous = current
            time.sleep(0.2)

        print("[WAIT] Timed out waiting for {}".format(description))
        return False

    def _smart_action(self, action, description, timeout=None, require_change=True):
        """Run an input action and wait until TruTops finishes changing."""
        before = self._capture_signature()
        action()
        return self._wait_for_ui_transition(
            before, description, timeout=timeout, require_change=require_change
        )

    def _wait_for_confirm(self, action_desc):
        """In step-by-step mode, wait for user to press Enter."""
        if self.step_by_step:
            print("\n  >>> NEXT: {} <<<".format(action_desc))
            print("  Press ENTER to continue (or 'q' to quit)...")
            response = input("  > ").strip().lower()
            if response == 'q':
                self.running = False
                return False
        return True

    def _click(self, x, y, description=""):
        """Click without creating a focus-stealing helper window."""
        print("[CLICK] ({}, {}) - {}".format(x, y, description))

        if not self.dry_run:
            pyautogui.moveTo(x, y, duration=0.15)
            pyautogui.click()
            time.sleep(0.15)
        else:
            print("  (dry run)")

    def _press(self, key, description=""):
        """Press key - simple."""
        print("[KEY] {} - {}".format(key, description))

        if not self.dry_run:
            pyautogui.press(key)
            time.sleep(0.15)
        else:
            print("  (dry run)")

    def _hotkey(self, *keys, description=""):
        """Press hotkey - simple."""
        key_str = "+".join(keys)
        print("[HOTKEY] {} - {}".format(key_str, description))

        if not self.dry_run:
            pyautogui.hotkey(*keys)
            time.sleep(0.2)
        else:
            print("  (dry run)")

    def _click_button_by_image(self, button_key, description):
        """Find and click a button using image detection."""
        image_path = self.config.get("buttons", button_key, "image")
        fallback = self.config.get("buttons", button_key, "fallback_coords")

        pos, strategy = ButtonDetector.find_button(image_path, fallback)

        if pos:
            print("[IMAGE] Found '{}' via {} at ({}, {})".format(
                description, strategy, pos[0], pos[1]))
            self._click(pos[0], pos[1], description)
            return True
        else:
            print("[IMAGE] Could not find '{}'".format(description))
            return False

    def _copy_to_clipboard(self, text):
        """Copy text to clipboard."""
        import subprocess
        # Use clip.exe on Windows
        process = subprocess.Popen(['clip'], stdin=subprocess.PIPE)
        process.communicate(text.encode('utf-8'))

    def _open_file_from_dialog(self, file_path):
        """Open a queued filename from TruTops' current file dialog folder."""
        file_name = os.path.basename(file_path)
        self._copy_to_clipboard(file_name)
        print("[CLIPBOARD] Copied filename: {}".format(file_name))
        self._hotkey('ctrl', 'a', description="Select filename")
        self._hotkey('ctrl', 'v', description="Paste DWG filename")
        self._press('enter', "Open drawing")

    @staticmethod
    def _expected_geo_path(dwg_path):
        """Return the GEO path used by the existing same-folder workflow."""
        return os.path.splitext(dwg_path)[0] + ".geo"

    @classmethod
    def _existing_geo_path(cls, dwg_path):
        """Find the normal GEO name or TruTops' numbered selection name."""
        expected = cls._expected_geo_path(dwg_path)
        if os.path.exists(expected):
            return expected

        folder = os.path.dirname(dwg_path)
        stem = os.path.splitext(os.path.basename(dwg_path))[0]
        pattern = re.compile(r"^{}_(\d+)\.geo$".format(re.escape(stem)), re.IGNORECASE)
        matches = []
        try:
            for name in os.listdir(folder):
                if pattern.match(name):
                    matches.append(os.path.join(folder, name))
        except OSError:
            return None

        return max(matches, key=os.path.getmtime) if matches else None

    def _skip_reason(self, dwg_path):
        """Return a reason to skip a DWG according to the selected policy."""
        policy = self.config.get("existing_geo_policy") or "skip_existing"
        geo_path = self._existing_geo_path(dwg_path)
        if policy == "replace_existing" or not geo_path:
            return None
        if policy == "skip_existing":
            return "GEO already exists"
        if policy == "newer_only" and os.path.getmtime(dwg_path) <= os.path.getmtime(geo_path):
            return "GEO is newer than DWG"
        return None

    def _dialog_kind(self):
        """Best-effort classification of a TruTops warning or save dialog."""
        try:
            import win32con
            import win32gui
            import win32process

            if not self.trutops_window:
                return "unknown"

            main_hwnd = self.trutops_window["hwnd"]
            _, main_pid = win32process.GetWindowThreadProcessId(main_hwnd)
            foreground = win32gui.GetForegroundWindow()
            main_rect = self._window_rect()
            main_area = 1
            if main_rect:
                main_area = max(1, (main_rect[2] - main_rect[0]) * (main_rect[3] - main_rect[1]))

            dialogs = []

            def enum_window(hwnd, _):
                if hwnd == main_hwnd or not win32gui.IsWindowVisible(hwnd):
                    return
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                if pid != main_pid:
                    return
                owner = win32gui.GetWindow(hwnd, win32con.GW_OWNER)
                if hwnd != foreground and owner != main_hwnd:
                    return

                texts = [win32gui.GetWindowText(hwnd)]

                def enum_child(child, child_texts):
                    if win32gui.IsWindowVisible(child):
                        text_value = win32gui.GetWindowText(child)
                        if text_value:
                            child_texts.append(text_value)

                win32gui.EnumChildWindows(hwnd, enum_child, texts)
                rect = win32gui.GetWindowRect(hwnd)
                area = max(0, rect[2] - rect[0]) * max(0, rect[3] - rect[1])
                dialogs.append((" ".join(texts).lower(), area / float(main_area)))

            win32gui.EnumWindows(enum_window, None)

            for text_value, area_ratio in dialogs:
                if any(token in text_value for token in (
                    "warning", "multiple geometr", "save changes", "don't save", "do not save"
                )):
                    return "warning"
                if any(token in text_value for token in (
                    ".geo", "file name", "filename", "save as", "file browser"
                )):
                    return "save"
                if any(token in text_value for token in (
                    ".dwg", "open drawing", "open file"
                )):
                    return "file"
                if area_ratio < 0.35:
                    return "warning"
                return "file"
        except Exception as exc:
            print("[DIALOG] Detection unavailable: {}".format(exc))

        return "unknown"

    def _show_group(self, group, file_name):
        self.current_group = group
        label = "Load DWG" if group == "load" else "Create GEO"
        self.app.after(0, lambda: self.overlay.show(
            "{}: {}".format(label, file_name), self.mode
        ))
        self.app.after(0, lambda: self.app.update_status(
            "{} - {}".format(label, file_name)
        ))

    def _run_load_group(self, item):
        """Open and import the current DWG as one recoverable operation."""
        file_path = item["dwg"]
        file_name = os.path.basename(file_path)
        self._show_group("load", file_name)

        if item.get("image"):
            self.app.after(0, lambda p=item["image"]: self.app.image_viewer.show_image(p))
        else:
            self.app.after(0, self.app.image_viewer.clear)
        self._interruptible_delay(0.2)

        if not self._focus_trutops():
            return False, "TruTops could not be focused"

        open_pos = self._resolve_location("open_drawing", prefer_image=True)
        if not open_pos:
            return False, "Open Drawing location was not found"
        if not self._smart_action(
            lambda: self._click(open_pos[0], open_pos[1], "Open Drawing"),
            "Open Drawing screen",
        ):
            return False, "Open Drawing screen did not appear"

        # Opening another drawing normally asks whether to save the current one.
        # If TruTops went directly to its file browser, do not click the old No
        # coordinates on top of that browser.
        if self._dialog_kind() == "warning":
            no_save_pos = self._resolve_location("no_save")
            if not no_save_pos:
                return False, "No button location was not found"
            if not self._smart_action(
                lambda: self._click(no_save_pos[0], no_save_pos[1], "No (don't save)"),
                "DWG file browser",
            ):
                return False, "DWG file browser did not appear"
        else:
            print("[DIALOG] No save warning detected; continuing with file browser")

        if not self._smart_action(
            lambda: self._open_file_from_dialog(file_path),
            "DWG import options",
        ):
            return False, "DWG import options did not appear"

        import_timeout = max(
            float(self.config.get("smart_wait_timeout") or 12.0),
            float(self.config.get("import_delay") or 3.0) + 5.0,
        )
        if not self._smart_action(
            lambda: self._press('enter', "Confirm import settings"),
            "imported drawing",
            timeout=import_timeout,
        ):
            return False, "The drawing did not finish importing"

        return True, None

    def _run_save_group(self, item):
        """Select the drawing and save it to GEO as one recoverable operation."""
        file_name = os.path.basename(item["dwg"])
        self._show_group("save", file_name)

        expected_geo = Path(item.get("geo") or self._expected_geo_path(item["dwg"]))
        if expected_geo.exists():
            return False, "GEO already exists; it was not overwritten"

        if not self._focus_trutops():
            return False, "TruTops could not be focused"

        save_pos = self._resolve_location("save_selected", prefer_image=True)
        if not save_pos:
            return False, "Save Selected location was not found"
        if not self._smart_action(
            lambda: self._click(save_pos[0], save_pos[1], "Save Selected to GEO"),
            "selection mode",
            require_change=False,
        ):
            return False, "Selection mode was not ready"

        top_left = self._resolve_location("select_top_left")
        bottom_right = self._resolve_location("select_bottom_right")
        if not top_left or not bottom_right:
            return False, "Selection area locations were not found"

        def select_geometry():
            self._click(top_left[0], top_left[1], "Selection top-left")
            self._click(bottom_right[0], bottom_right[1], "Selection bottom-right")

        if not self._smart_action(select_geometry, "selected geometry"):
            return False, "The geometry selection did not finish"

        # The warning only appears for some DWGs. Detect it instead of always
        # sending two Enter presses and shifting the workflow out of sequence.
        if self._dialog_kind() == "warning":
            if not self._smart_action(
                lambda: self._press('enter', "Confirm optional geometry warning"),
                "GEO save dialog",
            ):
                return False, "The optional warning did not close"

        save_timeout = max(
            float(self.config.get("smart_wait_timeout") or 12.0),
            float(self.config.get("save_delay") or 2.0) + 4.0,
        )
        if not self._smart_action(
            lambda: self._press('enter', "Save GEO"),
            "completed GEO save",
            timeout=save_timeout,
        ):
            return False, "The GEO save screen did not close"

        if not expected_geo.exists():
            return False, "Expected GEO was not created: {}".format(expected_geo)
        if item.get("manifest"):
            DwgProjectFilter.mark_geo_complete(item)

        return True, None

    def _process_current_file(self, item):
        """Run both groups, pausing for grouped keyboard recovery as needed."""
        phase = "load"
        run_full = self.mode == "auto"

        while self.running and not self.escape_pressed:
            if phase == "load":
                success, reason = self._run_load_group(item)
            else:
                success, reason = self._run_save_group(item)

            if success:
                if phase == "save":
                    return "done"

                phase = "save"
                if run_full:
                    self.app.after(0, lambda: self.overlay.show(
                        "Drawing loaded - preparing Create GEO", self.mode
                    ))
                    if not self._interruptible_delay(self.delay):
                        return "stopped"
                    continue

                command = self._wait_for_command(
                    "DWG loaded. Use Ctrl+2 to Create GEO"
                )
            else:
                command = self._wait_for_command(
                    "{} failed: {}".format(
                        "Load DWG" if phase == "load" else "Create GEO", reason
                    )
                )

            if not command:
                return "stopped"
            if command == "skip":
                return "skipped"
            if command == "retry":
                continue
            if command == "load":
                phase = "load"
                run_full = False
            elif command == "save":
                phase = "save"
                run_full = False
            elif command == "full":
                phase = "load"
                run_full = True

        return "stopped"

    def _run(self):
        """Main automation loop."""
        total = len(self.files)
        processed = 0
        skipped = 0

        print("\n" + "=" * 50)
        print("STARTING D2G {} - Press ESC to abort".format(APP_VERSION))
        print("=" * 50)
        self.app.after(0, self.app.image_viewer.deiconify)

        for i in range(self.current_index, total):
            if not self.running or self.escape_pressed:
                break

            item = self.files[i]
            file_path = item["dwg"]
            file_name = os.path.basename(file_path)
            self.current_index = i
            self.current_file_path = file_path
            self.config.set("last_processed_index", i)

            if item.get("geo") and Path(item["geo"]).exists():
                reason = "GEO already exists"
            else:
                reason = self._skip_reason(file_path)
            if reason:
                skipped += 1
                print("[SKIP] {} - {}".format(file_name, reason))
                self.app.after(0, lambda i=i: self.app.update_file_status(i, "skipped"))
                self.app.after(0, lambda f=file_name, r=reason: self.app.update_status(
                    "Skipped {}: {}".format(f, r)
                ))
                self.app.after(0, lambda n=i + 1, t=total: self.app.update_progress(n, t))
                continue

            self.app.after(0, lambda i=i: self.app.update_file_status(i, "processing"))
            self.app.after(0, lambda f=file_name, i=i, t=total: self.app.update_status(
                "Processing {} ({}/{}) - ESC to abort".format(f, i + 1, t)
            ))
            self.app.after(0, lambda i=i, t=total: self.app.update_progress(i, t))

            try:
                print("\n--- File {}/{}: {} ---".format(i + 1, total, file_name))
                outcome = self._process_current_file(item)
                if outcome == "done":
                    processed += 1
                    self.app.after(0, lambda i=i: self.app.update_file_status(i, "done"))
                    self.app.after(0, lambda n=i + 1, t=total: self.app.update_progress(n, t))
                    print("Done!")
                elif outcome == "skipped":
                    skipped += 1
                    self.app.after(0, lambda i=i: self.app.update_file_status(i, "skipped"))
                    self.app.after(0, lambda n=i + 1, t=total: self.app.update_progress(n, t))
                    print("Skipped by operator")
                else:
                    break

            except Exception as e:
                print("ERROR: {}".format(e))
                self.app.after(0, lambda e=e: self.app.update_status("Error: {}".format(e)))
                self.running = False
                break

        self.accepting_commands = False
        self._stop_listeners()

        if self.escape_pressed:
            self.app.after(0, lambda: self.app.update_status("Aborted by user (ESC)"))
            self.app.after(0, lambda: messagebox.showinfo("Aborted", "Automation stopped by ESC key"))
        elif self.running:
            self.config.set("last_processed_index", 0)
            summary = "Complete: {} processed, {} skipped".format(processed, skipped)
            self.app.after(0, lambda s=summary: self.app.update_status(s))
            self.app.after(0, lambda: self.app.update_progress(total, total))
            self.app.after(0, lambda s=summary: messagebox.showinfo("Done", s))

        self.running = False
        self.app.after(0, self.overlay.hide)
        self.app.after(0, self.app.on_automation_stopped)


class ManualController:
    """Global Ctrl shortcuts for small, operator-controlled jobs."""

    def __init__(self, app):
        self.app = app
        self.config = app.config
        self.listener = None
        self.busy = False
        self.cancelled = False

    def start(self):
        self.listener = keyboard.GlobalHotKeys({
            "<ctrl>+1": lambda: self.app.after(0, lambda: self.trigger("clean_geo")),
            "<ctrl>+2": lambda: self.app.after(0, lambda: self.trigger("geo")),
            "<ctrl>+3": lambda: self.app.after(0, lambda: self.trigger("next")),
            "<ctrl>+<enter>": lambda: self.app.after(0, lambda: self.trigger("all")),
            "<ctrl>+<esc>": lambda: self.app.after(0, self.stop),
        })
        self.listener.start()

    def close(self):
        if self.listener:
            self.listener.stop()
            self.listener = None

    def stop(self):
        self.cancelled = True
        if self.app.automation.running:
            self.app.automation.stop()
        self.app.update_status("Stopped by Ctrl+Esc")

    def trigger(self, action):
        if self.busy:
            self.app.update_status("Manual action already running")
            return
        if self.app.automation.running:
            # The AutomationRunner owns Ctrl+1 through Ctrl+5 while a batch is active.
            return
        if action in ("next", "all") and not self.app.files:
            self.app.update_status("Queue drawings before using Next")
            return
        self._start_action(action, self._selected_index() if self.app.files else None)

    def _start_action(self, action, index):
        self.busy = True
        self.cancelled = False
        threading.Thread(
            target=self._run_action, args=(action, index), daemon=True
        ).start()

    def _selected_index(self):
        selection = self.app.file_listbox.curselection()
        return selection[0] if selection else 0

    def _run_action(self, action, index):
        try:
            self.app.automation._focus_trutops()
            if action in ("clean_geo", "all"):
                self._cleanup()
            if action in ("clean_geo", "geo", "all") and not self.cancelled:
                self._geo(index)
            if action in ("next", "all") and not self.cancelled:
                self._open_next(index)
        except Exception as exc:
            self.app.after(0, lambda e=exc: messagebox.showerror("Manual Macro", str(e)))
            self.app.after(0, lambda e=exc: self.app.update_status("Manual macro failed: " + str(e)))
        finally:
            self.busy = False

    def _coords(self, name):
        value = self.app.automation._resolve_location(name)
        if not value:
            raise RuntimeError("Capture '{}' in Settings first.".format(name))
        return value

    def _click(self, name, description):
        if self.cancelled:
            return
        x, y = self._coords(name)
        self.app.after(0, lambda d=description: self.app.update_status(d))
        pyautogui.moveTo(x, y, duration=0.15)
        pyautogui.click()
        self._wait(0.8)

    def _wait(self, seconds):
        for _ in range(max(1, int(seconds * 10))):
            if self.cancelled:
                return
            time.sleep(0.1)

    def _cleanup(self):
        self._click("delete_selection", "Opening cleanup")
        self._click("cleanup_delete", "Confirming preset cleanup")

    def _geo(self, index):
        item = self.app.files[index] if index is not None else None
        geo_path = Path(item["geo"]) if item else None
        if geo_path and geo_path.exists():
            raise RuntimeError("GEO already exists; not overwritten: {}".format(geo_path))

        if item:
            self.app.after(0, lambda: self.app.update_file_status(index, "processing"))
        self._click("save_selected", "Starting GEO save")
        self._click("select_top_left", "Selecting part: first corner")
        self._click("select_bottom_right", "Selecting part: second corner")
        if self.cancelled:
            return
        pyautogui.press("enter")
        self._wait(0.4)
        pyautogui.press("enter")
        self._wait(self.config.get("save_delay") or 2.0)
        if geo_path and not geo_path.exists():
            raise RuntimeError("Expected GEO was not created: {}".format(geo_path))
        if item:
            DwgProjectFilter.mark_geo_complete(item)
            self.app.after(0, lambda: self.app.update_file_status(index, "done"))
            status = "GEO saved: " + geo_path.name
        else:
            status = "Cleanup and GEO actions completed"
        self.app.after(0, lambda s=status: self.app.update_status(s))

    def _open_next(self, current_index):
        next_index = current_index + 1
        if next_index >= len(self.app.files):
            self.app.after(0, lambda: self.app.update_status("No more queued files"))
            return
        item = self.app.files[next_index]
        self._click("open_drawing", "Opening next drawing")
        if self.app.automation._dialog_kind() == "warning":
            self._click("no_save", "Discarding current drawing changes")
        self.app.automation._open_file_from_dialog(item["dwg"])
        self._wait(1.0)
        pyautogui.press("enter")
        self._wait(self.config.get("import_delay") or 3.0)
        self.app.after(0, lambda i=next_index: self._select_file(i))
        if item.get("image"):
            self.app.after(0, lambda p=item["image"]: self.app.image_viewer.show_image(p))

    def _select_file(self, index):
        self.app.file_listbox.selection_clear(0, tk.END)
        self.app.file_listbox.selection_set(index)
        self.app.file_listbox.see(index)
        self.app.update_status("Opened " + os.path.basename(self.app.files[index]["dwg"]))


class App(tk.Tk):
    """Main application window."""

    def __init__(self):
        super().__init__()

        self.title("TruTops DWG to GEO Converter v{}".format(APP_VERSION))
        self.geometry("800x920")
        self.minsize(800, 760)
        
        # Set Window Icon
        try:
            icon_path = resource_path("d2g_custom.ico")
            self.iconbitmap(icon_path)
        except Exception:
            pass # Icon not found, ignore

        # Slate satin theme colors
        self.colors = {
            "bg": "#2d3436",           # Dark slate background
            "bg_light": "#3d4448",     # Lighter slate for frames
            "fg": "#dfe6e9",           # Light gray text
            "accent": "#636e72",       # Medium slate accent
            "highlight": "#74b9ff",    # Blue highlight
            "success": "#00b894",      # Green for done
            "processing": "#fdcb6e",   # Yellow for processing
        }

        self.configure(bg=self.colors["bg"])

        # Configure ttk styles
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.style.configure("TFrame", background=self.colors["bg"])
        self.style.configure("TLabel", background=self.colors["bg"], foreground=self.colors["fg"])
        self.style.configure("TLabelframe", background=self.colors["bg_light"], foreground=self.colors["fg"])
        self.style.configure("TLabelframe.Label", background=self.colors["bg"], foreground=self.colors["fg"])
        self.style.configure("TButton", background=self.colors["accent"], foreground=self.colors["fg"], padding=6)

        self.config = Config()
        self.image_viewer = ImagePreviewWindow(self)
        self.automation = AutomationRunner(self)
        self.manual_controller = ManualController(self)
        self.files = []
        self.file_status = {}
        self.project_root = self.config.get("project_root") or ""

        self._create_widgets()
        self.manual_controller.start()
        self.protocol("WM_DELETE_WINDOW", self._close_app)

    def _create_widgets(self):
        """Create main window widgets."""
        # Header
        header_frame = tk.Frame(self, bg=self.colors["bg"], pady=15)
        header_frame.pack(fill="x")
        
        tk.Label(
            header_frame, 
            text="TruTops DWG to GEO  v{}".format(APP_VERSION),
            font=("Segoe UI", 18, "bold"),
            bg=self.colors["bg"], fg=self.colors["fg"]
        ).pack()

        # Mode Selection
        mode_frame = tk.LabelFrame(
            self, text="Automation Mode", 
            font=("Segoe UI", 10, "bold"),
            bg=self.colors["bg_light"], fg=self.colors["fg"],
            padx=15, pady=10
        )
        mode_frame.pack(fill="x", padx=15, pady=5)
        
        self.mode_var = tk.StringVar(value=self.config.get("mode") or "auto")
        
        # Auto Mode
        auto_frame = tk.Frame(mode_frame, bg=self.colors["bg_light"])
        auto_frame.pack(fill="x", pady=2)
        
        tk.Radiobutton(
            auto_frame, text="Auto Mode", variable=self.mode_var, value="auto",
            bg=self.colors["bg_light"], fg=self.colors["fg"],
            selectcolor=self.colors["bg_light"],
            activebackground=self.colors["bg_light"], activeforeground=self.colors["highlight"],
            command=self._on_mode_change
        ).pack(side="left")
        
        tk.Label(
            auto_frame, text="Delay (sec):", 
            bg=self.colors["bg_light"], fg=self.colors["fg"]
        ).pack(side="left", padx=(15, 5))
        
        self.delay_var = tk.DoubleVar(value=self.config.get("auto_delay") or 3.0)
        self.delay_spin = tk.Spinbox(
            auto_frame, from_=0.5, to=60.0, increment=0.5,
            textvariable=self.delay_var, width=5
        )
        self.delay_spin.pack(side="left")

        # Manual Mode
        manual_frame = tk.Frame(mode_frame, bg=self.colors["bg_light"])
        manual_frame.pack(fill="x", pady=2)
        
        tk.Radiobutton(
            manual_frame, text="Manual Mode", variable=self.mode_var, value="manual",
            bg=self.colors["bg_light"], fg=self.colors["fg"],
            selectcolor=self.colors["bg_light"],
            activebackground=self.colors["bg_light"], activeforeground=self.colors["highlight"],
            command=self._on_mode_change
        ).pack(side="left")
        
        tk.Label(
            manual_frame, text="(Loads the DWG, then waits for Ctrl+2 to create the GEO)",
            bg=self.colors["bg_light"], fg=self.colors["accent"],
            font=("Segoe UI", 9, "italic")
        ).pack(side="left", padx=10)

        policy_frame = tk.Frame(mode_frame, bg=self.colors["bg_light"])
        policy_frame.pack(fill="x", pady=(8, 2))
        tk.Label(
            policy_frame, text="Existing GEO:",
            bg=self.colors["bg_light"], fg=self.colors["fg"]
        ).pack(side="left")

        current_policy = self.config.get("existing_geo_policy") or "skip_existing"
        self.geo_policy_var = tk.StringVar(
            value=GEO_POLICY_NAMES.get(current_policy, "Skip existing GEO")
        )
        self.geo_policy_combo = ttk.Combobox(
            policy_frame,
            textvariable=self.geo_policy_var,
            values=list(GEO_POLICY_LABELS.keys()),
            state="readonly",
            width=31,
        )
        self.geo_policy_combo.pack(side="left", padx=(8, 0))
        self.geo_policy_combo.bind("<<ComboboxSelected>>", self._on_geo_policy_change)

        tk.Label(
            mode_frame,
            text=(
                "Recovery shortcuts: Ctrl+1 Load DWG  |  Ctrl+2 Create GEO  |  "
                "Ctrl+3 Retry  |  Ctrl+4 Skip File  |  Ctrl+5 Full File"
            ),
            bg=self.colors["bg_light"], fg=self.colors["highlight"],
            font=("Segoe UI", 9), wraplength=730, justify="left"
        ).pack(fill="x", pady=(8, 0))

        tk.Label(
            mode_frame,
            text="When stopped: Ctrl+1 Clean + GEO | Ctrl+2 GEO Only | Ctrl+3 Next Drawing | Ctrl+Enter All | Ctrl+Esc Stop",
            bg=self.colors["bg_light"], fg=self.colors["highlight"],
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w", pady=(8, 0))

        # File List
        list_frame = ttk.LabelFrame(self, text="File Queue", padding=10)
        list_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # Toolbar
        toolbar = ttk.Frame(list_frame)
        toolbar.pack(fill="x", pady=(0, 5))

        self.select_folder_btn = ttk.Button(
            toolbar, text="+ Select Project Root", command=self._add_files
        )
        self.select_folder_btn.pack(side="left")
        ttk.Button(toolbar, text="Clear List", command=self._clear_files).pack(side="left", padx=5)
        
        self.file_count_label = ttk.Label(toolbar, text="0 files")
        self.file_count_label.pack(side="right")

        # Listbox with Scrollbar
        list_scroll_frame = ttk.Frame(list_frame)
        list_scroll_frame.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_scroll_frame)
        scrollbar.pack(side="right", fill="y")

        self.file_listbox = tk.Listbox(
            list_scroll_frame,
            yscrollcommand=scrollbar.set,
            bg=self.colors["bg_light"],
            fg=self.colors["fg"],
            selectbackground=self.colors["highlight"],
            selectforeground="#000000",
            highlightthickness=0,
            bd=0
        )
        self.file_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.file_listbox.yview)

        # Status
        status_frame = ttk.Frame(self)
        status_frame.pack(fill="x", padx=15, pady=8)

        self.status_label = ttk.Label(status_frame, text="Ready - Select project folder")
        self.status_label.pack(anchor="w")

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            status_frame, variable=self.progress_var, maximum=100
        )
        self.progress_bar.pack(fill="x", pady=8)

        self.progress_label = ttk.Label(status_frame, text="0/0")
        self.progress_label.pack(anchor="e")

        # Control buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=15, pady=10)

        self.start_btn = ttk.Button(btn_frame, text="START AUTOMATION", command=self._start)
        self.start_btn.pack(side="left", padx=(0, 8))

        self.stop_btn = ttk.Button(btn_frame, text="STOP", command=self._stop, state="disabled")
        self.stop_btn.pack(side="left", padx=(0, 8))

        ttk.Button(btn_frame, text="Show Preview Window", command=self.image_viewer.deiconify).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Settings", command=self._setup_locations).pack(side="right")

    def _on_mode_change(self):
        """Save mode change."""
        self.config.set("mode", self.mode_var.get())

    def _on_geo_policy_change(self, _event=None):
        """Save the selected behavior for existing GEO files."""
        policy = GEO_POLICY_LABELS.get(self.geo_policy_var.get(), "skip_existing")
        self.config.set("existing_geo_policy", policy)

    def _add_files(self):
        """Select a project root, preflight it, and filter only new drawings."""
        folder = filedialog.askdirectory(
            title="Select Project Root",
            initialdir=self.project_root or None,
        )
        if not folder:
            return
        try:
            project_filter = DwgProjectFilter(self.config.get("oda_converter_path"))
            records = project_filter.scan(folder)
            summary = project_filter.summarize(records)
            if not records:
                messagebox.showwarning("No Files", "No source DWG files found under:\n" + folder)
                return

            details = (
                "Material folders: {material_folders}\n"
                "Source DWGs: {total}\n"
                "New: {new}\n"
                "Ready for TruTops: {ready}\n"
                "Already completed: {complete}\n"
                "Conflicts detected: {conflict}"
            ).format(**summary)

            if summary["conflict"]:
                conflict_choice = messagebox.askyesnocancel(
                    "Output Conflicts",
                    details + "\n\n"
                    "Yes: Skip conflicts\n"
                    "No: Create versioned outputs (_v2, _v3, ...)\n"
                    "Cancel: Stop without changing files",
                )
                if conflict_choice is None:
                    return
                if not conflict_choice:
                    records = project_filter.version_conflicts(records)
                    summary = project_filter.summarize(records)
                    details = (
                        "Material folders: {material_folders}\n"
                        "Source DWGs: {total}\n"
                        "New/versioned: {new}\n"
                        "Ready for TruTops: {ready}\n"
                        "Already completed: {complete}\n"
                        "Conflicts skipped: {conflict}"
                    ).format(**summary)

            if summary["new"]:
                if not project_filter.oda_path:
                    if not messagebox.askyesno(
                        "ODA File Converter Required",
                        "New DWGs need filtering, but ODA File Converter was not found.\n\n"
                        "Locate ODAFileConverter.exe now?",
                    ):
                        return
                    oda_path = filedialog.askopenfilename(
                        title="Locate ODAFileConverter.exe",
                        filetypes=[("ODA File Converter", "ODAFileConverter.exe"), ("Programs", "*.exe")],
                    )
                    if not oda_path:
                        return
                    self.config.set("oda_converter_path", oda_path)
                    project_filter = DwgProjectFilter(oda_path)
                if not messagebox.askyesno(
                    "Project Preflight",
                    details + "\n\nFilter the new DWGs now? Existing files will not be overwritten.",
                ):
                    return
            else:
                messagebox.showinfo("Project Preflight", details)

            self.project_root = folder
            self.config.set("project_root", folder)
            self.select_folder_btn.config(state="disabled")
            self.update_status("Preparing project...")
            threading.Thread(
                target=self._prepare_project,
                args=(project_filter, folder, records),
                daemon=True,
            ).start()
        except (OSError, FilterError) as exc:
            messagebox.showerror("Project Preflight", str(exc))

    def _prepare_project(self, project_filter, folder, records):
        try:
            def progress(current, total, record):
                name = os.path.basename(record["source"])
                self.after(0, lambda n=name: self.update_status("Filtering " + n))
                self.after(0, lambda c=current, t=total: self.update_progress(c, t))

            project_filter.process_new(records, progress=progress)
            refreshed = project_filter.scan(folder)
            self.after(0, lambda: self._project_ready(refreshed))
        except Exception as exc:
            self.after(0, lambda e=exc: self._project_failed(e))

    def _project_ready(self, records):
        self.select_folder_btn.config(state="normal")
        self.files = [record for record in records if record["status"] == "ready"]
        self._update_file_list()
        if self.files:
            self.file_listbox.selection_set(0)
            first_image = self.files[0].get("image")
            if first_image:
                self.image_viewer.show_image(first_image)
        self.image_viewer.deiconify()
        summary = DwgProjectFilter.summarize(records)
        self.update_status(
            "Ready: {} queued, {} completed, {} conflicts skipped".format(
                len(self.files), summary["complete"], summary["conflict"]
            )
        )
        if summary["conflict"]:
            messagebox.showwarning(
                "Outputs Not Overwritten",
                "{} source file(s) have existing or changed outputs. They were skipped."
                .format(summary["conflict"]),
            )

    def _project_failed(self, error):
        self.select_folder_btn.config(state="normal")
        self.update_status("Project preparation failed")
        messagebox.showerror("Project Preparation", str(error))

    def _clear_files(self):
        """Clear file list."""
        self.files = []
        self.file_status = {}
        self.image_viewer.clear()
        self._update_file_list()

    def _update_file_list(self):
        """Update the file listbox."""
        self.file_listbox.delete(0, tk.END)
        for i, item in enumerate(self.files):
            material = os.path.basename(item["material_dir"])
            name = "{} / {}".format(material, os.path.basename(item["dwg"]))
            has_img = " [IMG]" if item["image"] else ""
            self.file_listbox.insert(tk.END, f"  {name}{has_img}")
            self.file_status[i] = "pending"

        self.file_count_label.config(text="{} files".format(len(self.files)))
        self.update_progress(0, len(self.files) or 1)

    def _start(self):
        """Start automation."""
        if not self.files:
            messagebox.showwarning("No Files", "Add DWG files first.")
            return

        # Check locations
        required = ["open_drawing", "no_save", "save_selected", "select_top_left", "select_bottom_right"]
        missing = [loc for loc in required if not self.config.get("click_locations", loc)]

        if missing:
            if messagebox.askyesno(
                "Setup Required",
                "Click locations not set. Run Setup?"
            ):
                self._setup_locations()
                return

        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")

        for i in range(len(self.files)):
            self.update_file_status(i, "pending")

        self.automation.start(
            self.files,
            mode=self.mode_var.get(),
            delay=self.delay_var.get(),
            manual_hotkey=self.config.get("manual_hotkey") or "f1"
        )

    def _stop(self):
        """Stop automation."""
        self.automation.stop()

    def _setup_locations(self):
        """Open setup dialog."""
        LocationSetupDialog(self, self.config)

    def _test_click(self):
        """Test click at open_drawing coordinates."""
        coords = self.config.get("click_locations", "open_drawing")
        if coords:
            x, y = coords[0], coords[1]
            messagebox.showinfo("Test Click", "Will move mouse to ({}, {}) and click.\n\nClick OK, then watch the mouse.".format(x, y))
            print("TEST: Moving to ({}, {})...".format(x, y))
            pyautogui.moveTo(x, y)
            print("TEST: Mouse moved. Clicking...")
            time.sleep(0.5)
            pyautogui.click()
            print("TEST: Click done.")
        else:
            messagebox.showerror("Error", "No open_drawing coordinates set!\n\nUse Setup Locations first.")

    def _list_windows(self):
        """List all visible windows for debugging."""
        try:
            import win32gui

            windows = []
            def callback(hwnd, windows_list):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title:
                        windows_list.append(title)

            win32gui.EnumWindows(callback, windows)

            print("\n" + "=" * 50)
            print("ALL VISIBLE WINDOWS:")
            print("=" * 50)
            for w in sorted(windows):
                print("  - {}".format(w))
            print("=" * 50 + "\n")

            messagebox.showinfo("Windows Listed", "Check the console for all window titles")
        except ImportError:
            messagebox.showerror("Error", "Install pywin32: pip install pywin32")

    def update_status(self, text):
        """Update status label."""
        self.status_label.config(text=text)

    def update_progress(self, current, total):
        """Update progress bar."""
        if total > 0:
            self.progress_var.set((current / total) * 100)
            self.progress_label.config(text="{}/{}".format(current, total))

    def update_file_status(self, index, status):
        """Update file status in listbox."""
        if index >= len(self.files):
            return

        self.file_status[index] = status
        item = self.files[index]
        name = "{} / {}".format(
            os.path.basename(item["material_dir"]), os.path.basename(item["dwg"])
        )

        prefix = {
            "pending": "  ", "processing": "> ", "done": "  ", "skipped": "  "
        }.get(status, "  ")
        suffix = {
            "pending": "", "processing": " ...", "done": " [Done]", "skipped": " [Skipped]"
        }.get(status, "")

        text = "{}{}{}".format(prefix, name, suffix)

        self.file_listbox.delete(index)
        self.file_listbox.insert(index, text)

        colors = {
            "done": self.colors["success"],
            "processing": self.colors["processing"],
            "skipped": self.colors["accent"],
            "pending": self.colors["fg"]
        }
        self.file_listbox.itemconfig(index, foreground=colors.get(status, self.colors["fg"]))

        if status == "processing":
            self.file_listbox.see(index)

    def on_automation_stopped(self):
        """Called when automation stops."""
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

    def _close_app(self):
        self.manual_controller.close()
        self.automation.stop()
        self.destroy()


def main():
    """Main entry point."""
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    
    # ANSI Colors
    RED = "\033[91m"
    RESET = "\033[0m"

    print(RED + r"""
██████████      ████████████      ██████████
████    ████            ████    ████      ████
████    ████            ████    ████
████    ████    ████████████    ████    ██████
████    ████    ████            ████      ████
████    ████    ████            ████      ████
████    ████    ████████████    ████      ████
██████████      ████████████      ██████████
    """ + RESET)
    print("TruTops DWG to GEO Converter v{}".format(APP_VERSION))
    print("=" * 60)
    print("Screen size: {}".format(pyautogui.size()))
    print("")

    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
