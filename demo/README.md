# Silent-speech recognition console runbook

## Truth boundary

This is a static **CONCEPT / SIMULATED** interaction demo. Eight-channel traces, feature values, token frames, candidates, scores, threshold, and timing are bundled synthetic/authored fixtures. The repository has no electrodes, capture hardware, biometric samples, trained model, live EMG inference, project accuracy, calibrated confidence, complete latency, user study, production system, or deployment evidence.

The page uses no microphone, camera, WebAudio, WebRTC, media capture, file upload, account, form, storage, cookie, analytics, telemetry, or runtime request. It works offline from `file://`. The visible upstream links navigate only if an operator explicitly opens them; they are not runtime dependencies.

## Verify and run

From the repository root:

```bash
python3 demo/generate_manifest.py
python3 demo/validate.py
node demo/tests/core.test.js
```

Open [`index.html`](index.html) directly, or rehearse on loopback:

```bash
python3 -m http.server 8000 --bind 127.0.0.1 --directory demo
```

Then open `http://127.0.0.1:8000/`. No install or build is required. Python’s development server is not approved for a public preview; use [`DEPLOYMENT.md`](DEPLOYMENT.md) for bounded static-host controls.

## 60-second operator path

1. Point to **CONCEPT / SIMULATED**, the temporary-demo banner, and “Not project evidence” before touching a control.
2. Choose **Unlock concept**, then **Play to human gate**. The clear lookup pauses after its authored score clears the fixture rule. Choose **Confirm candidate** and show staged text `1`, raw fixture `0`, and “no network transmission.”
3. Press `2`, then **Play to human gate**. The ambiguous fixture abstains at `0.54` below authored threshold `0.72`. Choose **Choose authored repair**; show that repair is still blocked. Confirm it.
4. Press `3`, then play to the gate. The state-changing cancellation cannot resolve without explicit confirmation even though its scripted top score is `0.91`. Reject it when emphasizing safe fallback; confirm only when demonstrating the mandatory human gate.
5. Close on the source-lineage panel: the upstream architecture inspired explanatory stage labels, but none of its code, data, weights, samples, or model outputs runs here.

Do not silently mouth a phrase during the walkthrough; that could imply sensing. Do not call playback “live inference.”

## Controls and deterministic outcomes

| Action | Keyboard | Deterministic page behavior |
|---|---|---|
| Lock / unlock | `L` | Starts locked; locking clears progress and closes staged output |
| Advance | `Space` | Moves through six explanatory stages; candidate paths pause at the human gate |
| Play to human gate | button | Local timer advances fixture stages, then always pauses for operator action |
| Select scenario | `1`, `2`, `3` | Resets to that bundled synthetic fixture |
| Reset | `R` | Reconstructs authored constants and clears counters |
| Clear lookup | scenario 1 | top scripted score `0.84`; output remains blocked until confirmation |
| Ambiguous + repair | scenario 2 | top scripted score `0.54`; abstains below `0.72`; manual repair remains gated |
| Safety-sensitive | scenario 3 | top scripted score `0.91`; state change cannot pass without confirmation |

Authored elapsed values (`612–646 ms` at resolution, depending on scenario) exist only to design information hierarchy and presentation pacing. They are not measured inference, endpointing, human-response, device, or end-to-end latency. Fixture scores are not probabilities, accuracy, or model output.

## Upstream technical lineage

Primary reference: David Gaddy’s [`dgaddy/silent_speech`](https://github.com/dgaddy/silent_speech/tree/a89357c2086609b432919b9d14ffc0be5d8983d5), exact inspected commit `a89357c2086609b432919b9d14ffc0be5d8983d5`. Exact files and commit metadata are summarized in [`SOURCE_LINEAGE.md`](SOURCE_LINEAGE.md) and recorded authoritatively in `provenance/upstream-reference.md`; the MIT notice is preserved in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

The upstream README’s approximate 36% open-vocabulary WER is a historical upstream research result, not reproduced project performance. Real recognition requires consented EMG hardware/data, trained weights, alignment/language-model assets, substantial Python/PyTorch/CTC tooling, calibration, and evaluation. None is bundled.

## Rehearsal and fallback

Rendered QA was attempted with `chrome-devtools-axi` on 2026-07-29. Both `open` and `newpage` reached the exact `file://` URL but returned `Protocol error (Target.setDiscoverTargets): Target closed`; `pages` reported zero open pages. Therefore this release is **not browser-render certified**. Dependency-free DOM/CSS checks cover narrow breakpoints, focus, keyboard hooks, reduced motion and print structure, but exact-browser desktop/narrow/print rehearsal remains a release gate.

- Test desktop, narrow/mobile, keyboard-only, reduced-motion, 200% zoom, and print/PDF in the exact presentation browser.
- **Unexpected state:** reload; no state persists.
- **JavaScript disabled/fails:** use the static six-stage rail and [`PRESENTER.md`](PRESENTER.md). Never improvise a sensing claim.
- **Server issue:** open `index.html` from `file://`.
- **Network disconnected:** normal playback is unchanged. Do not open the optional external citations.
- **Layout issue:** use narrow layout or one zoom-out step; disclose any unrehearsed rendering limitation.

## Deployment boundary

[`artifact-manifest.json`](artifact-manifest.json) records SHA-256 and byte length for every other committed file under `demo/`; verify it with `python3 demo/generate_manifest.py`. `robots.txt`, page metadata, and required host headers request non-indexing, but do not make a public URL confidential. A public preview must use a no-write static allowlist, true 404, correct MIME, no directory listing, no credentials/tracking, and the exact security headers in [`DEPLOYMENT.md`](DEPLOYMENT.md).

This worktree does not deploy or alter a host, service, listener, firewall, DNS, Pages setting, or project visibility.
