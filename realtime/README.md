# Quiet Channel real recorded-sEMG replay

> **Truth label:** **REPLAY OF REAL RECORDED sEMG THROUGH THE REAL RELEASED PRETRAINED MODEL — NOT LIVE CAPTURE.** The default path uses official single-speaker research recordings and David Gaddy's official 54M-parameter checkpoint. No synthetic sample or synthetic-trained model is selected.

This is a separate, local, **non-commercial research demonstration**. It does not modify the locked authored-fixture experience in [`../demo/`](../demo/). It is not measured project accuracy, live hardware, a new participant recording, identity/emotion inference, or medical/AAC/product evidence.

## One-command run with official assets

The captain-provided shared lab at `/root/.local/share/silent-speech-lab/` already contains the 3.92 GB dataset. This worktree's ignored `realtime/local_assets/` contains/links the released checkpoint and only the selected replay arrays. From the repository root:

```bash
./realtime/run-local.sh
```

Open <http://127.0.0.1:8765/>. The service binds to loopback only. It creates `realtime/.venv` if needed and calls [`fetch_assets.py`](fetch_assets.py) only when local assets are not prepared. Existing shared assets are used first; on another workstation `--download-missing` retrieves only the official Zenodo files into the ignored local directory.

No microphone, camera, device or live EMG capture is requested. There is no account, telemetry, upload or database. Do not expose the service beyond loopback.

## Official asset preparation

To explicitly locate, checksum and prepare assets without starting the service:

```bash
realtime/.venv/bin/python realtime/fetch_assets.py
```

The default command makes **no network request** when the shared lab assets are present. On a machine without them:

```bash
realtime/.venv/bin/python realtime/fetch_assets.py --download-missing
```

Downloaded archives, the 207 MB checkpoint and extracted `.npy` replays remain under git-ignored `realtime/local_assets/`. The script extracts only each selected recording, its immediate filter context and metadata—never audio. **Do not commit or redistribute those assets from this repository.** Exact machine-readable provenance is in [`assets-manifest.json`](assets-manifest.json).

