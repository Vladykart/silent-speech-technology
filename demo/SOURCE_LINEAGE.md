# Public source-lineage summary

Primary technical reference: David Gaddy’s [`dgaddy/silent_speech`](https://github.com/dgaddy/silent_speech), exact commit [`a89357c2086609b432919b9d14ffc0be5d8983d5`](https://github.com/dgaddy/silent_speech/tree/a89357c2086609b432919b9d14ffc0be5d8983d5), inspected 2026-07-29 through read-only GitHub API calls.

Exact-commit files consulted: `README.md` (blob `17e98c3a8ef6c09e06bd199d69d0680cc1f9c0e3`), `recognition_model.py` (`81c03527257f31d4e417055d32646388b30e0214`), `read_emg.py` (`c0a9ce99213ca6510ff835754c9d08cdfc12fb93`), `architecture.py` (`1aaf36e335efb7822def5158890b64a1924fd9dc`), `environment.yml` (`1d54660e4939d3c9de1901b42bf5df92ce55e8b9`), `LICENSE` (`02fde9d37f394f0d5e0368e406df7375a7576002`), plus repository/tree/commit metadata.

The upstream research path informed the explanatory order: multi-channel facial EMG → signal preprocessing/features → convolutional/Transformer sequence model → character CTC beam decoding/language model → WER evaluation. The demo uses original synthetic fixtures and UI code; it does not run or reproduce that path.

The upstream README reports approximately 36% WER in its historical ASR-based open-vocabulary evaluation. That result is upstream-only, not independently reproduced, not a project expectation, and not related to demo scores.

No upstream clone, submodule, package, code, data, checkpoint, model, audio, EMG/biometric sample, screenshot, figure, logo, or paper was downloaded or bundled. The MIT David Gaddy 2021 notice is preserved in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md). The repository’s fuller inspection authority is `provenance/upstream-reference.md`.
