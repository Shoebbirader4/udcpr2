#!/usr/bin/env python3
"""
Mock ingestion script for testing the admin UI.
Generates sample candidate rules without requiring OCR/LLM.
"""
import json
import os
from pathlib import Path
from datetime import datetime

WORK_DIR = Path("udcpr_master_data")
STAGING_DIR = WORK_DIR / "staging_rules"

# Comprehensive sample rules based on UDCPR and Mumbai DCPR
SAMPLE_RULES = [
    {
        "rule_id": "udcpr_fsi_residential_001",
        "title": "Base FSI for Residential Zone",
        "jurisdiction": "maharashtra_udcpr",
        "version": "udcpr_20250130",
        "clause_number": "3.1.1",
        "clause_text": "The base FSI for residential zones shall be 1.0 for plots up to 4000 sqm.",
        "parsed": {
            "type": "rule",
            "rule_logic": {
                "conditions": [
                    {"field": "use_type", "op": "==", "value": "Residential"},
                    {"field": "plot_area_sqm", "op": "<=", "value": 4000}
                ],
                "outputs": [
                    {"field": "base_fsi", "value": 1.0, "units": "ratio"}
                ]
            }
        },
        "examples": [
            {
                "input": {"use_type": "Residential", "plot_area_sqm": 500},
                "expected_output": {"base_fsi": 1.0}
            }
        ],
        "ambiguous": False,
        "ambiguity_reason": None,
        "source_pdf": {
            "filename": "UDCPR_Updated_30Jan2025.pdf",
            "page": 45,
            "text_snippet": "Base FSI for residential..."
        },
        "created_at": datetime.now().isoformat()
    },
    {
        "rule_id": "udcpr_setback_front_001",
        "title": "Front Setback for Road Width >= 18m",
        "jurisdiction": "maharashtra_udcpr",
        "version": "udcpr_20250130",
        "clause_number": "4.2.1",
        "clause_text": "For roads with width 18 meters or more, the minimum front setback shall be 6 meters.",
        "parsed": {
            "type": "rule",
            "rule_logic": {
                "conditions": [
                    {"field": "road_width_m", "op": ">=", "value": 18}
                ],
                "outputs": [
                    {"field": "front_setback", "value": 6.0, "units": "m"}
                ]
            }
        },
        "examples": [
            {
                "input": {"road_width_m": 18},
                "expected_output": {"front_setback": 6.0}
            }
        ],
        "ambiguous": False,
        "ambiguity_reason": None,
        "source_pdf": {
            "filename": "UDCPR_Updated_30Jan2025.pdf",
            "page": 67,
            "text_snippet": "Front setback requirements..."
        },
        "created_at": datetime.now().isoformat()
    },
    {
        "rule_id": "udcpr_setback_front_002",
        "title": "Front Setback for Road Width 12-18m",
        "jurisdiction": "maharashtra_udcpr",
        "version": "udcpr_20250130",
        "clause_number": "4.2.2",
        "clause_text": "For roads with width between 12 and 18 meters, the minimum front setback shall be 4.5 meters.",
        "parsed": {
            "type": "rule",
            "rule_logic": {
                "conditions": [
                    {"field": "road_width_m", "op": ">=", "value": 12},
                    {"field": "road_width_m", "op": "<", "value": 18}
                ],
                "outputs": [
                    {"field": "front_setback", "value": 4.5, "units": "m"}
                ]
            }
        },
        "examples": [],
        "ambiguous": False,
        "ambiguity_reason": None,
        "source_pdf": {
            "filename": "UDCPR_Updated_30Jan2025.pdf",
            "page": 67,
            "text_snippet": "Front setback requirements..."
        },
        "created_at": datetime.now().isoformat()
    },
    {
        "rule_id": "udcpr_parking_residential_001",
        "title": "Parking Requirement for Residential Buildings",
        "jurisdiction": "maharashtra_udcpr",
        "version": "udcpr_20250130",
        "clause_number": "5.3.1",
        "clause_text": "Residential buildings shall provide 1 ECS (Equivalent Car Space) per 100 sqm of built-up area.",
        "parsed": {
            "type": "rule",
            "rule_logic": {
                "conditions": [
                    {"field": "use_type", "op": "==", "value": "Residential"}
                ],
                "outputs": [
                    {"field": "parking_ratio", "value": 0.01, "units": "ECS/sqm"}
                ],
                "notes": "1 ECS = 25 sqm parking area"
            }
        },
        "examples": [
            {
                "input": {"use_type": "Residential", "built_up_sqm": 1000},
                "expected_output": {"required_ecs": 10}
            }
        ],
        "ambiguous": False,
        "ambiguity_reason": None,
        "source_pdf": {
            "filename": "UDCPR_Updated_30Jan2025.pdf",
            "page": 89,
            "text_snippet": "Parking requirements..."
        },
        "created_at": datetime.now().isoformat()
    },
    {
        "rule_id": "udcpr_tod_bonus_001",
        "title": "TOD Zone FSI Bonus",
        "jurisdiction": "maharashtra_udcpr",
        "version": "udcpr_20250130",
        "clause_number": "6.1.5",
        "clause_text": "Projects within TOD (Transit Oriented Development) zones are eligible for an additional FSI bonus of 0.5.",
        "parsed": {
            "type": "rule",
            "rule_logic": {
                "conditions": [
                    {"field": "tod_zone", "op": "==", "value": True}
                ],
                "outputs": [
                    {"field": "fsi_bonus", "value": 0.5, "units": "ratio"}
                ]
            }
        },
        "examples": [],
        "ambiguous": False,
        "ambiguity_reason": None,
        "source_pdf": {
            "filename": "UDCPR_Updated_30Jan2025.pdf",
            "page": 112,
            "text_snippet": "TOD incentives..."
        },
        "created_at": datetime.now().isoformat()
    },
    {
        "rule_id": "mumbai_dcpr_height_001",
        "title": "Maximum Height for Road Width >= 18m",
        "jurisdiction": "mumbai_dcpr",
        "version": "dcpr_2034",
        "clause_number": "7.2.1",
        "clause_text": "For roads with width 18 meters or more, the maximum permissible height is 70 meters.",
        "parsed": {
            "type": "rule",
            "rule_logic": {
                "conditions": [
                    {"field": "road_width_m", "op": ">=", "value": 18}
                ],
                "outputs": [
                    {"field": "max_height", "value": 70.0, "units": "m"}
                ]
            }
        },
        "examples": [],
        "ambiguous": False,
        "ambiguity_reason": None,
        "source_pdf": {
            "filename": "MUMBAI_DCPR_2034.pdf",
            "page": 134,
            "text_snippet": "Height restrictions..."
        },
        "created_at": datetime.now().isoformat()
    },
    {
        "rule_id": "mumbai_dcpr_corner_plot_001",
        "title": "Corner Plot Setback Relaxation",
        "jurisdiction": "mumbai_dcpr",
        "version": "dcpr_2034",
        "clause_number": "4.5.3",
        "clause_text": "Corner plots are eligible for 25% relaxation in front setback requirements.",
        "parsed": {
            "type": "rule",
            "rule_logic": {
                "conditions": [
                    {"field": "corner_plot", "op": "==", "value": True}
                ],
                "outputs": [
                    {"field": "setback_relaxation", "value": 0.25, "units": "ratio"}
                ],
                "notes": "Apply 0.75 multiplier to standard front setback"
            }
        },
        "examples": [],
        "ambiguous": False,
        "ambiguity_reason": None,
        "source_pdf": {
            "filename": "MUMBAI_DCPR_2034.pdf",
            "page": 78,
            "text_snippet": "Corner plot provisions..."
        },
        "created_at": datetime.now().isoformat()
    },
    {
        "rule_id": "udcpr_ambiguous_001",
        "title": "Unclear Provision on Mixed Use FSI",
        "jurisdiction": "maharashtra_udcpr",
        "version": "udcpr_20250130",
        "clause_number": "3.4.7",
        "clause_text": "Mixed use developments may be granted additional FSI subject to approval.",
        "parsed": {
            "type": "note",
            "rule_logic": None
        },
        "examples": [],
        "ambiguous": True,
        "ambiguity_reason": "The clause does not specify the quantum of additional FSI or the approval criteria. Requires clarification from planning authority.",
        "source_pdf": {
            "filename": "UDCPR_Updated_30Jan2025.pdf",
            "page": 52,
            "text_snippet": "Mixed use provisions..."
        },
        "created_at": datetime.now().isoformat()
    },

    # Additional comprehensive rules
    {
        "rule_id": "udcpr_setback_side_001",
        "title": "Side Setback for Small Plots",
        "jurisdiction": "maharashtra_udcpr",
        "version": "udcpr_20250130",
        "clause_number": "4.2.2",
        "clause_text": "For plots up to 125 sqm, no side setback is required. For plots between 125-250 sqm, minimum 1m side setback is required.",
        "parsed": {
            "type": "rule",
            "rule_logic": {
                "conditions": [
                    {"field": "plot_area_sqm", "op": "<=", "value": 125}
                ],
                "outputs": [
                    {"field": "side_setback", "value": 0, "units": "m"}
                ]
            }
        },
        "examples": [],
        "ambiguous": False,
        "ambiguity_reason": None,
        "source_pdf": {
            "filename": "UDCPR_Updated_30Jan2025.pdf",
            "page": 68,
            "text_snippet": "Side setback requirements..."
        },
        "created_at": datetime.now().isoformat()
    },
    {
        "rule_id": "udcpr_height_low_road_001",
        "title": "Height Limit for Narrow Roads",
        "jurisdiction": "maharashtra_udcpr",
        "version": "udcpr_20250130",
        "clause_number": "7.2.2",
        "clause_text": "For roads less than 6 meters wide, maximum building height shall not exceed 10 meters.",
        "parsed": {
            "type": "rule",
            "rule_logic": {
                "conditions": [
                    {"field": "road_width_m", "op": "<", "value": 6}
                ],
                "outputs": [
                    {"field": "max_height", "value": 10.0, "units": "m"}
                ]
            }
        },
        "examples": [],
        "ambiguous": False,
        "ambiguity_reason": None,
        "source_pdf": {
            "filename": "UDCPR_Updated_30Jan2025.pdf",
            "page": 135,
            "text_snippet": "Height restrictions for narrow roads..."
        },
        "created_at": datetime.now().isoformat()
    },
    {
        "rule_id": "mumbai_dcpr_commercial_fsi_001",
        "title": "Commercial FSI in Mumbai",
        "jurisdiction": "mumbai_dcpr",
        "version": "dcpr_2034",
        "clause_number": "3.2.1",
        "clause_text": "Commercial developments in Mumbai shall have a base FSI of 2.0 in island city and 1.5 in suburbs.",
        "parsed": {
            "type": "rule",
            "rule_logic": {
                "conditions": [
                    {"field": "use_type", "op": "==", "value": "Commercial"},
                    {"field": "location", "op": "==", "value": "island_city"}
                ],
                "outputs": [
                    {"field": "base_fsi", "value": 2.0, "units": "ratio"}
                ]
            }
        },
        "examples": [],
        "ambiguous": False,
        "ambiguity_reason": None,
        "source_pdf": {
            "filename": "MUMBAI_DCPR_2034.pdf",
            "page": 45,
            "text_snippet": "Commercial FSI provisions..."
        },
        "created_at": datetime.now().isoformat()
    },
    {
        "rule_id": "udcpr_parking_commercial_001",
        "title": "Parking for Commercial Buildings",
        "jurisdiction": "maharashtra_udcpr",
        "version": "udcpr_20250130",
        "clause_number": "5.3.2",
        "clause_text": "Commercial buildings shall provide 1 ECS per 50 sqm of built-up area. For malls and shopping centers, 1 ECS per 30 sqm is required.",
        "parsed": {
            "type": "rule",
            "rule_logic": {
                "conditions": [
                    {"field": "use_type", "op": "==", "value": "Commercial"}
                ],
                "outputs": [
                    {"field": "parking_ratio", "value": 0.02, "units": "ECS/sqm"}
                ]
            }
        },
        "examples": [],
        "ambiguous": False,
        "ambiguity_reason": None,
        "source_pdf": {
            "filename": "UDCPR_Updated_30Jan2025.pdf",
            "page": 90,
            "text_snippet": "Commercial parking norms..."
        },
        "created_at": datetime.now().isoformat()
    },
    {
        "rule_id": "udcpr_open_space_001",
        "title": "Minimum Open Space Requirement",
        "jurisdiction": "maharashtra_udcpr",
        "version": "udcpr_20250130",
        "clause_number": "4.3.1",
        "clause_text": "All plots shall maintain minimum 20% open space. For plots above 4000 sqm, minimum 25% open space is required.",
        "parsed": {
            "type": "rule",
            "rule_logic": {
                "conditions": [
                    {"field": "plot_area_sqm", "op": "<=", "value": 4000}
                ],
                "outputs": [
                    {"field": "min_open_space_percent", "value": 20, "units": "percent"}
                ]
            }
        },
        "examples": [],
        "ambiguous": False,
        "ambiguity_reason": None,
        "source_pdf": {
            "filename": "UDCPR_Updated_30Jan2025.pdf",
            "page": 72,
            "text_snippet": "Open space requirements..."
        },
        "created_at": datetime.now().isoformat()
    },
    {
        "rule_id": "mumbai_dcpr_heritage_001",
        "title": "Heritage Building Restrictions",
        "jurisdiction": "mumbai_dcpr",
        "version": "dcpr_2034",
        "clause_number": "11.2.1",
        "clause_text": "Buildings within 300m of Grade I heritage structures shall not exceed height of heritage building or 15m, whichever is lower.",
        "parsed": {
            "type": "rule",
            "rule_logic": {
                "conditions": [
                    {"field": "heritage_proximity_m", "op": "<=", "value": 300}
                ],
                "outputs": [
                    {"field": "max_height", "value": 15.0, "units": "m"}
                ]
            }
        },
        "examples": [],
        "ambiguous": False,
        "ambiguity_reason": None,
        "source_pdf": {
            "filename": "MUMBAI_DCPR_2034.pdf",
            "page": 201,
            "text_snippet": "Heritage conservation provisions..."
        },
        "created_at": datetime.now().isoformat()
    },
    {
        "rule_id": "udcpr_fire_safety_001",
        "title": "Fire Safety Requirements for High-Rise",
        "jurisdiction": "maharashtra_udcpr",
        "version": "udcpr_20250130",
        "clause_number": "8.5.1",
        "clause_text": "Buildings above 15m height shall provide fire escape staircases, sprinkler systems, and fire NOC from fire department.",
        "parsed": {
            "type": "rule",
            "rule_logic": {
                "conditions": [
                    {"field": "height_m", "op": ">", "value": 15}
                ],
                "outputs": [
                    {"field": "fire_safety_required", "value": True, "units": "boolean"}
                ]
            }
        },
        "examples": [],
        "ambiguous": False,
        "ambiguity_reason": None,
        "source_pdf": {
            "filename": "UDCPR_Updated_30Jan2025.pdf",
            "page": 156,
            "text_snippet": "Fire safety provisions..."
        },
        "created_at": datetime.now().isoformat()
    },
    {
        "rule_id": "udcpr_accessibility_001",
        "title": "Accessibility Requirements",
        "jurisdiction": "maharashtra_udcpr",
        "version": "udcpr_20250130",
        "clause_number": "9.3.1",
        "clause_text": "All buildings shall provide ramps with maximum 1:12 slope, accessible toilets, and lifts for buildings above ground+3 floors.",
        "parsed": {
            "type": "rule",
            "rule_logic": {
                "conditions": [
                    {"field": "floors", "op": ">", "value": 4}
                ],
                "outputs": [
                    {"field": "lift_required", "value": True, "units": "boolean"}
                ]
            }
        },
        "examples": [],
        "ambiguous": False,
        "ambiguity_reason": None,
        "source_pdf": {
            "filename": "UDCPR_Updated_30Jan2025.pdf",
            "page": 178,
            "text_snippet": "Accessibility provisions..."
        },
        "created_at": datetime.now().isoformat()
    },
    {
        "rule_id": "mumbai_dcpr_coastal_001",
        "title": "Coastal Regulation Zone Restrictions",
        "jurisdiction": "mumbai_dcpr",
        "version": "dcpr_2034",
        "clause_number": "12.1.1",
        "clause_text": "No construction permitted within 500m of high tide line except for specific permitted activities. CRZ clearance mandatory.",
        "parsed": {
            "type": "rule",
            "rule_logic": {
                "conditions": [
                    {"field": "distance_from_coast_m", "op": "<=", "value": 500}
                ],
                "outputs": [
                    {"field": "construction_permitted", "value": False, "units": "boolean"}
                ]
            }
        },
        "examples": [],
        "ambiguous": False,
        "ambiguity_reason": None,
        "source_pdf": {
            "filename": "MUMBAI_DCPR_2034.pdf",
            "page": 223,
            "text_snippet": "CRZ regulations..."
        },
        "created_at": datetime.now().isoformat()
    },
    {
        "rule_id": "udcpr_rainwater_001",
        "title": "Rainwater Harvesting Requirement",
        "jurisdiction": "maharashtra_udcpr",
        "version": "udcpr_20250130",
        "clause_number": "10.4.1",
        "clause_text": "All plots above 300 sqm shall provide rainwater harvesting system with minimum storage capacity of 1 liter per sqm of plot area.",
        "parsed": {
            "type": "rule",
            "rule_logic": {
                "conditions": [
                    {"field": "plot_area_sqm", "op": ">", "value": 300}
                ],
                "outputs": [
                    {"field": "rainwater_harvesting_required", "value": True, "units": "boolean"}
                ]
            }
        },
        "examples": [],
        "ambiguous": False,
        "ambiguity_reason": None,
        "source_pdf": {
            "filename": "UDCPR_Updated_30Jan2025.pdf",
            "page": 189,
            "text_snippet": "Rainwater harvesting provisions..."
        },
        "created_at": datetime.now().isoformat()
    }
]

