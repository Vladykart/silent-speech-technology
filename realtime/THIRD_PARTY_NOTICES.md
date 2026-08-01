# Third-party notices and attribution

This local non-commercial research demonstration uses official third-party research assets fetched outside git. Do not remove attribution or redistribute downloaded assets from this repository.

## dgaddy/silent_speech code

Reference: <https://github.com/dgaddy/silent_speech/tree/a89357c2086609b432919b9d14ffc0be5d8983d5>

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

`app/model.py`, `app/upstream_transformer.py`, and `app/preprocessing.py` adapt the exact layer/state layout and algorithms in upstream `architecture.py`, `transformer.py`, `read_emg.py`, and `data_utils.py`. The custom Transformer also notes its upstream fairseq/PyTorch derivation. No upstream repository clone is committed.

## Voicing Silent Speech Models

- Creator: **David Gaddy**
- Title: **Voicing Silent Speech Models**
- Official record/DOI: <https://doi.org/10.5281/zenodo.6747411>
- Deposit license: **Creative Commons Attribution 4.0 International (CC BY 4.0)**, <https://creativecommons.org/licenses/by/4.0/>
- Used file: released `pretrained_models/transduction_model.pt`, fetched and checksum-verified outside git.

The checkpoint is not redistributed in this repository. The UI and documentation provide creator/title/source/license attribution. Changes: the checkpoint is loaded unchanged into a modern PyTorch 2.5 adapter matching its original architecture. Legacy speech-synthesis/DeepSpeech text evaluation is not run; the released phoneme head is decoded directly as documented.

## Silent Speech EMG v1.0

- Creator: **David Gaddy, UC Berkeley**
- Title: **Silent Speech EMG**
- Version DOI: <https://doi.org/10.5281/zenodo.4064409>
- Concept DOI: <https://doi.org/10.5281/zenodo.4064408>
- Deposit license: **CC BY 4.0**
- Description at source: facial electromyography recordings during silent and vocalized speech; one research speaker in this source line.

Only selected silent-speech EMG arrays, their immediate recorded filter context and JSON prompt metadata are extracted locally. No audio is extracted, served or committed. Changes: arrays are replayed in chunks and processed through a source-faithful modern NumPy/SciPy implementation; raw sample values are not altered by acquisition replay.

## CMU Pronouncing Dictionary

The pinned `cmudict` Python package supplies pronunciations to the modern bounded phoneme decoder. CMUdict is distributed under a permissive 3-clause BSD-style license; package notice/source: <https://github.com/cmusphinx/cmudict>.

## Runtime dependencies

PyTorch, NumPy, SciPy, FastAPI, Uvicorn, HTTPX and their transitive dependencies retain their own licenses. They install into ignored `realtime/.venv` and are not vendored here. See pinned versions in `requirements.txt`.

## Project-use boundary

The captain has authorized these assets for a **non-commercial, local research demonstration only**. That internal limit does not replace or narrow the text of the upstream MIT or CC BY 4.0 licenses. There is no live capture, public asset serving, accuracy transfer, endorsement, medical/AAC use or identity/emotion use.
