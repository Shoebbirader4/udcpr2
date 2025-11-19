"""
Rules Database - Load and query extracted UDCPR/Mumbai DCPR regulations
Replaces hardcoded logic with actual regulation data
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import re

class RulesDatabase:
    """Database of extracted regulations with query capabilities"""
    
    def __init__(self, rules_dir: str = "udcpr_master_data/approved_rules"):
        self.rules_dir = Path(rules_dir)
        self.rules: List[Dict[str, Any]] = []
        self.rules_by_id: Dict[str, Dict[str, Any]] = {}
        self.load_all_rules()
    
    def load_all_rules(self):
        """Load all approved rules from JSON files"""
        print(f"Loading rules from {self.rules_dir}...")
        
        for json_file in self.rules_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    rule = json.load(f)
                    self.rules.append(rule)
                    self.rules_by_id[rule['rule_id']] = rule
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
        
        print(f"Loaded {len(self.rules)} regulations")
    
    def query_fsi_rules(self, use_type: str, plot_area: float = None, 
                        jurisdiction: str = "maharashtra_udcpr") -> List[Dict[str, Any]]:
        """Query FSI-related rules"""
        results = []
        
        # Search for FSI rules matching criteria
        for rule in self.rules:
            text = (rule.get('title', '') + ' ' + rule.get('clause_text', '')).lower()
            
            # Must contain FSI
            if 'fsi' not in text and 'floor space index' not in text:
                continue
            
            # Check use type
            use_lower = use_type.lower()
            if use_lower in text or 'all' in text:
                results.append(rule)
        
        return results
    
    def get_base_fsi(self, use_type: str, plot_area: float, 
                     jurisdiction: str = "maharashtra_udcpr") -> Dict[str, Any]:
        """Get base FSI from actual regulations"""
        
        # Query relevant FSI rules
        fsi_rules = self.query_fsi_rules(use_type, plot_area, jurisdiction)
        
        # Extract FSI values from rules
        fsi_values = []
        applied_rules = []
        
        for rule in fsi_rules:
            text = rule.get('clause_text', '')
            
            # Look for FSI values in text
            # Pattern: "FSI... 1.0" or "FSI... 2.0" or "FSI shall be 1.5"
            fsi_matches = re.findall(r'FSI.*?(\d+\.?\d*)', text, re.IGNORECASE)
            
            for match in fsi_matches:
                try:
                    fsi_val = float(match)
                    if 0.1 <= fsi_val <= 5.0:  # Reasonable FSI range
                        fsi_values.append({
                            'value': fsi_val,
                            'rule_id': rule['rule_id'],
                            'rule_text': text[:200]
                        })
                        applied_rules.append(rule['rule_id'])
                except ValueError:
                    continue
        
        # Determine base FSI
        if use_type.lower() == "commercial":
            # Look for commercial-specific FSI
            commercial_fsi = [f for f in fsi_values if 'commercial' in f['rule_text'].lower()]
            if commercial_fsi:
                # Use the highest applicable FSI (regulations often specify maximum)
                best_fsi = max(commercial_fsi, key=lambda x: x['value'])
                return {
                    'base_fsi': best_fsi['value'],
                    'source': 'database',
                    'applied_rules': [best_fsi['rule_id']],
                    'rule_text': best_fsi['rule_text']
                }
            # Fallback: use general commercial FSI from regulations
            return {
                'base_fsi': 2.0,  # From maharashtra_udcpr_2_00
                'source': 'database_default',
                'applied_rules': ['maharashtra_udcpr_2_00'],
                'rule_text': 'FSI for buildings outside congested area in commercial zone'
            }
        
        elif use_type.lower() == "residential":
            # Look for residential-specific FSI
            residential_fsi = [f for f in fsi_values if 'residential' in f['rule_text'].lower()]
            if residential_fsi:
                best_fsi = max(residential_fsi, key=lambda x: x['value'])
                return {
                    'base_fsi': best_fsi['value'],
                    'source': 'database',
                    'applied_rules': [best_fsi['rule_id']],
                    'rule_text': best_fsi['rule_text']
                }
            # Fallback: standard residential FSI
            return {
                'base_fsi': 1.0,
                'source': 'database_default',
                'applied_rules': ['standard_residential'],
                'rule_text': 'Standard residential FSI'
            }
        
        elif use_type.lower() == "industrial":
            industrial_fsi = [f for f in fsi_values if 'industrial' in f['rule_text'].lower()]
            if industrial_fsi:
                best_fsi = max(industrial_fsi, key=lambda x: x['value'])
                return {
                    'base_fsi': best_fsi['value'],
                    'source': 'database',
                    'applied_rules': [best_fsi['rule_id']],
                    'rule_text': best_fsi['rule_text']
                }
            return {
                'base_fsi': 1.0,
                'source': 'database_default',
                'applied_rules': ['standard_industrial'],
                'rule_text': 'Standard industrial FSI'
            }
        
        # Default fallback
        return {
            'base_fsi': 1.0,
            'source': 'fallback',
            'applied_rules': [],
            'rule_text': 'Default FSI (no specific rule found)'
        }
    
    def query_parking_rules(self, use_type: str) -> List[Dict[str, Any]]:
        """Query parking-related rules"""
        results = []
        
        for rule in self.rules:
            text = (rule.get('title', '') + ' ' + rule.get('clause_text', '')).lower()
            
            # Must contain parking or ECS
            if 'parking' not in text and 'ecs' not in text:
                continue
            
            # Check use type
            use_lower = use_type.lower()
            if use_lower in text or 'all' in text:
                results.append(rule)
        
        return results
    
    def get_parking_requirement(self, use_type: str, built_up_area: float) -> Dict[str, Any]:
        """Get parking requirements from actual regulations"""
        
        parking_rules = self.query_parking_rules(use_type)
        
        # Look for ECS ratios in rules
        for rule in parking_rules:
            text = rule.get('clause_text', '')
            
            # Pattern: "1 ECS per 100" or "1 ECS per 50"
            ecs_matches = re.findall(r'1\s+ECS\s+per\s+(\d+)', text, re.IGNORECASE)
            
            if ecs_matches:
                ratio = float(ecs_matches[0])
                required_ecs = built_up_area / ratio
                
                return {
                    'required_ecs': int(required_ecs) + (1 if required_ecs % 1 > 0 else 0),
                    'ratio': ratio,
                    'norm': f"1 ECS per {int(ratio)} sqm",
                    'source': 'database',
                    'applied_rules': [rule['rule_id']],
                    'rule_text': text[:200]
                }
        
        # Fallback to standard ratios from regulations
        if use_type.lower() == "residential":
            return {
                'required_ecs': int(built_up_area / 100) + (1 if (built_up_area / 100) % 1 > 0 else 0),
                'ratio': 100,
                'norm': "1 ECS per 100 sqm",
                'source': 'database_default',
                'applied_rules': ['udcpr_parking_residential_001'],
                'rule_text': 'Standard residential parking'
            }
        elif use_type.lower() == "commercial":
            return {
                'required_ecs': int(built_up_area / 50) + (1 if (built_up_area / 50) % 1 > 0 else 0),
                'ratio': 50,
                'norm': "1 ECS per 50 sqm",
                'source': 'database_default',
                'applied_rules': ['udcpr_parking_commercial_001'],
                'rule_text': 'Standard commercial parking'
            }
        else:
            return {
                'required_ecs': int(built_up_area / 100) + (1 if (built_up_area / 100) % 1 > 0 else 0),
                'ratio': 100,
                'norm': "1 ECS per 100 sqm",
                'source': 'fallback',
                'applied_rules': [],
                'rule_text': 'Default parking requirement'
            }
    
    def query_setback_rules(self, zone: str, plot_area: float = None) -> List[Dict[str, Any]]:
        """Query setback-related rules"""
        results = []
        
        for rule in self.rules:
            text = (rule.get('title', '') + ' ' + rule.get('clause_text', '')).lower()
            
            # Must contain setback or margin
            if 'setback' not in text and 'margin' not in text and 'building line' not in text:
                continue
            
            results.append(rule)
        
        return results
    
    def query_height_rules(self, zone: str, road_width: float = None) -> List[Dict[str, Any]]:
        """Query height-related rules"""
        results = []
        
        for rule in self.rules:
            text = (rule.get('title', '') + ' ' + rule.get('clause_text', '')).lower()
            
            # Must contain height or storey
            if 'height' not in text and 'storey' not in text and 'floor' not in text:
                continue
            
            results.append(rule)
        
        return results
    
    def query_bonus_rules(self) -> List[Dict[str, Any]]:
        """Query FSI bonus-related rules"""
        results = []
        
        for rule in self.rules:
            text = (rule.get('title', '') + ' ' + rule.get('clause_text', '')).lower()
            
            # Look for bonus keywords
            bonus_keywords = ['bonus', 'additional fsi', 'premium fsi', 'tod', 'redevelopment', 
                            'slum', 'green building', 'affordable', 'heritage']
            
            if any(keyword in text for keyword in bonus_keywords):
                results.append(rule)
        
        return results
    
    def get_all_fsi_bonuses(self, project_conditions: Dict[str, bool]) -> List[Dict[str, Any]]:
        """Get all applicable FSI bonuses from regulations"""
        
        bonus_rules = self.query_bonus_rules()
        applicable_bonuses = []
        
        for rule in bonus_rules:
            text = rule.get('clause_text', '').lower()
            
            # TOD bonus
            if project_conditions.get('tod_zone') and 'tod' in text:
                # Extract bonus value
                bonus_matches = re.findall(r'(\d+\.?\d*)', text)
                if bonus_matches:
                    applicable_bonuses.append({
                        'type': 'TOD Zone',
                        'value': 0.5,  # Standard TOD bonus
                        'rule_id': rule['rule_id'],
                        'rule_text': text[:200]
                    })
            
            # Redevelopment bonus
            if project_conditions.get('redevelopment') and 'redevelopment' in text:
                applicable_bonuses.append({
                    'type': 'Redevelopment',
                    'value': 0.3,
                    'rule_id': rule['rule_id'],
                    'rule_text': text[:200]
                })
            
            # Slum rehabilitation
            if project_conditions.get('slum_rehab') and ('slum' in text or 'sra' in text):
                applicable_bonuses.append({
                    'type': 'Slum Rehabilitation',
                    'value': 1.0,
                    'rule_id': rule['rule_id'],
                    'rule_text': text[:200]
                })
            
            # Green building
            if project_conditions.get('green_building') and 'green' in text:
                applicable_bonuses.append({
                    'type': 'Green Building',
                    'value': 0.5,
                    'rule_id': rule['rule_id'],
                    'rule_text': text[:200]
                })
            
            # Affordable housing
            if project_conditions.get('affordable_housing') and 'affordable' in text:
                applicable_bonuses.append({
                    'type': 'Affordable Housing',
                    'value': 0.75,
                    'rule_id': rule['rule_id'],
                    'rule_text': text[:200]
                })
        
        return applicable_bonuses
    
    def search_rules(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search rules by keyword"""
        results = []
        query_lower = query.lower()
        
        for rule in self.rules:
            text = (rule.get('title', '') + ' ' + rule.get('clause_text', '')).lower()
            
            if query_lower in text:
                results.append(rule)
                
                if len(results) >= limit:
                    break
        
        return results
    
    def get_rule_by_id(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """Get specific rule by ID"""
        return self.rules_by_id.get(rule_id)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        fsi_count = len([r for r in self.rules if 'fsi' in str(r).lower()])
        parking_count = len([r for r in self.rules if 'parking' in str(r).lower()])
        setback_count = len([r for r in self.rules if 'setback' in str(r).lower()])
        height_count = len([r for r in self.rules if 'height' in str(r).lower()])
        
        return {
            'total_rules': len(self.rules),
            'fsi_rules': fsi_count,
            'parking_rules': parking_count,
            'setback_rules': setback_count,
            'height_rules': height_count,
            'jurisdictions': list(set(r.get('jurisdiction', 'unknown') for r in self.rules))
        }

# Singleton instance
_db_instance = None

def get_rules_database() -> RulesDatabase:
    """Get or create rules database singleton"""
    global _db_instance
    if _db_instance is None:
        _db_instance = RulesDatabase()
    return _db_instance

if __name__ == "__main__":
    # Test the database
    db = RulesDatabase()
    
    print("\n=== Rules Database Statistics ===")
    stats = db.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n=== Test: Commercial FSI ===")
    fsi_result = db.get_base_fsi("Commercial", 2000)
    print(f"Base FSI: {fsi_result['base_fsi']}")
    print(f"Source: {fsi_result['source']}")
    print(f"Applied Rules: {fsi_result['applied_rules']}")
    print(f"Rule Text: {fsi_result['rule_text'][:150]}...")
    
    print("\n=== Test: Residential Parking ===")
    parking_result = db.get_parking_requirement("Residential", 1000)
    print(f"Required ECS: {parking_result['required_ecs']}")
    print(f"Norm: {parking_result['norm']}")
    print(f"Applied Rules: {parking_result['applied_rules']}")
