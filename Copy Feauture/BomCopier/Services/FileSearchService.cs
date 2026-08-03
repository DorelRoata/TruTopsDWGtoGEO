using BomCopier.Models;

namespace BomCopier.Services
{
    public class FileSearchService
    {
        /// <summary>
        /// Resolve every BOM row to normal and suffix/FLO drawing candidates.
        /// </summary>
        public List<BomRow> FindFiles(
            IReadOnlyCollection<BomRow> rows,
            string sourceDirectory,
            string targetExtension)
        {
            var resolvedRows = new List<BomRow>();

            if (string.IsNullOrWhiteSpace(sourceDirectory) || !Directory.Exists(sourceDirectory))
            {
                LogService.Log($"Source directory invalid or doesn't exist: {sourceDirectory}");
                return resolvedRows;
            }

            var fileMap = BuildFileMap(sourceDirectory, targetExtension);
            if (fileMap == null)
            {
                return resolvedRows;
            }

            int foundNormal = 0;
            int foundSuffix = 0;
            int ambiguous = 0;

            foreach (var row in rows)
            {
                var normal = CreateResolvedRow(row, row.NormalFileName, false, fileMap);
                resolvedRows.Add(normal);
                if (normal.IsFound)
                {
                    foundNormal++;
                }
                else if (normal.IsAmbiguous)
                {
                    ambiguous++;
                }

                if (!string.IsNullOrWhiteSpace(row.SuffixFileName) &&
                    !row.SuffixFileName.Equals(row.NormalFileName, StringComparison.OrdinalIgnoreCase))
                {
                    var suffix = CreateResolvedRow(row, row.SuffixFileName, true, fileMap);
                    resolvedRows.Add(suffix);
                    if (suffix.IsFound)
                    {
                        foundSuffix++;
                    }
                    else if (suffix.IsAmbiguous)
                    {
                        ambiguous++;
                    }
                }
            }

            LogService.Log(
                $"File matching complete: {foundNormal} normal, {foundSuffix} suffix, " +
                $"{ambiguous} ambiguous (total candidates: {resolvedRows.Count})");
            return resolvedRows;
        }

        /// <summary>
        /// Load all files from a source directory without a BOM.
        /// </summary>
        public List<BomRow> LoadFilesFromDirectory(string sourceDirectory, string targetExtension)
        {
            var rows = new List<BomRow>();

            if (string.IsNullOrWhiteSpace(sourceDirectory) || !Directory.Exists(sourceDirectory))
            {
                LogService.Log($"Source directory invalid or doesn't exist: {sourceDirectory}");
                return rows;
            }

            string extension = string.IsNullOrWhiteSpace(targetExtension) ? ".dwg" : targetExtension.Trim();
            if (!extension.StartsWith('.'))
            {
                extension = "." + extension;
            }

            var fileMap = BuildFileMap(sourceDirectory, extension);
            if (fileMap == null)
            {
                return rows;
            }

            foreach (var entry in fileMap.OrderBy(kvp => kvp.Key))
            {
                string fileName = entry.Key;
                var matches = entry.Value;

                rows.Add(new BomRow
                {
                    OriginalFileName = Path.GetFileNameWithoutExtension(fileName),
                    NormalFileName = fileName,
                    SuffixFileName = string.Empty,
                    TargetFileName = fileName,
                    Material = string.Empty,
                    Quantity = 1,
                    SourcePath = matches.Count == 1 ? matches[0] : null,
                    MatchCount = matches.Count,
                    IsSuffixVersion = false
                });
            }

            LogService.Log($"Loaded {rows.Count} files from source directory (no BOM)");
            return rows;
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

        private static BomRow CreateResolvedRow(
            BomRow source,
            string targetFileName,
            bool isSuffixVersion,
            Dictionary<string, List<string>> fileMap)
        {
            fileMap.TryGetValue(targetFileName, out var matches);
            int matchCount = matches?.Count ?? 0;

            return new BomRow
            {
                OriginalFileName = source.OriginalFileName,
                NormalFileName = source.NormalFileName,
                SuffixFileName = source.SuffixFileName,
                TargetFileName = targetFileName,
                Material = source.Material,
                Quantity = source.Quantity,
                SourcePath = matchCount == 1 ? matches![0] : null,
                MatchCount = matchCount,
                IsSuffixVersion = isSuffixVersion
            };
        }

        private static Dictionary<string, List<string>>? BuildFileMap(
            string sourceDirectory,
            string targetExtension)
        {
            string extension = string.IsNullOrWhiteSpace(targetExtension) ? ".dwg" : targetExtension.Trim();
            if (!extension.StartsWith('.'))
            {
                extension = "." + extension;
            }

            var fileMap = new Dictionary<string, List<string>>(StringComparer.OrdinalIgnoreCase);

            try
            {
                foreach (string file in EnumerateFilesSafely(sourceDirectory, "*" + extension))
                {
                    string fileName = Path.GetFileName(file);
                    if (!fileMap.TryGetValue(fileName, out var matches))
                    {
                        matches = new List<string>();
                        fileMap[fileName] = matches;
                    }

                    matches.Add(file);
                }

                foreach (var matches in fileMap.Values)
                {
                    matches.Sort(StringComparer.OrdinalIgnoreCase);
                }

                int duplicateNames = fileMap.Count(entry => entry.Value.Count > 1);
                LogService.Log(
                    $"Indexed {fileMap.Count} drawing names; {duplicateNames} have duplicate source matches");
                return fileMap;
            }
            catch (Exception ex)
            {
                LogService.Log($"Error scanning source directory: {ex.Message}");
                return null;
            }
        }

        private static IEnumerable<string> EnumerateFilesSafely(string rootDirectory, string pattern)
        {
            var pending = new Stack<string>();
            pending.Push(rootDirectory);

            while (pending.Count > 0)
            {
                string directory = pending.Pop();

                IEnumerable<string> files;
                try
                {
                    files = Directory.EnumerateFiles(directory, pattern, SearchOption.TopDirectoryOnly).ToList();
                }
                catch (Exception ex) when (ex is UnauthorizedAccessException or IOException)
                {
                    LogService.Log($"Skipped unreadable folder: {directory} ({ex.Message})");
                    continue;
                }

                foreach (string file in files)
                {
                    yield return file;
                }

                IEnumerable<string> subdirectories;
                try
                {
                    subdirectories = Directory.EnumerateDirectories(directory).ToList();
                }
                catch (Exception ex) when (ex is UnauthorizedAccessException or IOException)
                {
                    LogService.Log($"Could not list subfolders: {directory} ({ex.Message})");
                    continue;
                }

                foreach (string subdirectory in subdirectories)
                {
                    pending.Push(subdirectory);
                }
            }
        }
    }
}