| Artifact | Official record and rights | Verified file |
|---|---|---|
| Voicing Silent Speech Models | David Gaddy; [Zenodo 6747411](https://doi.org/10.5281/zenodo.6747411); CC BY 4.0 | `pretrained_models.zip`, 253,447,725 bytes, MD5 `2e172d2ff74126ca0e68d0f117d6466a`; extracted `transduction_model.pt`, 216,859,418 bytes, SHA-256 `67d40b64f7831ae15c3c24264e2d13cdff98a212953901048d2923b3db60171a` |
| Silent Speech EMG v1.0 | David Gaddy, UC Berkeley; version [Zenodo 4064409](https://doi.org/10.5281/zenodo.4064409), concept DOI [4064408](https://doi.org/10.5281/zenodo.4064408); CC BY 4.0 | `emg_data.tar.gz`, 3,919,507,637 bytes, MD5 `7f97d2182b896652999b1b2d0c69fd7b`, SHA-256 `1a4b205195185d2972923ed4fdaa71bb51cc01462c6b1ab279ed4d00acbd0089` |

CC BY 4.0 is the deposit license recorded at each official record. Attribution is mandatory. The captain has limited this experience to non-commercial local research demonstration; that project-use boundary is not a reinterpretation of the CC license.

## What executes

```text
Official 1 kHz recorded array [time, 8 facial/neck-region sEMG channels]
  → upstream 60 Hz notch + seven harmonics
  → upstream 2 Hz high-pass
  → upstream 689.06 Hz raw branch + tanh compression
  → upstream 516.79 Hz / 112-value feature extraction (inspectable)
  → released 3-block residual temporal CNN
  → released 6-layer, 768-wide relative-position Transformer
  → released 80-bin mel head + released 48-class phoneme head
  → free phoneme path
  → modern CMUdict bounded phoneme-edit decoder
  → uncalibrated score / abstention
  → mandatory human confirmation
  → local-only staged output
```

The checkpoint has **54,187,136 trainable parameters**. `load_state_dict(..., strict=True)` matches every released tensor, including custom relative-position attention. Each replay performs the real forward pass and exposes measured local software latency for that run only.

The upstream `architecture.py` accepts explicit EMG features but its released forward path uses the identically preprocessed raw branch. This implementation still computes the source's 112 features for inspection and labels that architecture fact. Numeric chunk lengths in official JSON reproduce upstream EMG/mel frame alignment without extracting audio; prompt text remains outside inference. It does not invent placeholder model inputs.

### Decoder adaptation

The original repository's text evaluation synthesizes speech and invokes legacy DeepSpeech 0.7. The DeepSpeech binary is not available for Python 3.12. We do **not** replace it with a synthetic model. Instead, the modern adapter decodes the released checkpoint's real trained 48-class phoneme emissions directly:

1. collapse the free framewise phoneme path;
2. obtain pronunciations from pinned open-source CMUdict;
3. compute phoneme edit distance against a bounded grammar of prompts that actually occur in the official dataset;
4. abstain when free-path agreement is below `0.60`.

Candidate score and threshold are local, uncalibrated diagnostics—not accuracy or a probability of correctness. The record's reference prompt is read from official metadata and revealed only **after** inference; it is never passed to model or decoder.

## Three real-recording paths

- **Held-out research replay:** real silent-sEMG record `silent_parallel_data/5-6_silent/314`, metadata prompt “What news?”, source `testset_largedev.json` development split; candidate is held for confirmation.
- **Abstain + repair:** real record `closed_vocab/silent/5-19_silent/379` falls below the phoneme agreement threshold. Repair replays second real take `310` of the same `09:48 AM` metadata prompt; no noise or signal is manufactured.
- **Safety-sensitive:** real silent-sEMG record `silent_parallel_data/5-5_silent/91`, metadata prompt “Keep back!”, development split; server requires explicit acknowledgement. No actuation is connected.

These selected paths demonstrate interaction behavior, not an accuracy estimate. They are not a representative evaluation and must not be counted as project WER, command accuracy or validation.

## Primary code reference

The released architecture and preprocessing adapter follow:

- David Gaddy, [`dgaddy/silent_speech`](https://github.com/dgaddy/silent_speech/tree/a89357c2086609b432919b9d14ffc0be5d8983d5), commit `a89357c2086609b432919b9d14ffc0be5d8983d5`, MIT; specifically `architecture.py`, `transformer.py`, `read_emg.py`, `data_utils.py`, and `transduction_model.py`.
- Gaddy & Klein, “Digital Voicing of Silent Speech,” EMNLP 2020, DOI [10.18653/v1/2020.emnlp-main.445](https://doi.org/10.18653/v1/2020.emnlp-main.445).
- Gaddy & Klein, “An Improved Model for Voicing Silent Speech,” ACL-IJCNLP 2021, DOI [10.18653/v1/2021.acl-short.23](https://doi.org/10.18653/v1/2021.acl-short.23).

MIT and CC BY 4.0 notices are in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md). External paper/repository results do not become project results.

## Acquisition seam

[`app/signal_source.py`](app/signal_source.py) defines `SignalSource.start()`, `frames()` and `stop()`:

- `RecordedEMGReplaySource` is the default. It yields untouched official `float32 [time, 8]` arrays at 1 kHz and supplies neighboring recorded context only to prevent filter-edge artifacts.
- `RealHardwareSignalSource` is the unimplemented reviewed-device seam. A future driver must map units/channels/timestamps to the same contract; preprocessing/model/decoder code remains unchanged.
- `SimulatedSignalSource` remains an explicit acquisition-only fallback for hardware plumbing, as directed, but no default scenario or service path instantiates it and it supports no model/performance claim.

A real device requires electrical-safety, placement, calibration, consent/ethics, retention/deletion, security, withdrawal, labor/jurisdiction and intended-use review. None is present.

## API

- `GET /api/health` — official checkpoint checksum/parameter count, dataset DOI/license and truth boundary.
- `GET /api/scenarios` — replay/split metadata without reference prompt leakage.
- `POST /api/sessions` — in-memory replay session.
- `GET /api/sessions/{id}/stream` — NDJSON recorded-frame → features → real inference → post-inference metadata → decision events.
- `POST /api/sessions/{id}/stop` — stop without output.
- `POST /api/sessions/{id}/decision` — confirm/reject; safety acknowledgement enforced server-side.
- `POST /api/sessions/{id}/repair` — replay a second real recording; downstream code unchanged.

## Validation

```bash
python3 realtime/validate.py
realtime/.venv/bin/python -m unittest discover -s realtime/tests -v
python3 tools/validate_project.py
```

Tests verify official hashes/rights metadata, untouched recording replay, upstream preprocessing shapes, strict checkpoint loading, a real forward pass and mel/phoneme outputs, recorded abstention/second-take repair/safety policy, API ordering, confirmation and visible boundaries. Asset-dependent tests skip with an explicit fetch instruction if official files are absent.

Rendered-browser status is in [`QA.md`](QA.md).

## Boundaries

Replay of existing, consented-for-release single-speaker research data is still sensitive and placement/session specific. No live capture or new collection occurs. No mind reading/inner speech, identity, authentication, emotion, productivity or health inference. Not medical, AAC, clinical, emergency, payment, access-control or safety automation. No measured project accuracy/WER, transfer, comfort, power, calibration, privacy, hardware or end-to-end product-latency claim. A conventional fallback remains required for future work.
