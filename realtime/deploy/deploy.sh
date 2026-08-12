#!/usr/bin/env bash
# Authorized later use only: validate an immutable candidate, then cut over only the replay unit.
set -euo pipefail
[[ ${QUIET_CHANNEL_DEPLOY_AUTHORIZED:-0} == 1 ]] || { echo "explicit deployment authorization is required" >&2; exit 1; }
CANDIDATE_DIR=${1:?usage: deploy.sh <clean-reviewed-candidate-checkout> <unused-loopback-port>}
CANDIDATE_PORT=${2:?candidate loopback port required}
SERVICE=firstmate-silent-speech-demo.service
CANDIDATE_SERVICE=firstmate-silent-speech-demo-candidate.service
RELEASE_ROOT=/opt/quiet-channel/releases
CURRENT=/opt/quiet-channel/current
ENV_FILE=/etc/quiet-channel/replay.env
LEGACY_STATE=${QUIET_CHANNEL_LEGACY_ROLLBACK_STATE:-}
DEPLOY_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)
VERIFY_SCRIPT="$DEPLOY_DIR/verify.sh"
UNIT_SOURCE="$CANDIDATE_DIR/realtime/deploy/firstmate-silent-speech-demo.service"

listener_snapshot() {
  ss -H -ltnp | grep -v ':8765 ' | sed -E 's/fd=[0-9]+/fd=*/g' || true
}

write_environment() {
  local runtime_revision=$1
  printf 'SILENT_SPEECH_ASSET_DIR=/var/lib/quiet-channel/assets\nQUIET_CHANNEL_REVISION=%s\nQUIET_CHANNEL_RELEASE_REVISION=%s\n' "$runtime_revision" "$runtime_revision" >"$ENV_FILE.prepare"
  chmod 0640 "$ENV_FILE.prepare"
  chown root:quiet-channel-replay "$ENV_FILE.prepare"
  mv -f "$ENV_FILE.prepare" "$ENV_FILE"
}

load_legacy_state() {
  [[ -n "$LEGACY_STATE" && -f "$LEGACY_STATE" ]] || { echo "captured legacy rollback state is required for a transient predecessor" >&2; return 1; }
  [[ $(stat -c %U "$LEGACY_STATE") == root && $(stat -c %a "$LEGACY_STATE") == 600 ]] || { echo "legacy rollback state must be root-owned mode 0600" >&2; return 1; }
  # The owner-created state is deliberately not committed: it contains the prior private source path.
  # shellcheck disable=SC1090
  source "$LEGACY_STATE"
  [[ ${LEGACY_REVISION:-} =~ ^[0-9a-f]{40}$ && -d ${LEGACY_WORKING_DIRECTORY:-} && -x ${LEGACY_EXEC_START:-} ]] || {
    echo "legacy rollback state is incomplete" >&2; return 1;
  }
  [[ $(git -C "$LEGACY_WORKING_DIRECTORY" rev-parse HEAD) == "$LEGACY_REVISION" && -z $(git -C "$LEGACY_WORKING_DIRECTORY" status --porcelain) ]] || {
    echo "legacy rollback source differs from its captured revision" >&2; return 1;
  }
}

restore_legacy() {
  load_legacy_state
  systemctl stop "$SERVICE" >/dev/null 2>&1 || true
  rm -f "/etc/systemd/system/$SERVICE"
  systemctl daemon-reload
  systemctl reset-failed "$SERVICE" >/dev/null 2>&1 || true
  systemd-run --unit="${SERVICE%.service}" --property=WorkingDirectory="$LEGACY_WORKING_DIRECTORY" \
    --property=Restart=on-failure --property=RestartSec=3s "$LEGACY_EXEC_START" >/dev/null
  for _ in {1..120}; do
    curl --fail --silent --max-time 2 http://127.0.0.1:8765/api/health >/dev/null 2>&1 && break
    sleep 1
  done
  curl --fail --silent --show-error --max-time 10 http://127.0.0.1:8765/api/health >/dev/null
  local pid
  pid=$(systemctl show "$SERVICE" -p MainPID --value)
  [[ $(ps -o user= -p "$pid" | xargs) == root ]]
  [[ $(readlink -f "/proc/$pid/cwd") == "$LEGACY_WORKING_DIRECTORY" ]]
  [[ $(git -C "$(readlink -f "/proc/$pid/cwd")" rev-parse HEAD) == "$LEGACY_REVISION" ]]
  ss -H -ltnp 'sport = :8765' | grep -F '127.0.0.1:8765' >/dev/null
}

"$CANDIDATE_DIR/realtime/deploy/preflight.sh"
if ! [[ "$CANDIDATE_PORT" =~ ^[0-9]+$ ]] || ! (( CANDIDATE_PORT > 1024 && CANDIDATE_PORT < 65536 && CANDIDATE_PORT != 8765 )); then
  echo "invalid alternate candidate port" >&2
  exit 1
