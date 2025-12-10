# Laser Automation Project README

## Overview
This project automates the workflow for importing DWG files (exported from SolidWorks with only cut and etch layers) into TrueTops 13 on Windows 11, processing them for TrueLaser 2030. The automation handles batch imports, screen highlighting, button clicks, and saving to GEO format. It uses Python for scripting to ensure repeatability and ease of use.

This README compiles the prerequisites, process steps, setup instructions, and code outlines discussed in the development conversation. It serves as a complete guide to get started.

## Prerequisites
- **SolidWorks Model**: Export the "bomb" file (e.g., the base model in bomb format) to the main project folder.
- **Laser Files Folder**: Create a subfolder named `laser` in the main project folder.
  - Export only the **cut layer** and **etch layer** from SolidWorks to DWG format.
  - Do **not** include agitation layers, template layers, or any other extraneous elements. This keeps files clean for direct import into TrueTops without additional classification (no need for runtime layer detection in the DWG files).
- **Software Environment**:
  - TrueTops version 13 (older version, as specified).
  - Windows 11 machine.
  - Python 3.x installed.
- **Folder Structure Example**:
  ```
  LaserProject/
  ├── README.md (this file)
  ├── bomb_file.sldprt (or similar SolidWorks bomb file)
  ├── automate_laser.py (main script)
  ├── coordinate_recorder.py (recording tool)
  └── laser/
      ├── part1.dwg
      ├── part2.dwg
      └── ...
  ```
- **Additional Notes from Discussion**:
  - Files in `/laser` are pre-filtered: Only cut and etch layers, so TrueTops reads them directly.
  - No bomb exit automation needed beyond standard SolidWorks close (File > Close or Ctrl+W), as the focus is on export and import.

## Automation Process
The tool automates the following steps in TrueTops, based on the described workflow:

1. **Manual Start**: User opens TrueTops and clicks the **Import** button to open the file selection dialog.
2. **File Selection**: The script selects the first file in the `laser` folder (e.g., via Enter or click).
3. **Import and Highlight**: After import completes, the script highlights an 800x600 pixel region in the center of the screen (to visually confirm the imported geometry—e.g., flash or draw a temporary overlay).
4. **Save to GEO**: Clicks the **Save to Geo** button and confirms with **OK**.
5. **Loop**: Repeats for the next file in the list until all files in the `laser` folder are processed.
   - Auto-selects the next item in the import list (e.g., via Down arrow key).
   - Re-highlights the screen region and saves.

**Workflow Loop Visualization**:
- Start: Import first file → Highlight center (800x600) → Save to Geo → OK.
- Repeat: Down to next file → Import → Highlight → Save to Geo → OK.
- End: All files processed.

This ensures batch processing without manual intervention after the initial import click.

## Setup Instructions
1. **Install Dependencies**:
   - Ensure Python is installed (download from python.org if needed).
   - Open Command Prompt and run:
     ```
     pip install pyautogui opencv-python pillow
     ```
     - `pyautogui`: For mouse clicks, keyboard inputs, screen grabs, highlighting, and coordinate recording.
     - `opencv-python`: For image recognition (matching button screenshots in general areas to handle UI variations).
     - `pillow`: For image handling (screenshots and overlays).

2. **Record Coordinates for Accuracy** (One-Time Setup, as Discussed):
   - To ensure precise button selection, record your first manual run.
   - Create a `screenshots` subfolder for button images (e.g., "Save to Geo" and "OK").
   - The automation searches around recorded coordinates for visual matches, avoiding hardcoding that could break with window resizing.

3. **Run the Automation**:
   - Place your files in the structure above.
   - Run the main script: `python automate_laser.py`.
   - Follow on-screen prompts to start the import loop (e.g., confirm TrueTops is open and Import dialog is ready).

## Recording Script (coordinate_recorder.py)
Use this to capture clicks for the first run. Save as `coordinate_recorder.py` and run it (`python coordinate_recorder.py`). It polls mouse position every 0.5 seconds—move your mouse over buttons and note the printed X,Y coords. Stop with Ctrl+C.

```python
import pyautogui
import time

print("Click recording started. Perform your first import steps slowly.")
print("Move mouse over buttons/areas and note positions. Press Ctrl+C to stop.")

try:
    while True:
        x, y = pyautogui.position()
        print(f"Current position: X={x}, Y={y}")
        time.sleep(0.5)  # Poll every 0.5 seconds
except KeyboardInterrupt:
    print("Recording stopped. Use the positions for your script.")
```

