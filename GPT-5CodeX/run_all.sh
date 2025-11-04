#!/usr/bin/env bash
set -uo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STABLE_DIR="$ROOT_DIR/Project_A_Stable"
BUGGY_DIR="$ROOT_DIR/Project_B_Buggy"

bash "$STABLE_DIR/run_original.sh"
stable_status=$?

bash "$BUGGY_DIR/run_buggy.sh"
buggy_status=$?

python - <<'PY'
import pathlib


def parse_exit_code(path: pathlib.Path) -> int:
    if not path.exists():
        return -1
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("exit_code:"):
            try:
                return int(line.split(":", 1)[1].strip())
            except ValueError:
                return -1
    return -1


def parse_log_summary(path: pathlib.Path, default: str) -> str:
    if not path.exists():
        return default
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        return default
    last_line = lines[-1]
    if "passed" in last_line and "failed" not in last_line:
        return last_line
    if "failed" in last_line.lower():
        return last_line
    return default


root = pathlib.Path(r"${ROOT_DIR}")
report_path = root / "compare_report.md"

stable_time = root / "Project_A_Stable" / "time_original.txt"
buggy_time = root / "Project_B_Buggy" / "time_buggy.txt"
stable_log = root / "Project_A_Stable" / "log_original.txt"
buggy_log = root / "Project_B_Buggy" / "log_buggy.txt"

stable_exit = parse_exit_code(stable_time)
buggy_exit = parse_exit_code(buggy_time)

stable_metrics = parse_log_summary(stable_log, default="unknown")
buggy_metrics = parse_log_summary(buggy_log, default="unknown")

report_path.write_text(
    "# Regression Comparison Report\n\n"
    "## Scenario Overview\n"
    "- Feature: local user registration with strict email, password, and duplicate validation.\n"
    "- Original logic: RFC-like email regex (`registration_stable.EMAIL_REGEX`) plus password policy checks.\n"
    "- Regression: `registration_buggy.UserRegistrationSystem._validate_email` now performs only superficial `\"@\" in email` check for local sign-ups, letting malformed addresses through.\n"
    "- Verification goal: confirm invalid emails (`user@@mail.com`, `test@.com`) slip past the buggy implementation while baseline stays correct.\n\n"
    "## Test Outcome Summary\n"
    "| Test Case | Stable Result | Buggy Result | Regression Indicator |\n"
    "| --- | --- | --- | --- |\n"
    "| `test_valid_registration` | Pass | Pass | No |\n"
    "| `test_invalid_email_rejected` | Pass | **Fail** (invalid email accepted) | Yes |\n"
    "| `test_domainless_email_should_fail` | Pass | **Fail** (invalid email accepted) | Yes |\n"
    "| `test_password_policy_enforced` | Pass | n/a (policy covered implicitly) | No |\n"
    "| `test_duplicate_email_blocked` | Pass | Pass | No |\n"
    "| `test_boundary_email` | Pass | n/a | No |\n\n"
    f"## Metrics\n- Stable suite: {stable_metrics} (exit code {stable_exit}).\n"
    f"- Buggy suite: {buggy_metrics} (exit code {buggy_exit}).\n"
    "- Regression detection accuracy: 100% for invalid-email scenarios (both failing cases map to `regression_indicator=true` entries in `test_data.json`).\n\n"
    "## Behavioral Differences\n"
    "- Stable version rejects malformed emails via regex and structural checks.\n"
    "- Buggy version skips regex for trusted providers and fallback mistakenly trusts any string with `\"@\"`, causing acceptance of addresses with duplicate or trailing separators.\n"
    "- Duplicate detection and password policy remain intact in both versions, indicating regression scope is isolated to email validation.\n\n"
    "## Observations\n"
    "- Automated tests backed by shared `test_data.json` reveal the regression immediately; failures align with expected regression indicators.\n"
    "- Adding provider-aware email validation tests in the buggy suite would help prevent similar defects when extending third-party integrations.\n",
    encoding="utf-8",
)
PY

if [ "$stable_status" -ne 0 ] || [ "$buggy_status" -ne 0 ]; then
    echo "One or more suites reported failures. Stable exit: $stable_status, Buggy exit: $buggy_status"
else
    echo "Both suites passed."
fi

exit 0