def generate_mock_candidates():
    """Generate mock candidate files."""
    print("UDCPR Master - Mock Ingestion (Enhanced)")
    print("="*60)
    
    # Create staging directory
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    
    # Split rules by jurisdiction
    udcpr_rules = [r for r in SAMPLE_RULES if r["jurisdiction"] == "maharashtra_udcpr"]
    mumbai_rules = [r for r in SAMPLE_RULES if r["jurisdiction"] == "mumbai_dcpr"]
    
    # Save UDCPR candidates
    timestamp = int(datetime.now().timestamp())
    udcpr_file = STAGING_DIR / f"UDCPR_candidates_{timestamp}.json"
    with open(udcpr_file, 'w', encoding='utf-8') as f:
        json.dump(udcpr_rules, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Created {udcpr_file.name}")
    print(f"  {len(udcpr_rules)} UDCPR rules")
    
    # Save Mumbai DCPR candidates
    mumbai_file = STAGING_DIR / f"MUMBAI_DCPR_candidates_{timestamp}.json"
    with open(mumbai_file, 'w', encoding='utf-8') as f:
        json.dump(mumbai_rules, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Created {mumbai_file.name}")
    print(f"  {len(mumbai_rules)} Mumbai DCPR rules")
    
    print("\n" + "="*60)
    print("✓ Mock ingestion complete!")
    print("="*60)
    print(f"\nTotal candidates: {len(SAMPLE_RULES)}")
    print(f"  - UDCPR: {len(udcpr_rules)}")
    print(f"  - Mumbai DCPR: {len(mumbai_rules)}")
    print(f"  - Ambiguous: {sum(1 for r in SAMPLE_RULES if r['ambiguous'])}")
    print("\nCategories covered:")
    print("  - FSI & Development Rights")
    print("  - Setbacks & Open Space")
    print("  - Parking Requirements")
    print("  - Height Restrictions")
    print("  - Fire Safety")
    print("  - Accessibility")
    print("  - Environmental (CRZ, Rainwater)")
    print("  - Heritage Conservation")
    print("\nNext step: Start admin UI to verify rules")
    print("  cd admin_ui && npm start")

if __name__ == "__main__":
    generate_mock_candidates()
