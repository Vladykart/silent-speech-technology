# `dgaddy/silent_speech` upstream inspection record

**Access:** 2026-07-29 UTC, read-only GitHub API through `gh-axi`  
**Repository:** <https://github.com/dgaddy/silent_speech>  
**Default branch reported:** `main`  
**Exact inspected commit:** [`a89357c2086609b432919b9d14ffc0be5d8983d5`](https://github.com/dgaddy/silent_speech/tree/a89357c2086609b432919b9d14ffc0be5d8983d5)  
**Commit metadata:** David Gaddy, 2023-12-11T01:01:14Z, “More version updates and cleanup.”  
**Repository license metadata:** MIT

## Exact material consulted

The GitHub repository, commit, tree, content, and code-search APIs were used. The repository was not cloned. The following exact-commit files and blobs were consulted:

| Path | Blob SHA | Why consulted |
|---|---|---|
| [`README.md`](https://github.com/dgaddy/silent_speech/blob/a89357c2086609b432919b9d14ffc0be5d8983d5/README.md) | `17e98c3a8ef6c09e06bd199d69d0680cc1f9c0e3` | Recognition instructions, data/model/toolchain prerequisites, papers, and reported historical result |
| [`recognition_model.py`](https://github.com/dgaddy/silent_speech/blob/a89357c2086609b432919b9d14ffc0be5d8983d5/recognition_model.py) | `81c03527257f31d4e417055d32646388b30e0214` | Character outputs, CTC loss, beam decoder/language-model path, WER evaluation, and training entry point |
| [`read_emg.py`](https://github.com/dgaddy/silent_speech/blob/a89357c2086609b432919b9d14ffc0be5d8983d5/read_emg.py) | `c0a9ce99213ca6510ff835754c9d08cdfc12fb93` | Multi-channel EMG loading, filtering, resampling, feature extraction, paired audio/alignment and dataset expectations |
| [`architecture.py`](https://github.com/dgaddy/silent_speech/blob/a89357c2086609b432919b9d14ffc0be5d8983d5/architecture.py) | `1aaf36e335efb7822def5158890b64a1924fd9dc` | Eight-channel raw input, residual convolution stack, Transformer sequence encoder, and output projection |
| [`environment.yml`](https://github.com/dgaddy/silent_speech/blob/a89357c2086609b432919b9d14ffc0be5d8983d5/environment.yml) | `1d54660e4939d3c9de1901b42bf5df92ce55e8b9` | Python 3.9, PyTorch 2.0/CUDA 11.8, audio/signal packages and legacy recognition dependencies |
| [`LICENSE`](https://github.com/dgaddy/silent_speech/blob/a89357c2086609b432919b9d14ffc0be5d8983d5/LICENSE) | `02fde9d37f394f0d5e0368e406df7375a7576002` | MIT terms and David Gaddy 2021 notice |

The exact commit endpoint and root tree were also consulted. GitHub reported tree `a6de72dfd7d0ea46bace82e836317fd38eb5fc29`, parent `cd96f46c9a9fbd06dd8f916b04bcfdd606bd81df`, and separate `hifi_gan` and `text_alignments` gitlink/submodule entries. API rate limiting ended the optional follow-up searches; no technical statement in the demo depends on those incomplete follow-ups.

## Accepted technical lineage

At this revision, the upstream research path expects recorded facial EMG and associated external assets. `read_emg.py` loads array files, applies notch/high-pass processing and resampling, obtains EMG features, and aligns lengths with audio-derived features. `architecture.py` begins its raw path with eight channels, uses three residual 1D-convolution blocks followed by a Transformer encoder, and projects sequence states to outputs. `recognition_model.py` applies character-level CTC training and a CTC beam decoder configured with a KenLM file, then calculates WER.

The demo’s labels—eight synthetic channels, filter/window, sequence encoder, CTC-style candidates—are a high-level explanatory analogy only. The demo implementation and fixture values are original and deterministic. No upstream function, model architecture implementation, parameter, trained output, signal, or evaluation code is running.

## External result and non-transfer boundary

The exact-commit README reports approximately **36% WER** on an ASR-based open-vocabulary evaluation for the upstream latest model. This is an upstream historical research result. It is not reproduced, independently verified, transferred to this project, converted to accuracy, or used as a demo score. The demo’s `0.84`, `0.54`, `0.91`, `0.72`, and timing values are authored interaction fixtures only.

## Upstream requirements outside the approved replay path

Upstream instructions point to external EMG/audio data, pretrained models, phoneme-alignment and HiFi-GAN submodules, DeepSpeech/KenLM assets, `ctcdecode`, and a Python/PyTorch/CUDA/audio toolchain. The separately governed replay approves only the checksum-bound transduction checkpoint and selected official sEMG records documented in [`realtime-assets.md`](realtime-assets.md); HiFi-GAN, DeepSpeech/KenLM, audio, and the remaining legacy path are not executed. A responsible physical system would additionally require consented capture hardware and placement protocol, governance, calibration, participant/session splits, failure analysis, complete-latency measurement, and safety review; those capabilities are absent.

## Rights and retention

GitHub and the exact file report MIT. The upstream notice—`Copyright (c) 2021 David Gaddy`—is preserved in [`../demo/THIRD_PARTY_NOTICES.md`](../demo/THIRD_PARTY_NOTICES.md) and surfaced in the demo. The upstream repository, submodules, dependencies, paper PDFs, audio, screenshots, logos, figures, and media were not downloaded or committed. Approved model/data assets are fetched only into ignored local storage under [`realtime-assets.md`](realtime-assets.md); they are not committed or redistributed.
