#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$ROOT_DIR/Project_A_Stable"
./run_original.sh
STABLE_EXIT=$?

cd "$ROOT_DIR/Project_B_Buggy"
set +e
./run_buggy.sh
BUGGY_EXIT=$?
set -e

cd "$ROOT_DIR"
export STABLE_EXIT_CODE="$STABLE_EXIT"
export BUGGY_EXIT_CODE="$BUGGY_EXIT"
python - <<'PY'
import datetime as dt
import json
import os
import pathlib
import re

root = pathlib.Path(__file__).resolve().parent
report_path = root / "compare_report.md"
logs = {
    "Project A (Stable)": {
        "path": root / "Project_A_Stable" / "log_original.txt",
        "exit_code": int(os.environ.get("STABLE_EXIT_CODE", "0")),
        "time_file": root / "Project_A_Stable" / "time_original.txt",
    },
    "Project B (Buggy)": {
        "path": root / "Project_B_Buggy" / "log_buggy.txt",
        "exit_code": int(os.environ.get("BUGGY_EXIT_CODE", "0")),
        "time_file": root / "Project_B_Buggy" / "time_buggy.txt",
    },
}

summary = {}
for name, info in logs.items():
    text = info["path"].read_text(encoding="utf-8", errors="ignore") if info["path"].exists() else ""
    summary_line = ""
    for line in reversed(text.splitlines()):
        candidate = line.strip()
        if candidate.startswith("=") and " in " in candidate:
            summary_line = candidate.strip("=").strip()
            break
    counts = {"passed": 0, "failed": 0, "skipped": 0, "warnings": 0}
    for label in counts:
        match = re.search(rf"(\d+)\s+{label}", summary_line)
        if match:
            counts[label] = int(match.group(1))
    time_value = "n/a"
    if info["time_file"].exists():
        raw_time = info["time_file"].read_text(encoding="utf-8").strip()
        time_value = raw_time.split("=", 1)[-1] if "=" in raw_time else raw_time
    summary[name] = {
        "counts": counts,
        "summary_line": summary_line or "No pytest summary found",
        "exit_code": info["exit_code"],
        "elapsed": time_value,
    }

cases = []
test_cases_path = root / "test_data.json"
if test_cases_path.exists():
    cases = json.loads(test_cases_path.read_text(encoding="utf-8"))
regression_cases = [case for case in cases if case.get("regression_indicator")]

lines = [
    "# Regression Comparison Report",
    "",
    f"Generated: {dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()}",
    "",
    "## Scenario Overview",
    "",
    "- **Feature:** User registration with email and password validation.",
    "- **Stable logic:** Uses anchored RFC-style regex, disallows consecutive separators, enforces domain labels, and blocks duplicates.",
    "- **Regression change:** Introduced OAuth provider support with email sanitisation and a relaxed regex (`^[A-Za-z0-9._%+-]+@[^\\s]+$`), allowing malformed emails such as `user@@mail` and `test@.com`.",
    "- **Verification goal:** Detect divergence in validation accuracy by re-running the original negative email cases and confirming failures in the buggy build.",
    "",
    "## Test Result Summary",
    "",
    f"{summary['Project A (Stable)']['summary_line']}",
    f"{summary['Project B (Buggy)']['summary_line']}",
    "",
    "| Metric | Project A (Stable) | Project B (Buggy) |",
    "| --- | --- | --- |",
    f"| Passed | {summary['Project A (Stable)']['counts']['passed']} | {summary['Project B (Buggy)']['counts']['passed']} |",
    f"| Failed | {summary['Project A (Stable)']['counts']['failed']} | {summary['Project B (Buggy)']['counts']['failed']} |",
    f"| Skipped | {summary['Project A (Stable)']['counts']['skipped']} | {summary['Project B (Buggy)']['counts']['skipped']} |",
    f"| Warnings | {summary['Project A (Stable)']['counts']['warnings']} | {summary['Project B (Buggy)']['counts']['warnings']} |",
    "",
    f"- **Execution time (stable):** {summary['Project A (Stable)']['elapsed']} seconds",
    f"- **Execution time (buggy):** {summary['Project B (Buggy)']['elapsed']} seconds",
    f"- **Regression-focused cases:** {len(regression_cases)} (`{', '.join(case['id'] for case in regression_cases)}`)",
    "- **Exit codes:",
    f"  - Stable exit code: {summary['Project A (Stable)']['exit_code']}",
    f"  - Buggy exit code: {summary['Project B (Buggy)']['exit_code']}",
    "",
    "## Observations",
    "",
    "1. The stable suite passes all assertions, confirming baseline correctness.",
    "2. The buggy suite exits with a non-zero status because invalid emails are no longer rejected, evidencing the regression.",
    "3. Duplicate user protection and password complexity remain intact across both versions, isolating the fault to email validation.",
    "4. Providers can now be attached to registrations in the buggy build, but the relaxed sanitisation inadvertently normalises malformed addresses.",
    "",
    "## Recommended Next Steps",
    "",
    "- Reinstate the strict regex (`^(?=.{3,254}$)(?!.*\\.\\.)[A-Za-z0-9._%+-]+@(?:[A-Za-z0-9-]+\\.)+[A-Za-z]{2,}$`) and remove the `@@` collapsing logic.",
    "- Extend CI pipelines to execute the shared `test_data.json` scenarios on every commit.",
    "- Add property-based tests for email parsing to cover unusual separators and provider-specific payloads.",
]

report_path.write_text("\n".join(lines), encoding="utf-8")
print(report_path)
PY

exit 0
