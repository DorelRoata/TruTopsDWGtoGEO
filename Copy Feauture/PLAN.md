# BOM Copier - Implementation Plan

## Project Overview
Create a C# WinForms application to copy DWG files based on Excel BOM data, with material filtering and dual-panel file management.

## Key Requirements (Confirmed)
- **Language**: C# WinForms (.NET 6+ Windows)
- **File Type**: DWG files (convert .SLDPRT names in BOM to .dwg)
- **Search**: Recursive (include subfolders)
- **BOM Format** (from sample 4711-100-FOR DOREL.xlsx):
  - Header row: Row 1 (0-indexed)
  - Data starts: Row 2
  - Document Name: Column B (index 1)
  - Material: Column L (index 11) - "Material (Cust Property)"
  - Quantity: Column F (index 5) - "QTY (AUTO)"

## Project Location
`D:\Coding\TruTopsDWGtoGEO\Copy Feauture\BomCopier\`

## Implementation Phases

### Phase 1: Project Setup
1. Create solution `BomCopier.sln` in `Copy Feauture\`
2. Create WinForms project targeting .NET 6-windows
3. Add NuGet packages:
   - `EPPlus` (for Excel reading - easier than OleDb)
   - `System.Text.Json` (built-in)
4. Create folder structure:
   ```
   BomCopier/
   ├── Models/
   ├── Services/
   └── Forms/
   ```

### Phase 2: Models
**Files to create:**
- `Models/AppConfig.cs` - Configuration settings
- `Models/BomRow.cs` - Single BOM entry

```csharp
// AppConfig.cs
public class AppConfig
{
    public int DocumentNameColumn { get; set; } = 2;  // Column B (1-based)
    public int MaterialColumn { get; set; } = 12;     // Column L
    public int QuantityColumn { get; set; } = 6;      // Column F
    public int HeaderRow { get; set; } = 2;           // Skip first 2 rows
    public bool OverwriteExisting { get; set; } = true;
    public string SourceDirectory { get; set; } = "";
    public string TargetDirectory { get; set; } = "";
    public string SourceFileExtension { get; set; } = ".dwg";
    public string BomFileExtension { get; set; } = ".SLDPRT";
}

// BomRow.cs
public class BomRow
{
    public string FileName { get; set; }      // Original from BOM
    public string DwgFileName { get; set; }   // Converted to .dwg
    public string Material { get; set; }
    public int Quantity { get; set; }
    public string FullSourcePath { get; set; } // Found path in source
}
```

### Phase 3: Services
**Files to create:**
- `Services/ConfigService.cs` - Load/save config.json
- `Services/ExcelService.cs` - Parse Excel BOM files
- `Services/FileSearchService.cs` - Recursive file search
- `Services/CopyService.cs` - File copy with progress
- `Services/LogService.cs` - Logging to log.txt

### Phase 4: Settings Form
**File:** `Forms/SettingsForm.cs`

UI Elements:
- GroupBox "Column Mapping" with NumericUpDown controls:
  - Document Name Column
  - Material Column
  - Quantity Column
  - Header Row (rows to skip)
- GroupBox "File Extensions":
  - Source Extension (.dwg)
  - BOM Extension (.SLDPRT) - for replacement
- CheckBox "Overwrite existing files"
- Save/Cancel buttons

### Phase 5: Main Form
**File:** `Forms/MainForm.cs`

Layout:
```
┌─────────────────────────────────────────────────────────────┐
│  BOM Copier                                        [Settings]│
├─────────────────────────────────────────────────────────────┤
│  [Load BOM]  Material: [▼ dropdown ▼]  Files: 0 matched     │
├─────────────────────────────────────────────────────────────┤
│  Source: [_______________________________] [Browse]          │
│  Target: [_______________________________] [Browse]          │
├────────────────────────┬────────────────────────────────────┤
│  Available Files       │  Copy Queue                        │
│  [Search: ________]    │  [Search: ________]                │
│  ┌──────────────────┐  │  ┌──────────────────┐              │
│  │ file1.dwg        │ ─┼─▶│                  │              │
│  │ file2.dwg        │ ◀┼─ │                  │              │
│  └──────────────────┘  │  └──────────────────┘              │
│  [Add >>]  [Add All]   │  [<< Remove] [Clear]               │
├────────────────────────┴────────────────────────────────────┤
│  [▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░░░░░░] 25%  Copying file3.dwg   │
│                                              [Start Copy]   │
└─────────────────────────────────────────────────────────────┘
```

Features:
- Load BOM button → OpenFileDialog for .xlsx/.xls
- Material dropdown populated with unique materials from BOM
- Selecting material filters left panel
- Double-click or Add button moves to queue
- Live search filters both panels
- Progress bar during copy
- Status label shows current file

### Phase 6: Core Logic Flow

1. **Load BOM**:
   - Read Excel with EPPlus
   - Skip header rows per config
   - Parse each row into BomRow
   - Convert filename extension (.SLDPRT → .dwg)
   - Populate material dropdown

2. **Select Material**:
   - Filter BomRows by selected material
   - For each filtered row, search source directory recursively
   - Display found files in left panel
   - Show "not found" files differently (gray/strikethrough)

3. **Manage Queue**:
   - Move items between panels
   - Support multi-select
   - Live search filters display (not data)

4. **Execute Copy**:
   - Validate directories exist
   - Loop through queue:
     - Check source exists
     - Check target exists + overwrite flag
     - File.Copy()
     - Update progress
     - Log operation
   - Show summary dialog

### Phase 7: Polish
- Drag-drop BOM file onto form
- Keyboard shortcuts (Enter=Add, Delete=Remove)
- Remember window size/position
- Error handling throughout
- Unit tests for services

## File Summary

| File | Description |
|------|-------------|
| `BomCopier.sln` | Solution file |
| `BomCopier.csproj` | Project file |
| `Program.cs` | Entry point |
| `Models/AppConfig.cs` | Config model |
| `Models/BomRow.cs` | BOM row model |
| `Services/ConfigService.cs` | Config load/save |
| `Services/ExcelService.cs` | Excel parsing |
| `Services/FileSearchService.cs` | Recursive search |
| `Services/CopyService.cs` | Copy logic |
| `Services/LogService.cs` | Logging |
| `Forms/MainForm.cs` | Main window |
| `Forms/MainForm.Designer.cs` | Main window designer |
| `Forms/SettingsForm.cs` | Settings dialog |
| `Forms/SettingsForm.Designer.cs` | Settings designer |
| `config.json` | User settings (generated) |
| `log.txt` | Copy log (generated) |

## Dependencies
- .NET 6.0 SDK (Windows)
- EPPlus NuGet package (Excel reading)
- No external runtime dependencies

## Notes
- Extension mapping is configurable (.SLDPRT → .dwg)
- Header rows configurable (default: skip 2)
- All column indices are 1-based in UI, 0-based in code
- Recursive search enabled by default
