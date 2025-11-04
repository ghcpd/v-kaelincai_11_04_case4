# Bug-Related Regression Evaluation

## 📌 Overview
This repository hosts two self-contained Python projects that demonstrate a regression in an email validation workflow for a user-registration feature. Project A provides the pre-regression, stable baseline, whereas Project B introduces a feature update (third-party provider integration) that accidentally loosens the email validation logic.

### 🔍 Regression Scenario & Description
- **Original behaviour (Project A):** Email addresses must pass a strict regular expression that rejects malformed inputs like `user@@mail`, `test@.com`, and repeated dots. Passwords must meet length and complexity rules, and duplicate registrations are blocked.
- **Broken behaviour (Project B):** To accommodate provider-based signups, the implementation normalises the email by collapsing consecutive `@` characters and applies a relaxed regex (`^[A-Za-z0-9._%+-]+@[^\s]+$`). This accepts malformed addresses (`user@@mail`, `test@.com`) that should be rejected, triggering a regression.
- **Input/Output format:** Registration requests and responses are Python dictionaries. Tests also use JSON payloads defined in `test_data.json` to drive scenario coverage.
- **Verification goal:** Execute both projects’ test suites to confirm the stable build passes while the buggy build fails on invalid email cases, thereby detecting the regression.

## 🗂 Project Layout
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
run_all.sh
compare_report.md (generated after running scripts)
test_data.json
README.md
```

## ⚙️ Environment Setup
Each project is isolated and ships with:
- `requirements_*.txt` for dependency pinning (`pytest`).
- `setup_*.sh` scripts that create a virtual environment and install dependencies.
- `run_*.sh` scripts that execute the entire test workflow, capture logs, and produce timing metrics.

> 💡 **Tip:** On Windows, run the shell scripts using Git Bash or WSL. Alternatively, replicate the commands manually (`python -m venv`, `pip install -r ...`, `pytest`).

## ▶️ Execution Guide
1. **Install dependencies:**
   - `cd Project_A_Stable && bash setup_original.sh`
   - `cd Project_B_Buggy && bash setup_buggy.sh`
2. **Run the stable suite:**
   - `cd Project_A_Stable && bash run_original.sh`
3. **Run the buggy suite:**
   - `cd Project_B_Buggy && bash run_buggy.sh` (expected to exit non-zero due to regression)
4. **Run both and aggregate:**
   - From the repository root, execute `bash run_all.sh` to run both suites sequentially, collect logs, and regenerate `compare_report.md`.

## 🧪 Test Coverage & Data
- `test_original.py` validates email, password, and duplicate scenarios.
- `test_buggy.py` repeats the checks while expecting strict email validation (fails under regression).
- `test_data.json` enumerates six structured inputs spanning normal, boundary, invalid, and regression-focused cases for reproducibility and downstream automation.

## 📄 Reporting & Metrics
- `log_original.txt` and `log_buggy.txt` store raw pytest output for each project.
- `time_original.txt` and `time_buggy.txt` hold execution duration measurements in seconds.
- `compare_report.md` summarises pass/fail counts, timing, exit codes, and regression observations after running `run_all.sh`.

## 🚫 Limitations
- The user store is in-memory; persistence and hashing are simplified for illustration only.
- Environment scripts rely on Bash; adapt commands for pure PowerShell if required.
- Performance timings are coarse-grained and intended for relative comparison rather than benchmarking.

## ✅ Next Steps for Experimentation
- Extend the dataset in `test_data.json` to stress-test provider-specific flows.
- Integrate these projects into CI workflows to benchmark regression-detection capabilities of different AI agents or testing strategies.
- Use the stable implementation as the ground truth when evaluating automated bug-fixing suggestions.
