"""
Test Runner - Run all tests with coverage
"""
import pytest
import sys
from pathlib import Path

def run_all_tests():
    """Run all tests with coverage"""
    
    print("\n" + "="*80)
    print("UDCPR MASTER - TEST SUITE")
    print("="*80 + "\n")
    
    # Test arguments
    args = [
        "tests/",
        "-v",                          # Verbose
        "--cov=rule_engine",          # Coverage for rule engine
        "--cov=vision",               # Coverage for vision
        "--cov-report=html",          # HTML coverage report
        "--cov-report=term-missing",  # Terminal report with missing lines
        "--tb=short",                 # Short traceback format
        "-ra",                        # Show summary of all test outcomes
    ]
    
    # Run tests
    exit_code = pytest.main(args)
    
    print("\n" + "="*80)
    if exit_code == 0:
        print("✓ ALL TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
    print("="*80 + "\n")
    
    print("Coverage report generated: htmlcov/index.html\n")
    
    return exit_code

def run_unit_tests():
    """Run only unit tests"""
    print("\n" + "="*80)
    print("RUNNING UNIT TESTS")
    print("="*80 + "\n")
    
    args = [
        "tests/unit/",
        "-v",
        "--cov=rule_engine",
        "--cov-report=term-missing",
    ]
    
    return pytest.main(args)

def run_integration_tests():
    """Run only integration tests"""
    print("\n" + "="*80)
    print("RUNNING INTEGRATION TESTS")
    print("="*80 + "\n")
    
    args = [
        "tests/integration/",
        "-v",
        "--tb=short",
    ]
    
    return pytest.main(args)

def run_quick_tests():
    """Run quick smoke tests"""
    print("\n" + "="*80)
    print("RUNNING QUICK TESTS")
    print("="*80 + "\n")
    
    args = [
        "tests/unit/test_rule_engine.py::TestRuleEngine::test_engine_initialization",
        "tests/unit/test_rules_database.py::TestRulesDatabase::test_database_initialization",
        "-v",
    ]
    
    return pytest.main(args)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run UDCPR Master tests")
    parser.add_argument(
        "--mode",
        choices=["all", "unit", "integration", "quick"],
        default="all",
        help="Test mode to run"
    )
    
    args = parser.parse_args()
    
    if args.mode == "all":
        exit_code = run_all_tests()
    elif args.mode == "unit":
        exit_code = run_unit_tests()
    elif args.mode == "integration":
        exit_code = run_integration_tests()
    elif args.mode == "quick":
        exit_code = run_quick_tests()
    
    sys.exit(exit_code)
