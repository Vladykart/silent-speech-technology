# Quiet Channel investor real replay

> **Permanent truth:** **Replay of official single-speaker recorded sEMG through David Gaddy’s official released pretrained model; not live capture.**

This private, non-commercial research experience executes one official checksum-bound recording through one official checksum-bound 54,187,136-parameter checkpoint. It exposes real bounded source/preprocessing/output evidence and a mandatory human gate. Operators run in **challenge mode** (prompt sealed until inference and metadata) or **guided mode** (prompt shown for presenter rehearsal before start). It is not a device, live capture, project accuracy/WER, representative evaluation, open-vocabulary/generalization claim, customer/product deployment, or medical/AAC/safety system.

Product authority: [`spec/INVESTOR_REAL_REPLAY_SPEC.md`](spec/INVESTOR_REAL_REPLAY_SPEC.md). Claim authority remains [`../research/claim-boundary.md`](../research/claim-boundary.md) and [`../research/claim-ledger.md`](../research/claim-ledger.md).

## Prepare once, then run offline

Use approved local assets only. Preparation is a separate operator step:

```bash
python3 -m venv realtime/.venv
realtime/.venv/bin/python -m pip install -r realtime/requirements.txt
realtime/.venv/bin/python realtime/fetch_assets.py
```

`fetch_assets.py` defaults to the approved shared lab and makes no network request. `--download-missing` is an explicit preparation-time action on another authorized workstation; it is never called by the service or presentation launcher. It verifies the 3.92 GB archive, model ZIP/checkpoint identities, and all selected/context/metadata members, then atomically prepares only allowlisted `_emg.npy` and selected `_info.json` files under ignored `realtime/local_assets/`. It never extracts audio, cleaned audio, or button arrays.

After preparation:

```bash
./realtime/run-local.sh
```

Open `http://127.0.0.1:8765/`. The launcher binds loopback, disables access logging, and fails closed instead of installing, downloading, simulating, or falling back. Large assets, weights, outputs, browser profiles, and screenshots are never committed.

A private Tailnet-only research demo route exists under owner control; it is **not public and not a product/customer deployment**. This repository task prepares service/deploy/rollback templates only. It does not install, restart, expose, or deploy them. See [`deploy/README.md`](deploy/README.md).

## Exactly what executes

```text
official native float64 [time,8] source at 1 kHz + immediate recorded context
  → 60 Hz notch and harmonics 2–7 → 2 Hz third-order high-pass → exact trim
  ├→ 516.79 Hz / 16-sample window / 6-sample hop / 112 features
  │    inspectable, real preprocessing output; not checkpoint input
  └→ 689.06 Hz / 8-sample offset+alignment / divide 20 / 50*tanh(x/50)
       → explicit float32 model-input conversion
       → 3 residual temporal CNN blocks
       → 6-layer, 768-wide, 8-head relative-position Transformer
       → real [frames,80] normalized predicted mel features
       → real [frames,48] auxiliary phoneme logits
       → project bounded CMUdict/edit-distance algorithm (not another model)
       → abstain or mandatory confirmation; safety acknowledgement where required
       → volatile local result; no actuation
```

The official `.npy` source remains native `float64` through acquisition. Browser traces are deterministic centered/scaled/quantized min/max envelopes—not untouched raw data. Model forward and project decoder timers are measured separately and exclude recording duration, sensing, hardware, network, endpointing, confirmation, and output.

## One model, separate registry

[`model-registry.json`](model-registry.json) contains exactly one `executed` checkpoint: David Gaddy, *Voicing Silent Speech Models*, DOI `10.5281/zenodo.6747411`, CC BY 4.0. `load_state_dict(..., strict=True)` checks every released tensor and the exact parameter count. The 48-class head is part of that checkpoint. It is the **only currently approved, checksum-bound, and executable checkpoint**—an artifact-readiness fact, not a best-model, accuracy, state-of-the-art, transfer, or product claim.

The project decoder is typed `algorithm`, not model. HiFi-GAN, upstream recognition DOI 7183877, DeepSpeech/KenLM, SilentWear, and MONA/LISA are evidence-only. The UI marks each **NOT EXECUTED HERE** and provides no run control. Each row names its pipeline role, modality/channels, task/output, metric family, complete-path readiness gates, and comparability boundary. Papers, architecture cards, datasets, algorithms, vocoders, language models, and authored fixtures are never aggregated into an executed-model count.

## Frozen official sample catalogue

[`sample-manifest.json`](sample-manifest.json) freezes `QC-R01`–`QC-R10` plus repair-only `QC-R02-T2` before the added recordings were executed. Every selected/context/metadata member has its own full private digest. Browser APIs expose only safe IDs and public source facts.

