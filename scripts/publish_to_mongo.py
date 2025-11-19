#!/usr/bin/env python3
"""
Publish approved rules to MongoDB.
"""
import os
import json
from pathlib import Path
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import hashlib

load_dotenv()

WORK_DIR = Path("udcpr_master_data")
APPROVED_DIR = WORK_DIR / "approved_rules"

def connect_mongo():
    """Connect to MongoDB."""
    uri = os.getenv("MONGO_URI")
    if not uri:
        raise ValueError("MONGO_URI not set in environment")
    
    client = MongoClient(uri)
    db = client.get_database()
    return db

def publish_rules():
    """Publish approved rules to MongoDB."""
    print("UDCPR Master - Publish Rules to MongoDB")
    print("="*60)
    
    db = connect_mongo()
    print("✓ Connected to MongoDB")
    
    # Find approved rule files
    approved_files = list(APPROVED_DIR.glob("*.json"))
    
    if not approved_files:
        print("\n⚠️  No approved rule files found in:")
        print(f"   {APPROVED_DIR}")
        print("\nRun the admin UI to approve parsed rules first.")
        return
    
    print(f"\nFound {len(approved_files)} approved rule file(s)")
    
    total_inserted = 0
    
    for file_path in approved_files:
        print(f"\nProcessing: {file_path.name}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            rules = json.load(f)
        
        if not isinstance(rules, list):
            rules = [rules]
        
        # Insert rules
        for rule in rules:
            # Ensure required fields
            if 'rule_id' not in rule:
                print(f"  ⚠️  Skipping rule without rule_id")
                continue
            
            # Upsert (insert or update)
            db.rules.update_one(
                {'rule_id': rule['rule_id'], 'version': rule.get('version', 'v1')},
                {'$set': rule},
                upsert=True
            )
            total_inserted += 1
        
        print(f"  ✓ Inserted {len(rules)} rules")
    
    # Create rule version record
    version_id = f"udcpr_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Calculate checksum
    all_rules = list(db.rules.find({}))
    checksum_data = json.dumps(all_rules, sort_keys=True, default=str)
    checksum = hashlib.sha256(checksum_data.encode()).hexdigest()
    
    version_doc = {
        'version_id': version_id,
        'source_files': [f.name for f in approved_files],
        'rule_count': total_inserted,
        'created_at': datetime.now(),
        'checksum': checksum
    }
    
    db.rule_versions.insert_one(version_doc)
    
    # Create changelog
    changelog_doc = {
        'version_id': version_id,
        'action': 'initial_publish',
        'rules_added': total_inserted,
        'timestamp': datetime.now()
    }
    
    db.changelogs.insert_one(changelog_doc)
    
    # Create indexes
    db.rules.create_index([('rule_id', 1), ('version', 1)], unique=True)
    db.rules.create_index([('jurisdiction', 1)])
    db.rules.create_index([('clause_number', 1)])
    
    print("\n" + "="*60)
    print(f"✓ Published {total_inserted} rules to MongoDB")
    print(f"  Version: {version_id}")
    print(f"  Checksum: {checksum[:16]}...")
    print("="*60)
    
    # Log to file
    log_file = WORK_DIR / "logs" / f"publish_{version_id}.log"
    log_file.parent.mkdir(exist_ok=True)
    
    with open(log_file, 'w') as f:
        f.write(f"Published at: {datetime.now()}\n")
        f.write(f"Version: {version_id}\n")
        f.write(f"Rules: {total_inserted}\n")
        f.write(f"Checksum: {checksum}\n")
    
    print(f"\nLog saved to: {log_file}")

if __name__ == "__main__":
    try:
        publish_rules()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
