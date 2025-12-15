namespace BomCopier.Models
{
    public class AppConfig
    {
        // Column indices (1-based for user-friendly display, converted to 0-based in code)
        public int DocumentNameColumn { get; set; } = 2;   // Column B
        public int MaterialColumn { get; set; } = 12;      // Column L
        public int QuantityColumn { get; set; } = 6;       // Column F
        public int HeaderRows { get; set; } = 2;           // Rows to skip (title + header)

        // File naming settings
        // BOM files have extension like .SLDPRT which gets replaced
        public string BomFileExtension { get; set; } = ".SLDPRT";
        // Target files are named: basename + suffix + extension (e.g., "partnameFLO.dwg")
        public string FilenameSuffix { get; set; } = "FLO";
        public string TargetFileExtension { get; set; } = ".dwg";

        // Copy behavior
        public bool OverwriteExisting { get; set; } = true;

        // Directories
        public string SourceDirectory { get; set; } = "";
        public string TargetDirectory { get; set; } = "";

        // Last used BOM file
        public string LastBomFile { get; set; } = "";
    }
}
