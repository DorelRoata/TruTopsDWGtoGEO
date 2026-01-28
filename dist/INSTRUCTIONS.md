# Manual/Auto Mode & Image Preview Walkthrough

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
-3. **Manual Trigger**: The automation will pause before the "Save" step.
   - Requires user confirmation to proceed.
   - Press **F2** to trigger the save action.
   - Allows time to physically check the part nesting/cleaning. Press **F2** when you are ready to proceed to the next file.

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
