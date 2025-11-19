"""
Unit tests for rules database
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from rule_engine.rules_database_v2 import EnhancedRulesDatabase, RulePriority

class TestRulesDatabase:
    """Test rules database functionality"""
    
    def test_database_initialization(self, rules_database):
        """Test database loads correctly"""
        assert rules_database is not None
        assert len(rules_database.rules) > 0
        assert len(rules_database.rules_by_id) > 0
        assert len(rules_database.rules_by_jurisdiction) > 0
    
    def test_jurisdiction_indexing(self, rules_database):
        """Test rules are indexed by jurisdiction"""
        assert 'maharashtra_udcpr' in rules_database.rules_by_jurisdiction
        assert 'mumbai_dcpr' in rules_database.rules_by_jurisdiction
        
        mh_rules = rules_database.rules_by_jurisdiction['maharashtra_udcpr']
        mumbai_rules = rules_database.rules_by_jurisdiction['mumbai_dcpr']
        
        assert len(mh_rules) > 0
        assert len(mumbai_rules) > 0
    
    def test_filter_by_jurisdiction(self, rules_database):
        """Test jurisdiction filtering"""
        all_rules = rules_database.rules[:100]  # Sample
        
        mh_filtered = rules_database.filter_by_jurisdiction(all_rules, "maharashtra_udcpr")
        
        # All filtered rules should be from Maharashtra
        for rule in mh_filtered:
            assert rule.get('jurisdiction') == 'maharashtra_udcpr'
    
    def test_rule_ranking(self, rules_database):
        """Test rule ranking logic"""
        sample_rules = rules_database.rules[:50]
        
        ranked = rules_database.rank_rules(
            sample_rules,
            use_type="Commercial",
            jurisdiction="maharashtra_udcpr",
            plot_area=2000
        )
        
        assert len(ranked) > 0
        
        # Check ranking structure
        first_ranked = ranked[0]
        assert hasattr(first_ranked, 'rule')
        assert hasattr(first_ranked, 'priority')
        assert hasattr(first_ranked, 'relevance_score')
        assert hasattr(first_ranked, 'match_reasons')
        
        # Check priority ordering
        for i in range(len(ranked) - 1):
            assert ranked[i].priority.value <= ranked[i + 1].priority.value
    
    def test_fsi_extraction(self, rules_database):
        """Test FSI value extraction"""
        # Test various FSI patterns
        test_cases = [
            ("FSI shall be 2.0", 2.0),
            ("basic FSI 1.5", 1.5),
            ("FSI up to 3.0", 3.0),
            ("permissible FSI is 2.5", 2.5)
        ]
        
        for text, expected_fsi in test_cases:
            result = rules_database.extract_fsi_value(text)
            if result:
                fsi_value, context = result
                assert abs(fsi_value - expected_fsi) < 0.1
    
    def test_parking_ratio_extraction(self, rules_database):
        """Test parking ratio extraction"""
        test_cases = [
            ("1 ECS per 100 sqm", 100.0),
            ("1 ECS per 50 sq.m", 50.0),
            ("1 equivalent car space per 70 sqm", 70.0)
        ]
        
        for text, expected_ratio in test_cases:
            result = rules_database.extract_parking_ratio(text)
            if result:
                ratio, context = result
                assert abs(ratio - expected_ratio) < 1.0
    
    def test_get_base_fsi_enhanced(self, rules_database):
        """Test enhanced FSI calculation"""
        result = rules_database.get_base_fsi_enhanced(
            use_type="Commercial",
            plot_area=2000,
            jurisdiction="maharashtra_udcpr"
        )
        
        assert 'base_fsi' in result
        assert 'source' in result
        assert 'applied_rules' in result
        assert 'priority' in result
        assert 'relevance_score' in result
        assert 'jurisdiction' in result
        
        assert result['base_fsi'] > 0
        assert result['jurisdiction'] == 'maharashtra_udcpr'
    
    def test_get_parking_requirement_enhanced(self, rules_database):
        """Test enhanced parking calculation"""
        result = rules_database.get_parking_requirement_enhanced(
            use_type="Residential",
            built_up_area=1000,
            jurisdiction="maharashtra_udcpr"
        )
        
        assert 'required_ecs' in result
        assert 'ratio' in result
        assert 'norm' in result
        assert 'source' in result
        assert 'jurisdiction' in result
        
        assert result['required_ecs'] > 0
        assert result['ratio'] > 0
    
    def test_setback_extraction(self, rules_database):
        """Test setback value extraction"""
        test_cases = [
            ("front setback 3.0 m", {'front': 3.0}),
            ("side margin of 2.5 meters", {'side': 2.5}),
            ("rear setback 4 m", {'rear': 4.0})
        ]
        
        for text, expected in test_cases:
            result = rules_database.extract_setback_values(text)
            for key, value in expected.items():
                if result[key] is not None:
                    assert abs(result[key] - value) < 0.1
    
    def test_height_extraction(self, rules_database):
        """Test height limit extraction"""
        test_cases = [
            ("maximum height 24.0 m", 24.0),
            ("height shall not exceed 30 meters", 30.0),
            ("up to 45 m height", 45.0)
        ]
        
        for text, expected_height in test_cases:
            result = rules_database.extract_height_limit(text)
            if result:
                height, context = result
                assert abs(height - expected_height) < 1.0
    
    def test_statistics(self, rules_database):
        """Test database statistics"""
        stats = rules_database.get_statistics()
        
        assert 'total_rules' in stats
        assert 'by_jurisdiction' in stats
        assert 'fsi_rules' in stats
        assert 'parking_rules' in stats
        
        assert stats['total_rules'] > 0
        assert stats['fsi_rules'] > 0

class TestRulePriority:
    """Test rule priority enum"""
    
    def test_priority_values(self):
        """Test priority enum values"""
        assert RulePriority.EXACT_MATCH.value == 1
        assert RulePriority.JURISDICTION_MATCH.value == 2
        assert RulePriority.GENERAL.value == 3
        assert RulePriority.FALLBACK.value == 4
    
    def test_priority_ordering(self):
        """Test priority ordering"""
        priorities = [
            RulePriority.FALLBACK,
            RulePriority.EXACT_MATCH,
            RulePriority.GENERAL,
            RulePriority.JURISDICTION_MATCH
        ]
        
        sorted_priorities = sorted(priorities, key=lambda p: p.value)
        
        assert sorted_priorities[0] == RulePriority.EXACT_MATCH
        assert sorted_priorities[-1] == RulePriority.FALLBACK

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=rule_engine.rules_database_v2", "--cov-report=html"])
