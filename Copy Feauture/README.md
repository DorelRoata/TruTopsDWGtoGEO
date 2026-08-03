# BOM Copier

BOM Copier is a Windows desktop app for finding DWG files from an exported SolidWorks Excel BOM and copying selected drawings into a manually chosen folder. It copies files only; it never moves or deletes the source drawings.

Current version: **1.1.0**

## Workflow

1. Open **Settings** and map the document name, material, and quantity columns used by the BOM.
2. Select **Load BOM**, then choose the folder containing the DWG library.
3. Select a material exactly as it appears in the BOM, such as `7GA2B`, `7GA#3`, or `11GA2B`.
4. Choose how normal and FLO drawings should be shown.
5. Select one or more available drawings and add them to the copy queue.
6. Browse to the copy folder for this batch, then select **Copy N Files**.

The app does not create material folders. The operator chooses the destination for every batch, so the same material can be sent to different job folders as needed.

## Selection and queue controls

- Click selects one row.
- `Ctrl`+click selects individual rows.
- `Shift`+click selects a range.
- `Ctrl`+`A` selects all visible rows.
- Double-click an available row to add it to the queue.
- Double-click a queued row, or press `Delete`, to remove it.
- **Add Selected** adds the current selection.
- **Add All Filtered** adds every copyable row currently visible after the material, variant, and search filters are applied.
- Changing a filter does not clear the queue.

## Drawing variants

- **Prefer FLO** shows one drawing per BOM part. A ready FLO drawing is used when available; otherwise the normal drawing is used.
- **Normal only** shows the normal DWG candidate.
- **FLO only** shows the configured suffix variant.
- **Show both** shows both candidates so either or both can be queued.

## File status and safety

- **Ready** means exactly one matching source drawing was found.
- **Missing** means no exact filename match was found.
- **Duplicate (N)** means the same filename exists in more than one source location. It is shown for review but cannot be queued, preventing an arbitrary drawing from being copied.
- Repeated scans always start from the original BOM data and do not multiply results.
- Repeated BOM lines for the same part and material are combined and their quantities are summed.
- Successfully copied files leave the queue. Skipped or failed files remain so they can be corrected and retried.
- Copy activity is recorded in `log.txt` beside the application.

## Settings

The settings file controls:

- BOM header row count
- document name, material, and quantity column numbers
- SolidWorks filename extension from the BOM
- DWG filename suffix (default `FLO`)
- target drawing extension (default `.dwg`)
- whether an existing destination file may be overwritten
- last-used BOM, source folder, and copy folder

## Build

Requirements:

- Windows 10 or 11
- .NET 8 SDK to build from source

From the repository root:

```powershell
dotnet build "Copy Feauture\BomCopier\BomCopier.csproj" --configuration Release
```

Create a self-contained Windows x64 build:

```powershell
dotnet publish "Copy Feauture\BomCopier\BomCopier.csproj" --configuration Release --runtime win-x64 --self-contained true --output "Copy Feauture\BomCopier\publish"
```

The current project reads Excel workbooks directly through EPPlus; Microsoft Excel and the Access Database Engine are not required.

## Versioning a new build

The release version has one source of truth: `VersionPrefix` in `BomCopier/BomCopier.csproj`. For the next release, change that value (for example, from `1.1.0` to `1.1.1`) before building and publishing.

The version is automatically applied to:

- the application window title and status bar
- the assembly version
- the Windows EXE file version
- the Windows product version

After publishing, right-click `publish/BomCopier.exe`, open **Properties > Details**, and confirm the file and product versions match the number shown inside the application.
