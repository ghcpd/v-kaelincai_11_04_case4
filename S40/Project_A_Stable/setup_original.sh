#!/usr/bin/env bash
set -euo pipefail
python -m venv .venv
if [ -f ".venv/Scripts/activate" ]; then
  # Windows virtual environment activation
  source .venv/Scripts/activate
else
  source .venv/bin/activate
fi
python -m pip install --upgrade pip
python -m pip install -r requirements_original.txt
