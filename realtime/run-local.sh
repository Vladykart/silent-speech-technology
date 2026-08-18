#!/usr/bin/env bash
# Presentation-safe launcher: no dependency install, asset download, or fallback.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$ROOT"
VENV="$ROOT/realtime/.venv"
[[ -x "$VENV/bin/python" ]] || { echo "realtime/.venv is missing; prepare dependencies before presentation" >&2; exit 1; }
"$VENV/bin/python" -c 'import cmudict,fastapi,numpy,scipy,torch,uvicorn' >/dev/null 2>&1 || {
  echo "pinned runtime dependencies are missing; no presentation-time install is permitted" >&2; exit 1;
}
[[ -f realtime/local_assets/ready.json ]] || { echo "approved assets are not prepared; run realtime/fetch_assets.py before presentation" >&2; exit 1; }
revision=${QUIET_CHANNEL_REVISION:-$(git rev-parse --short=12 HEAD)}
export QUIET_CHANNEL_REVISION="$revision"
printf '%s\n' 'Quiet Channel private research replay: http://127.0.0.1:8765/'
printf '%s\n' 'TRUTH: official single-speaker recorded sEMG; one official released model; not live capture.'
exec "$VENV/bin/python" -m uvicorn realtime.app.service:app --host 127.0.0.1 --port "${PORT:-8765}" --no-access-log --workers 1
