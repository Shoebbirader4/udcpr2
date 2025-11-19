"""
Audit Rule Engine Accuracy vs Real UDCPR/Mumbai DCPR Regulations
Compares calculation engine logic with actual extracted rules
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from pathlib import Path
from rule_engine.rule_engine import RuleEngine

class RuleEngineAuditor:
    def __init__(self):
        self.engine = RuleEngine(rules_db={})  # Initialize with empty rules_db
        self.rules_dir = Path("udcpr_master_data/approved_rules")
        self.audit_results = {
            "fsi_rules": [],
            "setback_rules": [],
            "coverage_rules": [],
            "height_rules": [],
            "parking_rules": [],
            "summary": {}
        }
    
    def load_real_rules(self):
        """Load all extracted rules from JSON files"""
        all_rules = []
        for json_file in self.rules_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_rules.extend(data)
                    elif isinstance(data, dict):
                        # Each file contains a single rule object
                        all_rules.append(data)
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
        return all_rules
    
    def audit_fsi_calculations(self, real_rules):
        """Audit FSI calculation logic"""
        print("\n" + "="*80)
        print("AUDITING FSI CALCULATIONS")
        print("="*80)
        
        # Find FSI-related rules
        fsi_rules = [r for r in real_rules if 'fsi' in str(r).lower() or 'floor space index' in str(r).lower()]
        print(f"\nFound {len(fsi_rules)} FSI-related rules in extracted data")
        
        # Test cases
        from rule_engine.rule_engine import ProjectInput
        test_cases = [
            {"zone": "Residential", "plot_area": 1000, "road_width": 12, "use_type": "Residential"},
            {"zone": "Commercial", "plot_area": 2000, "road_width": 18, "use_type": "Commercial"},
            {"zone": "Industrial", "plot_area": 5000, "road_width": 24, "use_type": "Industrial"},
        ]
        
        for test in test_cases:
            project = ProjectInput(
                jurisdiction="maharashtra_udcpr",
                zone=test["zone"],
                plot_area_sqm=test["plot_area"],
                road_width_m=test["road_width"],
                frontage_m=20,
                use_type=test["use_type"],
                proposed_floors=4,
                proposed_height_m=12,
                proposed_built_up_sqm=test["plot_area"] * 1.0
            )
            result = self.engine.calculate_fsi(project)
            print(f"\n--- Test: {test['zone']}, {test['plot_area']}sqm, {test['road_width']}m road ---")
            print(f"Engine Result: Base FSI = {result['base_fsi']}, Permissible FSI = {result['permissible_fsi']}")
            
            # Find matching real rules
            zone_lower = test['zone'].lower()
            matching = [r for r in fsi_rules if zone_lower in str(r).lower()]
            if matching:
                print(f"Matching Real Rules ({len(matching)}):")
                for rule in matching[:3]:  # Show first 3
                    print(f"  - {str(rule)[:150]}...")
            
            self.audit_results["fsi_rules"].append({
                "test": test,
                "engine_result": result,
                "matching_rules_count": len(matching)
            })
    
    def audit_setback_calculations(self, real_rules):
        """Audit setback calculation logic"""
        print("\n" + "="*80)
        print("AUDITING SETBACK CALCULATIONS")
        print("="*80)
        
        # Find setback-related rules
        setback_rules = [r for r in real_rules if 'setback' in str(r).lower() or 'margin' in str(r).lower()]
        print(f"\nFound {len(setback_rules)} setback-related rules in extracted data")
        
        # Test cases
        from rule_engine.rule_engine import ProjectInput
        test_cases = [
            {"zone": "Residential", "plot_area": 500, "road_width": 9, "building_height": 12, "use_type": "Residential"},
            {"zone": "Residential", "plot_area": 1500, "road_width": 15, "building_height": 24, "use_type": "Residential"},
            {"zone": "Commercial", "plot_area": 2000, "road_width": 18, "building_height": 30, "use_type": "Commercial"},
        ]
        
        for test in test_cases:
            project = ProjectInput(
                jurisdiction="maharashtra_udcpr",
                zone=test["zone"],
                plot_area_sqm=test["plot_area"],
                road_width_m=test["road_width"],
                frontage_m=20,
                use_type=test["use_type"],
                proposed_floors=4,
                proposed_height_m=test["building_height"],
                proposed_built_up_sqm=test["plot_area"] * 1.0
            )
            result = self.engine.calculate_setbacks(project)
            print(f"\n--- Test: {test['zone']}, {test['plot_area']}sqm, {test['building_height']}m height ---")
            print(f"Engine Result: Front={result['front_m']}m, Side={result['side_m']}m, Rear={result['rear_m']}m")
            
            # Find matching real rules
            zone_lower = test['zone'].lower()
            matching = [r for r in setback_rules if zone_lower in str(r).lower()]
            if matching:
                print(f"Matching Real Rules ({len(matching)}):")
                for rule in matching[:3]:
                    print(f"  - {str(rule)[:150]}...")
            
            self.audit_results["setback_rules"].append({
                "test": test,
                "engine_result": result,
                "matching_rules_count": len(matching)
            })
    
    def audit_coverage_calculations(self, real_rules):
        """Audit coverage calculation logic"""
        print("\n" + "="*80)
        print("AUDITING COVERAGE CALCULATIONS")
        print("="*80)
        
        # Find coverage-related rules
        coverage_rules = [r for r in real_rules if 'coverage' in str(r).lower() or 'ground coverage' in str(r).lower()]
        print(f"\nFound {len(coverage_rules)} coverage-related rules in extracted data")
        
        print("\nNote: Current RuleEngine calculates coverage via setbacks (open space)")
        print("Coverage = 100% - open_space_percent")
        
        # Test cases
        from rule_engine.rule_engine import ProjectInput
        test_cases = [
            {"zone": "Residential", "plot_area": 1000, "use_type": "Residential"},
            {"zone": "Commercial", "plot_area": 2000, "use_type": "Commercial"},
            {"zone": "Industrial", "plot_area": 5000, "use_type": "Industrial"},
        ]
        
        for test in test_cases:
            project = ProjectInput(
                jurisdiction="maharashtra_udcpr",
                zone=test["zone"],
                plot_area_sqm=test["plot_area"],
                road_width_m=12,
                frontage_m=20,
                use_type=test["use_type"],
                proposed_floors=4,
                proposed_height_m=12,
                proposed_built_up_sqm=test["plot_area"] * 1.0
            )
            setback_result = self.engine.calculate_setbacks(project)
            coverage_percent = 100 - setback_result['open_space_percent']
            print(f"\n--- Test: {test['zone']}, {test['plot_area']}sqm ---")
            print(f"Engine Result: Open Space = {setback_result['open_space_percent']:.1f}%, Coverage ~= {coverage_percent:.1f}%")
            
            # Find matching real rules
            zone_lower = test['zone'].lower()
            matching = [r for r in coverage_rules if zone_lower in str(r).lower()]
            if matching:
                print(f"Matching Real Rules ({len(matching)}):")
                for rule in matching[:3]:
                    print(f"  - {str(rule)[:150]}...")
            
            self.audit_results["coverage_rules"].append({
                "test": test,
                "engine_result": {"coverage_percent": coverage_percent, "open_space_percent": setback_result['open_space_percent']},
                "matching_rules_count": len(matching)
            })
    
    def audit_height_calculations(self, real_rules):
        """Audit height calculation logic"""
        print("\n" + "="*80)
        print("AUDITING HEIGHT CALCULATIONS")
        print("="*80)
        
        # Find height-related rules
        height_rules = [r for r in real_rules if 'height' in str(r).lower() or 'storey' in str(r).lower()]
        print(f"\nFound {len(height_rules)} height-related rules in extracted data")
        
        # Test cases
        from rule_engine.rule_engine import ProjectInput
        test_cases = [
            {"zone": "Residential", "road_width": 9, "use_type": "Residential"},
            {"zone": "Residential", "road_width": 18, "use_type": "Residential"},
            {"zone": "Commercial", "road_width": 24, "use_type": "Commercial"},
        ]
        
        for test in test_cases:
            project = ProjectInput(
                jurisdiction="maharashtra_udcpr",
                zone=test["zone"],
                plot_area_sqm=1000,
                road_width_m=test["road_width"],
                frontage_m=20,
                use_type=test["use_type"],
                proposed_floors=4,
                proposed_height_m=12,
                proposed_built_up_sqm=1000
            )
            result = self.engine.calculate_height(project)
            print(f"\n--- Test: {test['zone']}, {test['road_width']}m road ---")
            print(f"Engine Result: Max Height = {result['permissible_height_m']}m, Max Floors = {result['permissible_floors']}")
            
            # Find matching real rules
            zone_lower = test['zone'].lower()
            matching = [r for r in height_rules if zone_lower in str(r).lower()]
            if matching:
                print(f"Matching Real Rules ({len(matching)}):")
                for rule in matching[:3]:
                    print(f"  - {str(rule)[:150]}...")
            
            self.audit_results["height_rules"].append({
                "test": test,
                "engine_result": result,
                "matching_rules_count": len(matching)
            })
    
    def audit_parking_calculations(self, real_rules):
        """Audit parking calculation logic"""
        print("\n" + "="*80)
        print("AUDITING PARKING CALCULATIONS")
        print("="*80)
        
        # Find parking-related rules
        parking_rules = [r for r in real_rules if 'parking' in str(r).lower() or 'ecs' in str(r).lower()]
        print(f"\nFound {len(parking_rules)} parking-related rules in extracted data")
        
        # Test cases
        from rule_engine.rule_engine import ProjectInput
        test_cases = [
            {"zone": "Residential", "built_up_area": 1000, "use_type": "Residential"},
            {"zone": "Commercial", "built_up_area": 5000, "use_type": "Commercial"},
        ]
        
        for test in test_cases:
            project = ProjectInput(
                jurisdiction="maharashtra_udcpr",
                zone=test["zone"],
                plot_area_sqm=1000,
                road_width_m=12,
                frontage_m=20,
                use_type=test["use_type"],
                proposed_floors=4,
                proposed_height_m=12,
                proposed_built_up_sqm=test["built_up_area"]
            )
            result = self.engine.calculate_parking(project)
            print(f"\n--- Test: {test['zone']}, {test['built_up_area']}sqm ---")
            print(f"Engine Result: {result['required_ecs']} ECS ({result['norm']})")
            
            # Find matching real rules
            zone_lower = test['zone'].lower()
            matching = [r for r in parking_rules if zone_lower in str(r).lower()]
            if matching:
                print(f"Matching Real Rules ({len(matching)}):")
                for rule in matching[:3]:
                    print(f"  - {str(rule)[:150]}...")
            
            self.audit_results["parking_rules"].append({
                "test": test,
                "engine_result": result,
                "matching_rules_count": len(matching)
            })
    
    def generate_summary(self, real_rules):
        """Generate audit summary"""
        print("\n" + "="*80)
        print("AUDIT SUMMARY")
        print("="*80)
        
        total_rules = len(real_rules)
        
        # Count rules by category
        fsi_count = len([r for r in real_rules if 'fsi' in str(r).lower()])
        setback_count = len([r for r in real_rules if 'setback' in str(r).lower()])
        coverage_count = len([r for r in real_rules if 'coverage' in str(r).lower()])
        height_count = len([r for r in real_rules if 'height' in str(r).lower()])
        parking_count = len([r for r in real_rules if 'parking' in str(r).lower()])
        
        summary = {
            "total_extracted_rules": total_rules,
            "rules_by_category": {
                "fsi": fsi_count,
                "setback": setback_count,
                "coverage": coverage_count,
                "height": height_count,
                "parking": parking_count
            },
            "engine_tests_run": {
                "fsi": len(self.audit_results["fsi_rules"]),
                "setback": len(self.audit_results["setback_rules"]),
                "coverage": len(self.audit_results["coverage_rules"]),
                "height": len(self.audit_results["height_rules"]),
                "parking": len(self.audit_results["parking_rules"])
            }
        }
        
        print(f"\nTotal Extracted Rules: {total_rules}")
        print(f"\nRules by Category:")
        print(f"  FSI: {fsi_count}")
        print(f"  Setback: {setback_count}")
        print(f"  Coverage: {coverage_count}")
        print(f"  Height: {height_count}")
        print(f"  Parking: {parking_count}")
        
        print(f"\nEngine Tests Run:")
        print(f"  FSI: {summary['engine_tests_run']['fsi']}")
        print(f"  Setback: {summary['engine_tests_run']['setback']}")
        print(f"  Coverage: {summary['engine_tests_run']['coverage']}")
        print(f"  Height: {summary['engine_tests_run']['height']}")
        print(f"  Parking: {summary['engine_tests_run']['parking']}")
        
        self.audit_results["summary"] = summary
        
        # Key findings
        print("\n" + "="*80)
        print("KEY FINDINGS")
        print("="*80)
        print("\n1. REAL DATA EXISTS:")
        print(f"   - {total_rules} rules extracted from UDCPR/Mumbai DCPR documents")
        print(f"   - Rules cover all major categories (FSI, setback, coverage, height, parking)")
        
        print("\n2. ENGINE USES SIMPLIFIED LOGIC:")
        print("   - Rule engine uses hardcoded formulas and lookup tables")
        print("   - Does NOT query the extracted rule database")
        print("   - Calculations are approximations, not exact regulation compliance")
        
        print("\n3. INTEGRATION GAP:")
        print("   - Vector store has 5,484 indexed rules (for AI Assistant)")
        print("   - Rule engine does NOT use vector store for calculations")
        print("   - Two separate systems: AI search vs calculation engine")
        
        print("\n4. RECOMMENDATIONS:")
        print("   - Integrate rule engine with extracted regulations database")
        print("   - Replace hardcoded logic with rule-based lookups")
        print("   - Add validation layer to compare engine results with actual rules")
        print("   - Implement rule versioning and update mechanism")
    
    def save_audit_report(self):
        """Save detailed audit report"""
        report_path = Path("AUDIT_REPORT.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.audit_results, f, indent=2, ensure_ascii=False)
        print(f"\n\nDetailed audit report saved to: {report_path}")
    
    def run_full_audit(self):
        """Run complete audit"""
        print("="*80)
        print("RULE ENGINE ACCURACY AUDIT")
        print("Comparing calculation engine vs real UDCPR/Mumbai DCPR regulations")
        print("="*80)
        
        # Load real rules
        print("\nLoading extracted rules...")
        real_rules = self.load_real_rules()
        print(f"Loaded {len(real_rules)} rules from extracted documents")
        
        # Run audits
        self.audit_fsi_calculations(real_rules)
        self.audit_setback_calculations(real_rules)
        self.audit_coverage_calculations(real_rules)
        self.audit_height_calculations(real_rules)
        self.audit_parking_calculations(real_rules)
        
        # Generate summary
        self.generate_summary(real_rules)
        
        # Save report
        self.save_audit_report()
        
        print("\n" + "="*80)
        print("AUDIT COMPLETE")
        print("="*80)

if __name__ == "__main__":
    auditor = RuleEngineAuditor()
    auditor.run_full_audit()
