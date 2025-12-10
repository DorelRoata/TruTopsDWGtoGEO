# TruTops DWG to GEO Converter

A GUI automation tool that batch converts DWG files into GEO format for TrueTops/TrueLaser 2030 laser cutting software.

**Goal**: Make the GEO process so simple that anyone can process a laser project, regardless of experience level.

---

## Time Savings Estimate

| Task | Manual Time | With This Tool | Savings |
|------|-------------|----------------|---------|
| GEO a single file | 20-60 sec | ~5 sec (automated) | 15-55 sec/file |
| Sort files by material | 30-60 min | 2-3 min | 27-57 min |
| **Large project (50+ parts)** | **2-4 hours** | **15-30 min** | **1.5-3.5 hours** |

---

## Complete Workflow Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           LASER PROJECT WORKFLOW                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  STEP 1: SolidWorks Setup                                                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  Export BOM (Bill of Materials)                                          │   │
│  │  • File Name | Material | Quantity                                       │   │
│  │  • Save as CSV or Excel                                                  │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                              ▼                                                   │
│  STEP 2: SolidWorks DWG Export                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  Export DWGs with ONLY:                                                  │   │
│  │  • Cut Layer (geometry to be cut)                                        │   │
│  │  • Etch Layer (text/markings to be etched)                              │   │
│  │  • NO other layers (agitation, templates, dimensions, etc.)             │   │
│  │  • Save all to /laser folder                                            │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                              ▼                                                   │
│  STEP 3: Material Organizer (This Tool)                                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  • Load BOM file                                                         │   │
│  │  • Select material type to process                                       │   │
│  │  • Tool copies matching DWGs to material-specific folders               │   │
│  │  • Example: /laser/A36_Steel/, /laser/304_SS/, etc.                     │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                              ▼                                                   │
│  STEP 4: DWG to GEO Conversion (This Tool)                                      │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  • Select material folder                                                │   │
│  │  • Open TrueTops Import dialog                                           │   │
│  │  • Click START - tool processes all files automatically                 │   │
│  │  • GEO files ready for laser programming                                │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                              ▼                                                   │
│  STEP 5: Laser Programming                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  • GEO files ready in TrueTops                                          │   │
│  │  • Program nesting, cutting parameters, etc.                            │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Pre-Requirements (SolidWorks Setup)

Before using this tool, you must prepare your SolidWorks project correctly. This is **critical** for the automation to work.

### 1. Export the BOM (Bill of Materials)

The BOM file tells the tool which files belong to which material.

**Required columns:**
| Column | Description | Example |
|--------|-------------|---------|
| File Name | DWG filename (without extension) | `BRACKET-001` |
| Material | Material specification | `A36 Steel`, `304 SS`, `AL 6061` |
| Quantity | Number of parts needed | `4` |

**How to export from SolidWorks:**
1. Open your assembly in SolidWorks
2. Go to **File > Save As**
3. Select **Save as type: Excel (*.xlsx)** or **CSV (*.csv)**
4. In the BOM options, ensure these columns are included:
   - Part Number / File Name
   - Material
   - Quantity
5. Save to your project folder as `BOM.xlsx` or `BOM.csv`

**Example BOM:**
```
File Name         | Material      | Qty
------------------|---------------|----
FRAME-BASE-001    | SS 11GA       | 1
BRACKET-LEFT-002  | SS 14GA       | 2
BRACKET-RIGHT-003 | SS 14GA       | 2
COVER-PLATE-004   | SS 16GA       | 1
GUARD-PANEL-005   | SS 7GA        | 4
SPACER-006        | UHMW          | 8
SLIDE-PLATE-007   | HDPE          | 2
MOUNT-PLATE-008   | SS 11GA       | 2
```

