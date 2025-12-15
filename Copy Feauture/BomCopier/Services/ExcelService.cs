using OfficeOpenXml;
using BomCopier.Models;

namespace BomCopier.Services
{
    public class ExcelService
    {
        static ExcelService()
        {
            // Set EPPlus license (required for EPPlus 8+)
            ExcelPackage.License.SetNonCommercialPersonal("BomCopier");
        }

        public ExcelService()
        {
        }

        public List<BomRow> LoadBom(string filePath, AppConfig config)
        {
            var rows = new List<BomRow>();

            try
            {
                using var package = new ExcelPackage(new FileInfo(filePath));
                var worksheet = package.Workbook.Worksheets.FirstOrDefault();

                if (worksheet == null)
                {
                    throw new Exception("No worksheets found in Excel file");
                }

                int rowCount = worksheet.Dimension?.Rows ?? 0;
                if (rowCount == 0)
                {
                    throw new Exception("Excel file is empty");
                }

                // Column indices (convert from 1-based config to 1-based Excel)
                int nameCol = config.DocumentNameColumn;
                int materialCol = config.MaterialColumn;
                int qtyCol = config.QuantityColumn;

                // Start after header rows
                for (int row = config.HeaderRows + 1; row <= rowCount; row++)
                {
                    string? originalName = worksheet.Cells[row, nameCol].Text?.Trim();

                    // Skip empty rows
                    if (string.IsNullOrWhiteSpace(originalName))
                        continue;

                    string material = worksheet.Cells[row, materialCol].Text?.Trim() ?? "";
                    string qtyText = worksheet.Cells[row, qtyCol].Text?.Trim() ?? "0";

                    // Parse quantity
                    int quantity = 0;
                    int.TryParse(qtyText, out quantity);

                    // Get base name (remove BOM extension)
                    string baseName = GetBaseName(originalName, config.BomFileExtension);

                    // Generate both filename variants
                    string normalName = baseName + config.TargetFileExtension;           // e.g., "partname.dwg"
                    string suffixName = baseName + config.FilenameSuffix + config.TargetFileExtension;  // e.g., "partnameFLO.dwg"

                    rows.Add(new BomRow
                    {
                        OriginalFileName = originalName,
                        NormalFileName = normalName,
                        SuffixFileName = suffixName,
                        TargetFileName = normalName,  // Default to normal, will be updated when found
                        Material = material,
                        Quantity = quantity
                    });
                }

                LogService.Log($"Loaded {rows.Count} rows from BOM: {filePath}");
            }
            catch (Exception ex)
            {
                LogService.Log($"Error loading BOM: {ex.Message}");
                throw;
            }

            return rows;
        }

        public List<string> GetUniqueMaterials(List<BomRow> rows)
        {
            return rows
                .Where(r => !string.IsNullOrWhiteSpace(r.Material))
                .Select(r => r.Material)
                .Distinct()
                .OrderBy(m => m)
                .ToList();
        }

        private string GetBaseName(string fileName, string bomExtension)
        {
            // Remove the BOM extension if present
            if (fileName.EndsWith(bomExtension, StringComparison.OrdinalIgnoreCase))
            {
                return fileName.Substring(0, fileName.Length - bomExtension.Length);
            }

            // Remove whatever extension it has
            return Path.GetFileNameWithoutExtension(fileName);
        }
    }
}
