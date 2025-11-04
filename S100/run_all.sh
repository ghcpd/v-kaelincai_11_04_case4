#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
LOG_SUMMARY="$ROOT_DIR/compare_report.md"

pushd "$ROOT_DIR/Project_A_Stable" > /dev/null
./run_original.sh
popd > /dev/null

pushd "$ROOT_DIR/Project_B_Buggy" > /dev/null
set +e
./run_buggy.sh
BUGGY_EXIT=$?
set -e
popd > /dev/null

python - <<'PY'
import re
from pathlib import Path

root = Path(__file__).resolve().parent
stable_log = (root / "Project_A_Stable" / "log_original.txt").read_text().strip()
stable_time = (root / "Project_A_Stable" / "time_original.txt").read_text().strip()
buggy_log = (root / "Project_B_Buggy" / "log_buggy.txt").read_text().strip()
buggy_time = (root / "Project_B_Buggy" / "time_buggy.txt").read_text().strip()

pass_fail_re = re.compile(r"(?P<passed>\d+) passed(?:, (?P<failed>\d+) failed)?", re.IGNORECASE)

stable_match = pass_fail_re.search(stable_log)
buggy_match = pass_fail_re.search(buggy_log)

stable_passed = int(stable_match.group("passed")) if stable_match else "n/a"
stable_failed = int(stable_match.group("failed")) if stable_match and stable_match.group("failed") else 0

buggy_passed = int(buggy_match.group("passed")) if buggy_match else "n/a"
buggy_failed = int(buggy_match.group("failed")) if buggy_match and buggy_match.group("failed") else "n/a"

compare_path = root / "compare_report.md"
compare_path.write_text(f"""# Regression Comparison Report

## Test Outcome Summary

| Metric | Project A (Stable) | Project B (Buggy) |
| --- | --- | --- |
| Tests Passed | {stable_passed} | {buggy_passed} |
| Tests Failed | {stable_failed} | {buggy_failed} |
| Runtime (s) | {stable_time.split('=')[-1]} | {buggy_time.split('=')[-1]} |

## Observations

- Stable implementation enforces strict email validation and all tests succeed.
- Buggy implementation introduces relaxed email validation, allowing malformed addresses to pass.
- Automated suite surfaces the regression via failing tests covering invalid email formats.

## Log Excerpts

**Stable log:**

```
{stable_log}
```

**Buggy log:**

```
{buggy_log}
```
""")
PY

exit $BUGGY_EXIT
