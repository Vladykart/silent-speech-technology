#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$ROOT"
VENV="$ROOT/realtime/.venv"
if [[ ! -x "$VENV/bin/python" ]]; then
  python3 -m venv "$VENV"
fi
if ! "$VENV/bin/python" -c 'import fastapi,numpy,torch,uvicorn' >/dev/null 2>&1; then
  "$VENV/bin/python" -m pip install --upgrade pip
  "$VENV/bin/python" -m pip install -r realtime/requirements.txt
fi
if [[ ! -f realtime/models/silent_ctc_v1.pt ]]; then
  "$VENV/bin/python" -m realtime.train
fi
printf '%s\n' 'Quiet Channel local service: http://127.0.0.1:8765/'
printf '%s\n' 'TRUTH: sensor signal is simulated with noise; model weights and inference are real.'
exec "$VENV/bin/python" -m uvicorn realtime.app.service:app --host 127.0.0.1 --port "${PORT:-8765}"
