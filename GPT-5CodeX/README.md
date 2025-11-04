# Evaluation of GPT-5-Codex, GPT-5, Claude Sonnet 4.5, S100, and S40 on Bug-related – Regression Detection, Diagnosis, and Correction

## 1. Test Scenario & Description
- **Functional baseline:** The stable implementation (`Project_A_Stable/registration_stable.py`) validates user payloads with rigorous email regex checks, a configurable password policy, and duplicate prevention over a normalized email key.
- **Regression change:** The buggy implementation (`Project_B_Buggy/registration_buggy.py`) adds third-party login support but shortcuts local email validation: `_validate_email` now trusts any string containing `"@"`, so malformed addresses such as `user@@mail.com` or `test@.com` slip through.
- **Input format:** JSON-like dictionaries with `email`, `password`, and optional `display_name` (see `test_data.json`).
- **Expected outputs:** Successful registrations return `{"status": "success", "message": "Registration successful"}` in Project A and `{"status": "success", "message": "Registration accepted"}` in Project B. Invalid inputs must raise `RegistrationError` with descriptive messages.
- **Verification goal:** Detect and confirm the regression by replaying the shared scenarios; the buggy suite should fail for the malformed email cases flagged by `regression_indicator=true` entries in `test_data.json`.

## 2. Project Layout
```
Project_A_Stable/
  registration_stable.py
  requirements_original.txt
  setup_original.sh
  test_original.py
  run_original.sh
  log_original.txt
  time_original.txt
Project_B_Buggy/
  registration_buggy.py
  requirements_buggy.txt
  setup_buggy.sh
  test_buggy.py
  run_buggy.sh
  log_buggy.txt
  time_buggy.txt
compare_report.md
run_all.sh
test_data.json
README.md
```

## 3. Environment Setup
Each project provisions an isolated virtual environment when you execute its `setup_*.sh` or `run_*.sh` script. Required dependency is `pytest==7.4.4`. On Windows, run the shell scripts via Git Bash or WSL; alternatively adapt the commands to PowerShell manually.

### Manual setup (optional)
1. `python -m venv .venv && source .venv/bin/activate`
2. `pip install -r Project_A_Stable/requirements_original.txt`
3. Repeat with `Project_B_Buggy/requirements_buggy.txt` if running individually.

## 4. Execution Instructions
- **Stable baseline:**
  ```bash
  bash Project_A_Stable/run_original.sh
  ```
  Produces a clean log in `Project_A_Stable/log_original.txt` and timing metadata in `Project_A_Stable/time_original.txt`.

- **Buggy regression build:**
  ```bash
  bash Project_B_Buggy/run_buggy.sh
  ```
  The suite intentionally fails on malformed email scenarios; the failures are documented in `Project_B_Buggy/log_buggy.txt` with exit code `1` recorded in `Project_B_Buggy/time_buggy.txt`.

- **Full comparison:**
  ```bash
  bash run_all.sh
  ```
  Runs both suites sequentially, tolerates the expected regression failure, regenerates `compare_report.md`, and summarizes exit codes in the console.

## 5. Test Data & Coverage
`test_data.json` centralizes six scenarios covering:
- Valid baseline registration of a new user.
- Boundary email using plus addressing and multi-part TLD.
- Maximum-length password stress case.
- Known regression triggers (`user@@mail.com`, `test@.com`).
- Password policy violation (missing symbol).

The pytest suites hydrate from this file to ensure parity across both projects.

## 6. Comparison Reporting
`compare_report.md` highlights:
- Pass/fail deltas between the stable and buggy suites.
- Quantitative pass counts and exit codes sourced from the timing artifacts.
- Narrative analysis of the regression scope and residual protections that remain intact.

## 7. Reproducibility Notes
- Scripts assume Python 3.9+ with `venv` available. Adjust the shebangs or replace with PowerShell equivalents if Bash is unavailable.
- All logs and metrics are stored under their respective project directories for easy diffing across runs.
- No external services or databases are required; the in-memory user store resets per test fixture.

## 8. Limitations
- The persistence layer is in-memory and intended solely for regression demonstrations.
- Third-party login flows are simulated; OAuth token handling is out of scope.
- Performance metrics use coarse wall-clock timings suitable for relative regression tracking rather than precise benchmarking.
