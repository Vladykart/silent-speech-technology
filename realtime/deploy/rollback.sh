#!/usr/bin/env bash
# Authorized later use only: restore one named validated release or the captured transient predecessor.
set -euo pipefail
[[ ${QUIET_CHANNEL_DEPLOY_AUTHORIZED:-0} == 1 ]] || { echo "explicit deployment authorization is required" >&2; exit 1; }
TARGET=${1:?usage: rollback.sh <prior-reviewed-source-revision|legacy> [legacy-state] [authorized-tailnet-url]}
SERVICE=firstmate-silent-speech-demo.service
CURRENT=/opt/quiet-channel/current
ENV_FILE=/etc/quiet-channel/replay.env
DEPLOY_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)
VERIFY_SCRIPT="$DEPLOY_DIR/verify.sh"

write_environment() {
  local runtime_revision=$1
  printf 'SILENT_SPEECH_ASSET_DIR=/var/lib/quiet-channel/assets\nQUIET_CHANNEL_REVISION=%s\nQUIET_CHANNEL_RELEASE_REVISION=%s\n' "$runtime_revision" "$runtime_revision" >"$ENV_FILE.prepare"
  chmod 0640 "$ENV_FILE.prepare"
  chown root:quiet-channel-replay "$ENV_FILE.prepare"
  mv -f "$ENV_FILE.prepare" "$ENV_FILE"
}

serve_before=$(mktemp)
tailscale serve status >"$serve_before"
trap 'rm -f "$serve_before"' EXIT

if [[ "$TARGET" == legacy ]]; then
  LEGACY_STATE=${2:?legacy rollback requires the owner-only captured state file}
  TAILNET_URL=${3:-}
  [[ -f "$LEGACY_STATE" && $(stat -c %U "$LEGACY_STATE") == root && $(stat -c %a "$LEGACY_STATE") == 600 ]] || {
    echo "legacy rollback state must be root-owned mode 0600" >&2; exit 1;
  }
  # The owner-created state is deliberately not committed: it contains the prior private source path.
  # shellcheck disable=SC1090
  source "$LEGACY_STATE"
  [[ ${LEGACY_REVISION:-} =~ ^[0-9a-f]{40}$ && -d ${LEGACY_WORKING_DIRECTORY:-} && -x ${LEGACY_EXEC_START:-} ]] || {
    echo "legacy rollback state is incomplete" >&2; exit 1;
  }
  [[ $(git -C "$LEGACY_WORKING_DIRECTORY" rev-parse HEAD) == "$LEGACY_REVISION" && -z $(git -C "$LEGACY_WORKING_DIRECTORY" status --porcelain) ]] || {
    echo "legacy rollback source differs from its captured revision" >&2; exit 1;
  }
  systemctl stop "$SERVICE" >/dev/null 2>&1 || true
  rm -f "/etc/systemd/system/$SERVICE"
  systemctl daemon-reload
  systemctl reset-failed "$SERVICE" >/dev/null 2>&1 || true
  systemd-run --unit="${SERVICE%.service}" --property=WorkingDirectory="$LEGACY_WORKING_DIRECTORY" \
    --property=Restart=on-failure --property=RestartSec=3s "$LEGACY_EXEC_START" >/dev/null
  for _ in {1..120}; do curl --fail --silent --max-time 2 http://127.0.0.1:8765/api/health >/dev/null 2>&1 && break; sleep 1; done
  curl --fail --silent --show-error --max-time 10 http://127.0.0.1:8765/api/health >/dev/null
  pid=$(systemctl show "$SERVICE" -p MainPID --value)
  [[ $(ps -o user= -p "$pid" | xargs) == root ]]
  [[ $(readlink -f "/proc/$pid/cwd") == "$LEGACY_WORKING_DIRECTORY" ]]
  [[ $(git -C "$(readlink -f "/proc/$pid/cwd")" rev-parse HEAD) == "$LEGACY_REVISION" ]]
  socket=$(ss -H -ltnp 'sport = :8765')
  grep -F '127.0.0.1:8765' <<<"$socket" >/dev/null
  if [[ -n "$TAILNET_URL" ]]; then
    [[ "$TAILNET_URL" == 'https://srv1834218.tail8a7378.ts.net:8449/' ]] || { echo "unexpected authorized URL" >&2; exit 1; }
    curl --fail --silent --show-error --max-time 20 "$TAILNET_URL" >/dev/null
    curl --fail --silent --show-error --max-time 20 "${TAILNET_URL}api/health" >/dev/null
  fi
  diff -u "$serve_before" <(tailscale serve status)
  echo "captured transient predecessor restored with exact owner/source and unchanged route"
  exit 0
fi

SOURCE_REVISION=$TARGET
TAILNET_URL=${2:-}
[[ "$SOURCE_REVISION" =~ ^[0-9a-f]{40}$ ]] || { echo "prior source revision must be full lowercase git identity" >&2; exit 1; }
RELEASE=/opt/quiet-channel/releases/$SOURCE_REVISION
[[ -d "$RELEASE" && $(git -C "$RELEASE" rev-parse HEAD) == "$SOURCE_REVISION" && -z $(git -C "$RELEASE" status --porcelain) ]] || {
  echo "named prior reviewed release is absent, dirty, or mismatched" >&2; exit 1;
}
/opt/quiet-channel/venv/bin/python "$RELEASE/realtime/generate_release_manifest.py" --check
RUNTIME_REVISION=$(/opt/quiet-channel/venv/bin/python - "$RELEASE/realtime/release-manifest.json" <<'PY'
import json, pathlib, sys
value=json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))["application_revision"]
if len(value) != 40 or any(character not in "0123456789abcdef" for character in value): raise SystemExit(1)
print(value)
PY
)
ln -s "$RELEASE" "$CURRENT.rollback-link"
mv -Tf "$CURRENT.rollback-link" "$CURRENT"
write_environment "$RUNTIME_REVISION"
install -o root -g root -m 0644 "$RELEASE/realtime/deploy/firstmate-silent-speech-demo.service" "/etc/systemd/system/$SERVICE"
systemctl daemon-reload
systemctl restart "$SERVICE"
"$VERIFY_SCRIPT" "$RUNTIME_REVISION" "$TAILNET_URL"
diff -u "$serve_before" <(tailscale serve status)
echo "named reviewed release restored and exact runtime revision/route verified"
