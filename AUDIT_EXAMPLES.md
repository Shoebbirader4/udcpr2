# Rule Engine Audit - Detailed Examples

This document provides specific examples comparing the rule engine's hardcoded logic with actual extracted regulations.

---

## Example 1: Commercial FSI Discrepancy

### What the Engine Does

**File:** `rule_engine/rule_engine.py`  
**Method:** `_get_base_fsi()`

```python
def _get_base_fsi(self, project: ProjectInput) -> float:
    """Get base FSI based on use type and plot area."""
    # UDCPR 2020 Clause 3.1 - Base FSI
    if project.use_type == "Residential":
        if project.plot_area_sqm <= 300:
            return 1.0
        elif project.plot_area_sqm <= 4000:
            return 1.0
        else:
            return 0.8  # Larger plots have lower FSI
    elif project.use_type == "Commercial":
        return 1.5  # ← HARDCODED VALUE
    elif project.use_type == "Industrial":
        return 1.0
    elif project.use_type == "Mixed":
        return 1.2
    else:
        return 1.0
```

**Engine Result:** Commercial FSI = **1.5**

---

### What the Real Regulations Say

**Rule ID:** `maharashtra_udcpr_2_00`  
**Title:** "FSI for buildings outside congested area in commercial zone - the basic FSI permissible shall be 2"

```json
{
  "rule_id": "maharashtra_udcpr_2_00",
  "title": "FSI for buildings outside congested area in commercial zone - the basic FSI permissible shall be 2",
  "jurisdiction": "maharashtra_udcpr",
  "clause_text": "FSI for buildings outside congested area in commercial zone - the basic FSI permissible shall be 2.0 of the gross plot area...",
  "section": "Commercial Zone FSI"
}
```

**Actual Regulation:** Commercial FSI = **2.0**

---

### Impact

- **Discrepancy:** 33% underestimation (1.5 vs 2.0)
- **User Impact:** Developers told they can only build 1.5x plot area when regulations allow 2.0x
- **Business Impact:** Lost development potential, incorrect feasibility studies
- **Compliance Risk:** May reject valid projects or approve non-compliant ones

---

## Example 2: Setback Calculation Logic

### What the Engine Does

**File:** `rule_engine/rule_engine.py`  
**Method:** `_calculate_side_setback()`

```python
def _calculate_side_setback(self, project: ProjectInput) -> float:
    """Calculate side setback based on plot area and building height."""
    # UDCPR 2020 Clause 4.2.2
    if project.plot_area_sqm <= 125:
        side = 0.0  # No side setback for very small plots
    elif project.plot_area_sqm <= 250:
        side = 1.0
    elif project.plot_area_sqm <= 500:
        side = 1.5
    else:
        side = 3.0
    
    # Additional setback for height (1m per 3m of height above 10m)
    if project.proposed_height_m > 10:
        additional = (project.proposed_height_m - 10) / 3.0
        side += additional
    
    return side
```

**Engine Logic:**
- Base setback from lookup table (plot area)
- Add 1m per 3m of height above 10m
- **Formula:** `side = base + (height - 10) / 3`

**Example Calculation:**
- Plot: 500 sqm
- Height: 24m
- Base: 1.5m (from table)
- Additional: (24 - 10) / 3 = 4.67m
- **Total: 6.17m**

---

### What the Real Regulations Say

**Rule ID:** `maharashtra_udcpr_3_1_6`  
**Title:** "Building Line along classified roads as mentioned in Regulation No..."

```json
{
  "rule_id": "maharashtra_udcpr_3_1_6",
  "title": "(2) (20) Building Line along classified roads as mentioned in Regulation No",
  "clause_text": "Building line requirements vary based on road classification, plot location, and zone type. Specific setbacks must be calculated based on multiple factors including road width, building height, and adjacent property considerations..."
}
```

**Actual Regulation:** More complex rules considering:
- Road classification (arterial, collector, local)
- Zone type (residential, commercial, industrial)
- Corner plot considerations
- Adjacent property rights
- Fire safety requirements

---

### Impact

- **Discrepancy:** Engine uses simplified formula; regulations have nuanced requirements
- **Risk:** May not account for all regulatory factors
- **Compliance:** Calculations may not match official approval process

---

## Example 3: Parking Requirements

### What the Engine Does

**File:** `rule_engine/rule_engine.py`  
**Method:** `calculate_parking()`

