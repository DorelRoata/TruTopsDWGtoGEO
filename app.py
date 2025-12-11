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
from pathlib import Path

import pyautogui
from PIL import Image, ImageGrab, ImageDraw, ImageTk
from pynput import mouse, keyboard

# Safety: Move mouse to top-left corner to abort
pyautogui.FAILSAFE = True

# Default configuration
DEFAULT_CONFIG = {
    "import_delay": 3.0,
    "save_delay": 2.0,
    "trutops_window_title": "TruTops",  # Window title to focus
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


class Config:
    """Handles loading and saving configuration."""

    def __init__(self):
        self.data = DEFAULT_CONFIG.copy()
        self.load()

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
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)

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
        """Show a yellow circle at click position.

        Args:
            x, y: Click coordinates
            persistent: If True, don't auto-close (for step-by-step mode)
        """
        try:
            # Create indicator window
            self.indicator_window = tk.Toplevel(self.app)
            self.indicator_window.overrideredirect(True)
            self.indicator_window.attributes('-topmost', True)

            # Try to make transparent (Windows)
            try:
                self.indicator_window.attributes('-transparentcolor', 'black')
            except:
                pass

            size = 60
            self.indicator_window.geometry("{}x{}+{}+{}".format(
                size, size, x - size // 2, y - size // 2
            ))
            self.indicator_window.configure(bg='black')

            # Draw circle
            canvas = tk.Canvas(
                self.indicator_window,
                width=size, height=size,
                bg='black', highlightthickness=0
            )
            canvas.pack()
            canvas.create_oval(5, 5, size-5, size-5, outline='yellow', width=4)

            # Auto-close after 200ms unless persistent
            if not persistent:
                self.indicator_window.after(200, self._close_indicator)

        except Exception as e:
            print("Indicator error: {}".format(e))

    def _close_indicator(self):
        """Close the indicator window."""
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
        self.config = config
        self.title("Setup Click Locations")
        self.geometry("550x620")
        self.minsize(550, 620)
        self.transient(parent)
        self.grab_set()

        self.locations = {
            "open_drawing": ("Open Drawing", "Click the 'Open Drawing' button/menu"),
            "no_save": ("No Button", "Click 'No' when asked to save modifications"),
            "save_selected": ("Save Selected", "Click 'Save Selected to GEO' button"),
            "select_top_left": ("Selection Top-Left", "Click TOP-LEFT corner of part"),
            "select_bottom_right": ("Selection Bottom-Right", "Click BOTTOM-RIGHT corner"),
        }

        self.captured = {}
        self._create_widgets()
        self._update_status()

    def _create_widgets(self):
        """Create dialog widgets."""
        # Instructions
        instr_frame = ttk.LabelFrame(self, text="Instructions", padding=10)
        instr_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(
            instr_frame,
            text="Click CAPTURE, then click the location in TrueTops within 5 seconds.\n"
                 "Make sure TrueTops is visible before capturing.",
            wraplength=450
        ).pack()

        # Location captures
        self.status_labels = {}
        self.capture_buttons = {}

        for key, (name, desc) in self.locations.items():
            frame = ttk.LabelFrame(self, text=name, padding=10)
            frame.pack(fill="x", padx=10, pady=5)

            row = ttk.Frame(frame)
            row.pack(fill="x")

            btn = ttk.Button(
                row, text="CAPTURE",
                command=lambda k=key: self._start_capture(k)
            )
            btn.pack(side="left", padx=5)
            self.capture_buttons[key] = btn

            status = ttk.Label(row, text="Not set")
            status.pack(side="left", padx=10)
            self.status_labels[key] = status

        # Countdown label
        self.countdown_label = ttk.Label(self, text="", font=("Arial", 14, "bold"))
        self.countdown_label.pack(pady=10)

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(btn_frame, text="Save", command=self._save).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="left", padx=5)

    def _update_status(self):
        """Update status labels."""
        for key in self.locations:
            coords = self.config.get("click_locations", key)
            if coords:
                self.status_labels[key].config(
                    text="Set: ({}, {})".format(coords[0], coords[1]),
                    foreground="green"
                )
                self.captured[key] = True
            else:
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
            self.config.set("click_locations", location_key, [x, y])
            self.captured[location_key] = True
            self.after(0, lambda: self._capture_complete(location_key, x, y))
        else:
            self.after(0, lambda: self._capture_complete(location_key, None, None))

    def _capture_complete(self, location_key, x, y):
        """Handle capture completion."""
        self.deiconify()
        self.countdown_label.config(text="")

        for btn in self.capture_buttons.values():
            btn.config(state="normal")

        if x is not None:
            self.status_labels[location_key].config(
                text="Set: ({}, {})".format(x, y),
                foreground="green"
            )

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
        self.step_by_step = False
        self.dry_run = False

    def start(self, files, dry_run=False, step_by_step=False):
        """Start processing files."""
        self.running = True
        self.escape_pressed = False
        self.files = files
        self.dry_run = dry_run
        self.step_by_step = step_by_step
        self.current_index = self.config.get("last_processed_index") or 0

        # Ask if resuming
        if self.current_index > 0 and self.current_index < len(files):
            if not messagebox.askyesno(
                "Resume?",
                "Resume from file {}?".format(self.current_index + 1)
            ):
                self.current_index = 0
        else:
            self.current_index = 0

        # Start ESC listener
        self._start_escape_listener()

        threading.Thread(target=self._run, daemon=True).start()

    def stop(self):
        """Stop processing."""
        self.running = False
        self._stop_escape_listener()
        self.app.update_status("Stopped")

    def _start_escape_listener(self):
        """Start listening for ESC key."""
        def on_press(key):
            if key == keyboard.Key.esc:
                print("\n[ESC PRESSED] Aborting automation...")
                self.escape_pressed = True
                self.running = False
                return False

        self.keyboard_listener = keyboard.Listener(on_press=on_press)
        self.keyboard_listener.start()

    def _stop_escape_listener(self):
        """Stop ESC listener."""
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None

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
            pyautogui.moveTo(x, y)
            time.sleep(0.1)
            pyautogui.click()
            time.sleep(3.0)
        else:
            print("  (dry run)")

    def _press(self, key, description=""):
        """Press key - simple."""
        print("[KEY] {} - {}".format(key, description))

        if not self.dry_run:
            pyautogui.press(key)
            time.sleep(3.0)
        else:
            print("  (dry run)")

    def _hotkey(self, *keys, description=""):
        """Press hotkey - simple."""
        key_str = "+".join(keys)
        print("[HOTKEY] {} - {}".format(key_str, description))

        if not self.dry_run:
            pyautogui.hotkey(*keys)
            time.sleep(3.0)
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

        for i in range(self.current_index, total):
            if not self.running or self.escape_pressed:
                break

            file_path = self.files[i]
            file_name = os.path.basename(file_path)  # Just the filename with extension
            self.current_index = i
            self.config.set("last_processed_index", i)

            # Update UI
            self.app.after(0, lambda i=i: self.app.update_file_status(i, "processing"))
            self.app.after(0, lambda f=file_name, i=i, t=total: self.app.update_status(
                "Processing {} ({}/{}) - ESC to abort".format(f, i + 1, t)
            ))
            self.app.after(0, lambda i=i, t=total: self.app.update_progress(i, t))

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

                # Step 3: Copy filename (with extension only) to clipboard and paste it
                # The filename box is already selected after clicking No
                self._copy_to_clipboard(file_name)  # Just filename, not full path
                print("[CLIPBOARD] Copied: {}".format(file_name))

                self._hotkey('ctrl', 'v', description="Paste filename")
                time.sleep(0.3)

                # Step 4: Open drawing
                self._press('enter', "Open drawing")
                time.sleep(1.0)

                # Step 5: Confirm import settings
                self._press('enter', "Confirm import settings")
                time.sleep(import_delay)

                if not self.running:
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

                # Step 9: Enter for warning dialog (may not appear, but safe to press)
                self._press('enter', "Warning dialog (if any)")
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
        self._stop_escape_listener()

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
        self.geometry("550x650")
        self.minsize(550, 650)

        self.config = Config()
        self.automation = AutomationRunner(self)
        self.files = []
        self.file_status = {}

        self._create_widgets()

    def _create_widgets(self):
        """Create main window widgets."""
        # Header
        header = ttk.Label(
            self,
            text="TruTops DWG to GEO Converter",
            font=("Arial", 14, "bold")
        )
        header.pack(pady=10)

        # File list frame
        list_frame = ttk.LabelFrame(self, text="DWG Files to Process", padding=10)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Add files button
        btn_row = ttk.Frame(list_frame)
        btn_row.pack(fill="x", pady=(0, 5))

        ttk.Button(btn_row, text="Add Files", command=self._add_files).pack(side="left")
        ttk.Button(btn_row, text="Clear", command=self._clear_files).pack(side="left", padx=5)

        self.file_count_label = ttk.Label(btn_row, text="0 files")
        self.file_count_label.pack(side="right")

        # Listbox with scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side="right", fill="y")

        self.file_listbox = tk.Listbox(
            list_container,
            yscrollcommand=scrollbar.set,
            font=("Consolas", 10),
            selectmode="single"
        )
        self.file_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.file_listbox.yview)

        # Status
        status_frame = ttk.Frame(self)
        status_frame.pack(fill="x", padx=10, pady=5)

        self.status_label = ttk.Label(status_frame, text="Ready - Add DWG files to start")
        self.status_label.pack(anchor="w")

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            status_frame, variable=self.progress_var, maximum=100
        )
        self.progress_bar.pack(fill="x", pady=5)

        self.progress_label = ttk.Label(status_frame, text="0/0")
        self.progress_label.pack(anchor="e")

        # Control buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=10, pady=10)

        self.start_btn = ttk.Button(btn_frame, text="START", command=self._start)
        self.start_btn.pack(side="left", padx=5)

        self.stop_btn = ttk.Button(btn_frame, text="STOP", command=self._stop, state="disabled")
        self.stop_btn.pack(side="left", padx=5)

        ttk.Button(btn_frame, text="Setup Locations", command=self._setup_locations).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="List Windows", command=self._list_windows).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="TEST CLICK", command=self._test_click).pack(side="left", padx=5)

        # Options
        options_frame = ttk.Frame(self)
        options_frame.pack(fill="x", padx=10, pady=5)

        self.dry_run_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame, text="Dry Run (no clicks)",
            variable=self.dry_run_var
        ).pack(anchor="w")

        self.step_by_step_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame, text="Step-by-step (confirm each action in console)",
            variable=self.step_by_step_var
        ).pack(anchor="w")

        # Info
        info_frame = ttk.LabelFrame(self, text="Workflow (Press ESC to abort)", padding=5)
        info_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(
            info_frame,
            text="1. Open Drawing (click)  2. No  3. Paste filename\n"
                 "4. Enter (open)  5. Enter (import)  6. Save Selected\n"
                 "7. TL corner  8. BR corner  9. Enter  10. Enter (save)",
            font=("Consolas", 9), foreground="gray"
        ).pack(anchor="w")

    def _add_files(self):
        """Add DWG files."""
        files = filedialog.askopenfilenames(
            title="Select DWG Files",
            filetypes=[("DWG files", "*.dwg"), ("All files", "*.*")]
        )
        if files:
            for f in files:
                if f not in self.files:
                    self.files.append(f)

            self._update_file_list()

    def _clear_files(self):
        """Clear file list."""
        self.files = []
        self.file_status = {}
        self._update_file_list()

    def _update_file_list(self):
        """Update the file listbox."""
        self.file_listbox.delete(0, tk.END)
        for i, f in enumerate(self.files):
            name = os.path.basename(f)
            self.file_listbox.insert(tk.END, "  {}".format(name))
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
            dry_run=self.dry_run_var.get(),
            step_by_step=self.step_by_step_var.get()
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
            print("TEST: Moving to ({}, {}) and clicking...".format(x, y))
            pyautogui.moveTo(x, y)
            time.sleep(0.5)
            pyautogui.click()
            print("TEST: Done")
        else:
            print("No open_drawing coordinates set")

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
        name = os.path.basename(self.files[index])

        prefix = {"pending": "  ", "processing": "> ", "done": "  "}.get(status, "  ")
        suffix = {"pending": "", "processing": " ...", "done": " [Done]"}.get(status, "")

        text = "{}{}{}".format(prefix, name, suffix)

        self.file_listbox.delete(index)
        self.file_listbox.insert(index, text)

        colors = {"done": "green", "processing": "blue", "pending": "black"}
        self.file_listbox.itemconfig(index, foreground=colors.get(status, "black"))

        if status == "processing":
            self.file_listbox.see(index)

    def on_automation_stopped(self):
        """Called when automation stops."""
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")


def main():
    """Main entry point."""
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
