#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/log_buggy.txt"
TIME_FILE="$SCRIPT_DIR/time_buggy.txt"
VENV_DIR="$SCRIPT_DIR/.venv_buggy"

"$SCRIPT_DIR/setup_buggy.sh"

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

python - <<'PY'
import pathlib
import subprocess
import sys
import time

script_dir = pathlib.Path(r"${SCRIPT_DIR}")
log_path = script_dir / "log_buggy.txt"
time_path = script_dir / "time_buggy.txt"

start = time.perf_counter()
process = subprocess.run(
    [sys.executable, "-m", "pytest", "-q", "test_buggy.py"],
    cwd=script_dir,
    capture_output=True,
    text=True,
)
elapsed = time.perf_counter() - start

log_contents = process.stdout
if process.stderr:
    log_contents += "\nSTDERR:\n" + process.stderr
log_path.write_text(log_contents, encoding="utf-8")

time_path.write_text(
    f"elapsed_seconds: {elapsed:.6f}\nexit_code: {process.returncode}\n", encoding="utf-8"
)

sys.exit(process.returncode)
PY
