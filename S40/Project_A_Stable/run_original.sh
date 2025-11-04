#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
LOG_FILE="log_original.txt"
TIME_FILE="time_original.txt"
START_TIME=$(python - <<'PY'
import time
print(time.time())
PY
)
python -m pytest --maxfail=1 --disable-warnings --cache-clear | tee "$LOG_FILE"
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
