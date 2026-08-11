# Private replay deployment template

These files prepare a later, separately authorized private deployment. They do **not** authorize this implementation worker to install a service, create a user, change listeners, restart the existing demo, or alter Tailscale.

## Immutable contract

- Audience route: `https://srv1834218.tail8a7378.ts.net:8449/`, Tailnet only.
- Existing handler remains `/ → http://127.0.0.1:8765` byte-for-byte.
- Funnel remains disabled. No public DNS/tunnel/CDN/proxy and no route mutation command.
- The backend binds only `127.0.0.1:8765` and is owned only by `firstmate-silent-speech-demo.service`.
- Dedicated non-login user/group: `quiet-channel-replay`.
- Approved assets: owner-controlled `/var/lib/quiet-channel/assets`, read-only to the service, never under a web root.
- Reviewed source releases: `/opt/quiet-channel/releases/<full-reviewed-source-commit>` with atomic `/opt/quiet-channel/current` pointer and one retained validated predecessor. The no-self-reference `application_revision` inside the release manifest names the ancestor commit that last changed runtime content; health reports that runtime revision, not a later manifest/QA/evidence-only commit.

Stop if the handler/target differs, Funnel/public exposure is present, socket ownership is ambiguous, asset access would require world-readable permissions, the candidate is dirty/unbound, an unrelated listener/route would change, or exact rollback cannot be named.

## Later authorized sequence

1. Create the dedicated service account and private directories under owner change control. Never fall back to root or world-readable assets.
2. Stage an exact clean candidate commit under its full revision. Install pinned dependencies in the owner-controlled `/opt/quiet-channel/venv`; do not install at presentation time.
3. Set `QUIET_CHANNEL_DEPLOY_AUTHORIZED=1` only inside the authorized change window.
4. Run `preflight.sh`; retain only sanitized results.
5. Choose an unused alternate loopback port after `ss` inspection. Run `deploy.sh <clean-reviewed-candidate-checkout> <alternate-port>`. It validates the committed manifest without regenerating it, proves the runtime-content commit is an ancestor of the reviewed source, validates a temporary candidate, runs tests, stops it, atomically switches the release pointer, and restarts only the replay unit. For the first transition from the captured transient predecessor, provide its root-owned mode-0600 state file through `QUIET_CHANNEL_LEGACY_ROLLBACK_STATE`; the file stays outside the repository because it contains a private source path.
6. Run `verify.sh <full-runtime-revision> https://srv1834218.tail8a7378.ts.net:8449/` from an authorized Tailnet context. Compare unrelated listener and route snapshots. Listener comparison preserves endpoint, queue, process name, and PID and normalizes only systemd's inherited `fd=` number, which `daemon-reload` may renumber without changing listener ownership or behavior.
7. Rehearse `rollback.sh <prior-reviewed-source-revision>` and verify the old exact health revision. For the one-time captured transient predecessor use `rollback.sh legacy <owner-state-file> <authorized-url>`. On any failed cutover check, restore immediately rather than fixing forward.

The scripts contain read-only `tailscale ... status` calls only; they must never call route/Funnel mutation commands. Uvicorn access logging is disabled. Application logs exclude prompts, arrays, candidates, session IDs, paths, and full hashes.

## Release binding

`generate_release_manifest.py` hashes runtime/client files, the dependency lock, and private-manifest authorities while excluding itself. Generate it from the exact clean runtime-content commit, then commit that generated manifest and QA record in a later reviewed source commit. Deployment runs only `--check`: regenerating it from the later reviewed/evidence commit would destroy the intentional no-self-reference binding. The owner-only environment file sets both `QUIET_CHANNEL_REVISION` and `QUIET_CHANNEL_RELEASE_REVISION` to that runtime-content revision so the dedicated service can run the generator's check path without consulting Git ownership. The systemd unit enables `QUIET_CHANNEL_REQUIRE_RELEASE_BINDING=1`; readiness fails if runtime files, dependencies, manifests, or the configured runtime revision differ.

## Evidence

Use [`evidence/README.md`](evidence/README.md). Do not retain browser traces, signal/model payloads, prompts, credentials, peer/private-IP inventory, full hashes, source paths, or screenshots. Public exposure is not a deployment option.
