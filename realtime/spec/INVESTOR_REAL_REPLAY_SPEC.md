# Investor real-replay product specification

**Version:** 1.0 — frozen 2026-08-11

**Authority:** product, evidence, payload, claim, QA, and private-deployment preparation contract for `realtime/`
**Change control:** the frozen catalogue, executed artifact, payload bounds, event order, and claim language may change only in a reviewed manifest/spec version with rationale. A weak, mismatched, errored, or abstained selected result is retained; it is never replaced after execution to improve the demonstration.

## 1. Product proof

In a 3–5 minute private presentation, a technically literate viewer can verify one official recorded signal, one official released checkpoint, real output tensors, a separately identified project decoder, and a mandatory human decision path without trusting presenter narration.

Permanent truth:

> **Replay of official single-speaker recorded sEMG through David Gaddy’s official released pretrained model; not live capture.**

This experience proves local artifact execution only. It does not prove a device, live sensing, project accuracy/WER, representative source performance, open vocabulary, transfer, customer value, medical/AAC use, privacy, safety, production, or deployment performance.

## 2. Executed and non-executed boundary

Exactly one model executes: David Gaddy’s checksum-bound `transduction_model.pt`, DOI `10.5281/zenodo.6747411`, CC BY 4.0, with 54,187,136 parameters. Startup verifies size and SHA-256, strict-loads all state tensors, and checks the parameter count. Its three residual temporal CNN blocks, six 768-wide relative-position Transformer layers, 80-bin mel head, and 48-class phoneme head execute on the selected official recording.

The project bounded phoneme-edit decoder executes after the model but is an **algorithm, not another model**. It receives the released 48-class output and the same complete frozen grammar for every run. It never receives the selected reference.

`model-registry.json` is authoritative. HiFi-GAN, upstream recognition weights, DeepSpeech/KenLM, SilentWear, MONA/LISA, papers, and repositories occupy a visually separate evidence registry. Every row is marked **NOT EXECUTED HERE**, has no run control, and states why.

## 3. Frozen official-recording catalogue

`sample-manifest.json` freezes ten public cards `QC-R01`–`QC-R10` and the repair-only `QC-R02-T2`. Every item is an official native `float64 [time,8]`, 1,000 Hz recording from Silent Speech EMG v1.0 (David Gaddy / UC Berkeley, DOI `10.5281/zenodo.4064409`, CC BY 4.0, single-speaker research source). Selected arrays, immediate filter context, and metadata are member-hash bound.

The card API exposes only public ID, split label, channel/rate/count/duration, neutral story, and second-take availability. It does not expose source session/date, member path, book/sentence identity, prompt, or result. `QC-R02-T2` is reachable only from `QC-R02` after abstention or rejection.

The UI must show this disclosure verbatim:

> Curated official-recording examples chosen for a short demonstration and interaction coverage. Outcomes may be success, mismatch, or abstention. This set is not representative and must not be counted as accuracy, WER, validation, or generalization evidence.

All frozen examples run after freeze. Their output shape, finiteness, ordering, and retained outcome are tested; the catalogue is not used to compute a metric.

## 4. Source and transformation contract

1. Load the selected and neighboring official `.npy` arrays read-only in native `float64`. No audio, buttons, identity field, camera, microphone, hardware, or authored fixture is read.
2. Preserve native dtype through acquisition. At preprocessing entry, explicitly convert to runtime `float64` processing; model input is explicitly converted to `float32` only after filtering/resampling/compression. Never call a displayed derivative untouched raw data.
3. Filter every channel with 60 Hz notch plus harmonics 2–7 and a 2 Hz third-order high-pass over selected + immediate context, then trim exactly to the selection.
4. Feature branch: resample to 516.79 Hz and compute 14 named values per channel (112/frame), using 16-sample windows and 6-sample hop. It is **inspectable / not consumed by the released forward path**.
5. Model branch: resample to 689.06 Hz, align eight raw samples per model frame after an eight-sample offset, divide by 20, apply `50*tanh(x/50)`, and convert to `float32`.
6. Retain real `[F,80]` mel output and `[F,48]` logits only for the active run. Build bounded display evidence, then release full outputs at terminal cleanup where practical.
7. Time model forward and project decoding separately. Labels state that each is measured local software time for this run and excludes recording duration, sensing, hardware, network, endpointing, confirmation, and output.

Production has no simulator import, constructor, fallback, or configuration route. Missing/stale/mismatched assets, dependency failure, model error, or non-finite/constant output fails closed with no candidate or result.

## 5. Information architecture

One original, responsive, same-origin page has a sticky truth bar and five anchored regions:

1. **Hero / proof contract.** Headline: “One real recording. One released model. Every boundary visible.” Proof cards identify recorded source, executed model 1 of 1, and human gate. Primary action runs `QC-R01`; secondary action moves to the library.
2. **Official sample library.** Ten selectable cards with prompt sealed. No outcome is pre-badged. In-memory last-run state may appear and clears on reload.
3. **Three-stage workspace.** Exactly `Recorded source → Released model → Human decision`, preserving the sealed reducer and no-output invariants.
4. **Evidence and limitations drawer.** What executed; evidence-only registry; claims/limitations; text-only sources/rights.
5. **Attribution / deployment status.** Private Tailnet-only research demo delivery, not public or customer/product deployment.

