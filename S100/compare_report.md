# Regression Comparison Report

## Test Outcome Summary

| Metric | Project A (Stable) | Project B (Buggy) |
| --- | --- | --- |
| Tests Passed | 7 | 2 |
| Tests Failed | 0 | n/a |
| Runtime (s) | 0.5545 | 0.6544 |

## Observations
- ✅ Stable implementation enforces strict email validation and all tests succeed.
- ⚠️ Buggy implementation relaxes validation, allowing malformed emails and causing targeted tests to fail.
- 🔍 The discrepancy is isolated to email format handling; other validations (duplicates, password policy) still behave correctly.

## Log Excerpts

**Stable log:**

```
.......                                                                  [100%]
7 passed in 0.05s
```

**Buggy log:**

```
..F
================================== FAILURES ===================================
__________________ test_detect_invalid_email_missing_domain ___________________

system = <registration_buggy.UserRegistrationSystem object at 0x000001FD7EB2F9D0>

    def test_detect_invalid_email_missing_domain(system):
>       with pytest.raises(RegistrationError, match="Invalid email"):
E       Failed: DID NOT RAISE <class 'registration_buggy.RegistrationError'>

test_buggy.py:41: Failed
=========================== short test summary info ===========================
FAILED test_buggy.py::test_detect_invalid_email_missing_domain - Failed: DID ...
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
1 failed, 2 passed in 0.10s
```
