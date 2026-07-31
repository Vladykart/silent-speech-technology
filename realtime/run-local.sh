#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$ROOT"
VENV="$ROOT/realtime/.venv"
if [[ ! -x "$VENV/bin/python" ]]; then
  python3 -m venv "$VENV"
fi
if ! "$VENV/bin/python" -c 'import cmudict,fastapi,numpy,scipy,torch,uvicorn' >/dev/null 2>&1; then
  "$VENV/bin/python" -m pip install --upgrade pip
  "$VENV/bin/python" -m pip install -r realtime/requirements.txt
fi
if [[ ! -f realtime/local_assets/ready.json ]]; then
  # Uses the captain-provided shared lab first. Network is used only when an
  # official asset is absent, and fetched files remain under ignored local_assets/.
  "$VENV/bin/python" realtime/fetch_assets.py --download-missing
fi
printf '%s\n' 'Quiet Channel local service: http://127.0.0.1:8765/'
printf '%s\n' 'TRUTH: replay of real recorded sEMG through real released weights; not live capture.'
printf '%s\n' 'NON-COMMERCIAL LOCAL RESEARCH DEMO — CC BY 4.0 attribution required.'
exec "$VENV/bin/python" -m uvicorn realtime.app.service:app --host 127.0.0.1 --port "${PORT:-8765}"
