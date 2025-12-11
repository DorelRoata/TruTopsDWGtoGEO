# -*- coding: utf-8 -*-
"""
TruTops DWG to GEO Converter
A GUI automation tool for batch converting DWG files to GEO format.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import threading
import time
from pathlib import Path

import pyautogui
from PIL import Image, ImageGrab
from pynput import mouse

# Safety: Move mouse to top-left corner to abort
pyautogui.FAILSAFE = True

# Default configuration
DEFAULT_CONFIG = {
    "laser_folder": "laser",
    "import_delay": 3.0,
    "save_delay": 2.0,
    "click_locations": {
        "file_list": None,        # Where to click to focus file list in Open dialog
        "working_area": None,     # Click to highlight working area
        "deselect": None,         # Click to deselect
    },
    "buttons": {
        "save_selected": {
            "image": "ScreenShots/Save Selection.png",
            "fallback_coords": None
        },
        "save_to_geo": {
            "image": "screenshots/save_to_geo.png",
            "fallback_coords": None
        },
        "ok": {
            "image": "screenshots/ok.png",
            "fallback_coords": None
        }
    },
    "last_processed_index": 0
}

CONFIG_FILE = "config.json"
SCREENSHOTS_DIR = "screenshots"


class ClickIndicator:
    """Shows a yellow circle where clicks happen."""

    def __init__(self):
        self.overlay = None
        self.canvas = None

    def show_at(self, x, y, duration=0.3):
        """Show yellow circle at position for duration seconds."""
        def _show():
            # Create overlay window
            self.overlay = tk.Tk()
            self.overlay.overrideredirect(True)
            self.overlay.attributes('-topmost', True)
            self.overlay.attributes('-transparentcolor', 'black')
            self.overlay.configure(bg='black')

            # Size and position
            size = 50
            self.overlay.geometry("{}x{}+{}+{}".format(
                size, size, x - size // 2, y - size // 2
            ))

            # Draw yellow circle
            self.canvas = tk.Canvas(
                self.overlay,
                width=size,
                height=size,
                bg='black',
                highlightthickness=0
            )
            self.canvas.pack()
            self.canvas.create_oval(
                5, 5, size - 5, size - 5,
                outline='yellow',
                width=4
            )

            # Auto-close after duration
            self.overlay.after(int(duration * 1000), self._close)
            self.overlay.mainloop()

        # Run in separate thread to not block
        threading.Thread(target=_show, daemon=True).start()

    def _close(self):
        """Close the overlay."""
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None


def click_with_indicator(x, y, indicator=None):
    """Click at position and show yellow indicator."""
    if indicator:
        indicator.show_at(x, y)
    time.sleep(0.1)  # Brief pause for indicator to appear
    pyautogui.click(x, y)


def press_with_log(key, description=""):
    """Press a key and log the action."""
    print("[KEY] {} - {}".format(key, description))
    pyautogui.press(key)


def hotkey_with_log(keys, description=""):
    """Press hotkey combination and log the action."""
    print("[HOTKEY] {} - {}".format("+".join(keys), description))
    pyautogui.hotkey(*keys)


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
                    # Merge with defaults
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
        """
        Try multiple strategies to find a button on screen.
        Returns (center_point, strategy_name) or (None, "Not found").
        """
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

        # Final fallback: saved coordinates
        if fallback_coords:
            return tuple(fallback_coords), "Saved coordinates"

        return None, "Not found"


class LocationSetupDialog(tk.Toplevel):
    """Dialog for capturing click locations."""

    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        self.title("Setup Click Locations")
        self.geometry("500x500")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.locations = {
            "file_list": ("File List (in Open dialog)", "Click on the file list area"),
            "working_area": ("Working Area", "Click to highlight working area"),
            "deselect": ("Deselect Button", "Click to deselect"),
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
            text="Click CAPTURE for each location, then click the corresponding\n"
                 "button/area in TrueTops within 5 seconds.",
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

            ttk.Label(row, text=desc, foreground="gray").pack(side="right")

        # Countdown label
        self.countdown_label = ttk.Label(self, text="", font=("Arial", 14, "bold"))
        self.countdown_label.pack(pady=10)

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(btn_frame, text="Save", command=self._save).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="left", padx=5)

    def _update_status(self):
        """Update status labels based on existing config."""
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
        """Start the capture countdown."""
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
                text="Click the location in {}...".format(i)
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
        else:
            messagebox.showerror("Capture Failed", "Timeout - no click detected")

    def _save(self):
        """Save and close dialog."""
        missing = [name for key, (name, _) in self.locations.items()
                   if not self.captured.get(key)]

        if missing:
            if not messagebox.askyesno(
                "Incomplete Setup",
                "These locations are not set:\n- {}\n\nContinue anyway?".format(
                    "\n- ".join(missing)
                )
            ):
                return

        self.config.save()
        self.destroy()


class AutomationRunner:
    """Handles the automation process."""

    def __init__(self, app):
        self.app = app
        self.config = app.config
        self.running = False
        self.paused = False
        self.current_index = 0
        self.indicator = ClickIndicator()

    def start(self, files, dry_run=False):
        """Start processing files."""
        self.running = True
        self.paused = False
        self.files = files
        self.dry_run = dry_run
        self.current_index = self.config.get("last_processed_index") or 0

        # Ask if resuming
        if self.current_index > 0 and self.current_index < len(files):
            if messagebox.askyesno(
                "Resume?",
                "Previous session stopped at file {}.\nResume from there?".format(
                    self.current_index + 1
                )
            ):
                pass
            else:
                self.current_index = 0
        else:
            self.current_index = 0

        threading.Thread(target=self._run, daemon=True).start()

    def stop(self):
        """Stop processing."""
        self.running = False
        self.app.update_status("Stopped by user")

    def _click(self, x, y, description=""):
        """Click with indicator and logging."""
        print("[CLICK] ({}, {}) - {}".format(x, y, description))
        if not self.dry_run:
            self.indicator.show_at(x, y)
            time.sleep(0.15)
            pyautogui.click(x, y)
        else:
            print("  (dry run - skipped)")

    def _press(self, key, description=""):
        """Press key with logging."""
        print("[KEY] {} - {}".format(key, description))
        if not self.dry_run:
            pyautogui.press(key)
        else:
            print("  (dry run - skipped)")

    def _hotkey(self, *keys, description=""):
        """Press hotkey with logging."""
        print("[HOTKEY] {} - {}".format("+".join(keys), description))
        if not self.dry_run:
            pyautogui.hotkey(*keys)
        else:
            print("  (dry run - skipped)")

    def _click_button_by_image(self, button_key, description):
        """Find and click a button using image detection. Returns True on success."""
        image_path = self.config.get("buttons", button_key, "image")
        fallback = self.config.get("buttons", button_key, "fallback_coords")

        pos, strategy = ButtonDetector.find_button(image_path, fallback)

        if pos:
            print("[IMAGE DETECT] Found '{}' via {} at ({}, {})".format(
                description, strategy, pos[0], pos[1]))
            self._click(pos[0], pos[1], description)
            return True
        else:
            print("[IMAGE DETECT] Could not find '{}'".format(description))
            return False

    def _run(self):
        """Main automation loop."""
        import_delay = self.config.get("import_delay") or 3.0
        save_delay = self.config.get("save_delay") or 2.0

        # Get click locations
        file_list_pos = self.config.get("click_locations", "file_list")
        working_area_pos = self.config.get("click_locations", "working_area")
        deselect_pos = self.config.get("click_locations", "deselect")

        total = len(self.files)

        for i in range(self.current_index, total):
            if not self.running:
                break

            file = self.files[i]
            self.current_index = i

            # Save progress
            self.config.set("last_processed_index", i)

            # Update UI
            self.app.after(0, lambda i=i, f=file: self.app.update_file_status(i, "processing"))
            self.app.after(0, lambda f=file, i=i, t=total: self.app.update_status(
                "Processing {} ({}/{})...".format(f, i + 1, t)
            ))
            self.app.after(0, lambda i=i, t=total: self.app.update_progress(i, t))

            try:
                print("\n" + "=" * 50)
                print("Processing file {}/{}: {}".format(i + 1, total, file))
                print("=" * 50)

                # Step 1: Open Drawing (Ctrl+O)
                self._hotkey('ctrl', 'o', description="Open Drawing dialog")
                time.sleep(1.0)

                # Step 2: Navigate to next file in dialog
                if file_list_pos:
                    self._click(file_list_pos[0], file_list_pos[1], "Focus file list")
                    time.sleep(0.3)

                if i > 0:
                    # Move to next file
                    self._press('down', "Select next file")
                    time.sleep(0.2)

                self._press('enter', "Open selected file")
                time.sleep(import_delay)

                # Step 3: Save Selected (using image detection)
                if not self._click_button_by_image("save_selected", "Save Selected"):
                    self.app.after(0, lambda: self.app.update_status("Could not find Save Selected button"))
                    self.running = False
                    break
                time.sleep(0.5)

                # Step 4: Highlight working area
                if working_area_pos:
                    self._click(working_area_pos[0], working_area_pos[1], "Highlight working area")
                    time.sleep(0.5)

                # Step 5: Deselect
                if deselect_pos:
                    self._click(deselect_pos[0], deselect_pos[1], "Deselect")
                    time.sleep(0.5)

                # Step 6: Press Enter to save with new name
                self._press('enter', "Confirm save")
                time.sleep(save_delay)

                # Mark complete
                self.app.after(0, lambda i=i: self.app.update_file_status(i, "done"))
                print("File {} complete!".format(file))

            except Exception as e:
                print("ERROR: {}".format(e))
                self.app.after(0, lambda e=e: self.app.update_status("Error: {}".format(e)))
                self.running = False
                break

        if self.running:
            # All done
            self.config.set("last_processed_index", 0)
            self.app.after(0, lambda: self.app.update_status("All files processed!"))
            self.app.after(0, lambda: self.app.update_progress(total, total))
            self.app.after(0, lambda: messagebox.showinfo("Complete", "Processed {} files!".format(total)))

        self.running = False
        self.app.after(0, self.app.on_automation_stopped)


class App(tk.Tk):
    """Main application window."""

    def __init__(self):
        super().__init__()

        self.title("TruTops DWG to GEO Converter")
        self.geometry("550x600")
        self.resizable(True, True)

        self.config = Config()
        self.automation = AutomationRunner(self)
        self.files = []
        self.file_status = {}  # index -> status (pending/processing/done)

        self._create_widgets()
        self._load_files()

    def _create_widgets(self):
        """Create main window widgets."""
        # Folder selection
        folder_frame = ttk.LabelFrame(self, text="Laser Folder", padding=10)
        folder_frame.pack(fill="x", padx=10, pady=10)

        folder_row = ttk.Frame(folder_frame)
        folder_row.pack(fill="x")

        self.folder_var = tk.StringVar(value=self.config.get("laser_folder") or "laser")
        self.folder_entry = ttk.Entry(folder_row, textvariable=self.folder_var, width=40)
        self.folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        ttk.Button(folder_row, text="Browse", command=self._browse_folder).pack(side="left")

        # File list
        list_frame = ttk.LabelFrame(self, text="Files Found", padding=10)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.file_count_label = ttk.Label(list_frame, text="0 DWG files")
        self.file_count_label.pack(anchor="w")

        # Listbox with scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill="both", expand=True, pady=5)

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

        # Status and progress
        status_frame = ttk.Frame(self)
        status_frame.pack(fill="x", padx=10, pady=5)

        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.pack(anchor="w")

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            status_frame,
            variable=self.progress_var,
            maximum=100
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

        ttk.Button(btn_frame, text="Refresh", command=self._load_files).pack(side="right", padx=5)

        # Options
        options_frame = ttk.Frame(self)
        options_frame.pack(fill="x", padx=10, pady=5)

        self.dry_run_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="Dry Run (simulate without clicking)",
            variable=self.dry_run_var
        ).pack(anchor="w")

        # Workflow info
        info_frame = ttk.LabelFrame(self, text="Workflow", padding=10)
        info_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(
            info_frame,
            text="1. Ctrl+O (Open Drawing)\n"
                 "2. Click file list -> Down -> Enter (select next file)\n"
                 "3. Save Selected (image detection)\n"
                 "4. Click Working Area\n"
                 "5. Click Deselect\n"
                 "6. Enter (save with new name)",
            font=("Consolas", 9),
            foreground="gray"
        ).pack(anchor="w")

    def _browse_folder(self):
        """Open folder browser."""
        folder = filedialog.askdirectory(
            initialdir=self.folder_var.get(),
            title="Select Laser Folder"
        )
        if folder:
            self.folder_var.set(folder)
            self.config.set("laser_folder", folder)
            self._load_files()

    def _load_files(self):
        """Load DWG files from folder."""
        folder = self.folder_var.get()
        self.files = []
        self.file_status = {}

        if os.path.exists(folder):
            self.files = sorted([
                f for f in os.listdir(folder)
                if f.lower().endswith('.dwg')
            ])

        # Update listbox
        self.file_listbox.delete(0, tk.END)
        for i, f in enumerate(self.files):
            self.file_listbox.insert(tk.END, "  {}".format(f))
            self.file_status[i] = "pending"

        self.file_count_label.config(text="{} DWG files".format(len(self.files)))
        self.update_progress(0, len(self.files) or 1)

    def _start(self):
        """Start automation."""
        if not self.files:
            messagebox.showwarning("No Files", "No DWG files found in folder.")
            return

        # Check if locations are configured
        required = ["file_list", "working_area", "deselect"]
        missing = [loc for loc in required if not self.config.get("click_locations", loc)]

        if missing:
            if messagebox.askyesno(
                "Setup Required",
                "Some click locations are not configured:\n- {}\n\n"
                "Run Setup Locations first?".format("\n- ".join(missing))
            ):
                self._setup_locations()
                return

        # Disable controls
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.folder_entry.config(state="disabled")

        # Reset file status
        for i in range(len(self.files)):
            self.update_file_status(i, "pending")

        # Start automation
        self.automation.start(self.files, dry_run=self.dry_run_var.get())

    def _stop(self):
        """Stop automation."""
        self.automation.stop()

    def _setup_locations(self):
        """Open location setup dialog."""
        LocationSetupDialog(self, self.config)

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

        prefix = {
            "pending": "  ",
            "processing": "> ",
            "done": "  "
        }.get(status, "  ")

        suffix = {
            "pending": "",
            "processing": " ...",
            "done": " [Done]"
        }.get(status, "")

        text = "{}{}{}".format(prefix, self.files[index], suffix)

        self.file_listbox.delete(index)
        self.file_listbox.insert(index, text)

        # Color coding
        if status == "done":
            self.file_listbox.itemconfig(index, foreground="green")
        elif status == "processing":
            self.file_listbox.itemconfig(index, foreground="blue")
        else:
            self.file_listbox.itemconfig(index, foreground="black")

        # Scroll to show current item
        if status == "processing":
            self.file_listbox.see(index)

    def on_automation_stopped(self):
        """Called when automation stops."""
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.folder_entry.config(state="normal")


def main():
    """Main entry point."""
    # Ensure required directories exist
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    os.makedirs("laser", exist_ok=True)

    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
