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
    "buttons": {
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
            value = value.get(key)
            if value is None:
                return None
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
        if not os.path.exists(image_path):
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


class ButtonSetupDialog(tk.Toplevel):
    """Dialog for capturing button screenshots."""

    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        self.title("Button Setup")
        self.geometry("450x350")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Ensure screenshots directory exists
        os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

        self.captured = {
            "save_to_geo": False,
            "ok": False
        }

        self._create_widgets()
        self._update_status()

    def _create_widgets(self):
        """Create dialog widgets."""
        # Instructions
        instr_frame = ttk.LabelFrame(self, text="Instructions", padding=10)
        instr_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(
            instr_frame,
            text="1. Open TrueTops and make the buttons visible\n"
                 "2. Click CAPTURE, then click the button in TrueTops\n"
                 "3. You have 5 seconds to click after pressing CAPTURE",
            wraplength=400
        ).pack()

        # Save to Geo button capture
        geo_frame = ttk.LabelFrame(self, text="Save to Geo Button", padding=10)
        geo_frame.pack(fill="x", padx=10, pady=5)

        geo_row = ttk.Frame(geo_frame)
        geo_row.pack(fill="x")

        self.geo_capture_btn = ttk.Button(
            geo_row, text="CAPTURE", command=lambda: self._start_capture("save_to_geo")
        )
        self.geo_capture_btn.pack(side="left", padx=5)

        self.geo_status = ttk.Label(geo_row, text="Not captured")
        self.geo_status.pack(side="left", padx=10)

        # OK button capture
        ok_frame = ttk.LabelFrame(self, text="OK Button", padding=10)
        ok_frame.pack(fill="x", padx=10, pady=5)

        ok_row = ttk.Frame(ok_frame)
        ok_row.pack(fill="x")

        self.ok_capture_btn = ttk.Button(
            ok_row, text="CAPTURE", command=lambda: self._start_capture("ok")
        )
        self.ok_capture_btn.pack(side="left", padx=5)

        self.ok_status = ttk.Label(ok_row, text="Not captured")
        self.ok_status.pack(side="left", padx=10)

        # Countdown label
        self.countdown_label = ttk.Label(self, text="", font=("Arial", 14, "bold"))
        self.countdown_label.pack(pady=10)

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(btn_frame, text="Save", command=self._save).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="left", padx=5)

    def _update_status(self):
        """Update status labels based on existing captures."""
        geo_path = self.config.get("buttons", "save_to_geo", "image")
        ok_path = self.config.get("buttons", "ok", "image")

        if geo_path and os.path.exists(geo_path):
            self.geo_status.config(text="Captured", foreground="green")
            self.captured["save_to_geo"] = True

        if ok_path and os.path.exists(ok_path):
            self.ok_status.config(text="Captured", foreground="green")
            self.captured["ok"] = True

    def _start_capture(self, button_name):
        """Start the capture countdown."""
        self.geo_capture_btn.config(state="disabled")
        self.ok_capture_btn.config(state="disabled")

        # Minimize window
        self.withdraw()

        # Start countdown in thread
        threading.Thread(
            target=self._capture_countdown,
            args=(button_name,),
            daemon=True
        ).start()

    def _capture_countdown(self, button_name):
        """Countdown and wait for click."""
        for i in range(5, 0, -1):
            self.after(0, lambda i=i: self.countdown_label.config(
                text=f"Click the button in {i}..."
            ))
            time.sleep(1)

        self.after(0, lambda: self.countdown_label.config(text="Click now!"))

        # Wait for mouse click
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
            # Capture region around click (100x50 pixels)
            region = (x - 50, y - 25, x + 50, y + 25)

            try:
                screenshot = ImageGrab.grab(bbox=region)
                image_path = os.path.join(SCREENSHOTS_DIR, f"{button_name}.png")
                screenshot.save(image_path)

                # Save to config
                self.config.set("buttons", button_name, "image", image_path)
                self.config.set("buttons", button_name, "fallback_coords", [x, y])

                self.captured[button_name] = True
                self.after(0, lambda: self._capture_complete(button_name, True))
            except Exception as e:
                self.after(0, lambda: self._capture_complete(button_name, False, str(e)))
        else:
            self.after(0, lambda: self._capture_complete(button_name, False, "Timeout"))

    def _capture_complete(self, button_name, success, error=None):
        """Handle capture completion."""
        self.deiconify()
        self.countdown_label.config(text="")
        self.geo_capture_btn.config(state="normal")
        self.ok_capture_btn.config(state="normal")

        if success:
            if button_name == "save_to_geo":
                self.geo_status.config(text="Captured", foreground="green")
            else:
                self.ok_status.config(text="Captured", foreground="green")
        else:
            messagebox.showerror("Capture Failed", f"Could not capture: {error}")

    def _save(self):
        """Save and close dialog."""
        if not self.captured["save_to_geo"] or not self.captured["ok"]:
            if not messagebox.askyesno(
                "Incomplete Setup",
                "Not all buttons are captured. Continue anyway?"
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
                f"Previous session stopped at file {self.current_index + 1}.\n"
                f"Resume from there?"
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

    def _run(self):
        """Main automation loop."""
        import_delay = self.config.get("import_delay") or 3.0
        save_delay = self.config.get("save_delay") or 2.0

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
                f"Processing {f} ({i+1}/{t})..."
            ))
            self.app.after(0, lambda i=i, t=total: self.app.update_progress(i, t))

            try:
                # Select file (first file: just Enter, others: Down + Enter)
                if i > 0:
                    if not self.dry_run:
                        pyautogui.press('down')
                    time.sleep(0.3)

                if not self.dry_run:
                    pyautogui.press('enter')

                # Wait for import
                time.sleep(import_delay)

                # Find and click Save to Geo
                if not self._click_button("save_to_geo", "Save to Geo"):
                    self.running = False
                    break

                time.sleep(1)

                # Find and click OK
                if not self._click_button("ok", "OK"):
                    self.running = False
                    break

                # Wait for save
                time.sleep(save_delay)

                # Mark complete
                self.app.after(0, lambda i=i: self.app.update_file_status(i, "done"))

            except Exception as e:
                self.app.after(0, lambda e=e: self.app.update_status(f"Error: {e}"))
                self.running = False
                break

        if self.running:
            # All done
            self.config.set("last_processed_index", 0)
            self.app.after(0, lambda: self.app.update_status("All files processed!"))
            self.app.after(0, lambda: self.app.update_progress(total, total))
            self.app.after(0, lambda: messagebox.showinfo("Complete", f"Processed {total} files!"))

        self.running = False
        self.app.after(0, self.app.on_automation_stopped)

    def _click_button(self, button_key, button_name):
        """Find and click a button. Returns True on success."""
        image_path = self.config.get("buttons", button_key, "image")
        fallback = self.config.get("buttons", button_key, "fallback_coords")

        pos, strategy = ButtonDetector.find_button(image_path, fallback)

        if pos:
            self.app.after(0, lambda s=strategy: self.app.update_status(
                f"Found {button_name} via {s}"
            ))
            if not self.dry_run:
                pyautogui.click(pos[0], pos[1])
            return True
        else:
            # Button not found - ask user
            result = [None]
            event = threading.Event()

            def ask():
                result[0] = messagebox.askretrycancel(
                    "Button Not Found",
                    f"Could not find '{button_name}' button.\n\n"
                    f"Please click the button manually, then click Retry.\n"
                    f"Or click Cancel to stop."
                )
                event.set()

            self.app.after(0, ask)
            event.wait()

            if result[0]:
                # User clicked retry - assume they clicked the button
                return True
            else:
                return False


