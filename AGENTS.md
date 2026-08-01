# Project agent memory

This file is the project's committed home for project-intrinsic agent knowledge: build, test, release, architecture, and sharp-edge notes that should travel with the code.

- Claim authority: [`research/claim-boundary.md`](research/claim-boundary.md) and [`research/claim-ledger.md`](research/claim-ledger.md). External evidence never becomes project performance.
- Quick validation: `python3 tools/validate_project.py && python3 demo/validate.py && node demo/tests/core.test.js && python3 pitch/validate.py && python3 pitch/validate_pptx.py && python3 pitch/validate_4_slide_pptx.py && python3 realtime/validate.py`; after local dependencies exist, add `realtime/.venv/bin/python -m unittest discover -s realtime/tests -v`.
- Editable PPTX authority: rebuild with `python3 pitch/build_pptx.py` / `python3 pitch/build_4_slide_pptx.py`; validate byte-deterministically with the matching validator. Commit each `.pptx` and build JSON together.
- Keep `demo/` as the locked authored-fixture/no-model experience. Separately, `realtime/` replays official CC BY 4.0 single-speaker sEMG through official released weights; run `realtime/fetch_assets.py`, keep all model/data/replay files under ignored `local_assets/`, and treat selected outputs as neither live hardware nor accuracy evidence.
- Demo/deck are local/offline and must keep the concept/simulated label, authored failure/repair, no media capture/network dependency, and source conditions.
- Captain decisions and exact commercial boundaries are in [`provenance/decisions.md`](provenance/decisions.md); do not repurpose the AED 1,000,000 pilot fee for later pricing/funding/exit.
- Do not vendor third-party slides, figures, fonts, papers, datasets, models, screenshots, logos, video or audio. Catalogue all local media in [`provenance/media-catalogue.md`](provenance/media-catalogue.md).
- Four-slide Chromium previews are representative geometry QA, not exact PowerPoint rendering; see `pitch/quiet-channel-4-slide-qa.md`. Rehearse exact PowerPoint plus desktop/narrow/print surfaces before external circulation.

## Maintaining this file

Keep this file for knowledge useful to almost every future agent session in this project.
Do not repeat what the codebase already shows; point to the authoritative file or command instead.
Prefer rewriting or pruning existing entries over appending new ones.
When updating this file, preserve this bar for all agents and keep entries concise.
