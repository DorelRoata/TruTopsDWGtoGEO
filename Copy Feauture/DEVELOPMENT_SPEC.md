# BOM Copier - Development Specification

## Overview
**Project Name:** BOM Copier
**Purpose:** A lightweight Windows desktop application to streamline copying SolidWorks part files based on exported Excel Bills of Materials (BOMs). The app imports an Excel BOM, allows filtering by material type, lets the user manually select/queue files for copying, and performs safe copies (no moving or deleting of originals). Designed to consolidate multiple manual steps into one tool.

**Key Principles:**
- Copy only - originals are never touched.
- Simple, flat architecture - easy to read, maintain, and extend.
- Configurable column mapping via settings (BOM formats may change over time).
- No hard-coded assumptions about Excel structure.

**Target Platform:** Windows-only desktop app
**Language:** C# (.NET 6+ Windows-specific recommended)
**UI Framework:** Windows Forms (WinForms) - lightweight, fast, native feel.

---

## Core Features (Version 1.0)

### 1. Settings/Configuration
- First-run or manual access to a settings dialog.
- Map Excel columns by index (1-based, e.g., column A = 1):
  - Part File Name column
  - Quantity column
  - Material Type column
  - Handedness column (optional)
- Toggle: Overwrite existing files (default: true)
- Saved to `config.json`.
- Validation warnings for invalid column indices.

### 2. Main Workflow
1. Load Excel BOM (drag-drop or browse button).
2. Parse Excel into internal `List<BomRow>`.
3. Material dropdown populated with unique values from Material column.
4. Select material → left panel shows matching files.
5. Move items to right panel (Copy Queue) via buttons or double-click.
6. Live search boxes above each panel for filtering.
7. Sort options (alphabetical, date modified).
8. Source and target directory fields with browse buttons.
9. Start Copy → progress bar, copy with overwrite flag, log results, show summary.

### 3. Safety & Feedback
- Copy only - never move or delete originals.
- Progress bar during copy operation.
- Post-copy summary dialog (X files copied, Y skipped, Z errors).
- No undo functionality (keeps it simple).
- Detailed logging to `log.txt`.

---

## Future Features (Post v1.0)
- Auto-create material-named folders (e.g., "7 gauge 2B").
- Duplicate file preview before copy.
- SolidWorks API integration for direct file access.
- Optional backup before overwrite.
- Auto-open target folder after copy completes.

---

## Architecture & Classes

### Data Model

#### BomRow.cs
```csharp
public class BomRow
{
    public string FileName { get; set; }
    public string Material { get; set; }
    public int Quantity { get; set; }
    public string Handedness { get; set; }
}
```

#### AppConfig.cs
```csharp
public class AppConfig
{
    public int FileNameColumn { get; set; } = 1;
    public int QuantityColumn { get; set; } = 3;
    public int MaterialColumn { get; set; } = 5;
    public int HandednessColumn { get; set; } = 7;
    public bool OverwriteExisting { get; set; } = true;
    public string SourceDirectory { get; set; } = "";
    public string TargetDirectory { get; set; } = "";
}
```

### UI Components

#### SettingsWindow.cs (Modal Form)
**Purpose:** Configure column mappings and app settings.

**UI Elements:**
- 4x NumericUpDown controls for column indices
- CheckBox for OverwriteExisting
- Save and Cancel buttons

**Methods:**
- `LoadConfig()` - Read config.json into form fields
- `WriteConfig()` - Save form fields to config.json
- `ValidateSettings()` - Ensure column indices are valid (> 0)

#### BomCopierForm.cs (Main Form)
**Purpose:** Main application window with dual-panel file management.

**Key Fields:**
```csharp
private List<BomRow> bomData;
private AppConfig config;
private TextBox txtSourceDir, txtTargetDir;
private ComboBox cmbMaterial;
private ListBox lstSource, lstQueue;
private TextBox txtSearchSource, txtSearchQueue;
private ProgressBar progressBar;
private Button btnLoadBom, btnAddToQueue, btnRemoveFromQueue, btnStartCopy;
```

