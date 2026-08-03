namespace BomCopier.Models
{
    public class BomRow
    {
        /// <summary>
        /// Original filename from BOM (e.g., "4711-BHCS-#10-32-X-2.000L.SLDPRT")
        /// </summary>
        public string OriginalFileName { get; set; } = "";

        /// <summary>
        /// Normal filename with target extension (e.g., "partname.dwg")
        /// </summary>
        public string NormalFileName { get; set; } = "";

        /// <summary>
        /// Filename with suffix (e.g., "partnameFLO.dwg")
        /// </summary>
        public string SuffixFileName { get; set; } = "";

        /// <summary>
        /// The filename that was actually found (either Normal or Suffix)
        /// </summary>
        public string TargetFileName { get; set; } = "";

        /// <summary>
        /// Material type (e.g., "18-8 Stainless Steel", "AISI 304")
        /// </summary>
        public string Material { get; set; } = "";

        /// <summary>
        /// Quantity from BOM
        /// </summary>
        public int Quantity { get; set; }

        /// <summary>
        /// Full path to source file (populated when found in source directory)
        /// </summary>
        public string? SourcePath { get; set; }

        /// <summary>
        /// Number of source files with the requested filename. More than one match is
        /// treated as ambiguous so the app never silently copies the wrong drawing.
        /// </summary>
        public int MatchCount { get; set; }

        /// <summary>
        /// Whether the file was found in the source directory
        /// </summary>
        public bool IsFound => MatchCount == 1 && !string.IsNullOrEmpty(SourcePath);

        public bool IsAmbiguous => MatchCount > 1;

        public bool CanCopy => IsFound && !IsAmbiguous;

        /// <summary>
        /// Whether the found file is the FLO suffix version
        /// </summary>
        public bool IsSuffixVersion { get; set; }

        public override string ToString()
        {
            return $"{TargetFileName} (Qty: {Quantity})";
        }
    }
}
