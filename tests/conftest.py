"""
Pytest configuration and fixtures
"""
import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture
def sample_project_input():
    """Sample project input for testing"""
    from rule_engine.rule_engine_v2 import ProjectInput
    
    return ProjectInput(
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

@pytest.fixture
def sample_residential_project():
    """Sample residential project"""
    from rule_engine.rule_engine_v2 import ProjectInput
    
    return ProjectInput(
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

@pytest.fixture
def rules_database():
    """Get rules database instance"""
    from rule_engine.rules_database_v2 import get_enhanced_rules_database
    return get_enhanced_rules_database()

@pytest.fixture
def rule_engine():
    """Get rule engine instance"""
    from rule_engine.rule_engine_v2 import DatabaseDrivenRuleEngine
    return DatabaseDrivenRuleEngine()
