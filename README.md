# Silent Speech Technology — first local release

An evidence-gated research package, an offline concept demo, a professional evidence-first official-recording replay, and editable decision decks.

> **Claim boundary:** No silent-speech device, live sensor capture, newly collected participant data, measured project accuracy, customer, public/product deployment, or medical/AAC product is present. The locked [`demo/`](demo/) remains a deterministic **CONCEPT / SIMULATED PIPELINE** with authored fixtures. Separately, [`realtime/`](realtime/) replays a frozen official single-speaker recorded-sEMG catalogue through source-faithful preprocessing and David Gaddy's one official released 54,187,136-parameter model. That is real artifact execution—not live hardware or project performance. A private Tailnet-only research-demo delivery path exists; it is not public or a product/customer deployment.

## Quick start

### Real released backend + real recorded-data replay

```bash
./realtime/run-local.sh
```

Open `http://127.0.0.1:8765/`. Dependencies and approved ignored assets must be prepared before launch; presentation-time install/download/fallback is prohibited. The service verifies all frozen members and the strict-loaded checkpoint, then binds to loopback only with access logging disabled. No checkpoint or recording is committed. See [`realtime/README.md`](realtime/README.md) and the product authority at [`realtime/spec/INVESTOR_REAL_REPLAY_SPEC.md`](realtime/spec/INVESTOR_REAL_REPLAY_SPEC.md).

### Static concept and decks

```bash
python3 tools/validate_project.py
python3 demo/validate.py && node demo/tests/core.test.js
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

Direct `file://` use also works. Keep [`demo/PRESENTER.md`](demo/PRESENTER.md) open as the 3–5 minute operator script. Do not expose the static server beyond loopback.

## Current decision status

- **Beachhead:** e& frontline retail advisors and field technicians; Stage 0 selects one low-consequence workflow.
- **Lead path:** **AED 1,000,000 fixed-fee 90-day pilot**, then annual per-seat deployment at `TBD` pricing only if evidence gates pass.
- **Strategic upside:** unpriced e& funding/negotiated ownership of resulting foreground IP and a governed Gulf bilingual dataset, preserving acquisition/exit optionality. This is not a promised return.
- **Unknown:** workflow, cohort, thresholds, hardware, team, owners, allocations, annual price, strategic funding, IP/data terms, market and all project performance.

Authority and boundaries: [`provenance/decisions.md`](provenance/decisions.md), [`research/claim-ledger.md`](research/claim-ledger.md).

## Project map

- [`demo/`](demo/) — locked authored-fixture, no-model interaction; runbook, script, deterministic test and validator.
- [`realtime/`](realtime/) — evidence-first private FastAPI/client experience: ten frozen official CC BY 4.0 recordings plus one second take, all eight channels, explicit source/display transformations, 112-feature inspection, real 80-bin/48-class output views, exactly one strict-loaded 54,187,136-parameter model, separate project decoder, abstention/repair/safety/confirmation gates, provenance, tests, and private deployment/rollback templates. Large assets stay ignored and simulation is unreachable from production.
- [`pitch/`](pitch/) — matched 13-slide HTML/PPTX evidence deck plus a source-driven four-slide executive PPTX, notes, original SVGs, representative geometry QA and validators.
- [`research/`](research/) — landscape, evidence matrix, definitions, metrics, competitors, references, critical scout reconciliation and claim boundaries.
- [`provenance/`](provenance/) — captain-source retrieval/checksum, decision authority, and media-rights catalogue.
- [`tools/validate_project.py`](tools/validate_project.py) — local links, release invariants, media catalogue and secret guard.

## Evidence headline, correctly bounded

SilentWear v2 (arXiv preprint, 2026) reports n=4, 14 differential neck sEMG channels and eight commands plus rest: average silent top-1 accuracy **77.5±6.6%** in global cross-validation and **59.3±2.2%** with a held-out session. Its 2.47 ms figure is **model inference**, not complete latency. Those are external preprint results—not this project’s expectation. See [`research/evidence-matrix.md`](research/evidence-matrix.md).

## Quality status

Static HTML/SVG/OOXML parsing, JavaScript syntax, deterministic fixtures/PPTX rebuild, local references, claim/source authority, and offline dependency guards are validated without installs. With approved local assets present, `realtime/` adds full archive/member/checkpoint checks, native-dtype/conversion provenance, strict state load, all frozen real forward passes, bounded payload/event/prompt/human-policy tests, and isolated loopback rendered/network evidence across the required viewport matrix. Selected outputs are not project accuracy. The private Tailnet-only research-demo access path is not public or product/customer deployment. Exact PowerPoint plus target browser surfaces still require operator rehearsal before circulation.

This private local repository carries no general third-party or external-publication permission. See [`provenance/media-catalogue.md`](provenance/media-catalogue.md).
