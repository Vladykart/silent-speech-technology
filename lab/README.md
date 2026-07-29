# Pre-hardware lab foundation

This is a **project-local, synthetic-only planning and smoke-test workspace**. It does not make the browser demo hardware-backed. No hardware API, real device, microphone/audio capture, network listener, human recording, dataset, model, checkpoint, package installation, service, or background process runs by default.

## Fast offline checks

```bash
python3 lab/acquisition.py
python3 lab/signal_pipeline.py
python3 lab/model_contract.py
python3 lab/bootstrap_plan.py --doctor
python3 lab/split_rules.py lab/examples/split-manifest.json
python3 lab/validate.py
python3 -m unittest lab/tests/test_lab.py
```

All default paths use only the Python standard library and authored synthetic fixtures. Optional `--with-scipy` and `--with-torch` smoke paths run only against packages already available in the active environment; they do not install or download anything.

## Acquisition contract

[`acquisition.py`](acquisition.py) provides a deterministic eight-channel mock board with monotonic timestamps, channel/unit metadata, synthetic session IDs, explicit dropped-sample accounting, and context-managed safe shutdown. It deliberately exposes only `--mode mock`.

Future adapters may use:

- **BrainFlow** as the proposed hardware-neutral board API. A real adapter must separate prepare/start/read/stop/release, surface board timestamps and dropped packets, and default to no device.
- **Lab Streaming Layer / `pylsl`** as proposed synchronized EMG/reference-audio/event transport. No outlet, inlet, multicast discovery, socket, or listener is implemented here.
- **OpenBCI GUI** only as an operator-installed desktop sanity-check tool for supported boards. It is not a Python/server dependency and must not be installed on a demo host.

Before any real adapter is enabled: name the board, driver and firmware versions; lock channel map/sample rate/gain; bench-test disconnect and shutdown; establish electrical isolation; approve the protocol and consent route; and keep human mode behind an explicit non-default configuration.

## Signal processing contract

[`signal_pipeline.py`](signal_pipeline.py) validates a parameterized filter configuration and exercises rectification/envelope metadata on original synthetic data. If a reviewed project-local NumPy/SciPy environment exists, `--with-scipy` can smoke-test bandpass → notch → rectify → envelope shapes.

The default `20–450 Hz` bandpass and `50 Hz` notch are **planning examples**, not universal truths. Facial sEMG settings depend on sample rate/Nyquist, electrode and front-end response, analog anti-alias filtering, local mains frequency (often 50 Hz in Europe and many other regions), motion, placement, and the approved protocol. Record actual coefficients/config, package versions, channel map, input checksum/provenance, and discarded samples with each run. NeuroKit2 and MNE-Python are candidate higher-level tools, not validated dependencies.

## Model contract

[`model_contract.py`](model_contract.py) defines input/logit/mask shapes, split metadata, CTC blank/vocabulary configuration, abstention metadata, and a confirmation-required output schema. Its optional PyTorch smoke creates an untrained small Conv1D → Transformer → character-logit scaffold to validate dimensions only. It loads no checkpoint, calculates no accuracy, and does not claim compatibility with Gaddy weights or architecture.

The primary reference remains `dgaddy/silent_speech` commit `a89357c2086609b432919b9d14ffc0be5d8983d5` (MIT code; David Gaddy 2021 notice). Code, Gaddy dataset, pretrained-model, dependency, and tool/service licenses are separate. See [`../provenance/upstream-reference.md`](../provenance/upstream-reference.md), [`datasets.json`](datasets.json), and [`../demo/THIRD_PARTY_NOTICES.md`](../demo/THIRD_PARTY_NOTICES.md).

## Environments and future edge profiles

[`software-profiles.json`](software-profiles.json) keeps `core`, `acquisition`, `signal`, `model`, and `edge` groups separate. Version constraints are intentionally unresolved except the Python floor: compatibility has not been checked in a new isolated environment, so fabricating a lockfile would be misleading. [`bootstrap_plan.py`](bootstrap_plan.py) is dry-run/doctor only. A future owner should resolve current compatible releases into `lab/.venv`, retain resolver hashes, review licenses, and commit a real lock—without global pip/Conda, `sudo`, system services, Docker changes, or background processes.

TensorFlow Lite Micro, ExecuTorch, Edge Impulse, and GAP9/GAPflow are future profiles only. Each requires a separately versioned export interface (input shape/dtype/quantization, mask/length handling, vocabulary/blank, numerical tolerance, memory/latency test protocol), toolchain and license review. Do not create cloud accounts, accept terms, install SDKs, or claim export compatibility from this scaffold.

## Data, evaluation, procurement, and study

- [`DATASETS.md`](DATASETS.md) and [`datasets.json`](datasets.json) separate dataset, code, model, and service/tool terms.
- [`dataset_access.py`](dataset_access.py) defaults to metadata-only. It never extracts data and requires multiple explicit gates for the sole checksum-verified public file.
- [`split_rules.py`](split_rules.py) rejects session overlap; held-out-subject mode also rejects subject overlap. Held-out-session evaluation is the primary gate; global cross-validation alone is insufficient.
- [`PLAN.md`](PLAN.md) provides non-purchasing equipment tiers, human/electrical gates, and the week 1–2 / 3–4 / 5–8 / 9–12 / 13+ evidence sequence.

Data, models, environments, captures, and outputs belong under gitignored `lab/data/`, `lab/models/`, `lab/.venv/`, and `lab/runs/`. Never commit audio, EMG/biometric data, checkpoints, credentials, access tokens, or package caches.
