"""
Unit tests for rule engine.
"""
import pytest
from rule_engine import RuleEngine, ProjectInput

def test_fsi_calculation_residential():
    """Test FSI calculation for residential project."""
    project = ProjectInput(
        jurisdiction="maharashtra_udcpr",
        zone="Residential",
        plot_area_sqm=500,
        road_width_m=12,
        corner_plot=False,
        frontage_m=20,
        use_type="Residential",
        proposed_floors=4,
        proposed_height_m=12,
        proposed_built_up_sqm=500
    )
    
    engine = RuleEngine(rules_db={})
    result = engine.evaluate_project(project)
    
    assert result.fsi_result["base_fsi"] == 1.0
    assert result.fsi_result["proposed_fsi"] == 1.0
    assert result.compliant == True

def test_fsi_violation():
    """Test FSI violation detection."""
    project = ProjectInput(
        jurisdiction="maharashtra_udcpr",
        zone="Residential",
        plot_area_sqm=500,
        road_width_m=12,
        corner_plot=False,
        frontage_m=20,
        use_type="Residential",
        proposed_floors=6,
        proposed_height_m=18,
        proposed_built_up_sqm=800  # Exceeds FSI 1.0
    )
    
    engine = RuleEngine(rules_db={})
    result = engine.evaluate_project(project)
    
    assert result.compliant == False
    assert len(result.violations) > 0
    assert "FSI exceeds" in result.violations[0]

def test_tod_bonus():
    """Test TOD zone FSI bonus."""
    project = ProjectInput(
        jurisdiction="maharashtra_udcpr",
        zone="Residential",
        plot_area_sqm=500,
        road_width_m=12,
        corner_plot=False,
        frontage_m=20,
        use_type="Residential",
        proposed_floors=5,
        proposed_height_m=15,
        proposed_built_up_sqm=750,
        tod_zone=True
    )
    
    engine = RuleEngine(rules_db={})
    result = engine.evaluate_project(project)
    
    assert result.fsi_result["bonus_fsi"] == 0.5
    assert result.fsi_result["permissible_fsi"] == 1.5
    assert result.compliant == True

def test_setback_calculation():
    """Test setback calculations."""
    project = ProjectInput(
        jurisdiction="maharashtra_udcpr",
        zone="Residential",
        plot_area_sqm=500,
        road_width_m=18,
        corner_plot=False,
        frontage_m=20,
        use_type="Residential",
        proposed_floors=4,
        proposed_height_m=12,
        proposed_built_up_sqm=500
    )
    
    engine = RuleEngine(rules_db={})
    result = engine.evaluate_project(project)
    
    assert result.setback_result["front_m"] == 6.0
    # Side setback for 500 sqm plot with 12m height includes height adjustment
    assert result.setback_result["side_m"] > 1.5

def test_corner_plot_setback_relaxation():
    """Test corner plot setback relaxation."""
    project = ProjectInput(
        jurisdiction="maharashtra_udcpr",
        zone="Residential",
        plot_area_sqm=500,
        road_width_m=18,
        corner_plot=True,
        frontage_m=20,
        use_type="Residential",
        proposed_floors=4,
        proposed_height_m=12,
        proposed_built_up_sqm=500
    )
    
    engine = RuleEngine(rules_db={})
    result = engine.evaluate_project(project)
    
    assert result.setback_result["front_m"] == 4.5  # 6.0 * 0.75

def test_parking_calculation():
    """Test parking requirement calculation."""
    project = ProjectInput(
        jurisdiction="maharashtra_udcpr",
        zone="Commercial",
        plot_area_sqm=1000,
        road_width_m=18,
        corner_plot=False,
        frontage_m=30,
        use_type="Commercial",
        proposed_floors=5,
        proposed_height_m=20,
        proposed_built_up_sqm=2000
    )
    
    engine = RuleEngine(rules_db={})
    result = engine.evaluate_project(project)
    
    # Commercial: 1 ECS per 50 sqm
    assert result.parking_result["required_ecs"] == 40

def test_calculation_traces():
    """Test that calculation traces are generated."""
    project = ProjectInput(
        jurisdiction="maharashtra_udcpr",
        zone="Residential",
        plot_area_sqm=500,
        road_width_m=12,
        corner_plot=False,
        frontage_m=20,
        use_type="Residential",
        proposed_floors=4,
        proposed_height_m=12,
        proposed_built_up_sqm=500
    )
    
    engine = RuleEngine(rules_db={})
    result = engine.evaluate_project(project)
    
    assert len(result.calculation_traces) > 0
    assert all(trace.rule_ids for trace in result.calculation_traces)
    assert all(trace.step_id for trace in result.calculation_traces)


# Phase 2 Tests - Enhanced Rule Engine

