#!/usr/bin/env python3
"""
Auto-approve all candidate rules for development/testing.
In production, rules should be manually verified through the admin UI.
"""
import json
from pathlib import Path
from datetime import datetime

WORK_DIR = Path("udcpr_master_data")
STAGING_DIR = WORK_DIR / "staging_rules"
APPROVED_DIR = WORK_DIR / "approved_rules"

def auto_approve_all():
    """Auto-approve all candidate rules."""
    print("UDCPR Master - Auto-Approve Rules")
    print("="*60)
    print("⚠️  WARNING: Auto-approving all rules without verification")
    print("   In production, use the admin UI for manual verification")
    print("="*60)
    print()
    
    # Create approved directory
    APPROVED_DIR.mkdir(parents=True, exist_ok=True)
    
    # Find all candidate files
    candidate_files = list(STAGING_DIR.glob("*.json"))
    
    if not candidate_files:
        print("✗ No candidate files found in staging_rules/")
        print("  Run: python scripts/mock_ingestion.py first")
        return
    
    total_approved = 0
    
    for candidate_file in candidate_files:
        print(f"\nProcessing: {candidate_file.name}")
        
        with open(candidate_file, 'r', encoding='utf-8') as f:
            candidates = json.load(f)
        
        if not isinstance(candidates, list):
            candidates = [candidates]
        
        for i, rule in enumerate(candidates):
            # Add approval metadata
            rule['approved_at'] = datetime.now().isoformat()
            rule['approved_by'] = 'auto_approve_script'
            rule['verification_status'] = 'auto_approved'
            
            # Generate filename
            rule_id = rule.get('rule_id', f'rule_{total_approved}')
            approved_filename = f"approved_{rule_id}.json"
            approved_path = APPROVED_DIR / approved_filename
            
            # Save to approved directory
            with open(approved_path, 'w', encoding='utf-8') as f:
                json.dump(rule, f, indent=2, ensure_ascii=False)
            
            total_approved += 1
        
        print(f"  ✓ Approved {len(candidates)} rules")
    
    print("\n" + "="*60)
    print(f"✓ Auto-approved {total_approved} rules!")
    print("="*60)
    print(f"\nApproved rules saved to: {APPROVED_DIR}")
    print("\nNext steps:")
    print("  1. Start backend: cd backend && npm start")
    print("  2. Start frontend: cd frontend && npm start")
    print("  3. Browse rules at: http://localhost:3000/rules")
    print("\nOptional: Publish to MongoDB")
    print("  python scripts/publish_to_mongo.py")

if __name__ == "__main__":
    auto_approve_all()
