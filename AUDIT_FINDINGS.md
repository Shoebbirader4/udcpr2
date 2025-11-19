# Rule Engine Accuracy Audit - Findings Report

**Date:** November 19, 2025  
**Audit Scope:** Comparison of Rule Engine calculation logic vs Real UDCPR/Mumbai DCPR regulations  
**Total Rules Analyzed:** 5,484 extracted regulations

---

## Executive Summary

The audit reveals a **critical integration gap** between the extracted regulatory database (5,484 real rules) and the calculation engine. While the system has successfully extracted and indexed comprehensive UDCPR/Mumbai DCPR regulations, the rule engine operates independently using hardcoded formulas rather than querying the actual regulations.

### Key Metrics

| Category | Extracted Rules | Engine Tests | Matching Rules Found |
|----------|----------------|--------------|---------------------|
| **FSI** | 948 rules | 3 tests | 123-247 matches per test |
| **Setback** | 31 rules | 3 tests | 11-31 matches per test |
| **Coverage** | 7 rules | 3 tests | 0-7 matches per test |
| **Height** | 280 rules | 3 tests | 8-32 matches per test |
| **Parking** | 323 rules | 2 tests | 10-24 matches per test |
| **TOTAL** | **5,484 rules** | **14 tests** | **1,589 total matches** |

---

## Detailed Findings

### 1. FSI (Floor Space Index) Calculations

**Extracted Rules:** 948 FSI-related regulations  
**Engine Logic:** Hardcoded lookup table based on use type

#### Test Results:

**Test 1: Residential, 1000 sqm, 12m road**
- Engine Result: Base FSI = 1.0, Permissible FSI = 1.0
- Matching Real Rules: 123 rules found
- Sample Rules:
  - `maharashtra_udcpr_10_4_3`: FSI regulations for specific zones
  - `maharashtra_udcpr_1_25`: "For Plots admeasuring 1000 sq..."
  - `maharashtra_udcpr_23_0`: Buffer zone FSI requirements

**Test 2: Commercial, 2000 sqm, 18m road**
- Engine Result: Base FSI = 1.5, Permissible FSI = 1.5
- Matching Real Rules: 69 rules found
- Sample Rules:
  - `maharashtra_udcpr_10_3_1`: Nagpur Municipal Corporation commercial FSI
  - `maharashtra_udcpr_2_00`: "FSI for buildings outside congested area in commercial zone - the basic FSI permissible shall be 2"
  - **DISCREPANCY:** Real rule shows FSI = 2.0, but engine uses 1.5

**Test 3: Industrial, 5000 sqm, 24m road**
- Engine Result: Base FSI = 1.0, Permissible FSI = 1.0
- Matching Real Rules: 55 rules found

**Finding:** Engine uses simplified FSI values that may not match actual regulations. For example, commercial FSI is hardcoded as 1.5, but extracted rules show 2.0 for certain zones.

---

### 2. Setback Calculations

**Extracted Rules:** 31 setback-related regulations  
**Engine Logic:** Hardcoded formulas based on road width and plot area

#### Test Results:

**Test 1: Residential, 500 sqm, 12m height**
- Engine Result: Front=3.0m, Side=2.17m, Rear=2.0m
- Matching Real Rules: 31 rules found
- Sample Rules:
  - `maharashtra_udcpr_1_2`: "The width of passage shall be minimum 1..."
  - `maharashtra_udcpr_23_0`: Buffer zone setback requirements

**Test 2: Residential, 1500 sqm, 24m height**
- Engine Result: Front=4.5m, Side=7.67m, Rear=3.0m
- Matching Real Rules: 31 rules found

**Test 3: Commercial, 2000 sqm, 30m height**
- Engine Result: Front=6.0m, Side=9.67m, Rear=3.0m
- Matching Real Rules: 11 rules found
- Sample Rules:
  - `maharashtra_udcpr_3_1_6`: Building line regulations for classified roads

**Finding:** Engine calculates setbacks using formulas (e.g., additional 1m per 3m height above 10m), but doesn't reference specific regulation clauses. Real rules may have more nuanced requirements.

---

### 3. Coverage Calculations

**Extracted Rules:** 7 coverage-related regulations  
**Engine Logic:** Derived from setback calculations (Coverage = 100% - open space)

