import json
from pathlib import Path
from registration_stable import RegistrationSystem

# Load shared test data located one directory up
DATA_PATH = Path(__file__).parent.parent / 'test_data.json'
with DATA_PATH.open('r', encoding='utf-8') as f:
    ALL_CASES = json.load(f)

rs = RegistrationSystem()

def _run(case):
    result = rs.register(case['input'])
    return result

import pytest

@pytest.mark.parametrize('case', [c for c in ALL_CASES if c['expected_status'] == 'pass'])
def test_valid_cases(case):
    result = _run(case)
    assert result['ok'] is True, f"Should succeed: {case['input']['email']} => {result}"
    assert result['message'] == 'Registration successful'

@pytest.mark.parametrize('case', [c for c in ALL_CASES if c['expected_status'] == 'fail'])
def test_invalid_cases(case):
    result = _run(case)
    assert result['ok'] is False, f"Should fail: {case['input']['email']} incorrectly accepted"
    assert 'email' in case['input']

# Regression specific: emails previously valid should remain valid
@pytest.mark.parametrize('case', [c for c in ALL_CASES if c['regression']])
def test_regression_intact(case):
    result = _run(case)
    # For stable version regression-marked inputs are valid
    assert case['expected_status'] == 'pass'
    assert result['ok'] is True
