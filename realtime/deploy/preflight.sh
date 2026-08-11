#!/usr/bin/env bash
# Read-only deployment preflight. This script never changes service or Tailscale state.
set -euo pipefail
SERVICE=firstmate-silent-speech-demo.service
STABLE_HANDLER='https://srv1834218.tail8a7378.ts.net:8449'
BACKEND='http://127.0.0.1:8765'

for command in git systemctl ss tailscale curl; do command -v "$command" >/dev/null || { echo "missing required command: $command" >&2; exit 1; }; done
serve_status=$(tailscale serve status)
funnel_status=$(tailscale funnel status)
grep -F "$STABLE_HANDLER" <<<"$serve_status" >/dev/null || { echo "stable Tailnet handler missing" >&2; exit 1; }
grep -F "$BACKEND" <<<"$serve_status" >/dev/null || { echo "stable handler target differs from loopback contract" >&2; exit 1; }
grep -qi 'tailnet only' <<<"$serve_status$funnel_status" || { echo "Tailnet-only status not proven" >&2; exit 1; }
if grep -Eqi 'funnel[[:space:]]+(on|enabled)|available on the internet' <<<"$serve_status$funnel_status"; then
  echo "Funnel/public exposure detected" >&2; exit 1
fi
socket=$(ss -H -ltnp 'sport = :8765' || true)
[[ -n "$socket" ]] || { echo "loopback backend socket is absent" >&2; exit 1; }
grep -F '127.0.0.1:8765' <<<"$socket" >/dev/null || { echo "backend is not loopback-only" >&2; exit 1; }
systemctl show "$SERVICE" -p Id -p LoadState -p ActiveState -p FragmentPath -p User -p Group -p WorkingDirectory -p ExecStart --no-pager
if ! curl --fail --silent --show-error --max-time 10 http://127.0.0.1:8765/api/v1/health >/dev/null; then
  curl --fail --silent --show-error --max-time 10 http://127.0.0.1:8765/api/health >/dev/null || {
    echo "current loopback health contract unavailable" >&2; exit 1;
  }
fi
echo "read-only preflight passed; stable handler and unrelated routes were not changed"
