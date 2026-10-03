#!/bin/bash
# WALL-E talking, Mac (Apple Silicon). Double-click in Finder, or run in Terminal.
# Extra options pass through, e.g.:  ./start_walle.command --mind cloud
cd "$(dirname "$0")/.." || exit 1
# An old WALL-E still running (once one ignored Ctrl+C): ask it to quit,
# then force it, with its brain (llama-server) and Whisper process.
if pgrep -f "talk_english.py" >/dev/null; then
  echo "Stopping the WALL-E that is still running..."
  pkill -TERM -f "talk_english.py"
  for _ in 1 2 3 4 5; do pgrep -f "talk_english.py" >/dev/null || break; sleep 1; done
  pkill -9 -f "talk_english.py" 2>/dev/null
fi
pkill -f "multiprocessing.spawn" 2>/dev/null
pkill -f llama-server 2>/dev/null
if [ ! -x .venv/bin/python ]; then
  echo "No .venv here. Do the setup in mac/README.md first."
  read -r -p "Press Enter to close."
  exit 1
fi
.venv/bin/python talk_english.py --brain 30b-vl "$@"
