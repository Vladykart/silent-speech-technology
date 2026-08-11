#!/usr/bin/env bash
# Authorized later use only: restore one named validated release and verify it.
set -euo pipefail
[[ ${QUIET_CHANNEL_DEPLOY_AUTHORIZED:-0} == 1 ]] || { echo "explicit deployment authorization is required" >&2; exit 1; }
REVISION=${1:?usage: rollback.sh <prior-full-revision> [authorized-tailnet-url]}
TAILNET_URL=${2:-}
[[ "$REVISION" =~ ^[0-9a-f]{40}$ ]] || { echo "prior revision must be full lowercase git identity" >&2; exit 1; }
RELEASE=/opt/quiet-channel/releases/$REVISION
CURRENT=/opt/quiet-channel/current
SERVICE=firstmate-silent-speech-demo.service
[[ -d "$RELEASE" && $(git -C "$RELEASE" rev-parse HEAD) == "$REVISION" ]] || { echo "named prior release is absent or mismatched" >&2; exit 1; }
"$RELEASE/realtime/generate_release_manifest.py" --check
serve_before=$(mktemp)
tailscale serve status >"$serve_before"
trap 'rm -f "$serve_before"' EXIT
ln -s "$RELEASE" "$CURRENT.rollback-link"
mv -Tf "$CURRENT.rollback-link" "$CURRENT"
printf 'SILENT_SPEECH_ASSET_DIR=/var/lib/quiet-channel/assets\nQUIET_CHANNEL_REVISION=%s\n' "$REVISION" >/etc/quiet-channel/replay.env.prepare
chmod 0640 /etc/quiet-channel/replay.env.prepare
chown root:quiet-channel-replay /etc/quiet-channel/replay.env.prepare
mv -f /etc/quiet-channel/replay.env.prepare /etc/quiet-channel/replay.env
systemctl restart "$SERVICE"
"$RELEASE/realtime/deploy/verify.sh" "$REVISION" "$TAILNET_URL"
diff -u "$serve_before" <(tailscale serve status)
echo "named prior release restored and exact route/revision verified"
