# BOM Copier

## Overview
A lightweight Windows desktop app to copy SolidWorks part files based on exported Excel Bills of Materials (BOMs).

**Purpose:**
Import an Excel BOM, filter by material type, manually queue files for copying, and safely duplicate them to a target folder. Consolidates multiple manual tools into one. Original files are never moved or deleted - copy only.

## Features (Version 1.0)
- Configurable column mapping (material, filename, quantity, handedness) via Settings.
- Load Excel BOM, select material from dropdown.
- Dual-panel view: left = matching files, right = copy queue (move items with buttons or double-click).
- Live search and sorting on both panels.
- Set source and target directories.
- Start Copy with progress bar and summary.
- Overwrite toggle (default: on - newer CAD files win).
- Logs to `log.txt`.

## Future Features
- Auto-create folders named after material (e.g., "7 gauge 2B").
- Direct SolidWorks integration.
- Backup before overwrite.

## Usage
1. Run the app - Settings opens on first launch.
2. Map your BOM columns and save.
3. Load BOM Excel file.
4. Pick material, queue files, set directories.
5. Hit Start Copy.

Built in C# with WinForms for speed and simplicity.

## Project Structure
```
Copy Feauture/
├── README.md              # This file
├── DEVELOPMENT_SPEC.md    # Detailed development specification
├── TODO.md                # Implementation task list
├── config.example.json    # Example configuration file
└── src/                   # Source code (to be created)
    ├── BomCopier/
    │   ├── Program.cs
    │   ├── BomCopierForm.cs
    │   ├── SettingsWindow.cs
    │   ├── Models/
    │   │   └── BomRow.cs
    │   └── Services/
    │       ├── ConfigService.cs
    │       └── ExcelService.cs
    └── BomCopier.sln
```

## Requirements
- Windows 10/11
- .NET 6.0+ Runtime
- Microsoft Access Database Engine (for Excel OleDb access)
