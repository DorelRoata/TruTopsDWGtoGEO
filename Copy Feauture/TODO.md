# BOM Copier - Implementation TODO List

## Phase 1: Project Setup & Foundation

### 1.1 Project Structure
- [ ] Create new Visual Studio solution `BomCopier.sln`
- [ ] Create WinForms project targeting .NET 6+ (Windows)
- [ ] Create `Models/` folder
- [ ] Create `Services/` folder
- [ ] Add `System.Data.OleDb` NuGet package
- [ ] Configure project for Windows-only deployment

### 1.2 Configuration Model
- [ ] Create `Models/AppConfig.cs`
  - [ ] Add `FileNameColumn` property (int, default: 1)
  - [ ] Add `QuantityColumn` property (int, default: 3)
  - [ ] Add `MaterialColumn` property (int, default: 5)
  - [ ] Add `HandednessColumn` property (int, default: 7)
  - [ ] Add `OverwriteExisting` property (bool, default: true)
  - [ ] Add `SourceDirectory` property (string)
  - [ ] Add `TargetDirectory` property (string)

### 1.3 Configuration Service
- [ ] Create `Services/ConfigService.cs`
- [ ] Implement `LoadConfig()` method
  - [ ] Check if `config.json` exists
  - [ ] Deserialize JSON to `AppConfig` object
  - [ ] Return default config if file missing
- [ ] Implement `SaveConfig(AppConfig config)` method
  - [ ] Serialize `AppConfig` to JSON
  - [ ] Write to `config.json` with pretty formatting
- [ ] Add error handling for corrupt config files

---

## Phase 2: Settings Window

### 2.1 Settings Form Design
- [ ] Create `SettingsWindow.cs` (modal Form)
- [ ] Add form properties:
  - [ ] Size: 400 x 350 pixels
  - [ ] FormBorderStyle: FixedDialog
  - [ ] StartPosition: CenterParent
  - [ ] Text: "Settings"

### 2.2 Settings UI Controls
- [ ] Add GroupBox "Column Mappings"
  - [ ] Label + NumericUpDown for "File Name Column"
  - [ ] Label + NumericUpDown for "Quantity Column"
  - [ ] Label + NumericUpDown for "Material Column"
  - [ ] Label + NumericUpDown for "Handedness Column (optional)"
- [ ] Add GroupBox "Options"
  - [ ] CheckBox for "Overwrite existing files"
- [ ] Add Save button
- [ ] Add Cancel button

### 2.3 Settings Form Logic
- [ ] Implement `LoadConfigToForm()` - populate controls from config
- [ ] Implement `SaveFormToConfig()` - read controls and save
- [ ] Add validation (column indices must be > 0)
- [ ] Show warning for duplicate column indices
- [ ] Wire up Save button click event
- [ ] Wire up Cancel button click event
- [ ] Set DialogResult appropriately

---

## Phase 3: Data Model & Excel Service

### 3.1 BOM Row Model
- [ ] Create `Models/BomRow.cs`
  - [ ] Add `FileName` property (string)
  - [ ] Add `Material` property (string)
  - [ ] Add `Quantity` property (int)
  - [ ] Add `Handedness` property (string, nullable)
  - [ ] Override `ToString()` for display in ListBox

### 3.2 Excel Service
- [ ] Create `Services/ExcelService.cs`
- [ ] Implement `LoadExcel(string filePath, AppConfig config)` method
  - [ ] Build OleDb connection string for Excel
  - [ ] Open connection to Excel file
  - [ ] Query first sheet (or named sheet)
  - [ ] Read rows into `List<BomRow>`
  - [ ] Map columns based on config indices
  - [ ] Close connection properly
- [ ] Add error handling:
  - [ ] File not found
  - [ ] Invalid Excel format
  - [ ] Column index out of range
  - [ ] Empty file

### 3.3 Excel Service Helpers
- [ ] Implement `GetSheetNames(string filePath)` - list available sheets
- [ ] Implement `GetColumnCount(string filePath)` - for validation
- [ ] Handle both `.xls` and `.xlsx` formats

---

## Phase 4: Main Form Layout

