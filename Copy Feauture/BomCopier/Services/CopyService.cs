using BomCopier.Models;

namespace BomCopier.Services
{
    public class CopyResult
    {
        public int Copied { get; set; }
        public int Skipped { get; set; }
        public int Errors { get; set; }
        public List<string> ErrorMessages { get; } = new();
    }

    public class CopyService
    {
        public event Action<int, int, string>? ProgressChanged;

        public CopyResult CopyFiles(List<BomRow> files, string targetDirectory, bool overwrite)
        {
            var result = new CopyResult();
            int total = files.Count;
            int current = 0;

            // Ensure target directory exists
            if (!Directory.Exists(targetDirectory))
            {
                try
                {
                    Directory.CreateDirectory(targetDirectory);
                    LogService.Log($"Created target directory: {targetDirectory}");
                }
                catch (Exception ex)
                {
                    LogService.Log($"Failed to create target directory: {ex.Message}");
                    result.Errors = total;
                    result.ErrorMessages.Add($"Cannot create target directory: {ex.Message}");
                    return result;
                }
            }

            LogService.LogSessionStart(
                files.FirstOrDefault()?.SourcePath ?? "Unknown",
                targetDirectory,
                total);

            foreach (var file in files)
            {
                current++;
                ProgressChanged?.Invoke(current, total, file.TargetFileName);

                // Skip files that weren't found
                if (!file.IsFound || string.IsNullOrEmpty(file.SourcePath))
                {
                    LogService.LogSkipped(file.TargetFileName, "Source file not found");
                    result.Skipped++;
                    continue;
                }

                string targetPath = Path.Combine(targetDirectory, file.TargetFileName);

                try
                {
                    // Check if target exists
                    bool targetExists = File.Exists(targetPath);

                    if (targetExists && !overwrite)
                    {
                        LogService.LogSkipped(file.TargetFileName, "Target exists (overwrite disabled)");
                        result.Skipped++;
                        continue;
                    }

                    // Copy the file
                    File.Copy(file.SourcePath, targetPath, overwrite);
                    LogService.LogCopied(file.TargetFileName, targetExists);
                    result.Copied++;
                }
                catch (Exception ex)
                {
                    LogService.LogError(file.TargetFileName, ex.Message);
                    result.Errors++;
                    result.ErrorMessages.Add($"{file.TargetFileName}: {ex.Message}");
                }
            }

            LogService.LogSessionEnd(result.Copied, result.Skipped, result.Errors);
            return result;
        }
    }
}
