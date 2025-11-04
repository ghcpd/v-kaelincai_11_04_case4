#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
LOG_FILE="log_buggy.txt"
TIME_FILE="time_buggy.txt"
START_TIME=$(python - <<'PY'
import time
print(time.time())
PY
)
set +e
python -m pytest --maxfail=1 --disable-warnings --cache-clear | tee "$LOG_FILE"
TEST_EXIT=$?
set -e
END_TIME=$(python - <<'PY'
import time
print(time.time())
PY
)
python - <<PY
start = float("$START_TIME")
end = float("$END_TIME")
with open("$TIME_FILE", "w", encoding="utf-8") as fh:
    fh.write(f"elapsed_seconds={end-start:.6f}\n")
PY
exit "$TEST_EXIT"
