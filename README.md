# Silent Speech Technology — evidence-gated concept release

An evidence-gated research package, a deployment-ready offline concept demo, a separate local real-model bench, a pre-hardware lab foundation, and professional decision decks.

> **Claim boundary:** No silent-speech device, live sensor capture, newly collected participant data, measured project accuracy, customer, deployment, or medical/AAC product is present. The locked [`demo/`](demo/) remains a deterministic **CONCEPT / SIMULATED PIPELINE** with authored fixtures. Separately, [`realtime/`](realtime/) replays official single-speaker recorded sEMG through source-faithful preprocessing and David Gaddy's official released 54M-parameter model. That is real research-data/model execution—not live hardware or project performance.

## Quick start

### Real released backend + real recorded-data replay

```bash
./realtime/run-local.sh
```

Open `http://127.0.0.1:8765/`. The first run creates `realtime/.venv`, verifies the official assets from the captain-provided shared lab (or fetches missing Zenodo files into ignored local storage), and binds to loopback only. No checkpoint or recorded sample is committed. See [`realtime/README.md`](realtime/README.md) for sizes, licenses, architecture, hardware seam and tests.

### Static concept and decks

```bash
python3 tools/validate_project.py
python3 demo/generate_manifest.py
python3 demo/validate.py && node demo/tests/core.test.js
python3 lab/validate.py && python3 -m unittest lab/tests/test_lab.py
python3 pitch/validate.py
python3 pitch/validate_pptx.py
python3 pitch/validate_4_slide_pptx.py
python3 -m http.server 8000 --bind 127.0.0.1
```

Open:

- locked authored-fixture demo: `http://127.0.0.1:8000/demo/`
- HTML deck: `http://127.0.0.1:8000/pitch/`
- editable 13-slide evidence deck: [`pitch/quiet-channel-evidence-deck.pptx`](pitch/quiet-channel-evidence-deck.pptx)
- editable four-slide executive deck: [`pitch/quiet-channel-4-slide-deck.pptx`](pitch/quiet-channel-4-slide-deck.pptx)

Direct `file://` use also works. Keep [`demo/PRESENTER.md`](demo/PRESENTER.md) open as the 3–5 minute operator script. The development server is loopback rehearsal only; a separately authorized preview must follow [`demo/DEPLOYMENT.md`](demo/DEPLOYMENT.md), verify [`demo/artifact-manifest.json`](demo/artifact-manifest.json), and preserve the temporary/no-index boundary.

## Current decision status

- **Beachhead:** e& frontline retail advisors and field technicians; Stage 0 selects one low-consequence workflow.
- **Lead path:** **AED 1,000,000 fixed-fee 90-day pilot**, then annual per-seat deployment at `TBD` pricing only if evidence gates pass.
- **Strategic upside:** unpriced e& funding/negotiated ownership of resulting foreground IP and a governed Gulf bilingual dataset, preserving acquisition/exit optionality. This is not a promised return.
- **Unknown:** workflow, cohort, thresholds, hardware, team, owners, allocations, annual price, strategic funding, IP/data terms, market and all project performance.

Authority and boundaries: [`provenance/decisions.md`](provenance/decisions.md), [`research/claim-ledger.md`](research/claim-ledger.md).

## Project map

- [`demo/`](demo/) — locked authored-fixture/no-model recognition console with clear, abstention/repair, and safety-sensitive confirmation scenarios; runbook, deployment controls, SHA-256 manifest, tests and validator.
- [`lab/`](lab/) — default-safe mock acquisition, synthetic signal/model contracts, dependency planner, dataset/license registry, leakage validator, non-purchasing rig guide, and evidence-gated roadmap; no installs, hardware, capture, or downloads by default.
- [`realtime/`](realtime/) — separate loopback FastAPI service and client: official CC BY 4.0 recorded sEMG replay, source-faithful preprocessing, official 54,187,136-parameter residual/relative-Transformer weights, trained phoneme decoding, abstention, second-take repair, confirmation, tests and a physical-driver seam. Large assets are fetched locally and never committed.
- [`pitch/`](pitch/) — matched 13-slide HTML/PPTX evidence deck plus a source-driven four-slide executive PPTX, notes, original SVGs, representative geometry QA and validators.
- [`research/`](research/) — landscape, evidence matrix, definitions, metrics, competitors, references, critical scout reconciliation and claim boundaries.
- [`provenance/`](provenance/) — captain-source retrieval/checksum, decision authority, and media-rights catalogue.
- [`tools/validate_project.py`](tools/validate_project.py) — local links, release invariants, media catalogue and secret guard.

## Primary demo lineage, correctly bounded

The demo’s explanatory path is inspired by David Gaddy’s `dgaddy/silent_speech` at exact commit `a89357c2086609b432919b9d14ffc0be5d8983d5`; the exact files, MIT notice, prerequisites, and non-transfer boundary are recorded in [`provenance/upstream-reference.md`](provenance/upstream-reference.md). No upstream code, model, data, sample, or output runs in the demo. The upstream README’s approximate 36% open-vocabulary WER is a historical upstream result, not this project’s performance.

## Evidence headline, correctly bounded

SilentWear v2 (arXiv preprint, 2026) reports n=4, 14 differential neck sEMG channels and eight commands plus rest: average silent top-1 accuracy **77.5±6.6%** in global cross-validation and **59.3±2.2%** with a held-out session. Its 2.47 ms figure is **model inference**, not complete latency. Those are external preprint results—not this project’s expectation. See [`research/evidence-matrix.md`](research/evidence-matrix.md).

## Quality status

Static HTML/SVG/OOXML parsing, JavaScript syntax, deterministic fixtures, lab contracts/registries and PPTX rebuild, local references, claim decisions, source records and offline dependency guards are validated without installs. With official local assets present, the replay bench adds checksum/right checks, untouched-recording replay, upstream preprocessing, strict checkpoint load, real mel/phoneme forward output and API/policy tests; selected single-speaker replays are not measured project accuracy. The four-slide deck also passed representative 1920×1080 headless-Chromium geometry review from the same layout scene graph. This is not exact PowerPoint rendering: target-application opening plus desktop/narrow/print visual rehearsal remain gates before external circulation.

This private local repository carries no general third-party or external-publication permission. See [`provenance/media-catalogue.md`](provenance/media-catalogue.md).
