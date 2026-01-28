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
from pathlib import Path

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
    "trutops_window_title": "TruTops",  # Window title to focus
    "mode": "auto",                     # auto or manual
    "auto_delay": 3,                    # Seconds to wait in auto mode
    "manual_hotkey": "f2",              # Hotkey for manual trigger
    "click_locations": {
        "open_drawing": [549, 114],          # Open Drawing button (not Ctrl+O)
        "no_save": [3009, 672],              # "No" button - don't save modifications
        "save_selected": [680, 126],         # Save Selected to GEO button
        "select_top_left": [75, 209],        # Top-left corner of selection box
        "select_bottom_right": [3350, 1867], # Bottom-right corner of selection box
    },
    "last_processed_index": 0
}

CONFIG_FILE = "config.json"
SCREENSHOTS_DIR = "ScreenShots"


class ImagePreviewWindow(tk.Toplevel):
    """Window to display the part preview on a second screen."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Part Preview")
        self.geometry("600x600")
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

    def show_image(self, image_path):
        """Load and scale image to fit window."""
        self.deiconify()
        
        if not os.path.exists(image_path):
            self.status_label.config(text="Image not found:\n" + os.path.basename(image_path))
            self.status_label.place(relx=0.5, rely=0.5, anchor="center")
            self.image_label.configure(image='')
            return

        try:
            # Load and resize
            img = Image.open(image_path)
            
            # Get window size
            win_width = self.winfo_width()
            win_height = self.winfo_height()
            
            if win_width < 100: win_width = 600
            if win_height < 100: win_height = 600
            
            # Calculate input aspect ratio
            img_ratio = img.width / img.height
            win_ratio = win_width / win_height
            
            if img_ratio > win_ratio:
                # limited by width
                target_width = win_width
                target_height = int(win_width / img_ratio)
            else:
                # limited by height
                target_height = win_height
                target_width = int(win_height * img_ratio)
                
            img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            
            self.current_image = ImageTk.PhotoImage(img)
            self.image_label.configure(image=self.current_image)
            self.status_label.place_forget()
            
        except Exception as e:
            print(f"Error loading image: {e}")
            self.status_label.config(text=f"Error loading image")
            self.status_label.place(relx=0.5, rely=0.5, anchor="center")

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
    def find_button(image_path, fallback_coords=None):
        """Find a button on screen using image detection."""
        if not image_path or not os.path.exists(image_path):
            if fallback_coords:
                return tuple(fallback_coords), "Saved coordinates (no image)"
            return None, "Not found (no image file)"

        strategies = [
            ("High confidence", {"confidence": 0.8}),
            ("Medium confidence", {"confidence": 0.6}),
            ("Low confidence", {"confidence": 0.5}),
        ]

        for name, params in strategies:
            try:
                location = pyautogui.locateOnScreen(image_path, **params)
                if location:
                    return pyautogui.center(location), name
            except Exception:
                continue

        # Try grayscale
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=0.6, grayscale=True)
            if location:
                return pyautogui.center(location), "Grayscale match"
        except Exception:
            pass

        if fallback_coords:
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


class LocationSetupDialog(tk.Toplevel):
    """Dialog for capturing click locations."""

    def __init__(self, parent, config):
        super().__init__(parent)
        self.parent = parent
        self.config = config
        self.title("Setup Click Locations")
        self.geometry("650x580")
        self.minsize(650, 580)
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
        }

        self.captured = {}
        self._create_widgets()
        self._update_status()

    def _create_widgets(self):
        """Create dialog widgets."""
        # Instructions
        instr = tk.Label(
            self,
            text="Click CAPTURE, then click the button in TruTops within 5 seconds.",
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
            if coords:
                self.status_labels[key].config(
                    text="({}, {})".format(coords[0], coords[1]),
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
            self.config.set("click_locations", location_key, [x, y])
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
            self.status_labels[location_key].config(
                text="({}, {})".format(x, y),
                fg=self.colors["success"]
            )

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
                self.config.set("click_locations", location_key, [x, y])
                self.status_labels[location_key].config(
                    text="({}, {})".format(x, y),
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
        self.escape_pressed = False
        self.keyboard_listener = None
        self.manual_trigger = False
        self.dry_run = False
        self.step_by_step = False

    def start(self, files, mode="auto", delay=3.0, manual_hotkey="f1"):
        """Start processing files."""
        self.running = True
        self.escape_pressed = False
        self.files = files # List of dicts: {"dwg": path, "image": path}
        self.mode = mode
        self.delay = delay
        self.manual_hotkey = manual_hotkey
        
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
        self._stop_listeners()
        self.app.update_status("Stopped")

    def _start_listeners(self):
        """Start listening for keyboard events."""
        def on_press(key):
            # Check ESC
            if key == keyboard.Key.esc:
                print("\n[ESC PRESSED] Aborting automation...")
                self.escape_pressed = True
                self.running = False
                # Signal manual trigger too just to break wait loop if stuck
                self.manual_trigger = True 
                return False
            
            # Check Manual Hotkey
            try:
                k = None
                if isinstance(key, keyboard.KeyCode):
                    k = key.char
                elif isinstance(key, keyboard.Key):
                    k = key.name
                
                # Simple check - could be improved for modifiers
                if str(k).lower() == self.manual_hotkey.lower():
                    print("[MANUAL TRIGGER] Hotkey pressed!")
                    self.manual_trigger = True
            except:
                pass

        self.keyboard_listener = keyboard.Listener(on_press=on_press)
        self.keyboard_listener.start()

    def _stop_listeners(self):
        """Stop listeners."""
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None

    def _wait_for_trigger(self):
        """Wait based on mode."""
        if not self.running: return False
        
        if self.mode == "auto":
            print(f"[AUTO] Waiting {self.delay}s...")
            # Break sleep into small chunks to remain responsive
            for _ in range(int(self.delay * 10)):
                if not self.running: return False
                time.sleep(0.1)
            return True
        else:
            print(f"[MANUAL] Waiting for {self.manual_hotkey}...")
            self.app.update_status(f"WAITING FOR TRIGGER ({self.manual_hotkey.upper()}) - ESC to abort")
            self.manual_trigger = False
            
            while not self.manual_trigger:
                if not self.running: return False
                time.sleep(0.1)
            
            print("[MANUAL] Trigger received")
            return True

    def _focus_trutops(self):
        """Try to focus TrueTops window."""
        try:
            title = self.config.get("trutops_window_title")
            if not title:
                # No window title configured - skip focusing
                print("[FOCUS] Skipped (no window configured)")
                return True

            # Try pyautogui first
            windows = pyautogui.getWindowsWithTitle(title)
            if windows:
                win = windows[0]
                try:
                    # Try multiple activation methods
                    win.minimize()
                    win.restore()
                    win.activate()
                    time.sleep(0.3)
                    print("[FOCUS] Activated: {}".format(win.title))
                    return True
                except Exception as e:
                    print("[FOCUS] pyautogui activate failed: {}".format(e))

            # Fallback: Try win32gui directly
            try:
                import win32gui
                import win32con

                def find_window(hwnd, windows_list):
                    if win32gui.IsWindowVisible(hwnd):
                        window_title = win32gui.GetWindowText(hwnd)
                        if title.lower() in window_title.lower():
                            windows_list.append((hwnd, window_title))

                found = []
                win32gui.EnumWindows(find_window, found)

                if found:
                    hwnd, win_title = found[0]
                    # Force to foreground
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(hwnd)
                    time.sleep(0.3)
                    print("[FOCUS] win32gui activated: {}".format(win_title))
                    return True
                else:
                    # List all windows for debugging
                    all_windows = []
                    win32gui.EnumWindows(lambda h, l: l.append(win32gui.GetWindowText(h)) if win32gui.GetWindowText(h) else None, all_windows)
                    print("[FOCUS] Window '{}' not found!".format(title))
                    print("[FOCUS] Available windows containing 'tru':")
                    for w in all_windows:
                        if 'tru' in w.lower():
                            print("  - {}".format(w))
                    return False

            except ImportError:
                print("[FOCUS] win32gui not available - install pywin32: pip install pywin32")
                return False

        except Exception as e:
            print("[FOCUS] Error: {}".format(e))
            return False

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
        """Click at position - simple screen click."""
        print("[CLICK] ({}, {}) - {}".format(x, y, description))

        if not self.dry_run:
            # Show where we are going
            self.indicator.show_highlight(x, y, duration=500)
            pyautogui.moveTo(x, y, duration=0.15)
            
            # Brief pause to show the highlight/location
            time.sleep(0.1)
            
            # Show click and execute
            self.indicator.show_click(x, y)
            pyautogui.click()
            time.sleep(1.5) # Wait for UI to react
        else:
            print("  (dry run)")

    def _press(self, key, description=""):
        """Press key - simple."""
        print("[KEY] {} - {}".format(key, description))

        if not self.dry_run:
            pyautogui.press(key)
            time.sleep(1.0)
        else:
            print("  (dry run)")

    def _hotkey(self, *keys, description=""):
        """Press hotkey - simple."""
        key_str = "+".join(keys)
        print("[HOTKEY] {} - {}".format(key_str, description))

        if not self.dry_run:
            pyautogui.hotkey(*keys)
            time.sleep(1.0)
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

    def _run(self):
        """Main automation loop."""
        import_delay = self.config.get("import_delay") or 3.0
        save_delay = self.config.get("save_delay") or 2.0

        # Get all click locations
        open_drawing_pos = self.config.get("click_locations", "open_drawing")
        no_save_pos = self.config.get("click_locations", "no_save")
        save_selected_pos = self.config.get("click_locations", "save_selected")
        select_tl_pos = self.config.get("click_locations", "select_top_left")
        select_br_pos = self.config.get("click_locations", "select_bottom_right")

        total = len(self.files)

        # Focus TrueTops first
        print("\n" + "=" * 50)
        print("STARTING AUTOMATION - Press ESC to abort")
        print("=" * 50)

        self._focus_trutops()
        time.sleep(0.5)
        
        # Ensure image viewer is up
        self.app.after(0, self.app.image_viewer.deiconify)

        for i in range(self.current_index, total):
            if not self.running or self.escape_pressed:
                break

            item = self.files[i]
            file_path = item["dwg"]
            img_path = item["image"]
            file_name = os.path.basename(file_path) 
            
            self.current_index = i
            self.config.set("last_processed_index", i)

            # Update UI
            self.app.after(0, lambda i=i: self.app.update_file_status(i, "processing"))
            self.app.after(0, lambda f=file_name, i=i, t=total: self.app.update_status(
                "Processing {} ({}/{}) - ESC to abort".format(f, i + 1, t)
            ))
            self.app.after(0, lambda i=i, t=total: self.app.update_progress(i, t))
            
            # SHOW IMAGE
            if img_path:
                self.app.after(0, lambda p=img_path: self.app.image_viewer.show_image(p))
            else:
                 self.app.after(0, self.app.image_viewer.clear)

            try:
                print("\n--- File {}/{}: {} ---".format(i + 1, total, file_name))

                # Step 1: Click Open Drawing button
                if open_drawing_pos:
                    self._click(open_drawing_pos[0], open_drawing_pos[1], "Open Drawing")
                    time.sleep(0.5)

                if not self.running:
                    break

                # Step 2: Click "No" - don't save modifications
                if no_save_pos:
                    self._click(no_save_pos[0], no_save_pos[1], "No (don't save)")
                    time.sleep(0.5)

                # Step 3: Copy full file path to clipboard and paste it
                # The filename box is already selected after clicking No
                # IMPORTANT: Use full path to ensure we open the file from Filtered_DWGs
                self._copy_to_clipboard(file_path) 
                print("[CLIPBOARD] Copied: {}".format(file_path))

                self._hotkey('ctrl', 'v', description="Paste file path")
                time.sleep(0.3)

                # Step 4: Open drawing
                self._press('enter', "Open drawing")
                time.sleep(1.0)

                # Step 5: Confirm import settings
                self._press('enter', "Confirm import settings")
                time.sleep(import_delay)

                if not self.running:
                    break
                    
                # === PAUSE POINT FOR MANUAL/AUTO MODE ===
                # This is where the user checks the preview against TruTops
                if not self._wait_for_trigger():
                    break

                # Step 6: Click Save Selected to GEO
                if save_selected_pos:
                    self._click(save_selected_pos[0], save_selected_pos[1], "Save Selected to GEO")
                    time.sleep(0.5)

                # Step 7: Click top-left corner of selection box
                if select_tl_pos:
                    self._click(select_tl_pos[0], select_tl_pos[1], "Selection top-left")
                    time.sleep(0.3)

                # Step 8: Click bottom-right corner of selection box
                if select_br_pos:
                    self._click(select_br_pos[0], select_br_pos[1], "Selection bottom-right")
                    time.sleep(0.5)

                # Step 9: Enter for warning dialog
                self._press('enter', "Warning dialog")
                time.sleep(0.3)

                # Step 10: Enter to save file
                self._press('enter', "Save file")
                time.sleep(save_delay)

                # Mark complete
                self.app.after(0, lambda i=i: self.app.update_file_status(i, "done"))
                print("Done!")

            except Exception as e:
                print("ERROR: {}".format(e))
                self.app.after(0, lambda e=e: self.app.update_status("Error: {}".format(e)))
                self.running = False
                break

        # Cleanup
        self._stop_listeners()

        if self.escape_pressed:
            self.app.after(0, lambda: self.app.update_status("Aborted by user (ESC)"))
            self.app.after(0, lambda: messagebox.showinfo("Aborted", "Automation stopped by ESC key"))
        elif self.running:
            self.config.set("last_processed_index", 0)
            self.app.after(0, lambda: self.app.update_status("Complete!"))
            self.app.after(0, lambda: self.app.update_progress(total, total))
            self.app.after(0, lambda: messagebox.showinfo("Done", "Processed {} files!".format(total)))

        self.running = False
        self.app.after(0, self.app.on_automation_stopped)


class App(tk.Tk):
    """Main application window."""

    def __init__(self):
        super().__init__()

        self.title("TruTops DWG to GEO Converter")
        self.geometry("800x850")
        self.minsize(800, 850)

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
        self.files = []
        self.file_status = {}

        self._create_widgets()

    def _create_widgets(self):
        """Create main window widgets."""
        # Header
        header_frame = tk.Frame(self, bg=self.colors["bg"], pady=15)
        header_frame.pack(fill="x")
        
        tk.Label(
            header_frame, 
            text="TruTops DWG to GEO", 
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
        
        hk = self.config.get("manual_hotkey") or "F1"
        tk.Label(
            manual_frame, text=f"(Press '{hk.upper()}' to continue)", 
            bg=self.colors["bg_light"], fg=self.colors["accent"],
            font=("Segoe UI", 9, "italic")
        ).pack(side="left", padx=10)

        # File List
        list_frame = ttk.LabelFrame(self, text="File Queue", padding=10)
        list_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # Toolbar
        toolbar = ttk.Frame(list_frame)
        toolbar.pack(fill="x", pady=(0, 5))

        ttk.Button(toolbar, text="+ Select Folder", command=self._add_files).pack(side="left")
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

    def _add_files(self):
        """Select project folder and find files."""
        folder = filedialog.askdirectory(title="Select Folder (Project Root or Filtered_DWGs)")
        if not folder:
            return

        # Determine logic based on selection
        base_name = os.path.basename(folder)
        
        if base_name == "Filtered_DWGs":
            # User selected the Filtered_DWGs folder directly
            dwg_dir = folder
            # Assume images are in sibling folder
            img_dir = os.path.join(os.path.dirname(folder), "DWG_Images")
        else:
            # User likely selected project root
            potential_dwg = os.path.join(folder, "Filtered_DWGs")
            if os.path.exists(potential_dwg):
                dwg_dir = potential_dwg
                img_dir = os.path.join(folder, "DWG_Images")
            else:
                # Fallback: Assume simple folder with dwgs
                dwg_dir = folder
                img_dir = folder  # Or maybe None? Let's check same folder for now

        print(f"[FILE SCAN] DWG Dir: {dwg_dir}")
        print(f"[FILE SCAN] IMG Dir: {img_dir}")

        new_files = []
        try:
            # os.listdir is faster than glob for simple extension check
            for f in os.listdir(dwg_dir):
                if f.lower().endswith(".dwg"):
                    full_path = os.path.join(dwg_dir, f)
                    
                    # Look for corresponding image
                    name_base = os.path.splitext(f)[0]
                    img_path = None
                    
                    # Try common image extensions
                    # Check img_dir first
                    if os.path.exists(img_dir):
                        for ext in [".png", ".jpg", ".jpeg"]:
                            candidate = os.path.join(img_dir, name_base + ext)
                            if os.path.exists(candidate):
                                img_path = candidate
                                break
                    
                    # Store tuple: (dwg_path, image_path)
                    new_files.append({"dwg": full_path, "image": img_path})
            
            if not new_files:
                messagebox.showwarning("No Files", "No DWG files found in:\n" + dwg_dir)
                return
                
            self.files = new_files
            self._update_file_list()
            self.image_viewer.deiconify() # Show viewer so they can position it
            
        except Exception as e:
            messagebox.showerror("Error", f"Error scanning folder: {e}")

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
            name = os.path.basename(item["dwg"])
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
        name = os.path.basename(self.files[index]["dwg"])

        prefix = {"pending": "  ", "processing": "> ", "done": "  "}.get(status, "  ")
        suffix = {"pending": "", "processing": " ...", "done": " [Done]"}.get(status, "")

        text = "{}{}{}".format(prefix, name, suffix)

        self.file_listbox.delete(index)
        self.file_listbox.insert(index, text)

        colors = {
            "done": self.colors["success"],
            "processing": self.colors["processing"],
            "pending": self.colors["fg"]
        }
        self.file_listbox.itemconfig(index, foreground=colors.get(status, self.colors["fg"]))

        if status == "processing":
            self.file_listbox.see(index)

    def on_automation_stopped(self):
        """Called when automation stops."""
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")


def main():
    """Main entry point."""
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

    print("=" * 50)
    print("TruTops DWG to GEO Converter")
    print("=" * 50)
    print("Screen size: {}".format(pyautogui.size()))
    print("")

    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