class App(tk.Tk):
    """Main application window."""

    def __init__(self):
        super().__init__()

        self.title("TruTops DWG to GEO Converter")
        self.geometry("500x550")
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

        ttk.Button(btn_frame, text="Setup Buttons", command=self._setup_buttons).pack(side="left", padx=5)

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
            self.file_listbox.insert(tk.END, f"  {f}")
            self.file_status[i] = "pending"

        self.file_count_label.config(text=f"{len(self.files)} DWG files")
        self.update_progress(0, len(self.files) or 1)

    def _start(self):
        """Start automation."""
        if not self.files:
            messagebox.showwarning("No Files", "No DWG files found in folder.")
            return

        # Check if buttons are configured
        geo_img = self.config.get("buttons", "save_to_geo", "image")
        ok_img = self.config.get("buttons", "ok", "image")

        if not (geo_img and os.path.exists(geo_img)) or not (ok_img and os.path.exists(ok_img)):
            if not messagebox.askyesno(
                "Setup Required",
                "Button images are not configured.\n"
                "Run Setup Buttons first?\n\n"
                "(Click No to try with saved coordinates only)"
            ):
                pass
            else:
                self._setup_buttons()
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

    def _setup_buttons(self):
        """Open button setup dialog."""
        ButtonSetupDialog(self, self.config)

    def update_status(self, text):
        """Update status label."""
        self.status_label.config(text=text)

    def update_progress(self, current, total):
        """Update progress bar."""
        if total > 0:
            self.progress_var.set((current / total) * 100)
            self.progress_label.config(text=f"{current}/{total}")

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

        text = f"{prefix}{self.files[index]}{suffix}"

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