**Key Methods:**
- `OnLoad()` - Read config or open settings dialog
- `LoadExcel(string path)` - Parse Excel via OleDb
- `PopulateMaterials()` - Fill dropdown with unique materials
- `FilterSourceList(string selectedMaterial)` - Show matching files
- `MoveToQueue()` / `MoveFromQueue()` - Transfer items between panels
- `ApplySearch(ListBox list, string searchTerm)` - Live filter
- `ExecuteCopy()` - File.Copy loop with progress updates
- `WriteLog(string summary)` - Append to log.txt

---

## UI Layout Specification

```
┌─────────────────────────────────────────────────────────────────┐
│  BOM Copier                                            [─][□][×] │
├─────────────────────────────────────────────────────────────────┤
│  [Load BOM]  Material: [▼ Dropdown ▼]                [Settings] │
├─────────────────────────────────────────────────────────────────┤
│  Source Directory: [________________________] [Browse]           │
│  Target Directory: [________________________] [Browse]           │
├───────────────────────────┬─────────────────────────────────────┤
│  Available Files          │  Copy Queue                         │
│  Search: [____________]   │  Search: [____________]             │
│  ┌─────────────────────┐  │  ┌─────────────────────┐            │
│  │ file1.sldprt        │  │  │ file3.sldprt        │            │
│  │ file2.sldprt        │ ─┼─▶│ file4.sldprt        │            │
│  │ file5.sldprt        │ ◀┼─ │                     │            │
│  │                     │  │  │                     │            │
│  └─────────────────────┘  │  └─────────────────────┘            │
│       [Add ▶]  [◀ Remove] │                                     │
├───────────────────────────┴─────────────────────────────────────┤
│  [▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░] 45%                          │
│                                                    [Start Copy] │
└─────────────────────────────────────────────────────────────────┘
```

---

## Dependencies

### NuGet Packages
- `System.Data.OleDb` - Excel file reading
- `System.Text.Json` - Config file serialization (built-in)

### External Requirements
- Microsoft Access Database Engine 2016 (or later) for Excel OleDb

---

## File Structure

```
BomCopier/
├── BomCopier.sln
├── BomCopier/
│   ├── BomCopier.csproj
│   ├── Program.cs
│   ├── BomCopierForm.cs
│   ├── BomCopierForm.Designer.cs
│   ├── SettingsWindow.cs
│   ├── SettingsWindow.Designer.cs
│   ├── Models/
│   │   ├── BomRow.cs
│   │   └── AppConfig.cs
│   └── Services/
│       ├── ConfigService.cs
│       └── ExcelService.cs
├── config.json
└── log.txt
```

---

## Build Order (Recommended)

### Phase 1: Foundation
1. Create solution and project structure
2. Implement `AppConfig` model
3. Implement `ConfigService` (load/save config.json)
4. Build `SettingsWindow` form

### Phase 2: Data Layer
5. Implement `BomRow` model
6. Implement `ExcelService` (OleDb Excel parsing)

### Phase 3: Main UI
7. Build `BomCopierForm` layout
8. Wire up Load BOM button and Excel loading
9. Implement material dropdown population
10. Build dual-panel list management

### Phase 4: Copy Logic
11. Implement file copy logic with progress
12. Add logging functionality
13. Create post-copy summary dialog

### Phase 5: Polish
14. Add error handling throughout
15. Implement live search filtering
16. Add drag-and-drop for BOM file
17. Testing and bug fixes

---

## Error Handling Strategy

| Scenario | Handling |
|----------|----------|
| Missing config.json | Auto-open Settings dialog |
| Invalid Excel file | MessageBox with error details |
| Source file not found | Log and skip, continue with others |
| Target file exists (no overwrite) | Log and skip |
| Target directory doesn't exist | Create it automatically |
| Copy failure | Log error, show in summary |

---

## Logging Format

```
[2024-01-15 14:32:01] Copy session started
[2024-01-15 14:32:01] Source: C:\CAD\Parts
[2024-01-15 14:32:01] Target: C:\Projects\Job123
[2024-01-15 14:32:02] COPIED: part001.sldprt
[2024-01-15 14:32:02] COPIED: part002.sldprt (overwritten)
[2024-01-15 14:32:03] SKIPPED: part003.sldprt (not found in source)
[2024-01-15 14:32:03] ERROR: part004.sldprt - Access denied
[2024-01-15 14:32:03] Session complete: 2 copied, 1 skipped, 1 error
```