### 4.1 Main Form Design
- [ ] Create/modify `BomCopierForm.cs`
- [ ] Set form properties:
  - [ ] Size: 900 x 650 pixels (adjust as needed)
  - [ ] Text: "BOM Copier"
  - [ ] StartPosition: CenterScreen

### 4.2 Top Section - Controls
- [ ] Add "Load BOM" button (top-left)
- [ ] Add "Material:" label
- [ ] Add Material ComboBox (dropdown)
- [ ] Add "Settings" button (top-right)

### 4.3 Directory Section
- [ ] Add "Source Directory:" label
- [ ] Add Source Directory TextBox
- [ ] Add Source "Browse" button
- [ ] Add "Target Directory:" label
- [ ] Add Target Directory TextBox
- [ ] Add Target "Browse" button

### 4.4 Dual Panel Section
- [ ] Add "Available Files" label (left side)
- [ ] Add Source Search TextBox (left side)
- [ ] Add Source ListBox (left side)
- [ ] Add "Copy Queue" label (right side)
- [ ] Add Queue Search TextBox (right side)
- [ ] Add Queue ListBox (right side)
- [ ] Add "Add >>" button (between panels)
- [ ] Add "<< Remove" button (between panels)

### 4.5 Bottom Section
- [ ] Add ProgressBar (full width)
- [ ] Add Status Label (shows current operation)
- [ ] Add "Start Copy" button (bottom-right)

---

## Phase 5: Main Form Logic - Data Loading

### 5.1 Initialization
- [ ] Implement `Form_Load` event handler
  - [ ] Load config via ConfigService
  - [ ] If config missing, show SettingsWindow
  - [ ] Populate SourceDirectory and TargetDirectory from config
- [ ] Implement Settings button click
  - [ ] Show SettingsWindow as modal dialog
  - [ ] Reload config if user saved changes

### 5.2 BOM Loading
- [ ] Implement Load BOM button click
  - [ ] Show OpenFileDialog (filter: *.xlsx, *.xls)
  - [ ] Call ExcelService.LoadExcel()
  - [ ] Store result in `List<BomRow> bomData`
  - [ ] Call PopulateMaterials()
  - [ ] Show success/error message

### 5.3 Material Filtering
- [ ] Implement `PopulateMaterials()` method
  - [ ] Extract unique materials from bomData
  - [ ] Sort alphabetically
  - [ ] Populate Material ComboBox
  - [ ] Add "All" option at top (optional)
- [ ] Implement Material ComboBox SelectedIndexChanged
  - [ ] Filter bomData by selected material
  - [ ] Populate Source ListBox with matching files
  - [ ] Clear Queue ListBox

---

## Phase 6: Main Form Logic - List Management

### 6.1 Directory Browsing
- [ ] Implement Source Browse button click
  - [ ] Show FolderBrowserDialog
  - [ ] Update Source TextBox
  - [ ] Save to config
- [ ] Implement Target Browse button click
  - [ ] Show FolderBrowserDialog
  - [ ] Update Target TextBox
  - [ ] Save to config

### 6.2 Queue Management
- [ ] Implement "Add >>" button click
  - [ ] Get selected items from Source ListBox
  - [ ] Add to Queue ListBox
  - [ ] Remove from Source ListBox (optional - or just mark)
- [ ] Implement "<< Remove" button click
  - [ ] Get selected items from Queue ListBox
  - [ ] Remove from Queue ListBox
  - [ ] Add back to Source ListBox (if removed earlier)
- [ ] Implement double-click on Source ListBox to add
- [ ] Implement double-click on Queue ListBox to remove

### 6.3 Live Search
- [ ] Implement Source Search TextBox TextChanged
  - [ ] Filter Source ListBox items by search term
  - [ ] Case-insensitive matching
- [ ] Implement Queue Search TextBox TextChanged
  - [ ] Filter Queue ListBox items by search term
  - [ ] Case-insensitive matching
- [ ] Preserve full data while showing filtered view

---

## Phase 7: Copy Logic

### 7.1 Pre-Copy Validation
- [ ] Implement `ValidateBeforeCopy()` method
  - [ ] Check Source Directory exists
  - [ ] Check Target Directory exists (or create it)
  - [ ] Check Queue is not empty
  - [ ] Return validation result with error messages

