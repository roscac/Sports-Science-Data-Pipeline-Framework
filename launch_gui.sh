#!/usr/bin/env bash
set -euo pipefail
if [ ! -d ".venv" ]; then
  python3 scripts/first_time_setup.py
fi
source .venv/bin/activate
python gui/main_window.py
