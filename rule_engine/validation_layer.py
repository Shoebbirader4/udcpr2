"""
Validation Layer - Compare engine results with regulations and flag discrepancies
Provides confidence scores and warnings for calculation results
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ConfidenceLevel(Enum):
    """Confidence level for calculation results"""
    HIGH = "high"           # 90-100% confidence
    MEDIUM = "medium"       # 70-89% confidence
    LOW = "low"            # 50-69% confidence
    UNCERTAIN = "uncertain" # <50% confidence

class ValidationStatus(Enum):
    """Validation status"""
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"

@dataclass
class ValidationResult:
    """Result of validation check"""
    status: ValidationStatus
    confidence: ConfidenceLevel
    message: str
    details: Dict[str, Any]
    applied_rules: List[str]
    alternative_values: List[Dict[str, Any]] = None

class RuleEngineValidator:
    """Validates rule engine calculations against regulations"""
    
    def __init__(self, rules_db):
        self.db = rules_db
        self.validation_results: List[ValidationResult] = []
    
    def validate_fsi_calculation(self, project_input: Dict[str, Any], 
                                 engine_result: Dict[str, Any]) -> ValidationResult:
        """Validate FSI calculation"""
        
        # Query all applicable FSI rules
        fsi_rules = self.db.query_fsi_rules(
            project_input['use_type'],
            project_input['plot_area_sqm'],
            project_input['jurisdiction']
        )
        
        # Extract FSI values from rules
        found_fsi_values = []
        for rule in fsi_rules[:10]:  # Check top 10 rules
            text = rule.get('clause_text', '').lower()
            use_type = project_input['use_type'].lower()
            
            if use_type in text:
                # Look for FSI values
                import re
                matches = re.findall(r'fsi.*?(\d+\.?\d*)', text, re.IGNORECASE)
                for match in matches:
                    try:
                        fsi_val = float(match)
                        if 0.5 <= fsi_val <= 5.0:
                            found_fsi_values.append({
                                'value': fsi_val,
                                'rule_id': rule['rule_id'],
                                'rule_text': text[:150]
                            })
                    except ValueError:
                        continue
        
        engine_fsi = engine_result.get('base_fsi', 0)
        
        # Check if engine FSI matches any found values
        matching_rules = [f for f in found_fsi_values if abs(f['value'] - engine_fsi) < 0.1]
        
        if matching_rules:
            # Engine FSI matches regulations
            return ValidationResult(
                status=ValidationStatus.PASS,
                confidence=ConfidenceLevel.HIGH,
                message=f"FSI {engine_fsi} validated against {len(matching_rules)} regulation(s)",
                details={
                    'engine_fsi': engine_fsi,
                    'matching_rules': len(matching_rules),
                    'total_rules_checked': len(fsi_rules)
                },
                applied_rules=[r['rule_id'] for r in matching_rules],
                alternative_values=None
            )
        
        elif found_fsi_values:
            # Engine FSI doesn't match, but alternatives exist
            alternatives = sorted(found_fsi_values, key=lambda x: abs(x['value'] - engine_fsi))[:3]
            
            return ValidationResult(
                status=ValidationStatus.WARNING,
                confidence=ConfidenceLevel.MEDIUM,
                message=f"FSI {engine_fsi} doesn't match regulations. Found {len(found_fsi_values)} alternative values",
                details={
                    'engine_fsi': engine_fsi,
                    'alternatives_found': len(found_fsi_values),
                    'closest_alternative': alternatives[0]['value'] if alternatives else None
                },
                applied_rules=engine_result.get('base_fsi_rules', []),
                alternative_values=alternatives
            )
        
        else:
            # No FSI values found in regulations
            return ValidationResult(
                status=ValidationStatus.UNCERTAIN,
                confidence=ConfidenceLevel.LOW,
                message=f"Could not validate FSI {engine_fsi} - no matching regulations found",
                details={
                    'engine_fsi': engine_fsi,
                    'rules_searched': len(fsi_rules)
                },
                applied_rules=engine_result.get('base_fsi_rules', []),
                alternative_values=None
            )
    
    def validate_parking_calculation(self, project_input: Dict[str, Any],
                                     engine_result: Dict[str, Any]) -> ValidationResult:
        """Validate parking calculation"""
        
        parking_rules = self.db.query_parking_rules(project_input['use_type'])
        
        # Look for ECS ratios
        found_ratios = []
        for rule in parking_rules[:10]:
            text = rule.get('clause_text', '')
            
            import re
            # Pattern: "1 ECS per 100" or "1 ECS per 50"
            matches = re.findall(r'1\s+ECS\s+per\s+(\d+)', text, re.IGNORECASE)
            
            for match in matches:
                ratio = float(match)
                found_ratios.append({
                    'ratio': ratio,
                    'rule_id': rule['rule_id'],
                    'rule_text': text[:150]
                })
        
        engine_ratio = engine_result.get('ratio', 0)
        
        # Check if engine ratio matches
        matching = [r for r in found_ratios if abs(r['ratio'] - engine_ratio) < 1]
        
        if matching:
            return ValidationResult(
                status=ValidationStatus.PASS,
                confidence=ConfidenceLevel.HIGH,
                message=f"Parking ratio 1 ECS per {engine_ratio} sqm validated",
                details={
                    'engine_ratio': engine_ratio,
                    'matching_rules': len(matching)
                },
                applied_rules=[r['rule_id'] for r in matching],
                alternative_values=None
            )
        
        elif found_ratios:
            alternatives = sorted(found_ratios, key=lambda x: abs(x['ratio'] - engine_ratio))[:3]
            
            return ValidationResult(
                status=ValidationStatus.WARNING,
                confidence=ConfidenceLevel.MEDIUM,
                message=f"Parking ratio {engine_ratio} doesn't match regulations",
                details={
                    'engine_ratio': engine_ratio,
                    'alternatives_found': len(found_ratios)
                },
                applied_rules=engine_result.get('parking_rules', []),
                alternative_values=alternatives
            )
        
        else:
            return ValidationResult(
                status=ValidationStatus.UNCERTAIN,
                confidence=ConfidenceLevel.LOW,
                message=f"Could not validate parking ratio {engine_ratio}",
                details={
                    'engine_ratio': engine_ratio,
                    'rules_searched': len(parking_rules)
                },
                applied_rules=engine_result.get('parking_rules', []),
                alternative_values=None
            )
    
    def validate_jurisdiction_match(self, project_input: Dict[str, Any],
                                    engine_result: Dict[str, Any]) -> ValidationResult:
        """Validate that applied rules match project jurisdiction"""
        
        project_jurisdiction = project_input.get('jurisdiction', '').lower()
        applied_rules = engine_result.get('base_fsi_rules', [])
        
        mismatched_rules = []
        for rule_id in applied_rules:
            rule = self.db.get_rule_by_id(rule_id)
            if rule:
                rule_jurisdiction = rule.get('jurisdiction', '').lower()
                if rule_jurisdiction and rule_jurisdiction != project_jurisdiction:
                    mismatched_rules.append({
                        'rule_id': rule_id,
                        'rule_jurisdiction': rule_jurisdiction,
                        'project_jurisdiction': project_jurisdiction
                    })
        
        if not mismatched_rules:
            return ValidationResult(
                status=ValidationStatus.PASS,
                confidence=ConfidenceLevel.HIGH,
                message=f"All applied rules match jurisdiction: {project_jurisdiction}",
                details={
                    'project_jurisdiction': project_jurisdiction,
                    'rules_checked': len(applied_rules)
                },
                applied_rules=applied_rules,
                alternative_values=None
            )
        else:
            return ValidationResult(
                status=ValidationStatus.FAIL,
                confidence=ConfidenceLevel.LOW,
                message=f"Jurisdiction mismatch: {len(mismatched_rules)} rule(s) from wrong jurisdiction",
                details={
                    'project_jurisdiction': project_jurisdiction,
                    'mismatched_rules': mismatched_rules
                },
                applied_rules=applied_rules,
                alternative_values=None
            )
    
    def validate_full_evaluation(self, project_input: Dict[str, Any],
                                 evaluation_result: Any) -> Dict[str, Any]:
        """Validate complete project evaluation"""
        
        validations = {
            'fsi': self.validate_fsi_calculation(
                project_input,
                evaluation_result.fsi_result
            ),
            'parking': self.validate_parking_calculation(
                project_input,
                evaluation_result.parking_result
            ),
            'jurisdiction': self.validate_jurisdiction_match(
                project_input,
                evaluation_result.fsi_result
            )
        }
        
        # Calculate overall confidence
        confidence_scores = {
            ConfidenceLevel.HIGH: 4,
            ConfidenceLevel.MEDIUM: 3,
            ConfidenceLevel.LOW: 2,
            ConfidenceLevel.UNCERTAIN: 1
        }
        
        avg_confidence = sum(confidence_scores[v.confidence] for v in validations.values()) / len(validations)
        
        if avg_confidence >= 3.5:
            overall_confidence = ConfidenceLevel.HIGH
        elif avg_confidence >= 2.5:
            overall_confidence = ConfidenceLevel.MEDIUM
        elif avg_confidence >= 1.5:
            overall_confidence = ConfidenceLevel.LOW
        else:
            overall_confidence = ConfidenceLevel.UNCERTAIN
        
        # Count issues
        warnings = [k for k, v in validations.items() if v.status == ValidationStatus.WARNING]
        failures = [k for k, v in validations.items() if v.status == ValidationStatus.FAIL]
        
        return {
            'overall_confidence': overall_confidence.value,
            'confidence_score': f"{avg_confidence:.1f}/4.0",
            'validations': {
                k: {
                    'status': v.status.value,
                    'confidence': v.confidence.value,
                    'message': v.message,
                    'details': v.details,
                    'applied_rules': v.applied_rules,
                    'alternative_values': v.alternative_values
                }
                for k, v in validations.items()
            },
            'warnings': warnings,
            'failures': failures,
            'recommendation': self._generate_recommendation(overall_confidence, warnings, failures)
        }
    
    def _generate_recommendation(self, confidence: ConfidenceLevel, 
                                warnings: List[str], failures: List[str]) -> str:
        """Generate recommendation based on validation results"""
        
        if failures:
            return f"CAUTION: {len(failures)} validation failure(s). Review applied rules and verify jurisdiction match."
        
        elif warnings:
            return f"REVIEW: {len(warnings)} warning(s). Consider alternative values from regulations."
        
        elif confidence == ConfidenceLevel.HIGH:
            return "APPROVED: High confidence. Results validated against regulations."
        
        elif confidence == ConfidenceLevel.MEDIUM:
            return "ACCEPTABLE: Medium confidence. Results appear reasonable but verify with authorities."
        
        else:
            return "UNCERTAIN: Low confidence. Manual verification strongly recommended."

# Example usage
if __name__ == "__main__":
    from rules_database import get_rules_database
    from rule_engine_v2 import DatabaseDrivenRuleEngine, ProjectInput
    
    # Create project
    project = ProjectInput(
        jurisdiction="maharashtra_udcpr",
        zone="Commercial",
        plot_area_sqm=2000,
        road_width_m=18,
        frontage_m=40,
        use_type="Commercial",
        proposed_floors=5,
        proposed_height_m=18,
        proposed_built_up_sqm=3000
    )
    
    # Evaluate with engine
    engine = DatabaseDrivenRuleEngine()
    result = engine.evaluate_project(project)
    
    # Validate results
    print("\n" + "="*80)
    print("VALIDATION REPORT")
    print("="*80)
    
    db = get_rules_database()
    validator = RuleEngineValidator(db)
    
    validation = validator.validate_full_evaluation(
        project.dict(),
        result
    )
    
    print(f"\nOverall Confidence: {validation['overall_confidence'].upper()}")
    print(f"Confidence Score: {validation['confidence_score']}")
    print(f"\nRecommendation: {validation['recommendation']}")
    
    print("\n--- Validation Details ---")
    for category, details in validation['validations'].items():
        print(f"\n{category.upper()}:")
        print(f"  Status: {details['status']}")
        print(f"  Confidence: {details['confidence']}")
        print(f"  Message: {details['message']}")
        
        if details['alternative_values']:
            print(f"  Alternatives:")
            for alt in details['alternative_values']:
                print(f"    - {alt}")
    
    if validation['warnings']:
        print(f"\nWarnings: {', '.join(validation['warnings'])}")
    
    if validation['failures']:
        print(f"\nFailures: {', '.join(validation['failures'])}")