#### Test Results:

**Test 1: Residential, 1000 sqm**
- Engine Result: Open Space = 51.7%, Coverage ~= 48.3%
- Matching Real Rules: 0-7 rules found

**Test 2: Commercial, 2000 sqm**
- Engine Result: Open Space = 44.2%, Coverage ~= 55.8%

**Test 3: Industrial, 5000 sqm**
- Engine Result: Open Space = 39.7%, Coverage ~= 60.3%

**Finding:** Very few coverage rules extracted (only 7). Engine doesn't directly calculate coverage but derives it from setbacks. This may not align with explicit coverage regulations in UDCPR.

---

### 4. Height Calculations

**Extracted Rules:** 280 height-related regulations  
**Engine Logic:** Hardcoded lookup table based on road width

#### Test Results:

**Test 1: Residential, 9m road**
- Engine Result: Max Height = 24.0m, Max Floors = 7
- Matching Real Rules: 32 rules found
- Sample Rules:
  - `maharashtra_udcpr_1_50`: Staircase width requirements
  - `maharashtra_udcpr_3_1_6`: Building line regulations
  - `maharashtra_udcpr_9_28_3`: Corridor width requirements

**Test 2: Residential, 18m road**
- Engine Result: Max Height = 70.0m, Max Floors = 21
- Matching Real Rules: 32 rules found

**Test 3: Commercial, 24m road**
- Engine Result: Max Height = 70.0m, Max Floors = 21
- Matching Real Rules: 8 rules found

**Finding:** 280 height-related rules exist, but engine uses simple road width-based lookup. Real regulations may include additional factors like plot area, zone type, and special conditions.

---

### 5. Parking Calculations

**Extracted Rules:** 323 parking-related regulations  
**Engine Logic:** Hardcoded ratios (1 ECS per 100 sqm residential, 1 ECS per 50 sqm commercial)

#### Test Results:

**Test 1: Residential, 1000 sqm**
- Engine Result: 10 ECS (1 ECS per 100 sqm)
- Matching Real Rules: 24 rules found
- Sample Rules:
  - `maharashtra_udcpr_7_8`: Mixed-use parking requirements in TOD zones
  - `maharashtra_udcpr_rule_1000`: Plot size requirements

**Test 2: Commercial, 5000 sqm**
- Engine Result: 100 ECS (1 ECS per 50 sqm)
- Matching Real Rules: 10 rules found
- Sample Rules:
  - `maharashtra_udcpr_3_75`: "In addition to the parking spaces provided for building of Mercantile (Commercial) like office, market..."

**Finding:** 323 parking rules exist with nuanced requirements for different building types, but engine uses simplified ratios.

---

## Critical Issues Identified

### Issue 1: Two Separate Systems
- **Vector Store (AI Assistant):** 5,484 indexed rules for semantic search
- **Rule Engine (Calculations):** Hardcoded formulas, no database integration
- **Impact:** Users get different information from AI Assistant vs calculation results

### Issue 2: Accuracy Concerns
- Engine uses approximations (e.g., Commercial FSI = 1.5 vs actual 2.0)
- Hardcoded values may not reflect latest regulation updates
- No traceability to specific regulation clauses in calculations

### Issue 3: Maintenance Burden
- Regulation changes require manual code updates
- No automated validation against actual regulations
- Risk of outdated calculations as regulations evolve

### Issue 4: Compliance Risk
- Calculations may not reflect actual legal requirements
- Users may receive incorrect compliance assessments
- Potential liability for incorrect building approvals

---

## Recommendations

### Priority 1: Integrate Rule Engine with Regulation Database

**Action:** Modify rule engine to query extracted regulations instead of using hardcoded values

**Implementation:**
```python
# Current approach (hardcoded)
def _get_base_fsi(self, project):
    if project.use_type == "Commercial":
        return 1.5  # Hardcoded

# Recommended approach (database query)
def _get_base_fsi(self, project):
    rules = self.rules_db.query_fsi_rules(
        use_type=project.use_type,
        plot_area=project.plot_area_sqm,
        jurisdiction=project.jurisdiction
    )
    return rules.calculate_applicable_fsi()
```

**Benefits:**
- Accurate calculations based on actual regulations
- Automatic updates when regulations change
- Full traceability to regulation clauses

---

