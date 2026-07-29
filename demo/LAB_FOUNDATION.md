# Pre-hardware software foundation

The source repository includes a separate standard-library-first `lab/` workspace. It does **not** run in or behind this web demo and does not upgrade the demo’s capabilities.

Foundation scope:

- deterministic eight-channel mock acquisition with timestamps, channel metadata, synthetic session IDs, dropped-sample accounting, and safe shutdown;
- proposed future BrainFlow board abstraction, OpenBCI GUI desktop sanity checks, and Lab Streaming Layer synchronization—none enabled by default;
- parameterized synthetic sEMG filter/rectification/envelope contract, with NumPy/SciPy, NeuroKit2, and MNE as unresolved project-local dependency profiles;
- dry-run shape/mask/split/output contract plus an optional untrained PyTorch CNN/Transformer/CTC-style scaffold smoke test;
- separate dataset/code/model/tool license fields, metadata-only dataset access, explicit download gates, and subject/session leakage rules;
- non-purchasing rig tiers, electrical/human-subject gates, and a staged roadmap whose primary week 9–12 decision is held-out-session evaluation.

No package is installed, device/audio opened, listener started, dataset/model downloaded, cloud account created, SDK accepted, human recorded, or hardware purchased by this foundation. Future TensorFlow Lite Micro, ExecuTorch, Edge Impulse, and GAP9/GAPflow paths are documentation profiles only.

In the full source tree, start at `lab/README.md` and run `python3 lab/validate.py`. The public browser artifact remains static and independent.
