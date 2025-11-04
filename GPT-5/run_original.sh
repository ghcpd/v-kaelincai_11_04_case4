#!/usr/bin/env bash
set -euo pipefail
python -m venv .venv
source .venv/bin/activate
pip install -r requirements_original.txt > /dev/null
python - <<'PY'
import time, subprocess, pathlib
start=time.perf_counter()
proc=subprocess.run(["pytest","-vv"],capture_output=True,text=True)
pathlib.Path("log_original.txt").write_text(proc.stdout+"\n"+proc.stderr)
pathlib.Path("time_original.txt").write_text(f"{time.perf_counter()-start:.4f} seconds\n")
print(proc.stdout)
PY
