# Investor real-replay operator guide

Use only after approved assets and all checks in [`QA.md`](QA.md) pass. Presentation-time network access, asset preparation, service changes, and synthetic/authored fallback are prohibited.

## Preflight and reset

1. Confirm the service reports ready, **one executed model**, the expected short revision, and ten sealed cards. If any check fails, stop.
2. Confirm the browser is authorized and the page shows: **REAL RECORDED sEMG REPLAY · ONE REAL RELEASED PRETRAINED MODEL · NOT LIVE CAPTURE**.
   - If you choose **guided mode**, confirm the rehearsal phrase is visible before starting.
   - If you choose **challenge mode** (default), confirm no phrase text is visible until metadata reveal after candidate generation.
3. Reload to clear volatile state. No prompt should appear on cards; a guided rehearsal phrase may appear only in the dedicated mode card in guided mode, and only before start.
4. Do not open developer tools, external addresses, downloads, media, or another demo during the pitch.

## 3–5 minute flow

### 0:00–0:30 — Truth before theatre

Say:

> This is a replay of an official single-speaker recorded sEMG array through David Gaddy’s official released pretrained model. It is not live capture. No person or device is being sensed.

Point to the proof stack: official source, **executed model 1 of 1**, human gate. Describe it as the **only currently approved, checksum-bound, and executable checkpoint**, never the best or most accurate model. Select a mode (guided or challenge), then read the amber curation boundary. Selected behavior is not project accuracy or representative evaluation.

### 0:30–1:45 — Featured real execution

Choose **Run featured official recording** (`QC-R01`). While its recorded-duration visualization advances:

- identify all eight channels and the transformed, 16-source-sample min/max display envelope;
- say it is source-derived, independently centered/scaled, and **not untouched raw data**;
- show source/filtered comparison and 60 Hz + harmonics / 2 Hz high-pass labels;
- open provenance: native `float64` is preserved at acquisition; the model branch converts to `float32` only after documented processing;
- identify the 112-feature heatmap as real preprocessing output that is inspectable but not consumed by this checkpoint;
- point to the three residual blocks, six-layer 768-wide Transformer, strict load, and 54,187,136 parameters;
- show the real 80-bin predicted mel output (not audio/ground truth) and real 48-class top outputs (not text confidence).

If timing is discussed, read its complete this-run local-software scope. Model forward and project decoder are separate. Neither is end-to-end product latency.

### 1:45–2:20 — Decoder and human control

The metadata prompt appears only after model and decoder completion in challenge mode. In guided mode, a rehearsal phrase is visible before start and remains only presenter guidance. Say:

> A project-built bounded phoneme-edit decoder postprocesses the released model’s real 48-class output. It is not another released or trained model. Its phoneme-alignment score is an uncalibrated diagnostic—not accuracy, confidence, or probability of correctness.

Reject once or confirm the held local result. Nothing actuates or calls another system.

### 2:20–3:15 — Failure is evidence

Run `QC-R02`. Show abstention and the empty final-result state. In guided mode, you may use the visible phrase as rehearsal context before each run, but state that this is not source repair. Select **Run second official take**. Say it is `QC-R02-T2`, a second checksum-bound official recording of the same source prompt—not added noise, simulation, or signal repair. The downstream pipeline is unchanged. Confirm or reject what actually occurs.

### 3:15–3:50 — Safety boundary

Run `QC-R03`. Show that confirmation remains disabled until the safety acknowledgement is checked. Acknowledgement is additional to confirmation. This is not an emergency or safety system and no action is connected.

### 3:50–4:30 — Diligence close

Open **Evidence & limits**:

- one checkpoint executed because its complete rights/checksum/runtime gates pass;
- every other component says **NOT EXECUTED HERE** and names its different role, modality, task, metric, and missing gates;
- the next proof plan is **protocol only / no results**: deterministic pre-execution freeze, disjoint cohorts, no replacement, complete failure denominator, and unknown training overlap;
- source scope is single-speaker English research data;
- no live hardware, project metric, open vocabulary, transfer, customer, medical/AAC, privacy, comfort, production, or deployment-performance evidence.

Close with:

> This proves a released artifact path can execute locally, including honest failure and human control. More model names or replay cards do not widen that claim. The next software proof is a pre-registered complete-denominator evaluation; a pilot still has to prove hardware, users, transfer, task value, and governance.

If commercial scope is asked, the only approved number is **AED 1,000,000 fixed-fee 90-day pilot**. Annual pricing, strategic funding, valuation, and exit amounts are TBD.

## Failure and no-output policy

- Stop, error, mismatch, abstention, and rejection produce no final result.
- Every non-abstained result requires confirmation; safety-sensitive output additionally requires acknowledgement.
- If any real run fails, leave the error/limitations state visible and stop. Do not switch to `demo/`, cached output, an authored fixture, or another sample as if the run succeeded.
- Never rerun or replace a frozen sample to improve the story. `QC-R08`–`QC-R10` include retained abstention/mismatch behavior; the catalogue is not scored.
- Bounded transformed evidence is sent to the authorized browser. Do not call that “no egress,” secure, compliant, or private-by-default.

## Keyboard and viewport rehearsal

Tab through skip link, ten radios, run/stop, provenance, chart inspection, reject/confirm, second take, safety acknowledgement, drawer tabs, and close. Space is blocked on the confirmation button; use Enter or an intentional pointer click. Escape closes the drawer without trapping focus. Repeat featured, repair, and safety paths at required desktop, tablet, narrow, and projector sizes. Any clipping, hidden focus, external request, or misleading label blocks release.