fi
! ss -H -ltn "sport = :$CANDIDATE_PORT" | grep -q . || { echo "candidate port is already owned" >&2; exit 1; }
source_revision=$(git -C "$CANDIDATE_DIR" rev-parse HEAD)
[[ "$source_revision" =~ ^[0-9a-f]{40}$ ]] || exit 1
[[ -z $(git -C "$CANDIDATE_DIR" status --porcelain) ]] || { echo "candidate checkout is not clean" >&2; exit 1; }
release="$RELEASE_ROOT/$source_revision"
[[ -d "$release" ]] || { echo "versioned reviewed release must be staged by owner before cutover" >&2; exit 1; }
[[ $(git -C "$release" rev-parse HEAD) == "$source_revision" && -z $(git -C "$release" status --porcelain) ]] || { echo "staged release identity/cleanliness mismatch" >&2; exit 1; }
runtime_revision=$(/opt/quiet-channel/venv/bin/python - "$release/realtime/release-manifest.json" <<'PY'
import json, pathlib, sys
value=json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))["application_revision"]
if len(value) != 40 or any(character not in "0123456789abcdef" for character in value): raise SystemExit(1)
print(value)
PY
)
git -C "$release" merge-base --is-ancestor "$runtime_revision" "$source_revision" || { echo "runtime-content revision is not an ancestor of reviewed source" >&2; exit 1; }
/opt/quiet-channel/venv/bin/python "$release/realtime/generate_release_manifest.py" --check

before_target=$(readlink -f "$CURRENT" 2>/dev/null || true)
legacy_before=false
if [[ $(systemctl show "$SERVICE" -p Transient --value) == yes ]]; then
  legacy_before=true
  load_legacy_state
  [[ $(systemctl show "$SERVICE" -p WorkingDirectory --value) == "$LEGACY_WORKING_DIRECTORY" ]] || { echo "live transient predecessor differs from captured rollback state" >&2; exit 1; }
elif [[ -z "$before_target" || ! -d "$before_target" ]]; then
  echo "named predecessor release is absent and live service is not the captured transient predecessor" >&2; exit 1
fi
before_runtime=
if [[ "$legacy_before" == false ]]; then
  before_runtime=$(/opt/quiet-channel/venv/bin/python - "$before_target/realtime/release-manifest.json" <<'PY'
import json, pathlib, sys
print(json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))["application_revision"])
PY
)
fi
before_listeners=$(mktemp)
unit_backup=$(mktemp)
listener_snapshot >"$before_listeners"
[[ -f "/etc/systemd/system/$SERVICE" ]] && cp -a "/etc/systemd/system/$SERVICE" "$unit_backup" || : >"$unit_backup"
cleanup() { systemctl stop "$CANDIDATE_SERVICE" >/dev/null 2>&1 || true; rm -f "$before_listeners" "$unit_backup"; }
trap cleanup EXIT

systemd-run --unit="${CANDIDATE_SERVICE%.service}" --property=User=quiet-channel-replay --property=Group=quiet-channel-replay \
  --property=WorkingDirectory="$release" --property=NoNewPrivileges=true --property=PrivateTmp=true \
  --property=PrivateDevices=true --property=ProtectSystem=strict --property=ProtectHome=true \
  --property='RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6' --property=IPAddressDeny=any --property=IPAddressAllow=localhost \
  --setenv=SILENT_SPEECH_ASSET_DIR=/var/lib/quiet-channel/assets \
  --setenv=QUIET_CHANNEL_REVISION="$runtime_revision" --setenv=QUIET_CHANNEL_REQUIRE_RELEASE_BINDING=1 \
  /opt/quiet-channel/venv/bin/uvicorn realtime.app.service:app --app-dir "$release" --host 127.0.0.1 --port "$CANDIDATE_PORT" --no-access-log --workers 1
for _ in {1..120}; do curl --fail --silent "http://127.0.0.1:$CANDIDATE_PORT/api/v1/health" >/dev/null 2>&1 && break; sleep 1; done
candidate_health=$(curl --fail --silent --show-error "http://127.0.0.1:$CANDIDATE_PORT/api/v1/health")
python3 - "$runtime_revision" "$candidate_health" <<'PY'
import json, sys
revision, raw=sys.argv[1:]
value=json.loads(raw)
assert value["status"] == "ready" and value["revision"] == revision[:12]
PY
SILENT_SPEECH_ASSET_DIR=/var/lib/quiet-channel/assets /opt/quiet-channel/venv/bin/python -m unittest discover -s "$release/realtime/tests" -v
systemctl stop "$CANDIDATE_SERVICE"

rollback() {
  trap - ERR
  echo "cutover failed; restoring prior exact service and revision" >&2
  if [[ "$legacy_before" == true ]]; then
    restore_legacy
  else
    ln -s "$before_target" "$CURRENT.rollback-link"
    mv -Tf "$CURRENT.rollback-link" "$CURRENT"
    write_environment "$before_runtime"
    if [[ -s "$unit_backup" ]]; then install -o root -g root -m 0644 "$unit_backup" "/etc/systemd/system/$SERVICE"; fi
    systemctl daemon-reload
    systemctl restart "$SERVICE"
    "$VERIFY_SCRIPT" "$before_runtime" ''
  fi
}
trap 'rollback; cleanup' ERR

ln -s "$release" "$CURRENT.next"
mv -Tf "$CURRENT.next" "$CURRENT"
write_environment "$runtime_revision"
if [[ "$legacy_before" == true ]]; then
  systemctl stop "$SERVICE"
  systemctl reset-failed "$SERVICE" >/dev/null 2>&1 || true
fi
install -o root -g root -m 0644 "$UNIT_SOURCE" "/etc/systemd/system/$SERVICE"
systemctl daemon-reload
if [[ "$legacy_before" == true ]]; then systemctl start "$SERVICE"; else systemctl restart "$SERVICE"; fi
"$VERIFY_SCRIPT" "$runtime_revision" '' "$before_listeners"
trap cleanup EXIT
echo "authorized replay-only cutover verified; reviewed source $source_revision serves runtime content $runtime_revision; Tailscale configuration was not mutated"
