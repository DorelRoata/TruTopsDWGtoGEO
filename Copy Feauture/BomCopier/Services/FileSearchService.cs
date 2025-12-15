using BomCopier.Models;

namespace BomCopier.Services
{
    public class FileSearchService
    {
        private Dictionary<string, string>? _fileMap;

        /// <summary>
        /// Search for files in source directory and expand BomRows to include both normal and FLO versions if found
        /// </summary>
        public List<BomRow> FindFiles(List<BomRow> rows, string sourceDirectory)
        {
            var expandedRows = new List<BomRow>();

            if (string.IsNullOrWhiteSpace(sourceDirectory) || !Directory.Exists(sourceDirectory))
            {
                LogService.Log($"Source directory invalid or doesn't exist: {sourceDirectory}");
                // Return original rows with no files found
                return rows;
            }

            // Build a dictionary of all files in source directory (recursive)
            _fileMap = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);

            try
            {
                foreach (var file in Directory.EnumerateFiles(sourceDirectory, "*.*", SearchOption.AllDirectories))
                {
                    string fileName = Path.GetFileName(file);
                    // If multiple files have same name, keep the first one found
                    if (!_fileMap.ContainsKey(fileName))
                    {
                        _fileMap[fileName] = file;
                    }
                }

                LogService.Log($"Indexed {_fileMap.Count} files in source directory");
            }
            catch (Exception ex)
            {
                LogService.Log($"Error scanning source directory: {ex.Message}");
                return rows;
            }

            // For each BOM row, create separate entries for each found file variant
            int foundNormal = 0;
            int foundSuffix = 0;
            int notFound = 0;

            foreach (var row in rows)
            {
                bool foundAny = false;

                // Check for normal version (e.g., partname.dwg)
                if (_fileMap.TryGetValue(row.NormalFileName, out string? normalPath))
                {
                    expandedRows.Add(new BomRow
                    {
                        OriginalFileName = row.OriginalFileName,
                        NormalFileName = row.NormalFileName,
                        SuffixFileName = row.SuffixFileName,
                        TargetFileName = row.NormalFileName,
                        Material = row.Material,
                        Quantity = row.Quantity,
                        SourcePath = normalPath,
                        IsSuffixVersion = false
                    });
                    foundNormal++;
                    foundAny = true;
                }

                // Check for suffix/FLO version (e.g., partnameFLO.dwg)
                if (_fileMap.TryGetValue(row.SuffixFileName, out string? suffixPath))
                {
                    expandedRows.Add(new BomRow
                    {
                        OriginalFileName = row.OriginalFileName,
                        NormalFileName = row.NormalFileName,
                        SuffixFileName = row.SuffixFileName,
                        TargetFileName = row.SuffixFileName,
                        Material = row.Material,
                        Quantity = row.Quantity,
                        SourcePath = suffixPath,
                        IsSuffixVersion = true
                    });
                    foundSuffix++;
                    foundAny = true;
                }

                // If neither found, add a "not found" entry with normal filename
                if (!foundAny)
                {
                    expandedRows.Add(new BomRow
                    {
                        OriginalFileName = row.OriginalFileName,
                        NormalFileName = row.NormalFileName,
                        SuffixFileName = row.SuffixFileName,
                        TargetFileName = row.NormalFileName,
                        Material = row.Material,
                        Quantity = row.Quantity,
                        SourcePath = null,
                        IsSuffixVersion = false
                    });
                    notFound++;
                }
            }

            LogService.Log($"File matching complete: {foundNormal} normal, {foundSuffix} FLO suffix, {notFound} not found (total entries: {expandedRows.Count})");
            return expandedRows;
        }

        /// <summary>
        /// Filter rows by material and return only found files
        /// </summary>
        public List<BomRow> FilterByMaterial(List<BomRow> rows, string material)
        {
            if (string.IsNullOrWhiteSpace(material) || material == "(All)")
            {
                return rows.ToList();
            }

            return rows.Where(r => r.Material == material).ToList();
        }
    }
}
