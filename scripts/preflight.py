#!/usr/bin/env python3
"""
Preflight check and directory scaffolding for UDCPR Master project.
"""
import os
import sys
from pathlib import Path

# Expected PDF files
EXPECTED_PDFS = [
    "UDCPR Updated 30.01.25 with earlier provisions & corrections_compressed.pdf",
    "MUBAI-DCPR.pdf"
]

# Directory structure
WORK_DIR = "udcpr_master_data"
SUBDIRS = [
    "raw_text",
    "images", 
    "tables",
    "staging_rules",
    "approved_rules",
    "snippets",
    "tests",
    "changelogs",
    "logs",
    "deploy"
]

def check_pdfs():
    """Check if required PDF files exist."""
    print("Checking for required PDF files...")
    missing = []
    for pdf in EXPECTED_PDFS:
        if not Path(pdf).exists():
            missing.append(pdf)
            print(f"  ❌ Missing: {pdf}")
        else:
            print(f"  ✓ Found: {pdf}")
    
    if missing:
        print(f"\n⚠️  Warning: {len(missing)} PDF file(s) not found.")
        print("The ingestion pipeline will fail without these files.")
    else:
        print("\n✓ All required PDFs found!")
    
    return len(missing) == 0

def create_directories():
    """Create working directory structure."""
    print(f"\nCreating directory structure under {WORK_DIR}/...")
    
    base = Path(WORK_DIR)
    base.mkdir(exist_ok=True)
    
    for subdir in SUBDIRS:
        path = base / subdir
        path.mkdir(exist_ok=True)
        print(f"  ✓ {path}")
    
    # Create subdirectories for each PDF
    for pdf in EXPECTED_PDFS:
        pdf_name = Path(pdf).stem
        (base / "raw_text" / pdf_name).mkdir(exist_ok=True)
        (base / "raw_text" / pdf_name / "hocr").mkdir(exist_ok=True)
        (base / "images" / pdf_name).mkdir(exist_ok=True)
        (base / "tables" / pdf_name).mkdir(exist_ok=True)
    
    print(f"\n✓ Directory structure created!")

def init_git():
    """Initialize git repository if not already initialized."""
    if Path(".git").exists():
        print("\n✓ Git repository already initialized")
        return
    
    print("\nInitializing git repository...")
    os.system("git init")
    print("✓ Git initialized")

def create_env_template():
    """Create .env.template file."""
    env_content = """# MongoDB Configuration
MONGO_URI=mongodb://admin:password@localhost:27017/udcpr_master?authSource=admin

# OpenAI API (for LLM parsing and RAG)
OPENAI_API_KEY=your-openai-key-here

# JWT Secret (change in production)
JWT_SECRET=your-secret-key-here

# Environment
NODE_ENV=development

# Optional: Vector DB (if enabled)
# PINECONE_API_KEY=
# PINECONE_ENVIRONMENT=
"""
    
    with open(".env.template", "w") as f:
        f.write(env_content)
    
    print("\n✓ Created .env.template")
    print("  Copy to .env and fill in your credentials")

def main():
    print("=" * 60)
    print("UDCPR Master - Preflight Check")
    print("=" * 60)
    
    pdfs_ok = check_pdfs()
    create_directories()
    init_git()
    create_env_template()
    
    print("\n" + "=" * 60)
    if pdfs_ok:
        print("✓ Preflight complete! Ready to start ingestion.")
    else:
        print("⚠️  Preflight complete with warnings.")
        print("   Place the required PDFs in the project root before running ingestion.")
    print("=" * 60)
    
    print("\nNext steps:")
    print("  1. Copy .env.template to .env and configure")
    print("  2. Run: python ingestion/pdf_to_images_and_ocr.py")
    print("  3. Run: python ingestion/extract_tables.py")
    print("  4. Run: python ingestion/llm_parse_worker.py")

if __name__ == "__main__":
    main()