Always visible:

> No live hardware; no project accuracy/WER; no open-vocabulary, cross-speaker/session, customer, medical/AAC, safety-system, comfort, privacy, production, or deployment-performance evidence. Official source scope is single-speaker English research data.

### Stage 1 — Recorded source

Show safe source facts and all eight numbered channels under:

> **RECORDED SOURCE TRACE · TRANSFORMED DISPLAY ENVELOPE**

> 8/8 channels · 16-source-sample min/max bins · per-channel display centering/scaling · not untouched raw data

Canvas is supplementary to a concise text/table alternative. Animation follows recording duration only as a visualization and is never described as live, capture, streaming sensor, or real time. Stop is terminal and commits no output.

### Stage 2 — Preprocessing and released model

Show the rail `checksum-bound source → context-aware filter → dual resample → model raw branch → released CNN/Transformer → real output heads`, plus:

- aligned 8-channel source/filtered envelopes with independent display scaling and filter labels;
- stage provenance with input/output rates, shapes, dtypes, lineage, and model-input status;
- real 112-feature heatmap grouped by eight channels × 14 names;
- executed-model-1-of-1 architecture/checkpoint card with short fingerprint only;
- real 80-bin mel output labelled predicted normalized features, not audio or ground truth;
- exact per-frame top-1 48-class token and rounded top-class softmax diagnostic plus collapsed path; never full logits;
- separate model-forward and decoder timing.

### Stage 3 — Process result / human gate

Label candidate ranking **PROJECT BOUNDED DECODER · NOT THE RELEASED MODEL**. Show at most three candidates and an uncalibrated `phoneme_alignment_score`/`diagnostic_score`; never “confidence.” Reveal the exact official metadata prompt only after decoder completion and label it audit-only. A mismatch is displayed, not scored as accuracy.

Terminal policies:

- abstain: no result; only `QC-R02` may request its second official take;
- non-abstained candidate: confirmation required;
- safety-sensitive sample: acknowledgement **and** confirmation required;
- reject, stop, error: no result;
- confirmed: final result exists only in volatile service/browser memory; no actuation.

No CRM, assistant, downstream API, action, or actuator is connected.

## 6. Ordered event and browser API contract

Only explicit client files and versioned `/api/v1/...` routes are served. OpenAPI/docs, generic static/download/data/debug routes, directory listings, cookies, persistence, telemetry, and access-log identifiers are disabled.

Routes:

- `GET /api/v1/manifest`
- `POST /api/v1/runs`
- `GET /api/v1/runs/{opaque}/events`
- `POST /api/v1/runs/{opaque}/stop`
- `POST /api/v1/runs/{opaque}/decision`
- `POST /api/v1/runs/{opaque}/second-take`
- owner-safe readiness may use `GET /api/v1/health`, with prefixes only.

Runs are bounded in number, expire, and are cleaned. IDs are opaque and excluded from application logs. The server rejects replaying a run or impossible state/order.

Monotonic event order:

1. `asset_checks_passed`
2. `source_opened`
3. `replay_started`
4. `source_complete`
5. `preprocessing_complete`
6. `branches_aligned`
7. `model_forward_complete`
8. `decoder_complete`
9. `metadata_revealed`
10. `decision_required`
11. terminal human state through a decision/stop response

A prompt, candidate, decision, or reference before its permitted predecessor is a hard client/server boundary error. Browser errors are generic and contain no hash/path/prompt/array.

## 7. Browser payload contract

`DisplayPayloadBuilder` is the sole transformation implementation. Every derivative includes `display_transform`, `source_rate`, `display_bins`, and `not_untouched_raw: true` where relevant.

| View | Maximum payload | Required meaning |
|---|---:|---|
| Source oscilloscope | 8 channels × 256 chronological min/max bins; at least 16 source samples/bin | Robust per-channel centered/clipped/scaled signed-8-bit display envelope; no scale/center values |
| Source/filtered comparison | 2 branches × 8 channels × 128 aligned min/max bins | Branches independently display-scaled; filter operations named |
| Features | 64 time bins × 112 signed-8-bit values | Time-binned, per-feature normalized real preprocessing output; not model input |
| Mel | 64 time bins × 80 signed-8-bit values | Real normalized model prediction transformed/time-binned; not audio/ground truth |
| Phonemes | top index/token + top softmax rounded to 3 decimals for each bounded frame; collapsed path | Real released auxiliary-head output; top-class diagnostic, not text confidence |
| Decoder | at most 3 rows | Candidate text and rounded diagnostics only |

The browser may receive approved truth/source facts, safe IDs, short 8–12 hex fingerprint/revision prefixes, architecture/output shapes, current-run times, post-decoder prompt, and human state.

It must never receive identity/demographics/session/date, member/local/archive path, full digest, archive inventory, full arrays/tensors/logits/weights, audio/buttons, downloads, credentials, Tailnet inventory, prompt before inference, clickable external URL, analytics, beacon, service worker, cache, or persisted storage.

