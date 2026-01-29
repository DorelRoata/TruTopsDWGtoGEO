from pypdf import PdfReader
import sys

try:
    reader = PdfReader("d:/Coding/TruTopsDWGtoGEO/Copy Feauture/BomCopier/TCAD_EN.pdf")
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    # Save to a text file for searching
    with open("pdf_content.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print("PDF text extracted to pdf_content.txt")
except Exception as e:
    print(f"Error: {e}")
