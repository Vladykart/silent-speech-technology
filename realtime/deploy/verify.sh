#!/usr/bin/env bash
# Verify exact replay ownership/binding without mutating Tailscale or unrelated listeners.
set -euo pipefail
EXPECTED_REVISION=${1:?usage: verify.sh <full-revision> [authorized-tailnet-url] [before-listeners]}
TAILNET_URL=${2:-}
BEFORE_LISTENERS=${3:-}
SERVICE=firstmate-silent-speech-demo.service
[[ "$EXPECTED_REVISION" =~ ^[0-9a-f]{40}$ ]] || { echo "revision must be full lowercase git identity" >&2; exit 1; }
health=$(curl --fail --silent --show-error --max-time 15 http://127.0.0.1:8765/api/v1/health)
python3 - "$EXPECTED_REVISION" "$health" <<'PY'
import json, sys
revision, raw = sys.argv[1:]
value=json.loads(raw)
assert value["status"] == "ready"
assert value["revision"] == revision[:12]
assert value["executed_models"] == 1
assert value["live_capture"] is False
PY
socket=$(ss -H -ltnp 'sport = :8765')
grep -F '127.0.0.1:8765' <<<"$socket" >/dev/null
grep -F '0.0.0.0:8765' <<<"$socket" && { echo "wildcard backend bind detected" >&2; exit 1; } || true
[[ $(systemctl show "$SERVICE" -p User --value) == quiet-channel-replay ]]
[[ $(systemctl show "$SERVICE" -p Group --value) == quiet-channel-replay ]]
serve_status=$(tailscale serve status)
funnel_status=$(tailscale funnel status)
grep -F 'https://srv1834218.tail8a7378.ts.net:8449' <<<"$serve_status" >/dev/null
grep -F 'http://127.0.0.1:8765' <<<"$serve_status" >/dev/null
grep -qi 'tailnet only' <<<"$serve_status$funnel_status"
! grep -Eqi 'funnel[[:space:]]+(on|enabled)|available on the internet' <<<"$serve_status$funnel_status"
if [[ -n "$TAILNET_URL" ]]; then
  [[ "$TAILNET_URL" == 'https://srv1834218.tail8a7378.ts.net:8449/' ]] || { echo "unexpected authorized URL" >&2; exit 1; }
  curl --fail --silent --show-error --max-time 20 "$TAILNET_URL" >/dev/null
fi
if [[ -n "$BEFORE_LISTENERS" ]]; then
  # Deployment evidence review owns normalization; a raw mismatch is a stop.
  diff -u "$BEFORE_LISTENERS" <(ss -H -ltnp | grep -v ':8765 ' || true)
fi
echo "verified exact replay revision, loopback owner, unchanged Tailnet contract, and Funnel disabled"
