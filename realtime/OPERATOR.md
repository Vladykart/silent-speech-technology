# Replay interface operator guide

Use this guide only with the loopback service described in [`README.md`](README.md). Do not expose it publicly, connect hardware, download assets during a presentation, or imply the presenter is being sensed.

## Say this first

> This is a local replay of official single-speaker research recordings through David Gaddy's real released pretrained model. It is not live capture. No person, microphone, camera, wearable or EMG device is connected, and no new participant data is collected. A candidate is never executed automatically.

Keep the header truth label visible: **REAL RECORDED sEMG REPLAY • REAL RELEASED MODEL**. This is a non-commercial local research demonstration—not measured project accuracy, mind reading, identity/emotion inference, medical/AAC/emergency use, live hardware or a shipping product.

## Three-stage walkthrough

### 1 · Data collection

1. Point to the always-on boundary before selecting anything. Explain that “Data collection” names the acquisition stage, but this build only **selects and replays an existing official 1 kHz, eight-channel sEMG array**.
2. In **Recorded examples available now**, select one of the three deterministic bindings:
   - `QC-R01` / held-out question recording / one official take;
   - `QC-R02` / clock-prompt abstention and repair / two official takes;
   - `QC-R03` / safety-sensitive instruction / one official take.
3. Point to **Keep these three things separate**:
   - operator input: the QC dataset replay reference;
   - participant/dataset command label: sealed until inference ends;
   - actual model input: the recorded sEMG tensor only;
   - downstream model candidate: not yet available and never an automatic action.
4. Contrast the amber **Future command examples** group. Its eight phrases are authored ideas with no recordings, no selection controls and no execution path. Never call them recorded commands, outputs, supported vocabulary or current capability.
5. Choose **Run selected recorded example**. Do not mouth or type the sealed phrase as if it were sensed.

### 2 · Model

1. Follow the trace from recorded tensor through source-faithful preprocessing to the released 54,187,136-parameter residual CNN/relative-position Transformer.
2. The channel plot is a display subsample of the local official array, not a live sensor trace.
3. Open **Inspect preprocessing and phoneme emissions** only if technical depth is useful. The main path intentionally keeps those details collapsed.
4. If local forward-pass time appears, describe it only as a software diagnostic for that run. It is not end-to-end hardware/product latency.
5. Note that metadata remains sealed while model inference runs. Prompt text, dataset labels and future examples are never passed to the model or bounded decoder.

### 3 · Process result

1. Read the model candidate as **held—not executed**. Candidate ranking values and the 0.60 boundary are uncalibrated phoneme-alignment diagnostics, not confidence, accuracy or probabilities.
2. Only now point out the official dataset command label. The stream emitted it after inference for audit; it did not produce or steer the candidate.
3. Demonstrate the human gate:
   - **Accept as final local result** creates a local result only; it triggers no action or actuation.
   - **Reject candidate** leaves no final result.
   - an abstention below 0.60 leaves no final result and, for `QC-R02`, enables a second official recorded take.
   - `QC-R03` keeps acceptance disabled until the safety acknowledgement is checked. It is not an emergency or safety system.
4. Point to **NO EGRESS**. Arrays and outputs remain in the loopback service/browser session; there are no accounts, telemetry, external runtime requests, browser storage or recording APIs.

## Recommended path demonstrations

- **Ordinary human hold:** run `QC-R01`, wait for post-inference metadata, then reject once and rerun if an accepted-result view is needed.
- **Abstention and repair:** run `QC-R02`; show that the first take yields no final result. Choose **Replay second official recorded take**, then accept or reject the repaired candidate. No synthetic noise or signal is added.
- **Safety gate:** run `QC-R03`; first show that acceptance is disabled. Read and check the acknowledgement, then either reject or accept as a local-only result. Never suggest physical actuation.

These are selected interaction paths, not a representative evaluation. Do not count them as command accuracy, WER or validation.

## Keyboard, responsive and failure rehearsal

- Use `Tab` / `Shift+Tab` through recorded-example radios, run/stop controls, the optional-detail summaries, safety acknowledgement and decision controls. The skip link appears on focus.
- The three stage links jump to stage headings; the active step is also announced to screen readers. Do not rely on color alone—read the stage and state labels.
- Rehearse at desktop and narrow widths with no horizontal scrolling or obscured controls. At 4K the content remains centered rather than stretching indefinitely.
- With reduced motion enabled, the animated brand and transitions stop.
- **Stop replay** and every service/error path must end with no final result. If an error appears, do not retry by changing network, sandbox or security policy; use the locked static [`../demo/`](../demo/) only as its separately labelled concept/simulated fallback.
- Clear the volatile event log if needed. Reloading starts a new browser view; no history is persisted.

## Attribution

Recorded data: Silent Speech EMG v1.0, David Gaddy / UC Berkeley, Zenodo `10.5281/zenodo.4064409` (concept DOI `10.5281/zenodo.4064408`), CC BY 4.0, one speaker.

Released model: Voicing Silent Speech Models, David Gaddy, Zenodo `10.5281/zenodo.6747411`, CC BY 4.0. Adapted source reference: `dgaddy/silent_speech` commit `a89357c2086609b432919b9d14ffc0be5d8983d5`, MIT. External source results do not become project results.
