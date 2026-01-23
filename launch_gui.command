#!/usr/bin/env bash
set -euo pipefail

# Change to the script's directory (important for .command files on macOS)
cd "$(dirname "$0")"

echo "🚀 Launching Sports Science Pipeline GUI..."

if [ ! -d ".venv" ]; then
  echo "📦 Setting up virtual environment and dependencies..."
  python3 -m scripts.first_time_setup
  echo "✅ Setup complete!"
else
  echo "✅ Virtual environment found."
fi

echo "🔌 Activating virtual environment..."
source .venv/bin/activate

echo "🎨 Launching GUI..."
python gui/main_window.py
