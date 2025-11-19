"""
Enhanced Rules Database V2 - With jurisdiction filtering, rule ranking, and advanced parsing
Implements all 4 next steps from database integration
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import re
from dataclasses import dataclass
from enum import Enum

class RulePriority(Enum):
    """Rule priority levels"""
    EXACT_MATCH = 1      # Exact jurisdiction and use type match
    JURISDICTION_MATCH = 2  # Jurisdiction matches
    GENERAL = 3          # General rule (applies to all)
    FALLBACK = 4         # Fallback/default rule

@dataclass
class RankedRule:
    """Rule with ranking score"""
    rule: Dict[str, Any]
    priority: RulePriority
    relevance_score: float
    match_reasons: List[str]

class EnhancedRulesDatabase:
    """Enhanced database with jurisdiction filtering and rule ranking"""
    
    def __init__(self, rules_dir: str = "udcpr_master_data/approved_rules"):
        self.rules_dir = Path(rules_dir)
        self.rules: List[Dict[str, Any]] = []
        self.rules_by_id: Dict[str, Dict[str, Any]] = {}
        self.rules_by_jurisdiction: Dict[str, List[Dict[str, Any]]] = {}
        self.load_all_rules()
    
    def load_all_rules(self):
        """Load all approved rules and index by jurisdiction"""
        print(f"Loading rules from {self.rules_dir}...")
        
        for json_file in self.rules_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    rule = json.load(f)
                    self.rules.append(rule)
                    self.rules_by_id[rule['rule_id']] = rule
                    
                    # Index by jurisdiction
                    jurisdiction = rule.get('jurisdiction', 'unknown')
                    if jurisdiction not in self.rules_by_jurisdiction:
                        self.rules_by_jurisdiction[jurisdiction] = []
                    self.rules_by_jurisdiction[jurisdiction].append(rule)
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
        
        print(f"Loaded {len(self.rules)} regulations")
        print(f"Jurisdictions: {list(self.rules_by_jurisdiction.keys())}")
    
    def filter_by_jurisdiction(self, rules: List[Dict[str, Any]], 
                               jurisdiction: str) -> List[Dict[str, Any]]:
        """Filter rules by jurisdiction with priority"""
        if not jurisdiction:
            return rules
        
        jurisdiction_lower = jurisdiction.lower()
        
        # Exact matches first
        exact_matches = [r for r in rules if r.get('jurisdiction', '').lower() == jurisdiction_lower]
        
        # If we have exact matches, return only those
        if exact_matches:
            return exact_matches
        
        # Otherwise return all (might be general rules)
        return rules
    
    def rank_rules(self, rules: List[Dict[str, Any]], 
                   use_type: str, 
                   jurisdiction: str,
                   plot_area: float = None) -> List[RankedRule]:
        """Rank rules by relevance and priority"""
        ranked = []
        use_type_lower = use_type.lower()
        jurisdiction_lower = jurisdiction.lower()
        
        for rule in rules:
            rule_text = (rule.get('title', '') + ' ' + rule.get('clause_text', '')).lower()
            rule_jurisdiction = rule.get('jurisdiction', '').lower()
            
            # Determine priority
            if rule_jurisdiction == jurisdiction_lower and use_type_lower in rule_text:
                priority = RulePriority.EXACT_MATCH
            elif rule_jurisdiction == jurisdiction_lower:
                priority = RulePriority.JURISDICTION_MATCH
            elif 'all' in rule_text or 'general' in rule_text:
                priority = RulePriority.GENERAL
            else:
                priority = RulePriority.FALLBACK
            
            # Calculate relevance score
            relevance_score = 0.0
            match_reasons = []
            
            # Use type match
            if use_type_lower in rule_text:
                relevance_score += 10.0
                match_reasons.append(f"use_type:{use_type}")
            
            # Jurisdiction match
            if rule_jurisdiction == jurisdiction_lower:
                relevance_score += 5.0
                match_reasons.append(f"jurisdiction:{jurisdiction}")
            
            # Plot area specificity
            if plot_area:
                # Check if rule mentions specific plot sizes
                plot_mentions = re.findall(r'(\d+)\s*sq', rule_text)
                if plot_mentions:
                    for mention in plot_mentions:
                        mentioned_area = float(mention)
                        if abs(mentioned_area - plot_area) < plot_area * 0.2:  # Within 20%
                            relevance_score += 3.0
                            match_reasons.append(f"plot_area_match:{mentioned_area}")
                            break
            
            # Keyword density
            keywords = [use_type_lower, 'fsi', 'permissible', 'basic']
            keyword_count = sum(1 for kw in keywords if kw in rule_text)
            relevance_score += keyword_count * 0.5
            
            ranked.append(RankedRule(
                rule=rule,
                priority=priority,
                relevance_score=relevance_score,
                match_reasons=match_reasons
            ))
        
        # Sort by priority first, then relevance score
        ranked.sort(key=lambda x: (x.priority.value, -x.relevance_score))
        
        return ranked
    
    def extract_fsi_value(self, text: str, use_type: str = None) -> Optional[Tuple[float, str]]:
        """Enhanced FSI value extraction with context awareness"""
        text_lower = text.lower()
        
        # Pattern 1: "FSI shall be X" or "FSI permissible shall be X"
        pattern1 = r'fsi\s+(?:permissible\s+)?(?:shall\s+be|is|of)\s+(\d+\.?\d*)'
        matches1 = re.findall(pattern1, text_lower)
        
        # Pattern 2: "basic FSI X" or "base FSI X"
        pattern2 = r'(?:basic|base)\s+fsi\s+(?:of\s+)?(\d+\.?\d*)'
        matches2 = re.findall(pattern2, text_lower)
        
        # Pattern 3: "FSI up to X" (maximum FSI)
        pattern3 = r'fsi\s+up\s+to\s+(\d+\.?\d*)'
        matches3 = re.findall(pattern3, text_lower)
        
        # Combine all matches
        all_matches = []
        
        for match in matches1:
            try:
                val = float(match)
                if 0.1 <= val <= 10.0:
                    all_matches.append((val, 'explicit'))
            except ValueError:
                continue
        
        for match in matches2:
            try:
                val = float(match)
                if 0.1 <= val <= 10.0:
                    all_matches.append((val, 'basic'))
            except ValueError:
                continue
        
        for match in matches3:
            try:
                val = float(match)
                if 0.1 <= val <= 10.0:
                    all_matches.append((val, 'maximum'))
            except ValueError:
                continue
        
        # Return the most appropriate match
        if all_matches:
            # Prefer 'basic' or 'explicit' over 'maximum'
            for val, context in all_matches:
                if context in ['basic', 'explicit']:
                    return (val, context)
            # Otherwise return first match
            return all_matches[0]
        
        return None
    
    def get_base_fsi_enhanced(self, use_type: str, plot_area: float, 
                             jurisdiction: str = "maharashtra_udcpr") -> Dict[str, Any]:
        """Enhanced FSI calculation with jurisdiction filtering and rule ranking"""
        
        # Get rules for specific jurisdiction first
        jurisdiction_rules = self.rules_by_jurisdiction.get(jurisdiction, [])
        
        # Query FSI rules
        fsi_rules = []
        for rule in jurisdiction_rules:
            text = (rule.get('title', '') + ' ' + rule.get('clause_text', '')).lower()
            if 'fsi' in text or 'floor space index' in text:
                fsi_rules.append(rule)
        
        # If no jurisdiction-specific rules, search all
        if not fsi_rules:
            fsi_rules = [r for r in self.rules if 'fsi' in str(r).lower()]
        
        # Rank rules
        ranked_rules = self.rank_rules(fsi_rules, use_type, jurisdiction, plot_area)
        
        # Extract FSI values from top-ranked rules
        for ranked_rule in ranked_rules[:10]:  # Check top 10
            rule = ranked_rule.rule
            text = rule.get('clause_text', '')
            
            fsi_result = self.extract_fsi_value(text, use_type)
            
            if fsi_result:
                fsi_value, context = fsi_result
                
                return {
                    'base_fsi': fsi_value,
                    'source': 'database_enhanced',
                    'applied_rules': [rule['rule_id']],
                    'rule_text': text[:200],
                    'priority': ranked_rule.priority.name,
                    'relevance_score': ranked_rule.relevance_score,
                    'match_reasons': ranked_rule.match_reasons,
                    'extraction_context': context,
                    'jurisdiction': rule.get('jurisdiction')
                }
        
        # Fallback to known defaults by use type and jurisdiction
        defaults = {
            'maharashtra_udcpr': {
                'Commercial': 2.0,
                'Residential': 1.0,
                'Industrial': 1.0,
                'Mixed': 1.2
            },
            'mumbai_dcpr': {
                'Commercial': 2.5,
                'Residential': 1.33,
                'Industrial': 1.0,
                'Mixed': 1.5
            }
        }
        
        default_fsi = defaults.get(jurisdiction, {}).get(use_type, 1.0)
        
        return {
            'base_fsi': default_fsi,
            'source': 'fallback_default',
            'applied_rules': [f'{jurisdiction}_default_{use_type.lower()}'],
            'rule_text': f'Default FSI for {use_type} in {jurisdiction}',
            'priority': 'FALLBACK',
            'relevance_score': 0.0,
            'match_reasons': ['default_fallback'],
            'extraction_context': 'default',
            'jurisdiction': jurisdiction
        }
    
    def extract_parking_ratio(self, text: str) -> Optional[Tuple[float, str]]:
        """Enhanced parking ratio extraction"""
        
        # Pattern 1: "1 ECS per X sqm"
        pattern1 = r'1\s+(?:ecs|equivalent\s+car\s+space)\s+per\s+(\d+)\s*(?:sq\.?\s*m|sqm)'
        matches1 = re.findall(pattern1, text.lower())
        
        # Pattern 2: "X sqm per ECS"
        pattern2 = r'(\d+)\s*(?:sq\.?\s*m|sqm)\s+per\s+(?:ecs|equivalent\s+car\s+space)'
        matches2 = re.findall(pattern2, text.lower())
        
        if matches1:
            return (float(matches1[0]), 'per_ecs')
        elif matches2:
            return (float(matches2[0]), 'per_ecs')
        
        return None
    
    def get_parking_requirement_enhanced(self, use_type: str, built_up_area: float,
                                        jurisdiction: str = "maharashtra_udcpr") -> Dict[str, Any]:
        """Enhanced parking calculation with jurisdiction filtering"""
        
        # Get jurisdiction-specific rules
        jurisdiction_rules = self.rules_by_jurisdiction.get(jurisdiction, [])
        
        parking_rules = []
        for rule in jurisdiction_rules:
            text = (rule.get('title', '') + ' ' + rule.get('clause_text', '')).lower()
            if 'parking' in text or 'ecs' in text:
                parking_rules.append(rule)
        
        # Rank rules
        ranked_rules = self.rank_rules(parking_rules, use_type, jurisdiction)
        
        # Extract parking ratios
        for ranked_rule in ranked_rules[:5]:
            rule = ranked_rule.rule
            text = rule.get('clause_text', '')
            
            ratio_result = self.extract_parking_ratio(text)
            
            if ratio_result:
                ratio, context = ratio_result
                required_ecs = int(built_up_area / ratio) + (1 if (built_up_area / ratio) % 1 > 0 else 0)
                
                return {
                    'required_ecs': required_ecs,
                    'ratio': ratio,
                    'norm': f"1 ECS per {int(ratio)} sqm",
                    'source': 'database_enhanced',
                    'applied_rules': [rule['rule_id']],
                    'rule_text': text[:200],
                    'priority': ranked_rule.priority.name,
                    'relevance_score': ranked_rule.relevance_score,
                    'jurisdiction': rule.get('jurisdiction')
                }
        
        # Fallback defaults
        defaults = {
            'Residential': 100,
            'Commercial': 50,
            'Industrial': 150,
            'Mixed': 75
        }
        
        ratio = defaults.get(use_type, 100)
        required_ecs = int(built_up_area / ratio) + (1 if (built_up_area / ratio) % 1 > 0 else 0)
        
        return {
            'required_ecs': required_ecs,
            'ratio': ratio,
            'norm': f"1 ECS per {ratio} sqm",
            'source': 'fallback_default',
            'applied_rules': [f'default_parking_{use_type.lower()}'],
            'rule_text': f'Default parking for {use_type}',
            'priority': 'FALLBACK',
            'relevance_score': 0.0,
            'jurisdiction': jurisdiction
        }
    
    def extract_setback_values(self, text: str) -> Dict[str, Optional[float]]:
        """Extract setback values from regulation text"""
        setbacks = {
            'front': None,
            'side': None,
            'rear': None
        }
        
        text_lower = text.lower()
        
        # Pattern: "front setback X m" or "front margin X m"
        front_pattern = r'front\s+(?:setback|margin)\s+(?:of\s+)?(\d+\.?\d*)\s*(?:m|meter)'
        front_matches = re.findall(front_pattern, text_lower)
        if front_matches:
            setbacks['front'] = float(front_matches[0])
        
        # Pattern: "side setback X m"
        side_pattern = r'side\s+(?:setback|margin)\s+(?:of\s+)?(\d+\.?\d*)\s*(?:m|meter)'
        side_matches = re.findall(side_pattern, text_lower)
        if side_matches:
            setbacks['side'] = float(side_matches[0])
        
        # Pattern: "rear setback X m"
        rear_pattern = r'rear\s+(?:setback|margin)\s+(?:of\s+)?(\d+\.?\d*)\s*(?:m|meter)'
        rear_matches = re.findall(rear_pattern, text_lower)
        if rear_matches:
            setbacks['rear'] = float(rear_matches[0])
        
        return setbacks
    
    def get_setbacks_enhanced(self, zone: str, plot_area: float, road_width: float,
                             building_height: float, jurisdiction: str = "maharashtra_udcpr") -> Dict[str, Any]:
        """Enhanced setback calculation with regulation parsing"""
        
        # Get jurisdiction-specific rules
        jurisdiction_rules = self.rules_by_jurisdiction.get(jurisdiction, [])
        
        setback_rules = []
        for rule in jurisdiction_rules:
            text = (rule.get('title', '') + ' ' + rule.get('clause_text', '')).lower()
            if 'setback' in text or 'margin' in text or 'building line' in text:
                setback_rules.append(rule)
        
        # Rank rules
        ranked_rules = self.rank_rules(setback_rules, zone, jurisdiction, plot_area)
        
        # Try to extract setback values
        for ranked_rule in ranked_rules[:10]:
            rule = ranked_rule.rule
            text = rule.get('clause_text', '')
            
            setbacks = self.extract_setback_values(text)
            
            if any(setbacks.values()):
                return {
                    'setbacks': setbacks,
                    'source': 'database_enhanced',
                    'applied_rules': [rule['rule_id']],
                    'rule_text': text[:200],
                    'priority': ranked_rule.priority.name,
                    'rules_found': len(setback_rules)
                }
        
        # Fallback to formula-based calculation
        return {
            'setbacks': None,
            'source': 'formula_fallback',
            'applied_rules': [],
            'rule_text': 'Using formula-based calculation',
            'priority': 'FALLBACK',
            'rules_found': len(setback_rules)
        }
    
    def extract_height_limit(self, text: str) -> Optional[Tuple[float, str]]:
        """Extract height limit from regulation text"""
        text_lower = text.lower()
        
        # Pattern 1: "maximum height X m"
        pattern1 = r'maximum\s+height\s+(?:of\s+)?(\d+\.?\d*)\s*(?:m|meter)'
        matches1 = re.findall(pattern1, text_lower)
        
        # Pattern 2: "height shall not exceed X m"
        pattern2 = r'height\s+shall\s+not\s+exceed\s+(\d+\.?\d*)\s*(?:m|meter)'
        matches2 = re.findall(pattern2, text_lower)
        
        # Pattern 3: "up to X m height"
        pattern3 = r'up\s+to\s+(\d+\.?\d*)\s*(?:m|meter)\s+height'
        matches3 = re.findall(pattern3, text_lower)
        
        if matches1:
            return (float(matches1[0]), 'maximum')
        elif matches2:
            return (float(matches2[0]), 'not_exceed')
        elif matches3:
            return (float(matches3[0]), 'up_to')
        
        return None
    
    def get_height_limit_enhanced(self, zone: str, road_width: float,
                                  jurisdiction: str = "maharashtra_udcpr") -> Dict[str, Any]:
        """Enhanced height calculation with regulation parsing"""
        
        # Get jurisdiction-specific rules
        jurisdiction_rules = self.rules_by_jurisdiction.get(jurisdiction, [])
        
        height_rules = []
        for rule in jurisdiction_rules:
            text = (rule.get('title', '') + ' ' + rule.get('clause_text', '')).lower()
            if 'height' in text or 'storey' in text or 'floor' in text:
                height_rules.append(rule)
        
        # Rank rules
        ranked_rules = self.rank_rules(height_rules, zone, jurisdiction)
        
        # Try to extract height values
        for ranked_rule in ranked_rules[:10]:
            rule = ranked_rule.rule
            text = rule.get('clause_text', '')
            
            height_result = self.extract_height_limit(text)
            
            if height_result:
                height_value, context = height_result
                
                return {
                    'max_height_m': height_value,
                    'source': 'database_enhanced',
                    'applied_rules': [rule['rule_id']],
                    'rule_text': text[:200],
                    'priority': ranked_rule.priority.name,
                    'extraction_context': context,
                    'rules_found': len(height_rules)
                }
        
        # Fallback to formula-based calculation
        return {
            'max_height_m': None,
            'source': 'formula_fallback',
            'applied_rules': [],
            'rule_text': 'Using formula-based calculation',
            'priority': 'FALLBACK',
            'rules_found': len(height_rules)
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        stats = {
            'total_rules': len(self.rules),
            'by_jurisdiction': {
                j: len(rules) for j, rules in self.rules_by_jurisdiction.items()
            }
        }
        
        # Count by category
        for category in ['fsi', 'parking', 'setback', 'height']:
            count = len([r for r in self.rules if category in str(r).lower()])
            stats[f'{category}_rules'] = count
        
        return stats

# Singleton instance
_enhanced_db_instance = None

def get_enhanced_rules_database() -> EnhancedRulesDatabase:
    """Get or create enhanced rules database singleton"""
    global _enhanced_db_instance
    if _enhanced_db_instance is None:
        _enhanced_db_instance = EnhancedRulesDatabase()
    return _enhanced_db_instance

if __name__ == "__main__":
    # Test enhanced database
    db = EnhancedRulesDatabase()
    
    print("\n=== Enhanced Database Statistics ===")
    stats = db.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n=== Test: Commercial FSI (Maharashtra) ===")
    fsi_result = db.get_base_fsi_enhanced("Commercial", 2000, "maharashtra_udcpr")
    print(f"Base FSI: {fsi_result['base_fsi']}")
    print(f"Source: {fsi_result['source']}")
    print(f"Priority: {fsi_result['priority']}")
    print(f"Relevance Score: {fsi_result['relevance_score']}")
    print(f"Match Reasons: {fsi_result['match_reasons']}")
    print(f"Jurisdiction: {fsi_result['jurisdiction']}")
    print(f"Applied Rules: {fsi_result['applied_rules']}")
    
    print("\n=== Test: Residential Parking (Maharashtra) ===")
    parking_result = db.get_parking_requirement_enhanced("Residential", 1000, "maharashtra_udcpr")
    print(f"Required ECS: {parking_result['required_ecs']}")
    print(f"Norm: {parking_result['norm']}")
    print(f"Source: {parking_result['source']}")
    print(f"Priority: {parking_result['priority']}")
    print(f"Jurisdiction: {parking_result['jurisdiction']}")