### 7.2 Copy Execution
- [ ] Implement "Start Copy" button click
  - [ ] Run validation
  - [ ] Show confirmation dialog with file count
  - [ ] Disable UI controls during copy
  - [ ] Call ExecuteCopy() async
  - [ ] Re-enable controls when done

### 7.3 ExecuteCopy Implementation
- [ ] Implement `ExecuteCopy()` async method
  - [ ] Initialize counters (copied, skipped, errors)
  - [ ] Set ProgressBar maximum to queue count
  - [ ] Loop through Queue items:
    - [ ] Build source path (SourceDir + FileName)
    - [ ] Build target path (TargetDir + FileName)
    - [ ] Check if source file exists
    - [ ] Check if target exists and OverwriteExisting flag
    - [ ] Call File.Copy() with overwrite parameter
    - [ ] Update ProgressBar value
    - [ ] Update Status Label
    - [ ] Log each operation
  - [ ] Catch and log exceptions per file
  - [ ] Return copy summary

### 7.4 Post-Copy
- [ ] Show summary MessageBox (X copied, Y skipped, Z errors)
- [ ] Clear Queue ListBox (optional)
- [ ] Reset ProgressBar to 0

---

## Phase 8: Logging

### 8.1 Log Service
- [ ] Create `Services/LogService.cs` (or add to existing service)
- [ ] Implement `Log(string message)` method
  - [ ] Format: `[yyyy-MM-dd HH:mm:ss] message`
  - [ ] Append to `log.txt`
- [ ] Implement `LogSessionStart(string source, string target)`
- [ ] Implement `LogCopied(string fileName, bool overwritten)`
- [ ] Implement `LogSkipped(string fileName, string reason)`
- [ ] Implement `LogError(string fileName, string error)`
- [ ] Implement `LogSessionEnd(int copied, int skipped, int errors)`

### 8.2 Integrate Logging
- [ ] Log session start in ExecuteCopy
- [ ] Log each file operation
- [ ] Log session end with summary
- [ ] Log errors and exceptions

---

## Phase 9: Polish & Error Handling

### 9.1 Error Handling
- [ ] Add try-catch around Excel loading
- [ ] Add try-catch around file copy operations
- [ ] Add try-catch around config operations
- [ ] Show user-friendly error messages
- [ ] Log all errors with stack traces

### 9.2 UI Polish
- [ ] Add keyboard shortcuts (Enter to add, Delete to remove)
- [ ] Add multi-select support for ListBoxes
- [ ] Add tooltips to buttons
- [ ] Add status bar at bottom (optional)
- [ ] Disable "Start Copy" when queue empty
- [ ] Disable "Add" when nothing selected

### 9.3 Drag and Drop
- [ ] Enable AllowDrop on form
- [ ] Implement DragEnter event (check for Excel files)
- [ ] Implement DragDrop event (load dropped Excel file)

---

## Phase 10: Testing & Final

### 10.1 Testing
- [ ] Test with various Excel formats (.xls, .xlsx)
- [ ] Test with missing columns
- [ ] Test with empty BOM
- [ ] Test overwrite on/off
- [ ] Test with non-existent source files
- [ ] Test with locked/in-use files
- [ ] Test with very long file names
- [ ] Test with special characters in file names

### 10.2 Documentation
- [ ] Update README with final instructions
- [ ] Add inline code comments where needed
- [ ] Document any known limitations

### 10.3 Deployment
- [ ] Create Release build
- [ ] Test on clean Windows machine
- [ ] Create installer (optional)
- [ ] Document dependencies (Access Database Engine)

---

## Future Enhancements (Post v1.0)

- [ ] Auto-create material-named subfolders in target
- [ ] Preview duplicate files before copy
- [ ] SolidWorks API integration
- [ ] Backup files before overwrite
- [ ] Auto-open target folder after copy
- [ ] Remember last used directories
- [ ] Sort options for ListBoxes (alpha, date, size)
- [ ] Export copy log to CSV
- [ ] Dark mode theme (optional)

---

## Notes

- Always copy config.example.json to config.json before first run
- Access Database Engine must be installed for Excel support
- Test with real BOM exports before production use