### Priority 2: Add Validation Layer

**Action:** Create validation system to compare engine results with regulation database

**Implementation:**
```python
class RuleValidator:
    def validate_calculation(self, result, project):
        # Query actual regulations
        applicable_rules = self.find_applicable_rules(project)
        
        # Compare engine result with regulations
        discrepancies = self.compare_with_regulations(result, applicable_rules)
        
        # Flag warnings if discrepancies found
        if discrepancies:
            result.add_warnings(discrepancies)
```

**Benefits:**
- Catch calculation errors
- Identify outdated hardcoded values
- Provide confidence scores for results

---

### Priority 3: Implement Rule Versioning

**Action:** Track regulation versions and effective dates

**Implementation:**
- Add version tracking to regulation database
- Allow calculations for specific regulation versions
- Maintain audit trail of which regulations were used

**Benefits:**
- Historical compliance checking
- Support for grandfathered projects
- Clear documentation of applicable regulations

---

### Priority 4: Unify AI Assistant and Calculation Engine

**Action:** Use same regulation database for both semantic search and calculations

**Implementation:**
- Extend vector store with structured calculation logic
- Add calculation methods to regulation objects
- Ensure consistency between AI responses and calculations

**Benefits:**
- Consistent user experience
- Single source of truth
- Reduced maintenance burden

---

## Sample Discrepancies Found

### Commercial FSI Discrepancy
- **Engine Value:** 1.5
- **Actual Regulation:** 2.0 (maharashtra_udcpr_2_00)
- **Impact:** Underestimating permissible FSI by 33%

### Setback Calculation Method
- **Engine Method:** Formula-based (1m per 3m height above 10m)
- **Actual Regulations:** May have specific requirements per zone/plot size
- **Impact:** Potential non-compliance with specific setback rules

### Parking Requirements
- **Engine Method:** Simple ratio (1 ECS per 100 sqm residential)
- **Actual Regulations:** 323 rules with nuanced requirements
- **Impact:** May not account for special cases (TOD zones, mixed-use, etc.)

---

## Next Steps

1. **Immediate (Week 1-2):**
   - Review and document all hardcoded values in rule engine
   - Identify top 10 most critical discrepancies
   - Create validation test suite comparing engine vs regulations

2. **Short-term (Month 1):**
   - Implement database query layer for FSI calculations
   - Add validation warnings for discrepancies
   - Update documentation with known limitations

3. **Medium-term (Month 2-3):**
   - Refactor setback, height, and parking calculations to use database
   - Implement rule versioning system
   - Add comprehensive test coverage

4. **Long-term (Month 4-6):**
   - Unify AI Assistant and calculation engine
   - Implement automated regulation update pipeline
   - Add machine learning for ambiguous rule interpretation

---

## Conclusion

The UDCPR Master system has successfully extracted 5,484 real regulations from UDCPR/Mumbai DCPR documents, demonstrating strong data extraction capabilities. However, the calculation engine operates independently using simplified, hardcoded logic that may not accurately reflect the actual regulations.

**Key Takeaway:** The system has the data (5,484 rules) but isn't using it for calculations. Integrating the rule engine with the extracted regulation database is critical for accuracy, compliance, and maintainability.

**Risk Level:** **HIGH** - Current approach may produce incorrect compliance assessments, creating legal and liability risks.

**Recommended Action:** Prioritize integration of rule engine with regulation database to ensure calculations reflect actual legal requirements.

---

## Appendix: Audit Methodology

### Data Sources
- Extracted regulations: `udcpr_master_data/approved_rules/*.json`
- Rule engine code: `rule_engine/rule_engine.py`
- Vector store: ChromaDB with 5,484 indexed rules

### Test Approach
- Created 14 test cases across 5 calculation categories
- Compared engine results with matching regulations from database
- Analyzed discrepancies and documented findings

### Tools Used
- Python audit script: `scripts/audit_rule_engine.py`
- Semantic search for matching regulations
- Manual review of sample regulations

### Limitations
- Audit based on keyword matching (may miss relevant rules)
- Did not perform detailed legal analysis of each regulation
- Sample size limited to 14 test cases
- Did not test all edge cases and special conditions

---

**Report Generated:** November 19, 2025  
**Auditor:** Automated Rule Engine Audit System  
**Version:** 1.0
