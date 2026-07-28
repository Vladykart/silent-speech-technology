# Silent Speech Technology — first local release

An evidence-gated research package, offline concept demo, and professional 13-slide decision deck for a tomorrow demonstration.

> **Claim boundary:** This repository does **not** contain a silent-speech device, sensor capture, model, biometric data, measured project accuracy, customer, deployment, or medical/AAC product. The demo is a deterministic **CONCEPT / SIMULATED PIPELINE** using authored fixtures.

## Tomorrow quick start

From this repository:

```bash
python3 tools/validate_project.py
python3 demo/validate.py && node demo/tests/core.test.js
python3 pitch/validate.py
python3 pitch/validate_pptx.py
python3 pitch/validate_4_slide_pptx.py
python3 -m http.server 8000 --bind 127.0.0.1
```

Open:

- demo: `http://127.0.0.1:8000/demo/`
- HTML deck: `http://127.0.0.1:8000/pitch/`
- editable 13-slide evidence deck: [`pitch/quiet-channel-evidence-deck.pptx`](pitch/quiet-channel-evidence-deck.pptx)
- editable four-slide executive deck: [`pitch/quiet-channel-4-slide-deck.pptx`](pitch/quiet-channel-4-slide-deck.pptx)

Direct `file://` use also works. Keep [`demo/PRESENTER.md`](demo/PRESENTER.md) open as the 3–5 minute operator script. Do not expose the static server beyond loopback.

## Current decision status

- **Beachhead:** e& frontline retail advisors and field technicians; Stage 0 selects one low-consequence workflow.
- **Lead path:** **AED 1,000,000 fixed-fee 90-day pilot**, then annual per-seat deployment at `TBD` pricing only if evidence gates pass.
- **Strategic upside:** unpriced e& funding/negotiated ownership of resulting foreground IP and a governed Gulf bilingual dataset, preserving acquisition/exit optionality. This is not a promised return.
- **Unknown:** workflow, cohort, thresholds, hardware, team, owners, allocations, annual price, strategic funding, IP/data terms, market and all project performance.

Authority and boundaries: [`provenance/decisions.md`](provenance/decisions.md), [`research/claim-ledger.md`](research/claim-ledger.md).

## Project map

- [`demo/`](demo/) — locked, failure-and-repair offline interaction; runbook, script, deterministic test and validator.
- [`pitch/`](pitch/) — matched 13-slide HTML/PPTX evidence deck plus a source-driven four-slide executive PPTX, notes, original SVGs, representative geometry QA and validators.
- [`research/`](research/) — landscape, evidence matrix, definitions, metrics, competitors, references, critical scout reconciliation and claim boundaries.
- [`provenance/`](provenance/) — captain-source retrieval/checksum, decision authority, and media-rights catalogue.
- [`tools/validate_project.py`](tools/validate_project.py) — local links, release invariants, media catalogue and secret guard.

## Evidence headline, correctly bounded

SilentWear v2 (arXiv preprint, 2026) reports n=4, 14 differential neck sEMG channels and eight commands plus rest: average silent top-1 accuracy **77.5±6.6%** in global cross-validation and **59.3±2.2%** with a held-out session. Its 2.47 ms figure is **model inference**, not complete latency. Those are external preprint results—not this project’s expectation. See [`research/evidence-matrix.md`](research/evidence-matrix.md).

## Quality status

Static HTML/SVG/OOXML parsing, JavaScript syntax, deterministic fixtures and PPTX rebuild, local references, claim decisions, source records and offline dependency guards are validated without installs. The four-slide deck also passed representative 1920×1080 headless-Chromium geometry review from the same layout scene graph. This is not exact PowerPoint rendering: target-application opening plus desktop/narrow/print visual rehearsal remain gates before external circulation. No site is deployed.

This private local repository carries no general third-party or external-publication permission. See [`provenance/media-catalogue.md`](provenance/media-catalogue.md).