def test_fsi_with_multiple_bonuses():
    """Test FSI calculation with TOD and redevelopment bonuses."""
    project = ProjectInput(
        jurisdiction="maharashtra_udcpr",
        zone="Residential",
        plot_area_sqm=1000,
        road_width_m=18,
        corner_plot=False,
        frontage_m=25,
        use_type="Residential",
        proposed_floors=8,
        proposed_height_m=24,
        proposed_built_up_sqm=1800,
        tod_zone=True,
        redevelopment=True
    )
    
    engine = RuleEngine(rules_db={})
    result = engine.evaluate_project(project)
    
    # Base FSI 1.0 + TOD 0.5 + Redevelopment 0.3 = 1.8
    assert result.fsi_result["base_fsi"] == 1.0
    assert result.fsi_result["bonus_fsi"] == 0.8
    assert result.fsi_result["permissible_fsi"] == 1.8
    assert result.compliant == True

def test_slum_rehabilitation_bonus():
    """Test slum rehabilitation FSI bonus."""
    project = ProjectInput(
        jurisdiction="maharashtra_udcpr",
        zone="Residential",
        plot_area_sqm=2000,
        road_width_m=12,
        corner_plot=False,
        frontage_m=40,
        use_type="Residential",
        proposed_floors=10,
        proposed_height_m=30,
        proposed_built_up_sqm=4000,
        slum_rehab=True
    )
    
    engine = RuleEngine(rules_db={})
    result = engine.evaluate_project(project)
    
    # Base FSI 1.0 + Slum Rehab 1.0 = 2.0
    assert result.fsi_result["bonus_fsi"] == 1.0
    assert result.fsi_result["permissible_fsi"] == 2.0
    assert result.compliant == True

def test_premium_fsi_availability():
    """Test premium FSI calculation."""
    project = ProjectInput(
        jurisdiction="maharashtra_udcpr",
        zone="Commercial",
        plot_area_sqm=1000,
        road_width_m=18,
        corner_plot=False,
        frontage_m=25,
        use_type="Commercial",
        proposed_floors=6,
        proposed_height_m=20,
        proposed_built_up_sqm=1500
    )
    
    engine = RuleEngine(rules_db={})
    result = engine.evaluate_project(project)
    
    # Commercial base FSI is 1.5, premium FSI is 20% = 0.3
    assert result.fsi_result["base_fsi"] == 1.5
    assert abs(result.fsi_result["premium_fsi_available"] - 0.3) < 0.01

def test_enhanced_setback_calculations():
    """Test enhanced setback calculations with height consideration."""
    project = ProjectInput(
        jurisdiction="maharashtra_udcpr",
        zone="Residential",
        plot_area_sqm=600,
        road_width_m=30,
        corner_plot=False,
        frontage_m=20,
        use_type="Residential",
        proposed_floors=10,
        proposed_height_m=30,
        proposed_built_up_sqm=600
    )
    
    engine = RuleEngine(rules_db={})
    result = engine.evaluate_project(project)
    
    # Front setback for 30m road should be 9m
    assert result.setback_result["front_m"] == 9.0
    # Side setback should increase with height
    assert result.setback_result["side_m"] > 1.5

def test_corner_plot_setback_relaxation_enhanced():
    """Test corner plot setback relaxation."""
    project = ProjectInput(
        jurisdiction="maharashtra_udcpr",
        zone="Residential",
        plot_area_sqm=500,
        road_width_m=18,
        corner_plot=True,
        frontage_m=20,
        use_type="Residential",
        proposed_floors=5,
        proposed_height_m=15,
        proposed_built_up_sqm=500
    )
    
    engine = RuleEngine(rules_db={})
    result = engine.evaluate_project(project)
    
    # Front setback for 18m road is 6m, with corner plot relaxation: 6 * 0.75 = 4.5m
    assert result.setback_result["front_m"] == 4.5

def test_parking_with_mechanical_option():
    """Test parking calculation with mechanical parking option."""
    project = ProjectInput(
        jurisdiction="maharashtra_udcpr",
        zone="Commercial",
        plot_area_sqm=1000,
        road_width_m=18,
        corner_plot=False,
        frontage_m=25,
        use_type="Commercial",
        proposed_floors=8,
        proposed_height_m=28,
        proposed_built_up_sqm=3000
    )
    
    engine = RuleEngine(rules_db={})
    result = engine.evaluate_project(project)
    
    # Commercial: 1 ECS per 50 sqm = 60 ECS
    assert result.parking_result["required_ecs"] == 60
    # Should allow mechanical parking for > 20 ECS
    assert result.parking_result["mechanical_parking_allowed"] == True

