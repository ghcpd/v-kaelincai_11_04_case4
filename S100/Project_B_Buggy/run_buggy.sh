#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$SCRIPT_DIR"

LOG_FILE="log_buggy.txt"
TIME_FILE="time_buggy.txt"

python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements_buggy.txt

SECONDS=0
# Allow the command to fail so logs capture the regression while script exits non-zero.
set +e
pytest --maxfail=1 --disable-warnings -q | tee "$LOG_FILE"
EXIT_CODE=${PIPESTATUS[0]}
set -e
DURATION=$SECONDS

echo "elapsed_seconds=$DURATION" > "$TIME_FILE"
exit $EXIT_CODE