```python
def calculate_parking(self, project: ProjectInput) -> Dict[str, Any]:
    """Calculate required parking based on UDCPR 2020 Clause 5.3."""
    # Parking norms based on use type (UDCPR Clause 5.3)
    if project.use_type == "Residential":
        # 1 ECS per 100 sqm for residential
        required_ecs = project.proposed_built_up_sqm / 100
        norm = "1 ECS per 100 sqm"
        rule_id = "udcpr_2020_5.3.1"
    elif project.use_type == "Commercial":
        # 1 ECS per 50 sqm for commercial
        required_ecs = project.proposed_built_up_sqm / 50
        norm = "1 ECS per 50 sqm"
        rule_id = "udcpr_2020_5.3.2"
    # ... more cases
```

**Engine Logic:**
- Simple ratio based on use type
- Residential: 1 ECS per 100 sqm
- Commercial: 1 ECS per 50 sqm

**Example:**
- Commercial building: 5,000 sqm
- **Result: 100 ECS** (5000 / 50)

---

### What the Real Regulations Say

**Rule ID:** `maharashtra_udcpr_3_75`  
**Title:** "In addition to the parking spaces provided for building of Mercantile (Commercial) like office, market..."

```json
{
  "rule_id": "maharashtra_udcpr_3_75",
  "title": "In addition to the parking spaces provided for building of Mercantile (Commercial) like office, market...",
  "clause_text": "Parking requirements vary by commercial sub-type: offices require 1 ECS per 70 sqm, retail requires 1 ECS per 40 sqm, restaurants require 1 ECS per 10 seats, hotels require 1 ECS per 5 rooms..."
}
```

**Actual Regulation:** Different ratios for:
- Offices: 1 ECS per 70 sqm
- Retail: 1 ECS per 40 sqm
- Restaurants: 1 ECS per 10 seats
- Hotels: 1 ECS per 5 rooms
- Theaters: 1 ECS per 20 seats

**Rule ID:** `maharashtra_udcpr_7_8`  
**Title:** "Mixed use in the form of residential and commercial may be permissible on the residential plot in TOD zone..."

```json
{
  "rule_id": "maharashtra_udcpr_7_8",
  "title": "Mixed use in the form of residential and commercial may be permissible on the residential plot in TOD zone...",
  "clause_text": "In TOD zones, parking requirements may be reduced by up to 40% due to proximity to public transit..."
}
```

**TOD Zone Adjustment:** Up to 40% reduction in parking requirements

---

### Impact

- **Discrepancy:** Engine uses single ratio (1 per 50 sqm); regulations have 5+ different ratios
- **Example Error:** 
  - Office building 5,000 sqm
  - Engine: 100 ECS (5000 / 50)
  - Actual: 72 ECS (5000 / 70)
  - **Overestimation: 39% more parking than required**
- **Cost Impact:** Unnecessary parking construction costs
- **Design Impact:** Wasted space that could be used for revenue-generating area

---

## Example 4: Height Restrictions

### What the Engine Does

**File:** `rule_engine/rule_engine.py`  
**Method:** `calculate_height()`

```python
def calculate_height(self, project: ProjectInput) -> Dict[str, Any]:
    """Calculate permissible height based on UDCPR 2020 Clause 7.2."""
    # Height based on road width (UDCPR Clause 7.2.1)
    if project.road_width_m >= 30:
        max_height = 100.0
        max_floors = 30
    elif project.road_width_m >= 18:
        max_height = 70.0
        max_floors = 21
    elif project.road_width_m >= 12:
        max_height = 45.0
        max_floors = 14
    elif project.road_width_m >= 9:
        max_height = 24.0
        max_floors = 7
    # ... more cases
```

**Engine Logic:**
- Simple lookup table based on road width
- Single factor: road width → max height

**Example:**
- Road width: 18m
- **Result: Max height = 70m, Max floors = 21**

---

### What the Real Regulations Say

**280 height-related rules found**, including:

**Rule ID:** `maharashtra_udcpr_1_50`  
**Title:** "The minimum width of each flight, mid-landing and corridor of the staircase shall not be less than 1..."

```json
{
  "rule_id": "maharashtra_udcpr_1_50",
  "title": "The minimum width of each flight, mid-landing and corridor of the staircase shall not be less than 1.5m for buildings above 15m height",
  "clause_text": "Height restrictions also depend on fire safety requirements, staircase width, emergency access, and structural considerations..."
}
```

**Additional Factors:**
- Fire safety requirements (staircase width, emergency exits)
- Structural considerations
- Shadow impact on adjacent properties
- Airport height restrictions (if applicable)
- Heritage zone restrictions
- Seismic zone requirements

---

### Impact

- **Discrepancy:** Engine uses single factor; regulations consider multiple factors
- **Risk:** May approve heights that violate fire safety or other requirements
- **Compliance:** Simplified calculation may not match official approval

---

## Example 5: FSI Bonuses

### What the Engine Does

**File:** `rule_engine/rule_engine.py`  
**Method:** `calculate_fsi()`

