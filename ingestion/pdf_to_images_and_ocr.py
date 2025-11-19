#!/usr/bin/env python3
"""
Convert PDFs to images and run OCR with Tesseract.
Outputs: page images, text files, and HOCR files.
"""
import os
from pathlib import Path
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

WORK_DIR = Path("udcpr_master_data")
PDF_FILES = [
    "UDCPR Updated 30.01.25 with earlier provisions & corrections_compressed.pdf",
    "MUBAI-DCPR.pdf"
]

def process_pdf(pdf_path: str):
    """Process a single PDF file."""
    pdf_name = Path(pdf_path).stem
    print(f"\n{'='*60}")
    print(f"Processing: {pdf_name}")
    print(f"{'='*60}")
    
    # Output directories
    img_dir = WORK_DIR / "images" / pdf_name
    text_dir = WORK_DIR / "raw_text" / pdf_name
    hocr_dir = text_dir / "hocr"
    
    img_dir.mkdir(parents=True, exist_ok=True)
    text_dir.mkdir(parents=True, exist_ok=True)
    hocr_dir.mkdir(parents=True, exist_ok=True)
    
    # Convert PDF to images at 300 DPI
    print(f"Converting PDF to images (300 DPI)...")
    try:
        images = convert_from_path(pdf_path, dpi=300)
        print(f"  ✓ Converted {len(images)} pages")
    except Exception as e:
        print(f"  ❌ Error converting PDF: {e}")
        return
    
    # Process each page
    for i, image in enumerate(images, start=1):
        page_num = f"{i:04d}"
        
        # Save image
        img_path = img_dir / f"page_{page_num}.png"
        image.save(img_path, "PNG")
        
        # Run OCR for text
        print(f"  Page {i}/{len(images)}: OCR...", end=" ")
        try:
            text = pytesseract.image_to_string(image, lang='eng')
            text_path = text_dir / f"page_{page_num}.txt"
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            # Generate HOCR (with bounding boxes)
            hocr = pytesseract.image_to_pdf_or_hocr(image, extension='hocr')
            hocr_path = hocr_dir / f"page_{page_num}.html"
            with open(hocr_path, 'wb') as f:
                f.write(hocr)
            
            print("✓")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n✓ Completed: {pdf_name}")
    print(f"  Images: {img_dir}")
    print(f"  Text: {text_dir}")

def main():
    print("UDCPR Master - PDF to Images & OCR")
    print("="*60)
    
    # Check if PDFs exist
    missing = [pdf for pdf in PDF_FILES if not Path(pdf).exists()]
    if missing:
        print(f"\n❌ Missing PDF files:")
        for pdf in missing:
            print(f"  - {pdf}")
        print("\nPlace PDFs in project root and try again.")
        return
    
    # Process each PDF
    for pdf in PDF_FILES:
        process_pdf(pdf)
    
    print("\n" + "="*60)
    print("✓ All PDFs processed!")
    print("="*60)
    print("\nNext step: python ingestion/extract_tables.py")

if __name__ == "__main__":
    main()
