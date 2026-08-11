# Third-party notices and attribution

This private non-commercial research demonstration references or executes third-party artifacts fetched into ignored owner-controlled storage. No model, recording, paper, figure, logo, font, screenshot, audio, or video is redistributed in git. Attribution does not imply endorsement or project ownership. A complete distribution/dependency review is required before broader delivery.

## dgaddy/silent_speech adapted code — MIT

Source: `github.com/dgaddy/silent_speech`, exact commit `a89357c2086609b432919b9d14ffc0be5d8983d5`.

```text
MIT License

Copyright (c) 2021 David Gaddy

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

`app/model.py`, `app/upstream_transformer.py`, and `app/preprocessing.py` adapt the state layout and algorithms in upstream `architecture.py`, `transformer.py`, `read_emg.py`, and `data_utils.py`. Changes: modern pinned NumPy/SciPy/PyTorch implementation, explicit source/model dtype provenance, bounded browser derivatives, and direct inspection/decoding of the released phoneme head. No upstream clone is committed.

## Voicing Silent Speech Models — CC BY 4.0 deposit

- Creator: David Gaddy
- Title: *Voicing Silent Speech Models*
- DOI: `10.5281/zenodo.6747411`
- Deposit license: Creative Commons Attribution 4.0 International (CC BY 4.0)
- Executed member: `pretrained_models/transduction_model.pt`, checksum-verified outside git

The checkpoint is not redistributed or downloadable. Its state tensors strict-load unchanged into the adapted architecture. Legacy synthesis/DeepSpeech evaluation and the archived HiFi-GAN artifact are **not executed here**. The UI attributes creator/title/DOI/license and labels modifications. CC BY 4.0 requires attribution and change indication and does not imply endorsement.

## Silent Speech EMG v1.0 — CC BY 4.0 deposit

- Creator: David Gaddy, UC Berkeley
- Title: *Silent Speech EMG*
- Version DOI: `10.5281/zenodo.4064409`; concept DOI: `10.5281/zenodo.4064408`
- Deposit license: CC BY 4.0
- Source scope: single-speaker facial-EMG research line

Only 11 selected silent-speech EMG arrays, their immediate recorded filter context, and selected JSON metadata are prepared locally. No audio, cleaned audio, or button array is extracted, served, or committed. Changes: native `float64` arrays are replayed read-only, context-filtered, resampled, converted at a documented runtime boundary, and transformed/quantized into bounded non-downloadable browser evidence. Public licensing does not itself resolve human-subject, privacy, patent, endorsement, intended-use, or redistribution questions; the project applies a stricter private-demo boundary.

## `cmudict==1.0.32` Python package — GPL-3.0-or-later

The installed package metadata and packaged top-level `LICENSE` identify the **Python package/distribution** as **GPL-3.0-or-later**. It supplies the runtime wrapper used by the project bounded pronunciation/edit-distance algorithm. It must not be described as a permissive-only package. Broader distribution requires review of GPL obligations and all transitive dependencies.

## CMU Pronouncing Dictionary data — separate CMU notice

The packaged `cmudict/data/LICENSE` applies separately to the **dictionary data** and permits redistribution/use in source and binary forms subject to retaining its copyright, conditions, acknowledgements, and disclaimer. It begins:

```text
Copyright (C) 1993-2015 Carnegie Mellon University. All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the stated conditions are met.
```

Do not conflate this data notice with the GPL-3.0-or-later Python package metadata. The repository does not vendor either package or dictionary payload.

## Runtime dependencies

Pinned PyTorch, NumPy, SciPy, FastAPI, Uvicorn, HTTPX, and their transitive dependencies retain their own terms. They are installed only under ignored `realtime/.venv`; [`requirements.txt`](requirements.txt) is a version lock, not a complete license conclusion.

## Project-use boundary

The captain has authorized this path for a **private, non-commercial research demonstration**. That internal boundary does not rewrite MIT, CC BY 4.0, GPL, CMU data terms, or transitive licenses. There is no public asset serving, live capture, project accuracy transfer, medical/AAC use, identity/emotion use, or endorsement.
