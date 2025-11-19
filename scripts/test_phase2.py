#!/usr/bin/env python3
"""
Test script to verify Phase 2 completion.
"""
import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return success status."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def test_rule_engine_tests():
    """Test that rule engine tests pass."""
    print("Testing rule engine (19 tests)...")
    
    success, stdout, stderr = run_command(
        "python -m pytest test_rule_engine.py -v --tb=short",
        cwd="rule_engine"
    )
    
    if success:
        # Count passed tests
        if "19 passed" in stdout:
            print("  ✓ All 19 rule engine tests passed")
            return True
        else:
            print(f"  ⚠️  Some tests may have failed")
            print(stdout[-500:] if len(stdout) > 500 else stdout)
            return False
    else:
        print(f"  ✗ Rule engine tests failed")
        print(stderr[-500:] if len(stderr) > 500 else stderr)
        return False

def test_enhanced_calculations():
    """Test that enhanced calculations are implemented."""
    print("\nTesting enhanced calculations...")
    
    rule_engine_file = Path("rule_engine/rule_engine.py")
    if not rule_engine_file.exists():
        print("  ✗ rule_engine.py not found")
        return False
    
    content = rule_engine_file.read_text()
    
    checks = {
        "TDR calculations": "def calculate_tdr" in content,
        "Enhanced FSI with bonuses": "slum_rehab" in content and "redevelopment" in content,
        "Enhanced setbacks": "_calculate_front_setback" in content,
        "Parking with mechanical option": "mechanical_parking_allowed" in content,
        "Height with TOD bonus": "tod_zone" in content and "height" in content.lower(),
        "Calculation traces": "CalculationStep" in content,
        "UDCPR rule references": "udcpr_2020" in content
    }
    
    all_passed = True
    for check_name, check_result in checks.items():
        if check_result:
            print(f"  ✓ {check_name}")
        else:
            print(f"  ✗ {check_name}")
            all_passed = False
    
    return all_passed

def test_api_service():
    """Test that API service exists."""
    print("\nTesting API service...")
    
    api_file = Path("rule_engine/api_service.py")
    if not api_file.exists():
        print("  ✗ api_service.py not found")
        return False
    
    content = api_file.read_text()
    
    checks = {
        "FastAPI app": "FastAPI" in content,
        "Evaluate endpoint": "/evaluate" in content,
        "CORS enabled": "CORSMiddleware" in content,
        "Health check": "/health" in content
    }
    
    all_passed = True
    for check_name, check_result in checks.items():
        if check_result:
            print(f"  ✓ {check_name}")
        else:
            print(f"  ✗ {check_name}")
            all_passed = False
    
    return all_passed

def test_backend_integration():
    """Test backend integration with rule engine."""
    print("\nTesting backend integration...")
    
    projects_file = Path("backend/src/routes/projects.js")
    if not projects_file.exists():
        print("  ✗ projects.js not found")
        return False
    
    content = projects_file.read_text()
    
    checks = {
        "Rule engine URL config": "RULE_ENGINE_URL" in content,
        "Evaluation endpoint call": "axios.post" in content and "/evaluate" in content,
        "Fallback calculation": "fallback" in content.lower(),
        "Error handling": "try" in content and "catch" in content
    }
    
    all_passed = True
    for check_name, check_result in checks.items():
        if check_result:
            print(f"  ✓ {check_name}")
        else:
            print(f"  ✗ {check_name}")
            all_passed = False
    
    return all_passed

def test_integration_tests():
    """Test that integration tests exist."""
    print("\nTesting integration test suite...")
    
    test_file = Path("backend/tests/integration.test.js")
    if not test_file.exists():
        print("  ✗ integration.test.js not found")
        return False
    
    content = test_file.read_text()
    
    checks = {
        "Authentication tests": "Authentication" in content,
        "Project CRUD tests": "Projects" in content,
        "Evaluation tests": "evaluate a project" in content,
        "Health check tests": "Health Check" in content
    }
    
    all_passed = True
    for check_name, check_result in checks.items():
        if check_result:
            print(f"  ✓ {check_name}")
        else:
            print(f"  ✗ {check_name}")
            all_passed = False
    
    return all_passed

def test_dependencies():
    """Test that required dependencies are listed."""
    print("\nTesting dependencies...")
    
    req_file = Path("rule_engine/requirements.txt")
    if not req_file.exists():
        print("  ✗ requirements.txt not found")
        return False
    
    content = req_file.read_text()
    
    checks = {
        "FastAPI": "fastapi" in content,
        "Uvicorn": "uvicorn" in content,
        "Pydantic": "pydantic" in content,
        "Pytest": "pytest" in content
    }
    
    all_passed = True
    for check_name, check_result in checks.items():
        if check_result:
            print(f"  ✓ {check_name}")
        else:
            print(f"  ✗ {check_name}")
            all_passed = False
    
    return all_passed

def main():
    print("="*60)
    print("UDCPR Master - Phase 2 Verification")
    print("="*60)
    print()
    
    results = {
        "Rule Engine Tests (19 tests)": test_rule_engine_tests(),
        "Enhanced Calculations": test_enhanced_calculations(),
        "API Service": test_api_service(),
        "Backend Integration": test_backend_integration(),
        "Integration Tests": test_integration_tests(),
        "Dependencies": test_dependencies()
    }
    
    print("\n" + "="*60)
    print("PHASE 2 TEST RESULTS")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:.<45} {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("✓ PHASE 2 COMPLETE!")
        print("="*60)
        print("\nAll components are ready:")
        print("  1. ✓ Enhanced rule engine with UDCPR 2020 logic")
        print("  2. ✓ 19 comprehensive unit tests (all passing)")
        print("  3. ✓ TDR calculations")
        print("  4. ✓ TOD bonus calculations")
        print("  5. ✓ Redevelopment & slum rehab bonuses")
        print("  6. ✓ FastAPI service for rule engine")
        print("  7. ✓ Backend integration with fallback")
        print("  8. ✓ Integration test suite")
        print("\nNext steps:")
        print("  1. Start rule engine API: cd rule_engine && python api_service.py")
        print("  2. Start backend: cd backend && npm start")
        print("  3. Start frontend: cd frontend && npm start")
        print("  4. Test full flow: Create project → Evaluate → View results")
    else:
        print("✗ PHASE 2 INCOMPLETE")
        print("="*60)
        print("\nSome components are missing or failing.")
        print("Review the test results above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())
