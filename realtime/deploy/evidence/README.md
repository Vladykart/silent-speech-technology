# Sanitized private-deployment evidence schema

No deployment evidence is committed by the implementation worker. A later authorized deployment owner may add a dated text/JSON record containing only:

- application revision prefix plus an owner-side statement that the full revision matched the release manifest;
- pass/fail and UTC time for preflight, candidate acceptance, cutover, loopback check, authorized Tailnet check, Funnel-disabled check, unrelated-listener/route comparison, and rollback rehearsal;
- service template revision, dedicated UID/GID names (not numeric host inventory), and bounded status/timing;
- reviewer and rollback decision.

Never commit credentials/tokens/cookies, peer names or private IPs, source/session/member paths, prompts/candidates, full hashes, browser payloads/network traces, raw/filtered arrays, model outputs/weights, screenshots, logs, or Tailscale state dumps. Redact at collection; do not store a sensitive original in this repository. A failed check records only the category and no-output/rollback disposition.
