#!/usr/bin/env python3
"""
Demo script for Rules Browser feature.
"""
import json
from pathlib import Path

def show_rules_browser_demo():
    print("="*70)
    print(" "*20 + "RULES BROWSER FEATURE")
    print("="*70)
    print()
    print("📚 New Feature: Search and Browse UDCPR/Mumbai DCPR Rules")
    print()
    
    # Count rules
    approved_dir = Path("udcpr_master_data/approved_rules")
    approved_files = list(approved_dir.glob("*.json"))
    
    udcpr_count = 0
    mumbai_count = 0
    categories = set()
    
    for file in approved_files:
        with open(file, 'r', encoding='utf-8') as f:
            rule = json.load(f)
            if rule['jurisdiction'] == 'maharashtra_udcpr':
                udcpr_count += 1
            else:
                mumbai_count += 1
            
            # Extract category from clause
            clause = rule.get('clause_number', '')
            if clause:
                chapter = clause.split('.')[0]
                categories.add(chapter)
    
    print("📊 STATISTICS:")
    print("-" * 70)
    print(f"  Total Rules: {len(approved_files)}")
    print(f"  UDCPR Rules: {udcpr_count}")
    print(f"  Mumbai DCPR Rules: {mumbai_count}")
    print(f"  Categories: {len(categories)}")
    print()
    
    print("✨ FEATURES:")
    print("-" * 70)
    print("  1. Full-Text Search")
    print("     - Search by keyword, clause number, or description")
    print("     - Real-time results")
    print("     - Case-insensitive")
    print()
    print("  2. Smart Filtering")
    print("     - Filter by jurisdiction (UDCPR / Mumbai DCPR)")
    print("     - Filter by category (FSI, Setbacks, Parking, etc.)")
    print("     - Combine multiple filters")
    print()
    print("  3. Detailed View")
    print("     - Full clause text")
    print("     - Rule logic (JSON)")
    print("     - Source PDF reference")
    print("     - Ambiguity warnings")
    print()
    print("  4. User-Friendly UI")
    print("     - Clean, modern design")
    print("     - Responsive layout")
    print("     - Color-coded badges")
    print("     - Easy navigation")
    print()
    
    print("📋 SAMPLE RULES:")
    print("-" * 70)
    
    # Show first 5 rules
    for i, file in enumerate(approved_files[:5], 1):
        with open(file, 'r', encoding='utf-8') as f:
            rule = json.load(f)
            print(f"\n  {i}. {rule['title']}")
            print(f"     Clause: {rule['clause_number']}")
            print(f"     Jurisdiction: {rule['jurisdiction']}")
            print(f"     Text: {rule['clause_text'][:80]}...")
    
    if len(approved_files) > 5:
        print(f"\n  ... and {len(approved_files) - 5} more rules")
    
    print()
    print("="*70)
    print("🚀 HOW TO USE:")
    print("="*70)
    print()
    print("STEP 1: Start Backend")
    print("   cd backend")
    print("   npm start")
    print()
    print("STEP 2: Start Frontend")
    print("   cd frontend")
    print("   npm start")
    print()
    print("STEP 3: Access Rules Browser")
    print("   http://localhost:3000/rules")
    print("   Or click 'Browse Rules' from Dashboard")
    print()
    print("STEP 4: Try These Searches")
    print("   - Search: 'FSI' → Find FSI-related rules")
    print("   - Search: 'parking' → Find parking requirements")
    print("   - Search: 'setback' → Find setback rules")
    print("   - Search: '3.1' → Find rules in Chapter 3.1")
    print("   - Filter: 'Mumbai DCPR' → Mumbai-specific rules")
    print("   - Category: 'Height' → Height restriction rules")
    print()
    
    print("="*70)
    print("💡 EXAMPLE USE CASES:")
    print("="*70)
    print()
    print("1. Architect Planning a Project")
    print("   - Search for 'FSI residential' to find base FSI")
    print("   - Search for 'setback 12m' to find setback for 12m road")
    print("   - Search for 'parking commercial' for parking norms")
    print()
    print("2. Developer Checking Compliance")
    print("   - Filter by 'Mumbai DCPR' for Mumbai-specific rules")
    print("   - Search for 'TOD' to find TOD zone benefits")
    print("   - Search for 'height' to check height limits")
    print()
    print("3. Student Learning Regulations")
    print("   - Browse by category (FSI, Setbacks, etc.)")
    print("   - Read full clause text and rule logic")
    print("   - Compare UDCPR vs Mumbai DCPR rules")
    print()
    
    print("="*70)
    print("✅ Feature Status: COMPLETE")
    print("📊 Rules Available: {} ({} UDCPR + {} Mumbai DCPR)".format(
        len(approved_files), udcpr_count, mumbai_count
    ))
    print("🎯 Ready for Use: YES")
    print("="*70)
    print()
    print("Enjoy browsing the rules! 📚")
    print()

if __name__ == "__main__":
    show_rules_browser_demo()
