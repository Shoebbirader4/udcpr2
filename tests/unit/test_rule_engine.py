"""
Unit tests for rule engine
"""
import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from rule_engine.rule_engine_v2 import DatabaseDrivenRuleEngine, ProjectInput

class TestRuleEngine:
    """Test rule engine calculations"""
    
    def test_engine_initialization(self):
        """Test engine initializes correctly"""
        engine = DatabaseDrivenRuleEngine()
        assert engine is not None
        assert engine.db is not None
        assert len(engine.db.rules) > 0
    
    def test_fsi_calculation_commercial(self, rule_engine, sample_project_input):
        """Test FSI calculation for commercial project"""
        result = rule_engine.calculate_fsi(sample_project_input)
        
        assert 'base_fsi' in result
        assert 'permissible_fsi' in result
        assert 'proposed_fsi' in result
        assert result['base_fsi'] > 0
        assert result['permissible_fsi'] >= result['base_fsi']
        assert result['base_fsi_source'] in ['database_enhanced', 'fallback_default']
    
    def test_fsi_calculation_residential(self, rule_engine, sample_residential_project):
        """Test FSI calculation for residential project"""
        result = rule_engine.calculate_fsi(sample_residential_project)
        
        assert result['base_fsi'] > 0
        assert result['base_fsi'] <= 2.0  # Reasonable FSI range
        assert 'applied_rules' in result['base_fsi_rules']
    
    def test_parking_calculation(self, rule_engine, sample_project_input):
        """Test parking calculation"""
        result = rule_engine.calculate_parking(sample_project_input)
        
        assert 'required_ecs' in result
        assert 'norm' in result
        assert 'ratio' in result
        assert result['required_ecs'] > 0
        assert result['ratio'] > 0
    
    def test_setback_calculation(self, rule_engine, sample_project_input):
        """Test setback calculation"""
        result = rule_engine.calculate_setbacks(sample_project_input)
        
        assert 'front_m' in result
        assert 'side_m' in result
        assert 'rear_m' in result
        assert result['front_m'] >= 0
        assert result['side_m'] >= 0
        assert result['rear_m'] >= 0
    
    def test_height_calculation(self, rule_engine, sample_project_input):
        """Test height calculation"""
        result = rule_engine.calculate_height(sample_project_input)
        
        assert 'permissible_height_m' in result
        assert 'proposed_height_m' in result
        assert result['permissible_height_m'] > 0
        assert result['permissible_height_m'] >= result['proposed_height_m'] or \
               result['proposed_height_m'] <= result['permissible_height_m'] * 1.1  # Allow 10% tolerance
    
    def test_full_evaluation(self, rule_engine, sample_project_input):
        """Test complete project evaluation"""
        result = rule_engine.evaluate_project(sample_project_input)
        
        assert result is not None
        assert hasattr(result, 'fsi_result')
        assert hasattr(result, 'parking_result')
        assert hasattr(result, 'setback_result')
        assert hasattr(result, 'height_result')
        assert hasattr(result, 'compliant')
        assert hasattr(result, 'violations')
        assert hasattr(result, 'warnings')
    
    def test_fsi_bonuses(self, rule_engine):
        """Test FSI bonuses"""
        project = ProjectInput(
            jurisdiction="maharashtra_udcpr",
            zone="Residential",
            plot_area_sqm=1000,
            road_width_m=12,
            frontage_m=25,
            use_type="Residential",
            proposed_floors=4,
            proposed_height_m=12,
            proposed_built_up_sqm=1000,
            tod_zone=True,  # Enable TOD bonus
            green_building=True  # Enable green building bonus
        )
        
        result = rule_engine.calculate_fsi(project)
        
        assert result['bonus_fsi'] > 0
        assert len(result['bonus_details']) > 0
    
    def test_calculation_traces(self, rule_engine, sample_project_input):
        """Test calculation traces are generated"""
        result = rule_engine.evaluate_project(sample_project_input)
        
        assert len(result.calculation_traces) > 0
        
        # Check trace structure
        trace = result.calculation_traces[0]
        assert hasattr(trace, 'step_id')
        assert hasattr(trace, 'description')
        assert hasattr(trace, 'rule_ids')
        assert hasattr(trace, 'result')

class TestProjectInput:
    """Test project input validation"""
    
    def test_valid_project_input(self):
        """Test valid project input"""
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
        
        assert project.jurisdiction == "maharashtra_udcpr"
        assert project.plot_area_sqm == 2000
        assert project.use_type == "Commercial"
    
    def test_project_input_defaults(self):
        """Test project input default values"""
        project = ProjectInput(
            jurisdiction="maharashtra_udcpr",
            zone="Residential",
            plot_area_sqm=1000,
            road_width_m=12,
            frontage_m=25,
            use_type="Residential",
            proposed_floors=4,
            proposed_height_m=12,
            proposed_built_up_sqm=1000
        )
        
        assert project.tod_zone == False
        assert project.redevelopment == False
        assert project.slum_rehab == False
        assert project.corner_plot == False

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=rule_engine", "--cov-report=html"])
