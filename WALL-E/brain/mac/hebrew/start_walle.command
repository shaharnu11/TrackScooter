#!/bin/bash
# WALL-E talking Hebrew, Mac (Apple Silicon): ivrit.ai Whisper, DictaLM 3.0, Kokoro Hebrew. Double-click in Finder, or run in Terminal.
# Extra options pass through, e.g.:  ./start_walle.command --mind cloud
cd "$(dirname "$0")/../.." || exit 1
# An old WALL-E still running (once one ignored Ctrl+C): ask it to quit,
# then force it. It is found by the lock port it holds (talk_english.py
# INSTANCE_PORT), not by name: a name pattern also hit other programs.
OLD=$(lsof -nP -t -iTCP:18088 -sTCP:LISTEN 2>/dev/null)
if [ -n "$OLD" ]; then
  echo "Stopping the WALL-E that is still running..."
  kill -TERM $OLD
  for _ in 1 2 3 4 5; do kill -0 $OLD 2>/dev/null || break; sleep 1; done
  kill -9 $OLD 2>/dev/null
fi
# Leftover brain servers: only a process that IS our llama-server (anchored
# at the start of its command line), not one that merely mentions it.
pkill -f "^$PWD/models/llama-cpp/llama-server " 2>/dev/null
if [ ! -x .venv/bin/python ]; then
  echo "No .venv here. Do the setup in mac/README.md first."
  read -r -p "Press Enter to close."
  exit 1
fi
.venv/bin/python talk_english.py --lang he --brain dicta-12b "$@"