**Common Materials:**
| Material | Description |
|----------|-------------|
| SS 7GA   | Stainless Steel 7 Gauge (.1875") |
| SS 11GA  | Stainless Steel 11 Gauge (.1196") |
| SS 14GA  | Stainless Steel 14 Gauge (.0747") |
| SS 16GA  | Stainless Steel 16 Gauge (.0598") |
| UHMW     | Ultra-High Molecular Weight Polyethylene |
| HDPE     | High-Density Polyethylene |

### 2. Export DWGs with Correct Layers

**CRITICAL: Only export these layers:**

| Layer | Purpose | Include? |
|-------|---------|----------|
| **Cut Layer** | Geometry to be laser cut | YES |
| **Etch Layer** | Text/markings to be laser etched | YES |
| Agitation Layer | Internal features | NO |
| Template Layer | Drawing templates | NO |
| Dimension Layer | Dimensions/annotations | NO |
| Construction Layer | Reference geometry | NO |
| Any other layers | - | NO |

**Why this matters:**
- Clean DWGs import directly into TrueTops without manual layer cleanup
- No need to delete unwanted geometry in TrueTops
- Faster processing, fewer errors
- Enables full automation

**How to export from SolidWorks:**
1. Open the part/drawing
2. Go to **File > Save As**
3. Select **Save as type: DWG (*.dwg)**
4. Click **Options**
5. In layer mapping, ensure only Cut and Etch layers are exported
6. Save to the `laser/` folder

### 3. Folder Structure

After exporting, your project should look like this:

```
YourProject/
├── BOM.xlsx                    # Bill of Materials export
├── Assembly.sldasm             # SolidWorks assembly (optional)
└── laser/                      # ALL DWG exports go here
    ├── FRAME-BASE-001.dwg      # SS 11GA
    ├── BRACKET-LEFT-002.dwg    # SS 14GA
    ├── BRACKET-RIGHT-003.dwg   # SS 14GA
    ├── COVER-PLATE-004.dwg     # SS 16GA
    ├── GUARD-PANEL-005.dwg     # SS 7GA
    ├── SPACER-006.dwg          # UHMW
    ├── SLIDE-PLATE-007.dwg     # HDPE
    └── MOUNT-PLATE-008.dwg     # SS 11GA
```

---

## Features

### Current Features
- **Simple GUI Interface** - No command-line knowledge required
- **Batch Processing** - Process multiple DWG files automatically
- **Reliable Button Detection** - Multiple strategies ensure buttons are always found
- **Progress Tracking** - Visual progress bar and file status
- **Resume Capability** - Continue from where you left off after interruption
- **Dry Run Mode** - Test the workflow without actually clicking

### Planned Features
- **BOM Import** - Load Excel/CSV BOM files
- **Material Organizer** - Sort files into folders by material type
- **Material Selection** - Choose which material to process
- **Quantity Display** - Show part quantities from BOM

---

## Usage Guide

### First-Time Setup (One Time Only)

Before processing files, you need to capture the button images:

1. **Open TrueTops** and navigate to where the "Save to Geo" and "OK" buttons are visible
2. **Launch the app** and click **"Setup Buttons"**
3. **Capture each button**:
   - Click "Capture" next to "Save to Geo"
   - You have 5 seconds to click on the button in TrueTops
   - The tool captures a screenshot of that button
   - Repeat for the "OK" button
4. **Save** your configuration

This only needs to be done once (unless TrueTops UI changes).

### Processing Files (Daily Use)

1. **Prepare your files**:
   - Export BOM from SolidWorks
   - Export DWGs with only Cut and Etch layers
   - Place all DWG files in the `laser/` folder

2. **Open TrueTops**:
   - Click the Import button
   - Navigate to your `laser/` folder
   - Make sure the file list is visible

3. **Start the automation**:
   - Launch `app.py`
   - Verify the file list shows your DWG files
   - Click **START**
   - Don't touch the mouse/keyboard until complete

4. **Monitor progress**:
   - Watch the progress bar
   - Each file shows status indicators
   - Status messages show what's happening

### Tips for Best Results

- **Don't move TrueTops** window during processing
- **Keep the Import dialog open** throughout the batch
- **Use consistent DWG exports** - same layers, same settings
- **Test with Dry Run** first to verify timing
- **Export BOM first** before exporting DWGs (ensures names match)

---

## GUI Overview

### Main Window

```
┌─────────────────────────────────────────────────────┐
│  TruTops DWG to GEO Converter                    [X]│
├─────────────────────────────────────────────────────┤
│                                                     │
│  Laser Folder: [  laser/                  ] [Browse]│
│                                                     │
│  Files Found: 12 DWG files                          │
│  ┌─────────────────────────────────────────────┐   │
│  │ [Done] FRAME-BASE-001.dwg                   │   │
│  │ [Done] BRACKET-LEFT-002.dwg                 │   │
│  │ > BRACKET-RIGHT-003.dwg  <- Processing      │   │
│  │   COVER-PLATE-004.dwg                       │   │
│  │   ...                                       │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  Status: Processing BRACKET-RIGHT-003.dwg...        │
│  Progress: [████████░░░░░░░░░░░░] 3/12              │
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │  START   │  │   STOP   │  │  SETUP BUTTONS   │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
│                                                     │
│  [  ] Dry Run (simulate without clicking)          │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Material Organizer (Planned)

```
┌─────────────────────────────────────────────────────┐
│  Material Organizer                              [X]│
├─────────────────────────────────────────────────────┤
│                                                     │
│  BOM File: [ BOM.xlsx                    ] [Browse] │
│                                                     │
│  Materials Found:                                   │
│  ┌─────────────────────────────────────────────┐   │
│  │ [x] SS 11GA           (3 files, 4 parts)    │   │
│  │ [ ] SS 14GA           (2 files, 4 parts)    │   │
│  │ [ ] SS 16GA           (1 file,  1 part)     │   │
│  │ [ ] SS 7GA            (1 file,  4 parts)    │   │
│  │ [ ] UHMW              (1 file,  8 parts)    │   │
│  │ [ ] HDPE              (1 file,  2 parts)    │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  Output Folder: [ laser/SS_11GA/         ] [Browse] │
│                                                     │
│  ┌─────────────────────────┐                       │
│  │  COPY SELECTED FILES    │                       │
│  └─────────────────────────┘                       │
│                                                     │
│  Status: Ready                                      │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Detailed Time Savings Analysis

### Manual Process (Without This Tool)

**For a project with 50 DWG files:**

| Step | Time per File | Total Time |
|------|---------------|------------|
| Open file in TrueTops | 10 sec | 8 min |
| Navigate menus | 5 sec | 4 min |
| Click Save to GEO | 5 sec | 4 min |
| Confirm dialogs | 5 sec | 4 min |
| Wait for save | 5 sec | 4 min |
| **Subtotal (GEO only)** | **30 sec** | **25 min** |
| Sort files by material | - | **30-60 min** |
| **TOTAL** | - | **55-85 min** |

*Note: Complex files requiring mirroring or text editing take 45-60 seconds each.*

### Automated Process (With This Tool)

**For the same 50-file project:**

| Step | Time |
|------|------|
| Load BOM and organize by material | 2-3 min |
| Start automation | 30 sec |
| Automated GEO processing (50 files @ 5 sec) | ~4 min |
| **TOTAL** | **~7-8 min** |

### Savings Summary

| Project Size | Manual Time | Automated Time | Time Saved |
|--------------|-------------|----------------|------------|
| Small (10 parts) | 15-20 min | 3-4 min | 12-16 min |
| Medium (30 parts) | 35-50 min | 5-6 min | 30-44 min |
| Large (50+ parts) | 55-85 min | 7-8 min | 48-77 min |
| XL (100+ parts) | 2-3 hours | 12-15 min | 1.75-2.75 hours |

**Additional Benefits:**
- Reduced errors from manual clicking
- Consistent processing (no missed files)
- Anyone can run the process (no training required)
- Free up skilled programmers for actual laser programming

---

## Configuration

Settings are saved in `config.json` (auto-created):

```json
{
  "laser_folder": "laser",
  "import_delay": 3.0,
  "save_delay": 2.0,
  "buttons": {
    "save_to_geo": {
      "image": "screenshots/save_to_geo.png",
      "fallback_coords": [500, 300]
    },
    "ok": {
      "image": "screenshots/ok.png",
      "fallback_coords": [600, 400]
    }
  },
  "last_processed_index": 0
}
```

### Adjustable Timings

If TrueTops is slow, increase the delays in `config.json`:

| Setting | Default | Description |
|---------|---------|-------------|
| `import_delay` | 3.0 sec | Wait after pressing Enter to import |
| `save_delay` | 2.0 sec | Wait after clicking OK to save |

---

## Troubleshooting

### "Button not found" error

1. **Re-capture the button** - UI may have changed
2. **Check screenshot quality** - Ensure `screenshots/` folder has clear images
3. **Verify TrueTops window** - Make sure buttons are visible on screen
4. **Check screen resolution** - Buttons may look different on different monitors

### Processing stops mid-batch

1. **Check TrueTops** - May have shown an error dialog
2. **Resume processing** - The tool saves progress, just click START again
3. **Increase delays** - If timing issues, edit `config.json`

### Files not appearing in list

1. **Check file extension** - Must be `.dwg` (case insensitive)
2. **Verify folder path** - Ensure files are in the correct folder
3. **Refresh** - Click Browse and re-select the folder

### DWG has unwanted geometry in TrueTops

1. **Check SolidWorks export settings** - Only Cut and Etch layers should be exported
2. **Re-export the DWG** with correct layer settings
3. **Verify layer names** in SolidWorks match your export filter

---

## Safety Features

- **Failsafe**: Move mouse to top-left corner to abort immediately
- **Dry Run**: Test without clicking (checkbox in main window)
- **Progress Save**: Interrupted batches can be resumed
- **User Alerts**: Pauses and asks for help if buttons can't be found
- **Non-Destructive**: Original DWG files are never modified

---

## Project Structure

```
TruTopsDWGtoGEO/
├── README.md               # This documentation
├── app.exe                 # Main application
├── config.json             # Settings (auto-generated)
├── screenshots/            # Button images (auto-created)
│   ├── save_to_geo.png
│   └── ok.png
└── laser/                  # Your DWG files go here
    ├── SS_7GA/             # Material-specific subfolders
    ├── SS_11GA/
    ├── SS_14GA/
    ├── SS_16GA/
    ├── UHMW/
    ├── HDPE/
    └── *.dwg
```

---

## Roadmap

### Phase 1 (Current)
- [x] Basic GUI application
- [x] Button capture and detection
- [x] Automated DWG to GEO conversion
- [x] Progress tracking and resume

### Phase 2 (Next)
- [ ] BOM file import (Excel/CSV)
- [ ] Material organizer
- [ ] File copying by material
- [ ] Quantity display

### Phase 3 (Future)
- [ ] Mirror detection/automation
- [ ] Text editing assistance
- [ ] Batch reporting
- [ ] Integration with laser programming

---

## License

This project is provided as-is for internal use.

## Support

For issues or feature requests, please open an issue on GitHub.
