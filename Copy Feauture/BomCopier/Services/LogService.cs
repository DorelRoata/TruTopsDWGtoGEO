namespace BomCopier.Services
{
    public static class LogService
    {
        private const string LOG_FILE = "log.txt";
        private static readonly object LockObj = new();

        public static void Log(string message)
        {
            string timestamp = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");
            string logLine = $"[{timestamp}] {message}";

            lock (LockObj)
            {
                try
                {
                    File.AppendAllText(LOG_FILE, logLine + Environment.NewLine);
                }
                catch
                {
                    // Silently fail if we can't write to log
                }
            }

            // Also write to debug output
            System.Diagnostics.Debug.WriteLine(logLine);
        }

        public static void LogSessionStart(string source, string target, int fileCount)
        {
            Log("========================================");
            Log("Copy session started");
            Log($"Source: {source}");
            Log($"Target: {target}");
            Log($"Files to copy: {fileCount}");
            Log("========================================");
        }

        public static void LogCopied(string fileName, bool overwritten)
        {
            string suffix = overwritten ? " (overwritten)" : "";
            Log($"COPIED: {fileName}{suffix}");
        }

        public static void LogSkipped(string fileName, string reason)
        {
            Log($"SKIPPED: {fileName} - {reason}");
        }

        public static void LogError(string fileName, string error)
        {
            Log($"ERROR: {fileName} - {error}");
        }

        public static void LogSessionEnd(int copied, int skipped, int errors)
        {
            Log("========================================");
            Log($"Session complete: {copied} copied, {skipped} skipped, {errors} errors");
            Log("========================================");
        }
    }
}
