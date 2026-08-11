#!/usr/bin/env bash
# Authorized later use only: validate an immutable candidate, then cut over only the replay unit.
set -euo pipefail
[[ ${QUIET_CHANNEL_DEPLOY_AUTHORIZED:-0} == 1 ]] || { echo "explicit deployment authorization is required" >&2; exit 1; }
CANDIDATE_DIR=${1:?usage: deploy.sh <clean-candidate-checkout> <unused-loopback-port>}
CANDIDATE_PORT=${2:?candidate loopback port required}
SERVICE=firstmate-silent-speech-demo.service
CANDIDATE_SERVICE=firstmate-silent-speech-demo-candidate.service
RELEASE_ROOT=/opt/quiet-channel/releases
CURRENT=/opt/quiet-channel/current
ENV_FILE=/etc/quiet-channel/replay.env
UNIT_SOURCE="$CANDIDATE_DIR/realtime/deploy/firstmate-silent-speech-demo.service"

"$CANDIDATE_DIR/realtime/deploy/preflight.sh"
[[ "$CANDIDATE_PORT" =~ ^[0-9]+$ ]] && (( CANDIDATE_PORT > 1024 && CANDIDATE_PORT < 65536 && CANDIDATE_PORT != 8765 )) || { echo "invalid alternate candidate port" >&2; exit 1; }
! ss -H -ltn "sport = :$CANDIDATE_PORT" | grep -q . || { echo "candidate port is already owned" >&2; exit 1; }
revision=$(git -C "$CANDIDATE_DIR" rev-parse HEAD)
[[ "$revision" =~ ^[0-9a-f]{40}$ ]] || exit 1
[[ -z $(git -C "$CANDIDATE_DIR" status --porcelain) ]] || { echo "candidate checkout is not clean" >&2; exit 1; }
release="$RELEASE_ROOT/$revision"
[[ -d "$release" ]] || { echo "versioned release must be staged by owner before cutover" >&2; exit 1; }
[[ $(git -C "$release" rev-parse HEAD) == "$revision" && -z $(git -C "$release" status --porcelain) ]] || { echo "staged release identity/cleanliness mismatch" >&2; exit 1; }
QUIET_CHANNEL_RELEASE_REVISION="$revision" /opt/quiet-channel/venv/bin/python "$release/realtime/generate_release_manifest.py" --revision "$revision"
/opt/quiet-channel/venv/bin/python "$release/realtime/generate_release_manifest.py" --check
before_target=$(readlink -f "$CURRENT")
before_listeners=$(mktemp)
ss -H -ltnp | grep -v ':8765 ' >"$before_listeners" || true
cleanup() { systemctl stop "$CANDIDATE_SERVICE" >/dev/null 2>&1 || true; rm -f "$before_listeners"; }
trap cleanup EXIT

systemd-run --unit="${CANDIDATE_SERVICE%.service}" --property=User=quiet-channel-replay --property=Group=quiet-channel-replay \
  --property=WorkingDirectory="$release" --setenv=SILENT_SPEECH_ASSET_DIR=/var/lib/quiet-channel/assets \
  --setenv=QUIET_CHANNEL_REVISION="$revision" --setenv=QUIET_CHANNEL_REQUIRE_RELEASE_BINDING=1 \
  /opt/quiet-channel/venv/bin/uvicorn realtime.app.service:app --app-dir "$release" --host 127.0.0.1 --port "$CANDIDATE_PORT" --no-access-log --workers 1
for _ in {1..90}; do curl --fail --silent "http://127.0.0.1:$CANDIDATE_PORT/api/v1/health" >/dev/null && break; sleep 1; done
curl --fail --silent --show-error "http://127.0.0.1:$CANDIDATE_PORT/api/v1/health" >/dev/null
SILENT_SPEECH_ASSET_DIR=/var/lib/quiet-channel/assets /opt/quiet-channel/venv/bin/python -m unittest discover -s "$release/realtime/tests" -v
systemctl stop "$CANDIDATE_SERVICE"

rollback() {
  echo "cutover failed; restoring prior exact release" >&2
  ln -s "$before_target" "$CURRENT.rollback-link"
  mv -Tf "$CURRENT.rollback-link" "$CURRENT"
  systemctl restart "$SERVICE"
}
trap 'rollback; cleanup' ERR
ln -s "$release" "$CURRENT.next"
mv -Tf "$CURRENT.next" "$CURRENT"
printf 'SILENT_SPEECH_ASSET_DIR=/var/lib/quiet-channel/assets\nQUIET_CHANNEL_REVISION=%s\n' "$revision" >"$ENV_FILE.prepare"
chmod 0640 "$ENV_FILE.prepare"
chown root:quiet-channel-replay "$ENV_FILE.prepare"
mv -f "$ENV_FILE.prepare" "$ENV_FILE"
install -o root -g root -m 0644 "$UNIT_SOURCE" /etc/systemd/system/firstmate-silent-speech-demo.service
systemctl daemon-reload
systemctl restart "$SERVICE"
"$release/realtime/deploy/verify.sh" "$revision" '' "$before_listeners"
trap cleanup EXIT
echo "authorized replay-only cutover verified; Tailscale configuration was not mutated"
