#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$SCRIPT_DIR"

LOG_FILE="log_original.txt"
TIME_FILE="time_original.txt"

python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements_original.txt

SECONDS=0
pytest --maxfail=1 --disable-warnings -q | tee "$LOG_FILE"
DURATION=$SECONDS

echo "elapsed_seconds=$DURATION" > "$TIME_FILE"