Disclosure:

> Bounded transformed evidence is sent to this authorized browser; no third-party telemetry, persistence, raw archive, or actuation.

## 8. Security, accessibility, and responsive contract

All responses are `no-store`. CSP is self-only with `base-uri 'none'`, `form-action 'none'`, `object-src 'none'`, and `frame-ancestors 'none'`. Permissions Policy denies camera, microphone, geolocation, payment, USB, serial, and Bluetooth. There are no remote assets, URLs, fonts, images, source maps, service workers, media APIs, file inputs, or external anchors.

At 1100 px and below, the workspace fully stacks. Validate 320×568, 375×812, 768×1024, 1024×768, 1366×768, 1920×1080, and 3840×2160: viewport and document widths match; no clipped text, overlap, chart spill, hidden focus, or inaccessible control. Projector content is capped; body text and panel headings remain presentation-readable. Reduced motion removes tweening. Canvas scales by device pixel ratio and always has text alternatives.

Keyboard contract: skip link, semantic ordered headings, fieldset/legend, visible focus, run/stop, sample selection, details, reject/confirm, second take, acknowledgement, and Escape drawer close. Space cannot accidentally confirm. Dynamic focus remains trustworthy; no focus trap. Status and alert roles are distinct and state does not rely on color.

## 9. Claims and operator flow

Approved labels:

- “This run strict-loaded and executed the checksum-bound 54,187,136-parameter released transduction checkpoint.”
- “A project-built bounded phoneme-edit decoder postprocesses the released model’s real 48-class output. It is not another released or trained model.”
- “Transformed, decimated display derived from the official recorded source—not untouched raw data.”
- “Released model’s normalized 80-bin mel-head prediction; not audio or ground truth.”
- “Uncalibrated phoneme-alignment diagnostic; not accuracy, confidence, or probability of correctness.”
- “Private Tailnet-only research demo delivery; not public or a product/customer deployment.”

Never imply thought reading, live sensing, a wearable, on-device/real-time/product readiness, successful understanding, held-out/project performance, open vocabulary, Arabic/customer capability, “no egress,” security/compliance merely from Tailnet, medical/AAC/emergency/payment/authentication/safety use, or multiple executed models.

Operator sequence:

1. **0:00–0:30:** read truth badge and one-model proof.
2. **0:30–1:45:** run `QC-R01`; show 8 channels, transformations, inspectable-not-consumed features, architecture, real mel/phoneme outputs, and correctly scoped timings.
3. **1:45–2:20:** show post-inference metadata and decoder separation; reject or confirm; point out no actuation.
4. **2:20–3:15:** run `QC-R02`; show abstention and no output; run `QC-R02-T2` as a second official take, never synthetic repair.
5. **3:15–3:50:** run `QC-R03`; show acknowledgement is additional to confirmation.
6. **3:50–4:30:** open limitations/evidence registry and close on the next pilot evidence programme. Commercial discussion, if any, uses only the captain-approved AED 1,000,000 fixed-fee 90-day pilot boundary.

If a run fails, show the error and stop. Never substitute the authored-fixture demo as a successful real replay.

## 10. Release acceptance and stop rules

Release requires:

- exact archive/model/member hashes, native dtype/shape/count/metadata verification, strict state load, parameter count, finite nonconstant real `[F,80]` and `[F,48]` outputs;
- all frozen runs retained and interaction regressions for `QC-R01`, `QC-R02`, `QC-R02-T2`, and `QC-R03` under the pinned runtime;
- timer scope, model-input branch, event order, prompt sealing, immutable safe-ID mapping, no-output/human/safety policies;
- deterministic display bounds and source causality; no simulator, authored value, canned output, stale asset, or fallback in production;
- claim, payload, no-external, accessibility, responsive, service-template, release-binding, deployment-script, and rollback tests;
- loopback-only rendered/network evidence at every required viewport using the approved isolated browser path.

Stop on any rights contradiction; asset/hash/shape/dtype mismatch; strict-load/output failure; prompt leak; simulation/fabrication; forbidden payload/request/storage/download; browser QA failure; misleading claim; ambiguous service/socket/route ownership; Funnel/public exposure; unproven revision/rollback; or durable artifact outside this repository.

## 11. Private deployment preparation (not authorization to deploy)

The stable contract is Tailnet-only `:8449` to `127.0.0.1:8765`, Funnel disabled. Templates prepare a dedicated non-login `quiet-channel-replay` service owner, immutable versioned release, owner-controlled non-served assets, loopback-only backend, hardened systemd unit, candidate alternate-loopback validation, atomic `current` symlink cutover, and named rollback. Scripts must not mutate Tailscale, other listeners/routes, or another unit.

Preflight stops unless the exact handler, Funnel state, socket owner, clean release identity, asset permissions, and rollback revision are known. Deployment later validates a candidate on an unused loopback port, cuts over only the replay service, verifies loopback and one authorized Tailnet client, compares route/listener snapshots, and restores the prior exact release on any failure. Sanitized evidence contains no credentials, peers/private IPs, prompts, paths, full hashes, payloads, or assets.
