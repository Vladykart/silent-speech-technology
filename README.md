# Silent Speech Technology — evidence-gated concept release

An evidence-gated research package, deployment-ready static recognition interaction demo, and professional decision deck.

> **Claim boundary:** This repository does **not** contain a silent-speech device, sensor capture, model, biometric data, measured project accuracy, customer, deployment, or medical/AAC product. The demo is a deterministic **CONCEPT / SIMULATED PIPELINE** using authored fixtures.

## Tomorrow quick start

From this repository:

```bash
python3 tools/validate_project.py
python3 demo/generate_manifest.py
python3 demo/validate.py && node demo/tests/core.test.js
python3 lab/validate.py && python3 -m unittest lab/tests/test_lab.py
python3 pitch/validate.py
python3 pitch/validate_pptx.py
python3 -m http.server 8000 --bind 127.0.0.1
```

Open:

- demo: `http://127.0.0.1:8000/demo/`
- HTML deck: `http://127.0.0.1:8000/pitch/`
- editable deck: [`pitch/quiet-channel-evidence-deck.pptx`](pitch/quiet-channel-evidence-deck.pptx)

Direct `file://` use also works. Keep [`demo/PRESENTER.md`](demo/PRESENTER.md) open as the 3–5 minute operator script. The development server is loopback rehearsal only; a separately authorized preview must follow [`demo/DEPLOYMENT.md`](demo/DEPLOYMENT.md), verify [`demo/artifact-manifest.json`](demo/artifact-manifest.json), and preserve the temporary/no-index boundary.

## Current decision status

- **Beachhead:** e& frontline retail advisors and field technicians; Stage 0 selects one low-consequence workflow.
- **Lead path:** **AED 1,000,000 fixed-fee 90-day pilot**, then annual per-seat deployment at `TBD` pricing only if evidence gates pass.
- **Strategic upside:** unpriced e& funding/negotiated ownership of resulting foreground IP and a governed Gulf bilingual dataset, preserving acquisition/exit optionality. This is not a promised return.
- **Unknown:** workflow, cohort, thresholds, hardware, team, owners, allocations, annual price, strategic funding, IP/data terms, market and all project performance.

Authority and boundaries: [`provenance/decisions.md`](provenance/decisions.md), [`research/claim-ledger.md`](research/claim-ledger.md).

## Project map

- [`demo/`](demo/) — self-contained static recognition console with clear, abstention/repair, and safety-sensitive confirmation fixtures; runbook, deployment controls, SHA-256 manifest, tests and validator.
- [`lab/`](lab/) — default-safe mock acquisition, synthetic signal/model contracts, dependency planner, dataset/license registry, leakage validator, non-purchasing rig guide, and evidence-gated roadmap; no installs, hardware, capture, or downloads by default.
- [`pitch/`](pitch/) — matched 13-slide HTML and deterministic editable PPTX decks, source, notes, original SVGs and validators.
- [`research/`](research/) — landscape, evidence matrix, definitions, metrics, competitors, references, critical scout reconciliation and claim boundaries.
- [`provenance/`](provenance/) — captain-source retrieval/checksum, decision authority, and media-rights catalogue.
- [`tools/validate_project.py`](tools/validate_project.py) — local links, release invariants, media catalogue and secret guard.

## Primary demo lineage, correctly bounded

The demo’s explanatory path is inspired by David Gaddy’s `dgaddy/silent_speech` at exact commit `a89357c2086609b432919b9d14ffc0be5d8983d5`; the exact files, MIT notice, prerequisites, and non-transfer boundary are recorded in [`provenance/upstream-reference.md`](provenance/upstream-reference.md). No upstream code, model, data, sample, or output runs in the demo. The upstream README’s approximate 36% open-vocabulary WER is a historical upstream result, not this project’s performance.

## Evidence headline, correctly bounded

SilentWear v2 (arXiv preprint, 2026) reports n=4, 14 differential neck sEMG channels and eight commands plus rest: average silent top-1 accuracy **77.5±6.6%** in global cross-validation and **59.3±2.2%** with a held-out session. Its 2.47 ms figure is **model inference**, not complete latency. Those are external preprint results—not this project’s expectation. See [`research/evidence-matrix.md`](research/evidence-matrix.md).

## Quality status

Static HTML/SVG/OOXML parsing, JavaScript syntax, deterministic fixtures, lab contracts/registries and PPTX rebuild, local references, claim decisions, source records and offline dependency guards are validated without installs. PowerPoint, Keynote and LibreOffice were unavailable. On 2026-07-29, two `chrome-devtools-axi` attempts reached the exact demo `file://` URL but failed with `Protocol error (Target.setDiscoverTargets): Target closed`, leaving zero pages; no browser-render certification is claimed. Target-application opening plus desktop/narrow/print visual rehearsal remain gates before external circulation. No site is deployed and no remote mutation was performed; read-only source metadata was checked, and pre-existing worktree remotes were left untouched.

This private local repository carries no general third-party or external-publication permission. See [`provenance/media-catalogue.md`](provenance/media-catalogue.md).
