# Quiet Channel real-model bench

> **Truth label:** **SIMULATED SIGNAL + NOISE / REAL MODEL + REAL INFERENCE.** Only the hardware acquisition signal is simulated. Baseline drift, Gaussian sensor noise, 50 Hz pickup and occasional artifacts are injected. Preprocessing, feature extraction, trained weights, neural-network forward pass, CTC decoding, confidence/abstention, confirmation and repair are executable backend code.

This is a separate local experience; it does not replace or modify the authored-fixture concept in [`../demo/`](../demo/). It is not measured accuracy, evidence from physical hardware, participant evidence, a biometric capture system, or a production-performance claim.

## One-command local run

From the repository root, on Python 3.12:

```bash
./realtime/run-local.sh
```

The script creates the project-local `realtime/.venv` when needed, installs pinned CPU dependencies, verifies the committed trained model exists, and starts FastAPI/Uvicorn on **loopback only**. Open <http://127.0.0.1:8765/>. API documentation is local at <http://127.0.0.1:8765/api/docs>.

No microphone, camera, physical EMG device, account or telemetry is used. Do not expose the service beyond loopback. The browser talks only to this local backend.

## What is real

`models/silent_ctc_v1.pt` contains **185,820 learned PyTorch parameters**, not fixture values. It is a checksum-verified `state_dict` loaded into this pipeline:

```text
SignalSource frames: [time, 8 electrodes] at 1 kHz
  → 8 Hz high-pass + fixed calibration normalization
  → MAV / RMS / waveform-length / zero-crossing features (16 sample, hop 8)
  → three stride-2 temporal residual CNN blocks
  → raw/features fusion
  → two-layer Transformer encoder
  → character CTC emissions (28 symbols)
  → CTC free path + grammar-constrained CTC forward scoring
  → uncalibrated decoder score and abstention threshold
  → mandatory human confirmation
  → local output
```

This is a real sequence model, trained with `torch.nn.CTCLoss`, and every run executes its forward pass. The UI's candidates, free CTC path, score and latency come from backend emissions. Application policy names which simulated utterance to generate, but that label is never sent to preprocessing, the model or decoder.

The model is intentionally a fixed, low-consequence 12-command channel. It is not open vocabulary, speaker-independent, an on-device claim or a claim that real EMG works. UI “confidence” is an **uncalibrated decoder score**, not accuracy or a probability of correctness.

## Weight provenance and regeneration

No human, audio, biometric or upstream dataset is included or used. The committed weights were deterministically trained on project-generated multi-channel signals, augmented with the same classes of noise used by `SimulatedSignalSource`. See the byte-bound manifest [`models/silent_ctc_v1.json`](models/silent_ctc_v1.json).

Regenerate from source:

```bash
realtime/.venv/bin/python -m realtime.train --force
```

Training uses no download after dependencies are installed. A rebuilt checkpoint and manifest must be committed together. The synthetic CTC loss in the manifest only documents optimizer execution; it is not measured silent-speech accuracy.

### Why not vendor upstream weights/data?

The primary reference repository's direct-recognition instructions train `recognition_model.py`; they do not publish a compact direct-recognition checkpoint. Its linked Zenodo `6747411` archive is approximately **253 MB**, CC BY 4.0, and contains speech-transduction/vocoder models rather than a drop-in direct recognizer. The linked participant EMG dataset at Zenodo `4064409` is approximately **3.92 GB**, CC BY 4.0. Neither was downloaded, vendored or used. This project therefore takes the task-authorized route: a small but genuine CTC model trained locally on synthetic-yet-representative acquisition data. It supports only this synthetic bench.

## Primary reference and attribution

Architecture follows the raw-EMG residual front end and Transformer/CTC recognition pattern in:

- David Gaddy, [`dgaddy/silent_speech`](https://github.com/dgaddy/silent_speech/tree/a89357c2086609b432919b9d14ffc0be5d8983d5), commit `a89357c2086609b432919b9d14ffc0be5d8983d5`, MIT (copyright David Gaddy, 2021); specifically `architecture.py`, `recognition_model.py`, and `data_utils.py`.
- Gaddy & Klein, “Digital Voicing of Silent Speech,” EMNLP 2020, DOI [10.18653/v1/2020.emnlp-main.445](https://doi.org/10.18653/v1/2020.emnlp-main.445).
- Gaddy & Klein, “An Improved Model for Voicing Silent Speech,” ACL-IJCNLP 2021, DOI [10.18653/v1/2021.acl-short.23](https://doi.org/10.18653/v1/2021.acl-short.23).

The implementation and synthetic weights here are project-authored. See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md). External paper or repository performance does not transfer to this demo.

## Acquisition seam: simulator → reviewed hardware driver

[`app/signal_source.py`](app/signal_source.py) defines `SignalSource.start()`, `frames()` and `stop()`. Both simulated and physical adapters yield the same `SignalFrame` (`float32 [time, channel]`, sample rate, first-sample offset, provenance flag). `InferencePipeline.infer()` accepts only the accumulated numeric signal; it cannot see scenario text.

A physical driver would:

1. implement `SignalSource` using the reviewed vendor SDK, BrainFlow board or LSL inlet;
2. expose exactly eight ordered channels at 1 kHz (or perform reviewed resampling/mapping at the adapter boundary);
3. convert physical units to the calibration convention and preserve contiguous sample/timestamp checks;
4. set `simulated=False`; and
5. be selected by deployment configuration/injection, without changing preprocessing, feature, model, decode or policy code.

That seam is code shape, not hardware readiness. Before any human recording: approve electrical safety, electrode placement, ethics/consent, voluntariness and fallback, calibration, retention/deletion, security/access, withdrawal, labor/jurisdiction and intended-use review. None has occurred.

## Service contract

- `GET /api/health` — loaded model checksum/parameter count and truth boundary.
- `GET /api/scenarios` — scenario metadata without an output fixture.
- `POST /api/sessions` — create an in-memory local capture session.
- `GET /api/sessions/{id}/stream` — NDJSON raw-frame → features → inference → decision events.
- `POST /api/sessions/{id}/stop` — stop acquisition without output.
- `POST /api/sessions/{id}/decision` — confirm/reject a held model candidate; safety acknowledgement is enforced server-side.
- `POST /api/sessions/{id}/repair` — acquire a new, lower-noise simulated frame; all downstream code is unchanged.

Sessions are memory-only and disappear with the process. There is no database, remote call, telemetry or authentication because the service is deliberately loopback-local.

## Validation

After `./realtime/run-local.sh` has installed dependencies (stop it with Ctrl-C before tests):

```bash
realtime/.venv/bin/python -m unittest discover -s realtime/tests -v
python3 realtime/validate.py
python3 tools/validate_project.py
```

The tests cover noise/shape, features, checkpoint integrity, a real forward pass, CTC decode, abstention, repair, confirmation, the safety gate, API contract and visible truth/claim boundaries. Rendered-browser status and the recorded `chrome-devtools-axi` limitation are in [`QA.md`](QA.md).

## Boundaries

No mind reading or inner-speech claim. No identity, authentication, emotion, productivity or health inference. Not medical, AAC, clinical, emergency, payment, access-control or safety automation. No user-data collection, accounts or telemetry. No measured real-world/project accuracy, WER, latency guarantee, transfer, comfort, safety, privacy, calibration or hardware claim. A conventional fallback is required for any future study.