def test_height_with_tod_bonus():
    """Test height calculation with TOD bonus."""
    project = ProjectInput(
        jurisdiction="maharashtra_udcpr",
        zone="Residential",
        plot_area_sqm=1000,
        road_width_m=18,
        corner_plot=False,
        frontage_m=25,
        use_type="Residential",
        proposed_floors=25,
        proposed_height_m=75,
        proposed_built_up_sqm=1500,
        tod_zone=True
    )
    
    engine = RuleEngine(rules_db={})
    result = engine.evaluate_project(project)
    
    # Base height for 18m road is 70m, with TOD bonus: 70 * 1.5 = 105m
    assert result.height_result["permissible_height_m"] == 105.0
    assert result.compliant == True

def test_floor_height_violation():
    """Test floor height adequacy check."""
    project = ProjectInput(
        jurisdiction="maharashtra_udcpr",
        zone="Commercial",
        plot_area_sqm=500,
        road_width_m=12,
        corner_plot=False,
        frontage_m=20,
        use_type="Commercial",
        proposed_floors=10,
        proposed_height_m=25,  # Only 2.5m per floor - inadequate
        proposed_built_up_sqm=750
    )
    
    engine = RuleEngine(rules_db={})
    result = engine.evaluate_project(project)
    
    # Commercial requires min 3.0m floor height
    assert result.height_result["floor_height_adequate"] == False
    assert result.compliant == False
    assert any("Floor height inadequate" in v for v in result.violations)

def test_tdr_calculation():
    """Test TDR calculation and eligibility."""
    project = ProjectInput(
        jurisdiction="maharashtra_udcpr",
        zone="Residential",
        plot_area_sqm=1500,  # Large enough for TDR
        road_width_m=18,
        corner_plot=False,
        frontage_m=30,
        use_type="Residential",
        proposed_floors=8,
        proposed_height_m=24,
        proposed_built_up_sqm=1800,  # Exceeds base FSI
        tod_zone=False,
        redevelopment=False
    )
    
    engine = RuleEngine(rules_db={})
    result = engine.evaluate_project(project)
    
    # Should be able to receive TDR (plot > 1000 sqm)
    assert result.tdr_result["can_receive_tdr"] == True
    # Max TDR loadable is 20% of base FSI
    assert result.tdr_result["max_tdr_loadable_fsi"] == 0.2

def test_open_space_compliance():
    """Test open space requirement compliance."""
    project = ProjectInput(
        jurisdiction="maharashtra_udcpr",
        zone="Residential",
        plot_area_sqm=500,
        road_width_m=12,
        corner_plot=False,
        frontage_m=20,
        use_type="Residential",
        proposed_floors=4,
        proposed_height_m=12,
        proposed_built_up_sqm=500
    )
    
    engine = RuleEngine(rules_db={})
    result = engine.evaluate_project(project)
    
    # Should have open space percentage calculated
    assert "open_space_percent" in result.setback_result
    assert result.setback_result["min_open_space_required_percent"] == 20.0

def test_comprehensive_compliance_check():
    """Test comprehensive compliance with multiple violations."""
    project = ProjectInput(
        jurisdiction="maharashtra_udcpr",
        zone="Residential",
        plot_area_sqm=300,
        road_width_m=9,
        corner_plot=False,
        frontage_m=15,
        use_type="Residential",
        proposed_floors=10,
        proposed_height_m=30,  # Exceeds limit
        proposed_built_up_sqm=600  # Exceeds FSI
    )
    
    engine = RuleEngine(rules_db={})
    result = engine.evaluate_project(project)
    
    # Should have multiple violations
    assert result.compliant == False
    assert len(result.violations) >= 2
    # Should have FSI and height violations
    assert any("FSI exceeds" in v for v in result.violations)
    assert any("Height exceeds" in v for v in result.violations)

def test_calculation_traces_completeness():
    """Test that all calculations generate proper traces."""
    project = ProjectInput(
        jurisdiction="maharashtra_udcpr",
        zone="Residential",
        plot_area_sqm=500,
        road_width_m=12,
        corner_plot=False,
        frontage_m=20,
        use_type="Residential",
        proposed_floors=4,
        proposed_height_m=12,
        proposed_built_up_sqm=500
    )
    
    engine = RuleEngine(rules_db={})
    result = engine.evaluate_project(project)
    
    # Should have traces from all modules
    trace_ids = [t.step_id for t in result.calculation_traces]
    assert "fsi_base" in trace_ids
    assert "setback_front" in trace_ids
    assert "parking_calc" in trace_ids
    assert "height_calc" in trace_ids
    assert "tdr_analysis" in trace_ids
    
    # All traces should have rule_ids
    assert all(len(t.rule_ids) > 0 for t in result.calculation_traces)
