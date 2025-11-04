# User Registration System - Regression Testing Suite

## Overview
This project evaluates AI model capabilities in detecting, reproducing, and diagnosing **regression bugs** in a user registration system. It contains two complete implementations demonstrating a real-world regression scenario where email validation logic was broken during a feature update.

## Regression Bug Description

### The Scenario
During an integration of third-party OAuth login functionality, a developer accidentally simplified the email validation logic. What was meant to be a temporary change during testing was committed to production, introducing a critical regression bug.

### What Changed
- **Stable Version (Project A)**: Uses proper regex-based email validation with comprehensive checks
- **Buggy Version (Project B)**: Email validation simplified to only check for presence of '@' symbol

### Impact
The buggy version accepts invalid emails such as:
- `user@@invalid.com` (double @ symbol)
- `test@.com` (missing domain name)  
- `@example.com` (missing local part)
- `user@domain` (missing TLD)

## Project Structure

```
chatWorkspace/
├── Project_A_Stable/          # Pre-regression stable implementation
│   ├── registration_stable.py  # Correct implementation
│   ├── test_original.py        # Test suite
│   ├── requirements_original.txt
│   ├── setup_original.sh
│   ├── run_original.sh
│   ├── log_original.txt        # Generated during test run
│   └── time_original.txt       # Generated during test run
│
├── Project_B_Buggy/           # Post-regression buggy implementation
│   ├── registration_buggy.py   # Implementation with regression bug
│   ├── test_buggy.py           # Test suite (detects regressions)
│   ├── requirements_buggy.txt
│   ├── setup_buggy.sh
│   ├── run_buggy.sh
│   ├── log_buggy.txt          # Generated during test run
│   └── time_buggy.txt         # Generated during test run
│
├── test_data.json             # Shared test cases (10 scenarios)
├── run_all.sh / run_all.ps1   # Master execution scripts
├── compare_report.md          # Generated comparison report
└── README.md                  # This file
```

## Quick Start

### Prerequisites
- Python 3.7 or higher
- No external dependencies required (uses standard library only)

### Option 1: Run Both Projects (Recommended)

**On Linux/Mac:**
```bash
chmod +x run_all.sh
./run_all.sh
```

**On Windows (PowerShell):**
```powershell
.\run_all.ps1
```

This will:
1. Execute Project A (stable version)
2. Execute Project B (buggy version)
3. Generate a comparison report
4. Display summary of results

### Option 2: Run Projects Individually

**Project A - Stable Version:**
```bash
cd Project_A_Stable
chmod +x run_original.sh
./run_original.sh
```

**Project B - Buggy Version:**
```bash
cd Project_B_Buggy
chmod +x run_buggy.sh
./run_buggy.sh
```

**Windows (PowerShell):**
```powershell
# Project A
cd Project_A_Stable
python test_original.py | Tee-Object -FilePath log_original.txt

# Project B
cd Project_B_Buggy
python test_buggy.py | Tee-Object -FilePath log_buggy.txt
```

## Test Cases

The `test_data.json` file contains 10 comprehensive test cases covering:

1. **Normal Cases**: Valid email and password combinations
2. **Invalid Email Formats**: Double @, missing domain, no TLD, etc.
3. **Password Validation**: Weak passwords, length boundaries
4. **Edge Cases**: Complex emails, boundary conditions
5. **Regression Checks**: Cases that expose the bug in Project B

### Key Regression Test Cases
- Test 2: `user@@invalid.com` - Should fail but passes in buggy version
- Test 3: `test@.com` - Should fail but passes in buggy version  
- Test 4: `user@domain` - Should fail but passes in buggy version
- Test 5: `@example.com` - Should fail but passes in buggy version

## Expected Results

### Project A (Stable) - Expected Output
- **Pass Rate**: 100% (10/10 tests pass)
- All invalid emails properly rejected
- All valid emails accepted with correct password
- No regressions detected

### Project B (Buggy) - Expected Output
- **Pass Rate**: ~60% (6/10 tests pass, 4 fail)
- **Regressions Detected**: 4 tests
- Invalid emails with '@' incorrectly accepted
- Password validation still works correctly
- Clear indication of email validation failure

## Evaluation Criteria

This project enables evaluation of AI models on:

1. **Correctness**: Both implementations run without errors
2. **Regression Detection**: Buggy version clearly shows failures
3. **Test Coverage**: Comprehensive edge cases and invalid inputs
4. **Reproducibility**: Fully automated setup and execution
5. **Comparison**: Clear differences between stable and buggy versions
6. **Documentation**: Complete explanation of bug and impact

## Limitations

- **In-Memory Database**: User data not persisted (suitable for testing)
- **Simplified Security**: Passwords stored in plain text (demonstration only)
- **No Network Operations**: All validation is local
- **Single Regression Type**: Focuses on email validation bug

## Files Generated During Execution

- `log_original.txt`: Full test output from stable version
- `log_buggy.txt`: Full test output from buggy version
- `time_original.txt`: Execution timestamp for Project A
- `time_buggy.txt`: Execution timestamp for Project B  
- `compare_report.md`: Side-by-side comparison of both versions

## Understanding the Bug

The regression was introduced in `registration_buggy.py` at the `validate_email()` method:

**Before (Stable):**
```python
if not self.email_pattern.match(email):
    return False, "Invalid email format"
```

**After (Buggy):**
```python
if '@' in email:
    return True, "Email is valid"  # BUG: Too permissive
```

This change was meant to be temporary during OAuth integration testing but was accidentally committed, breaking the email validation entirely.

## Verification

To verify the regression is properly detected:

1. Run both projects
2. Check `log_buggy.txt` for "REGRESSION DETECTED" messages
3. Compare pass rates between projects
4. Review `compare_report.md` for detailed analysis

## Support

This is a self-contained demonstration project. All code and tests are included. No external services or API keys required.

---

**Project Type**: Regression Testing / Bug Detection  
**Focus Area**: Email Validation Logic  
**Complexity**: Intermediate  
**Automation Level**: Fully Automated