| ID | Split | Duration | Retained pinned-runtime interaction outcome |
|---|---|---:|---|
| QC-R01 | largedev dev | 1.752 s | candidate held for confirmation |
| QC-R02 | closed-vocabulary research set | 2.514 s | abstain; no result |
| QC-R02-T2 | closed-vocabulary research set | 2.736 s | second official take; candidate held |
| QC-R03 | largedev dev | 1.830 s | safety hold; acknowledgement + confirmation |
| QC-R04 | largedev test | 3.210 s | candidate held |
| QC-R05 | largedev test | 2.448 s | candidate held |
| QC-R06 | largedev test | 2.922 s | candidate held |
| QC-R07 | largedev test | 3.108 s | candidate held |
| QC-R08 | largedev test | 1.878 s | abstain; no result |
| QC-R09 | largedev dev | 2.808 s | mismatch + abstain; retained |
| QC-R10 | largedev dev | 2.712 s | abstain; retained |

These are selected behavior regressions, not semantic success requirements or a metric. In guided mode, `POST /api/v1/runs` returns the official prompt only as `prompt_hint` rehearsal metadata before run start. Prompts are never embedded in client assets or passed as per-sample model/decoder input; in challenge mode they appear only in the official audit path after metadata reveal. A future catalogue change requires a new version and selection rationale; weak outcomes cannot be swapped out.

## Protocol-only next sample proof

[`evaluation-protocol.json`](evaluation-protocol.json) defines a future output-blind, deterministic selection and complete-denominator contract. It contains **no results**, selects no new cohort, and grants **no execution authority**. [`app/evaluation_protocol.py`](app/evaluation_protocol.py) tests seeded ranking, disjoint development/evaluation cohorts, prohibited replacement, and retention of executions, abstentions, errors, and asset failures using synthetic IDs only. Training overlap remains unknown, so no cohort is called held out. See the independent [`software expansion review`](../research/software-expansion-review.md).

## Bounded browser evidence

`DisplayPayloadBuilder` is the sole derivative builder:

- source: 8 × ≤256 min/max bins, at least 16 source samples/bin, robust per-channel display scaling, signed 8-bit;
- source/filtered: two independently scaled 8 × ≤128 aligned envelopes;
- features: ≤64 × 112 per-feature normalized signed-8-bit values;
- mel: ≤64 × 80 transformed signed-8-bit model-output values;
- phoneme head: exact top class/token and rounded top softmax diagnostic per bounded frame, plus collapsed path; no full logits;
- decoder: at most three candidates.
- synthetic-noise sandbox: local deterministic preview only; no synthetic signal is replayed or used as official evidence.

The browser receives no participant/session/date identity, source/member/local path, full digest, archive inventory, full arrays/tensors/logits/weights, audio/buttons, download, credential, challenge-mode prompt before inference, telemetry, service worker, persistent storage, or external URL. Guided mode's sole exception is the selected phrase in the explicit pre-run `prompt_hint` rehearsal field. It receives only explicit client files and `/api/v1/...` responses with `no-store` and hardened CSP/Permissions Policy. OpenAPI/docs and old/generic routes are disabled.

Disclosure: **Bounded transformed evidence is sent to this authorized browser; no third-party telemetry, persistence, raw archive, or actuation.** Do not call this “no egress.”

## Versioned API and event order

- `GET /api/v1/health`
- `GET /api/v1/manifest`
- `POST /api/v1/runs`
- `GET /api/v1/runs/{opaque}/events`
- `POST .../stop`, `.../decision`, `.../second-take`

The stream is exactly:

`asset_checks_passed → source_opened → replay_started → source_complete → preprocessing_complete → branches_aligned → model_forward_complete → decoder_complete → metadata_revealed → decision_required`.

Duplicate/out-of-order disclosure fails closed. Runs are bounded, expire, cannot be replayed, and release full active tensors after stream termination. Stop/reject/error/abstain commit no output. Confirmation is mandatory for every accepted result; safety acknowledgement is additional.

## Source and dependency authority

- Data: David Gaddy / UC Berkeley, *Silent Speech EMG v1.0*, version DOI `10.5281/zenodo.4064409` (concept `10.5281/zenodo.4064408`), CC BY 4.0, one-speaker source line.
- Checkpoint: David Gaddy, *Voicing Silent Speech Models*, DOI `10.5281/zenodo.6747411`, CC BY 4.0.
- Adapted code: `dgaddy/silent_speech` commit `a89357c2086609b432919b9d14ffc0be5d8983d5`, MIT.
- `cmudict==1.0.32` Python package: GPL-3.0-or-later. CMU Pronouncing Dictionary data carries a separate CMU redistribution notice. See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md); broader distribution requires a complete dependency review.

Full unserved archive/checkpoint identities are in [`assets-manifest.json`](assets-manifest.json); human-readable provenance is in [`../provenance/realtime-assets.md`](../provenance/realtime-assets.md).

## Validation

```bash
python3 realtime/validate.py
node realtime/tests/client_contract.test.js
realtime/.venv/bin/python -m unittest discover -s realtime/tests -v
python3 tools/validate_project.py
```

The complete project command is in [`../AGENTS.md`](../AGENTS.md). Rendered loopback-only network/accessibility/geometry evidence for 320×568, 375×812, 768×1024, 1024×768, 1366×768, 1920×1080, and 3840×2160 is recorded in [`QA.md`](QA.md). A failed browser harness is a release block, not a static-check waiver.