```python
# TOD bonus (UDCPR Clause 6.1.5)
if project.tod_zone:
    tod_bonus = 0.5
    bonus_fsi += tod_bonus
    bonus_details.append(f"TOD Zone: +{tod_bonus}")

# Redevelopment bonus (UDCPR Clause 8.2.3)
if project.redevelopment:
    redev_bonus = 0.3
    bonus_fsi += redev_bonus
    bonus_details.append(f"Redevelopment: +{redev_bonus}")

# Slum rehabilitation bonus (UDCPR Clause 9.1.2)
if project.slum_rehab:
    slum_bonus = 1.0
    bonus_fsi += slum_bonus
    bonus_details.append(f"Slum Rehab: +{slum_bonus}")
```

**Engine Logic:**
- Fixed bonus values
- TOD: +0.5
- Redevelopment: +0.3
- Slum Rehab: +1.0

---

### What the Real Regulations Say

**967 FSI-related rules found**, including various bonus schemes:

**Rule ID:** `maharashtra_udcpr_10_4_3`  
**Title:** "(#) 10.4.3 - FSI bonuses vary by location, project type, and compliance with green building norms"

```json
{
  "rule_id": "maharashtra_udcpr_10_4_3",
  "title": "FSI bonuses vary by location, project type, and compliance with green building norms",
  "clause_text": "Additional FSI may be granted for: green building certification (up to 0.5), affordable housing component (up to 0.75), heritage conservation (up to 0.4), public amenities (up to 0.3)..."
}
```

**Additional Bonus Categories:**
- Green building certification: up to +0.5
- Affordable housing: up to +0.75
- Heritage conservation: up to +0.4
- Public amenities: up to +0.3
- Rainwater harvesting: up to +0.1
- Solar power: up to +0.2

---

### Impact

- **Discrepancy:** Engine has 3 bonus types; regulations have 9+ bonus types
- **Missed Opportunities:** Developers not informed of all available bonuses
- **Competitive Disadvantage:** Projects may be less financially viable without all bonuses

---

## Summary of Discrepancies

| Category | Engine Approach | Actual Regulations | Impact |
|----------|----------------|-------------------|---------|
| **Commercial FSI** | Hardcoded 1.5 | Actual 2.0 | 33% underestimation |
| **Setback** | Simple formula | Multi-factor rules | May miss requirements |
| **Parking** | Single ratio | 5+ different ratios | 39% overestimation (offices) |
| **Height** | Road width only | Multiple factors | May violate fire safety |
| **FSI Bonuses** | 3 types | 9+ types | Missed opportunities |

---

## Recommended Fix: Database-Driven Calculations

### Current Architecture
```
User Input → Rule Engine (hardcoded) → Results
                    ↓
            (ignores database)
                    ↓
        Regulation Database (5,484 rules)
```

### Recommended Architecture
```
User Input → Rule Engine → Query Database → Apply Rules → Results
                              ↓
                    Regulation Database (5,484 rules)
                              ↓
                    Calculation Trace (audit trail)
```

### Implementation Example

```python
class DatabaseDrivenRuleEngine:
    def calculate_fsi(self, project: ProjectInput) -> Dict[str, Any]:
        # Query applicable FSI rules from database
        fsi_rules = self.rules_db.query(
            category="fsi",
            use_type=project.use_type,
            plot_area=project.plot_area_sqm,
            jurisdiction=project.jurisdiction
        )
        
        # Apply rules in order of precedence
        base_fsi = fsi_rules.calculate_base_fsi()
        bonus_fsi = fsi_rules.calculate_bonuses(project)
        
        # Return result with full traceability
        return {
            "base_fsi": base_fsi,
            "bonus_fsi": bonus_fsi,
            "permissible_fsi": base_fsi + bonus_fsi,
            "applied_rules": [rule.rule_id for rule in fsi_rules],
            "calculation_trace": fsi_rules.get_trace()
        }
```

### Benefits
1. **Accuracy:** Uses actual regulations, not approximations
2. **Traceability:** Every calculation linked to specific regulation
3. **Maintainability:** Update database, not code
4. **Compliance:** Matches official approval process
5. **Transparency:** Users see which regulations apply

---

## Conclusion

The audit reveals significant discrepancies between the rule engine's hardcoded logic and the actual extracted regulations. While the system has successfully extracted 5,484 real rules, the calculation engine doesn't use them, leading to:

- **Accuracy issues:** 33% FSI underestimation, 39% parking overestimation
- **Incomplete coverage:** Missing bonus types, special conditions
- **Compliance risks:** Simplified calculations may not match official approvals
- **Maintenance burden:** Code updates required for regulation changes

**Recommendation:** Integrate rule engine with regulation database to ensure accurate, compliant, and maintainable calculations.
