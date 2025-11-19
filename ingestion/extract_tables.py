#!/usr/bin/env python3
"""
Extract tables from PDFs using Camelot and Tabula.
"""
import os
from pathlib import Path
import camelot
import pandas as pd

WORK_DIR = Path("udcpr_master_data")
PDF_FILES = [
    "UDCPR Updated 30.01.25 with earlier provisions & corrections_compressed.pdf",
    "MUBAI-DCPR.pdf"
]

def extract_tables_from_pdf(pdf_path: str):
    """Extract tables from a PDF file."""
    pdf_name = Path(pdf_path).stem
    print(f"\n{'='*60}")
    print(f"Extracting tables: {pdf_name}")
    print(f"{'='*60}")
    
    output_dir = WORK_DIR / "tables" / pdf_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Use Camelot for table extraction (lattice mode for bordered tables)
        print("Running Camelot (lattice mode)...")
        tables = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
        print(f"  Found {len(tables)} tables (lattice)")
        
        for i, table in enumerate(tables, start=1):
            csv_path = output_dir / f"table_{i:03d}_lattice.csv"
            table.to_csv(str(csv_path))
            print(f"  ✓ Saved: {csv_path.name}")
        
        # Try stream mode for non-bordered tables
        print("Running Camelot (stream mode)...")
        tables_stream = camelot.read_pdf(pdf_path, pages='all', flavor='stream')
        print(f"  Found {len(tables_stream)} tables (stream)")
        
        for i, table in enumerate(tables_stream, start=1):
            csv_path = output_dir / f"table_{i:03d}_stream.csv"
            table.to_csv(str(csv_path))
            print(f"  ✓ Saved: {csv_path.name}")
        
        total = len(tables) + len(tables_stream)
        print(f"\n✓ Extracted {total} tables from {pdf_name}")
        
    except Exception as e:
        print(f"❌ Error extracting tables: {e}")

def main():
    print("UDCPR Master - Table Extraction")
    print("="*60)
    
    for pdf in PDF_FILES:
        if Path(pdf).exists():
            extract_tables_from_pdf(pdf)
        else:
            print(f"\n⚠️  Skipping missing file: {pdf}")
    
    print("\n" + "="*60)
    print("✓ Table extraction complete!")
    print("="*60)
    print("\nNext step: python ingestion/llm_parse_worker.py")

if __name__ == "__main__":
    main()
