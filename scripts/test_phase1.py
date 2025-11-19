#!/usr/bin/env python3
"""
Test script to verify Phase 1 completion.
"""
import os
import json
from pathlib import Path

def test_directory_structure():
    """Test that all required directories exist."""
    print("Testing directory structure...")
    
    required_dirs = [
        "udcpr_master_data/staging_rules",
        "udcpr_master_data/approved_rules",
        "udcpr_master_data/raw_text",
        "udcpr_master_data/images",
        "udcpr_master_data/tables",
        "udcpr_master_data/logs",
        "admin_ui",
        "admin_ui/public"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"  ✓ {dir_path}")
        else:
            print(f"  ✗ {dir_path} - MISSING")
            all_exist = False
    
    return all_exist

def test_candidate_files():
    """Test that candidate files were generated."""
    print("\nTesting candidate files...")
    
    staging_dir = Path("udcpr_master_data/staging_rules")
    if not staging_dir.exists():
        print("  ✗ Staging directory not found")
        return False
    
    json_files = list(staging_dir.glob("*.json"))
    
    if len(json_files) == 0:
        print("  ✗ No candidate files found")
        return False
    
    total_candidates = 0
    for file in json_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            count = len(data) if isinstance(data, list) else 1
            total_candidates += count
            print(f"  ✓ {file.name}: {count} candidates")
    
    print(f"\n  Total candidates: {total_candidates}")
    return total_candidates > 0

def test_admin_ui_files():
    """Test that admin UI files exist."""
    print("\nTesting admin UI files...")
    
    required_files = [
        "admin_ui/server.js",
        "admin_ui/package.json",
        "admin_ui/public/index.html"
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} - MISSING")
            all_exist = False
    
    return all_exist

def test_admin_ui_dependencies():
    """Test that admin UI dependencies are installed."""
    print("\nTesting admin UI dependencies...")
    
    node_modules = Path("admin_ui/node_modules")
    if node_modules.exists():
        print(f"  ✓ node_modules exists")
        return True
    else:
        print(f"  ✗ node_modules not found - run 'npm install' in admin_ui/")
        return False

def test_ingestion_scripts():
    """Test that ingestion scripts exist."""
    print("\nTesting ingestion scripts...")
    
    required_scripts = [
        "scripts/preflight.py",
        "scripts/mock_ingestion.py",
        "scripts/publish_to_mongo.py",
        "ingestion/pdf_to_images_and_ocr.py",
        "ingestion/extract_tables.py",
        "ingestion/llm_parse_worker.py"
    ]
    
    all_exist = True
    for script_path in required_scripts:
        if Path(script_path).exists():
            print(f"  ✓ {script_path}")
        else:
            print(f"  ✗ {script_path} - MISSING")
            all_exist = False
    
    return all_exist

def main():
    print("="*60)
    print("UDCPR Master - Phase 1 Verification")
    print("="*60)
    print()
    
    results = {
        "Directory Structure": test_directory_structure(),
        "Candidate Files": test_candidate_files(),
        "Admin UI Files": test_admin_ui_files(),
        "Admin UI Dependencies": test_admin_ui_dependencies(),
        "Ingestion Scripts": test_ingestion_scripts()
    }
    
    print("\n" + "="*60)
    print("PHASE 1 TEST RESULTS")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:.<40} {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("✓ PHASE 1 COMPLETE!")
        print("="*60)
        print("\nAll components are ready:")
        print("  1. ✓ Ingestion pipeline (mock data generated)")
        print("  2. ✓ Admin UI (React-based verification interface)")
        print("  3. ✓ Directory structure")
        print("  4. ✓ All scripts in place")
        print("\nNext steps:")
        print("  1. Start admin UI: cd admin_ui && npm start")
        print("  2. Access at: http://localhost:3002")
        print("  3. Verify and approve rules")
        print("  4. Run: python scripts/publish_to_mongo.py")
    else:
        print("✗ PHASE 1 INCOMPLETE")
        print("="*60)
        print("\nSome components are missing. Review the test results above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())
