# D2G 1.2.0 Quick Guide

I have updated the TruTops DWG to GEO Converter to support user-controlled pauses and visual verification.

## New Features

### 1. Folder Structure Support
The tool now expects the following structure when you select a project folder:
- `ProjectFolder/`
    - `Filtered_DWGs/` (Contains .dwg files)
    - `DWG_Images/` (Contains matching .png/.jpg files)

### 2. Image Preview Window
- A separate black window pops up when files are loaded.
- **Usage**: Drag this window to your second monitor. It will display the part image corresponding to the DWG currently being processed.

### 3. Automation Modes

#### Auto Mode
- **Behavior**: The automation runs through the steps but pauses for a set time before the "Save Selected" step.
- **Config**: Use the "Delay (sec)" spinner to adjust this pause (e.g., 3.0 seconds).
- **Purpose**: Gives you a few seconds to glance at the Preview Window and the TruTops screen to verify match before it continues.

#### Manual Mode
- D2G loads the current DWG and pauses before creating the GEO.
- Press **Ctrl+2** when you are ready to run the complete Create GEO group.

### Grouped Recovery Shortcuts

- **Ctrl+1** - Load the current DWG
- **Ctrl+2** - Create the current GEO
- **Ctrl+3** - Retry the current group
- **Ctrl+4** - Skip the current file
- **Ctrl+5** - Process the complete current file
- **Esc** - Stop safely

The shortcuts are accepted only while D2G is paused or recovering. This prevents accidental commands while an automation group is already running.

### Smart Waiting and Locations

- D2G waits for the TruTops screen to change and settle instead of using only fixed delays.
- If the expected screen does not appear, D2G pauses and shows the recovery shortcuts.
- Re-capture each location once in Settings to store it relative to the TruTops window.

### Existing GEO Files

Choose **Skip existing GEO**, **Replace existing GEO**, or **Only process changed DWGs** before starting. Existing GEO files are expected beside their matching DWGs.

### 4. Status Overlay
- A persistent overlay appears in the bottom-left corner of the screen.
- **Display**: Shows `[AUTO]` or `[MANUAL]` followed by the current step description (e.g., `Opening Drawing...`, `Waiting...`).
- **Purpose**: Keeps you informed of the automation's progress without needing to look at the console.

## How to Run
1.  Launch `app.py`.
2.  Select "Auto Mode" or "Manual Mode".
3.  Click "+ Select Folder" and choose your project root.
4.  Verify the files list shows `[IMG]` next to files with found images.
5.  Position the "Part Preview" window on your secondary screen.
6.  Click "START AUTOMATION".

## Deployment (How to run on another PC)
To run this tool on another computer without installing Python:
1.  Copy `TruTopsDWGtoGEO.exe` (from the `dist` folder) to the target PC.
2.  (Optional) Copy `config.json` if you want to keep your current settings (hotkeys, delays). If you don't copy it, the app will create a fresh one with defaults.
3.  **Requirements**:
    - Windows 10/11.
    - No other installation needed.
    - **Note**: The app needs permission to control the mouse/keyboard (Run as Admin if TruTops is running as Admin).
