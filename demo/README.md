# Tomorrow demo runbook

## Truth label

This is an **offline concept / simulated pipeline**. Every trace, feature value, candidate, and confidence is authored fixture data. The experience does not measure silent-speech accuracy and uses no hardware, model, microphone, camera, biometric input, account, credential, storage API, or network request.

## Quick start

Direct file use works: open [`index.html`](index.html) in a current browser. For a local static server, from the repository root:

```bash
python3 -m http.server 8000 --directory demo
```

Then open `http://127.0.0.1:8000/`. This binds Python's default server on all interfaces; for a loopback-only rehearsal use:

```bash
python3 -m http.server 8000 --bind 127.0.0.1 --directory demo
```

No installation is required. Do not expose this server beyond the rehearsal machine.

## Preflight (2 minutes)

1. Run `python3 demo/validate.py` and `node demo/tests/core.test.js`.
2. Disconnect networking if desired; reload and confirm the page still works.
3. Confirm the page starts **LOCKED**, then choose **Unlock concept**.
4. Open scenario **Clear command**, press **Run next stage** three times, confirm the human gate appears, then confirm it; the simulated text-egress counter becomes `1` while raw fixture stays `0`.
5. Select **Ambiguous input**, advance to the confidence gate, choose the authored repair, and confirm that repair still requires confirmation.
6. Reset, lock the concept, set browser zoom to 100%, and leave the clear scenario selected.
7. Keep [`PRESENTER.md`](PRESENTER.md) available in a text editor as the fallback talk track.

Rendered cross-browser QA was not available during this release. Rehearsal in the exact presentation browser/display remains a gate.

## Controls and expected output

| Action | Keyboard | Expected deterministic result |
|---|---|---|
| Lock / unlock | `L` or button | Locked state closes the output gate; unlock is deliberate |
| Advance | `Space` or button | Advances one stage until the human gate; confirmation or rejection resolves the output gate |
| Auto-run | button | Pauses at the confidence/human gate for an explicit operator decision |
| Choose scenario | `1`, `2`, `3` or selector | Demo resets with selected authored trace |
| Reset | `R` or button | Returns to stage 1 with output closed and counters cleared |
| Clear command | Scenario 1 | top scripted candidate `0.84`; asks for confirmation |
| Ambiguous input | Scenario 2 | top scripted candidate `0.54`; rejects below `0.72`; manual authored repair remains gated |
| Safety command | Scenario 3 | top scripted candidate `0.91`; asks for confirmation |

Confidence values demonstrate interaction policy; they are **not probabilities calibrated on people, accuracy measurements, or model results**.

## Presenter operating sequence

Use the 3–5 minute script in [`PRESENTER.md`](PRESENTER.md). The strongest path is:

1. Point to the simulation boundary before touching the controls.
2. Unlock, then advance scenario 1 through features and candidates; confirm it and show the egress log.
3. Switch to scenario 2 and show automatic uncertainty rejection.
4. Choose the clearly labelled manual authored repair, then confirm it.
5. Close on the visible privacy controls and evidence gates.

## Reset and fallback

- **Normal reset:** press `R`; use `L` to restore the opening locked state.
- **Unexpected state:** reload `index.html`; no state is persisted.
- **JavaScript failure:** do not improvise a live capability. Show the static page and narrate the five-stage rail using `PRESENTER.md`.
- **Display/layout issue:** use browser zoom out once or use the narrow responsive layout; do not claim rendered QA was completed.
- **Server issue:** open `demo/index.html` directly with `file://`.

## Safety and privacy boundary

The switches demonstrate proposed product controls only. They do not establish encryption, isolation, legal compliance, or device security. The intended research beachhead is opt-in, low-consequence command/control. Assistive AAC, medical use, covert inference, workplace scoring, authentication, and safety-critical actions are outside tomorrow's claim boundary.
