# Bug-related Regression Evaluation

This repository hosts two intentionally divergent implementations of a user registration system for benchmarking regression detection capabilities of AI-assisted engineering workflows.

## 📂 Project Layout

- `Project_A_Stable/` – Baseline implementation with correct validation logic and passing automated tests.
- `Project_B_Buggy/` – Feature-extended implementation that regresses the email validation logic causing test failures.
- `test_data.json` – Shared structured scenarios spanning nominal, boundary, and malformed inputs, annotated for regression tracking.
- `run_all.sh` – Orchestrates environment setup, executes both projects, and compiles the aggregate comparison in `compare_report.md`.
- `compare_report.md` – Generated summary comparing pre- and post-regression behavior (created after running `run_all.sh`).

## 🧪 Regression Scenario

- **Original behavior:** `Project_A_Stable/registration_stable.py` enforces strict email validation via a RFC-compliant regular expression, blocking malformed addresses (`user@@mail`, `test@.com`, etc.).
- **Broken behavior:** `Project_B_Buggy/registration_buggy.py` relaxes validation to only require the `@` symbol (introduced while adding third-party login support). As a result, invalid emails are erroneously accepted, breaking historical guarantees.
- **Verification goal:** Automatically detect the regression by contrasting the passing stable suite with the failing buggy suite, inspecting logs, runtimes, and generated report artifacts.

## 🚀 Running the Projects

> These examples use Bash; on Windows, execute via Git Bash or WSL for POSIX compatibility.

1. **Project A – Stable**
   ```bash
   cd Project_A_Stable
   ./setup_original.sh  # optional if not using run script
   ./run_original.sh
   ```
   Outputs: `log_original.txt`, `time_original.txt` with fully passing tests.

2. **Project B – Buggy**
   ```bash
   cd Project_B_Buggy
   ./setup_buggy.sh     # optional if not using run script
   ./run_buggy.sh       # exits non-zero to flag the regression
   ```
   Outputs: `log_buggy.txt`, `time_buggy.txt` showing failing regression tests.

3. **Aggregate Comparison**
   ```bash
   ./run_all.sh
   ```
   - Sequentially runs both suites
   - Aggregates timing and log data
   - Generates `compare_report.md` summarizing pass/fail deltas

## 🧰 Environment & Reproducibility

- Each project ships an isolated `requirements_*.txt` for deterministic dependency resolution (`pytest==8.1.1`).
- `setup_*.sh` scripts create virtual environments, upgrade `pip`, and install dependencies.
- All tests rely solely on the Python standard library + `pytest`, avoiding external data stores.
- Logs and comparison report capture timestamps and evidence for reproducibility and audit trails.

## 📊 Test Data Overview

`test_data.json` enumerates five canonical scenarios:

| ID | Category | Expected | Regression Sensitive |
| --- | --- | --- | --- |
| TC01 | Normal | Success | No |
| TC02 | Boundary | Success | No |
| TC03 | Boundary | Success | No |
| TC04 | Malformed | Failure | Yes |
| TC05 | Malformed | Failure | Yes |

## ⚠️ Limitations

- In-memory storage only (no persistent database). Duplicate checks are case-insensitive but scoped to process lifetime.
- Shell scripts assume a POSIX-like environment; Windows users should leverage Git Bash/WSL.
- Performance metrics focus on relative comparisons rather than absolute benchmarks.

## 📚 Experiment Goal

This setup supports evaluation of models such as GPT-5-Codex, GPT-5, Claude Sonnet 4.5, S100, and S40 on their ability to:

1. Reproduce the regression bug from shared scenarios.
2. Diagnose the faulty validation logic.
3. Propose corrective patches aligned with the stable baseline behavior.

Run `run_all.sh` and inspect `compare_report.md` to kick off your analysis.