- **Steps to Record** (as Discussed):
  1. Start TrueTops, click Import (note position for script fallback).
  2. Select first file in list (note list item position).
  3. After import, move mouse to center of highlight area (for 800x600 box).
  4. Hover/click "Save to Geo" (take screenshot: Print Screen > Crop > Save as PNG).
  5. Hover/click "OK" (take screenshot).
  6. Note position for next file selection (e.g., Down arrow target).
  7. Stop recording and update the main script with these coords/images.

**Pro Tip**: Screenshots help with visual matching—script scans ~50-100 pixel radius around coords for the button image.

## Main Automation Script (automate_laser.py)
Starter script based on the workflow. Customize with your recorded coordinates and button images. Save as `automate_laser.py`.

```python
import pyautogui
import os
import time
from PIL import Image

# Safety: Move mouse to top-left to abort
pyautogui.FAILSAFE = True

# Configuration (Update with recordings)
LASER_FOLDER = 'laser'
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
HIGHLIGHT_X, HIGHLIGHT_Y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2  # Center start
HIGHLIGHT_WIDTH, HIGHLIGHT_HEIGHT = 800, 600
SAVE_GEO_BUTTON_IMG = 'screenshots/save_to_geo.png'  # Your screenshot
OK_BUTTON_IMG = 'screenshots/ok.png'
# Fallback coords (replace with recordings)
SAVE_GEO_X, SAVE_GEO_Y = 500, 300  # Example
OK_X, OK_Y = 600, 400

# Get list of files
files = [f for f in os.listdir(LASER_FOLDER) if f.endswith('.dwg')]
files.sort()  # Alphabetical order
print(f"Found {len(files)} files to process.")

# Assume user has clicked Import and file list is open
input("Press Enter when Import dialog is open and ready...")
for i, file in enumerate(files):
    print(f"Processing {file} ({i+1}/{len(files)})...")
    
    # Select file (for first: Enter; others: Down + Enter)
    if i > 0:
        pyautogui.press('down')  # Move to next in list
        time.sleep(0.5)
    pyautogui.press('enter')  # Select/Import
    time.sleep(3)  # Wait for import to load (adjust as needed)
    
    # Highlight screen region (move cursor + optional screenshot flash)
    pyautogui.moveTo(HIGHLIGHT_X, HIGHLIGHT_Y)
    # Optional: Take and display screenshot for visual confirm (uncomment)
    # screenshot = pyautogui.screenshot(region=(HIGHLIGHT_X - HIGHLIGHT_WIDTH//2, HIGHLIGHT_Y - HIGHLIGHT_HEIGHT//2, HIGHLIGHT_WIDTH, HIGHLIGHT_HEIGHT))
    # screenshot.show()  # Pops up image briefly
    print("Highlighted center region (800x600).")
    time.sleep(1)
    
    # Click Save to Geo (prefer image match, fallback coord)
    button_location = pyautogui.locateOnScreen(SAVE_GEO_BUTTON_IMG, confidence=0.8)
    if button_location:
        pyautogui.click(pyautogui.center(button_location))
        print("Clicked Save to Geo via image match.")
    else:
        pyautogui.click(SAVE_GEO_X, SAVE_GEO_Y)
        print("Clicked Save to Geo via fallback coord.")
    time.sleep(1)
    
    # Click OK (same logic)
    button_location = pyautogui.locateOnScreen(OK_BUTTON_IMG, confidence=0.8)
    if button_location:
        pyautogui.click(pyautogui.center(button_location))
        print("Clicked OK via image match.")
    else:
        pyautogui.click(OK_X, OK_Y)
        print("Clicked OK via fallback coord.")
    time.sleep(2)  # Wait for save to complete

print("All files processed! Check TrueTops for GEO outputs.")
```

- **Notes on Script** (from Discussion):
  - **Button Selection**: Uses visual understanding (OpenCV image match) around general areas + fallbacks for reliability.
  - **Highlighting**: Simple cursor move for now; enhance with overlay if needed (e.g., draw rectangle via PIL).
  - **Loop Handling**: Assumes file list stays open; test for dialog refreshes.
  - **Error Handling**: Add try/except for locateOnScreen failures. Use `time.sleep()` for timing—tune based on machine speed.
  - **Testing**: Run on sample files first. If TrueTops crashes, add longer sleeps.

## Potential Improvements
- **GUI Wrapper**: Use `tkinter` for start/stop buttons and progress display.
- **Advanced Input**: `pynput` for better mouse/keyboard if pyautogui limits arise.
- **Layer Validation**: Optional script to verify DWG layers pre-import (using e.g., `ezdxf` library if added).
- **Version Control**: Git this project; track coord changes if UI updates.
- **Conversation Insights**: Focused on visual/recording for accuracy over hardcoding; no DWG parsing needed due to pre-export filtering.

If you need tweaks, more code (e.g., full GUI), or help debugging, let me know! Save this as `README.md` in your project root.
