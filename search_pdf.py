import sys

# Force stdout to utf-8
sys.stdout.reconfigure(encoding='utf-8')

keywords = ["pdmCLI", "Import", "DXF", "DWG", "Batch"]
with open("d:/Coding/TruTopsDWGtoGEO/pdf_content.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    # Only search roughly relevant sections to reduce noise
    # Checking for CLI usage or specific Import commands
    if "pdmCLI" in line or ("Import" in line and "format" in line):
        start = max(0, i - 4)
        end = min(len(lines), i + 15)
        print(f"\n--- MATCH (Line {i}) ---")
        for j in range(start, end):
            print(lines[j].strip())
