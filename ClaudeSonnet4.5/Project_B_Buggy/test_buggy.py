"""
Test Suite for Buggy Registration System (Post-Regression)
These tests will reveal the regression bug in email validation
"""

import json
import sys
import time
from registration_buggy import RegistrationSystem

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
        self.regressions_detected = 0
    
    def run_tests(self, test_data_path='../test_data.json'):
        """Run all test cases from JSON file"""
        try:
            with open(test_data_path, 'r') as f:
                test_cases = json.load(f)
        except FileNotFoundError:
            print(f"Test data file not found: {test_data_path}")
            return
        
        system = RegistrationSystem()
        
        print("=" * 60)
        print("BUGGY VERSION - TEST EXECUTION")
        print("=" * 60)
        
        for idx, test in enumerate(test_cases, 1):
            test_name = test.get('test_name', f'Test {idx}')
            email = test['input']['email']
            password = test['input']['password']
            expected_success = test['expected']['success']
            expected_msg_contains = test['expected'].get('message_contains', '')
            is_regression_check = test.get('regression_check', False)
            
            print(f"\n[Test {idx}] {test_name}")
            print(f"  Input: email='{email}', password='{password}'")
            if is_regression_check:
                print(f"  [!] REGRESSION CHECK TEST")
            
            start_time = time.time()
            result = system.register_user(email, password)
            elapsed = time.time() - start_time
            
            print(f"  Result: {result}")
            print(f"  Expected Success: {expected_success}")
            print(f"  Actual Success: {result['success']}")
            
            # Check if result matches expectation
            success_match = result['success'] == expected_success
            message_match = True
            if expected_msg_contains:
                message_match = expected_msg_contains.lower() in result['message'].lower()
            
            passed = success_match and message_match
            
            # Detect regression
            if is_regression_check and not passed:
                self.regressions_detected += 1
                print(f"  [!] REGRESSION DETECTED: Test behavior changed from stable version!")
            
            if passed:
                self.passed += 1
                status = "PASS"
            else:
                self.failed += 1
                status = "FAIL"
            
            print(f"  Status: {status}")
            print(f"  Execution Time: {elapsed*1000:.2f}ms")
            
            self.results.append({
                'test_name': test_name,
                'email': email,
                'passed': passed,
                'expected_success': expected_success,
                'actual_success': result['success'],
                'message': result['message'],
                'execution_time_ms': elapsed * 1000,
                'regression_detected': is_regression_check and not passed
            })
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY - BUGGY VERSION")
        print("=" * 60)
        print(f"Total Tests: {self.passed + self.failed}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Success Rate: {self.passed / (self.passed + self.failed) * 100:.1f}%")
        print(f"Regressions Detected: {self.regressions_detected}")
        print("=" * 60)
        
        if self.regressions_detected > 0:
            print(f"\n[!] WARNING: {self.regressions_detected} regression(s) detected!")
            print("Email validation is not working as expected.")
        
        return self.results

if __name__ == "__main__":
    runner = TestRunner()
    results = runner.run_tests()
    
    # Exit with appropriate code
    sys.exit(0 if runner.failed == 0 else 1)
