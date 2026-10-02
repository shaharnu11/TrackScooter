#!/bin/bash
# WALL-E talking, Mac (Apple Silicon). Double-click in Finder, or run in Terminal.
# Extra options pass through, e.g.:  ./start_walle.command --mind cloud
cd "$(dirname "$0")/.." || exit 1
# An old brain left running holds port 8089: stop it first.
pkill -f llama-server 2>/dev/null
if [ ! -x .venv/bin/python ]; then
  echo "No .venv here. Do the setup in mac/README.md first."
  read -r -p "Press Enter to close."
  exit 1
fi
.venv/bin/python talk_english.py --brain 4b-vl "$@"
