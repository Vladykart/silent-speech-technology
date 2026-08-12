# Project agent memory

This file is the project's committed home for project-intrinsic agent knowledge: build, test, release, architecture, and sharp-edge notes that should travel with the code.

- Claim authority: [`research/claim-boundary.md`](research/claim-boundary.md) and [`research/claim-ledger.md`](research/claim-ledger.md). External evidence never becomes project performance.
- Quick validation: `python3 tools/validate_project.py && python3 demo/generate_manifest.py && python3 demo/validate.py && node demo/tests/core.test.js && python3 lab/validate.py && python3 -m unittest lab/tests/test_lab.py && python3 pitch/validate.py && python3 pitch/validate_pptx.py`.
- Editable PPTX authority: rebuild with `python3 pitch/build_pptx.py`; validate byte-deterministically with `python3 pitch/validate_pptx.py`. Commit the `.pptx` and `pptx-build.json` together.
- Demo/deck are local/offline and must keep the concept/simulated label, authored failure/repair, no media capture/network dependency, and source conditions. Demo artifact integrity/deployment authority: [`demo/artifact-manifest.json`](demo/artifact-manifest.json) and [`demo/DEPLOYMENT.md`](demo/DEPLOYMENT.md).
- Captain decisions and exact commercial boundaries are in [`provenance/decisions.md`](provenance/decisions.md); do not repurpose the AED 1,000,000 pilot fee for later pricing/funding/exit.
- Do not vendor third-party slides, figures, fonts, papers, datasets, models, screenshots, logos, video or audio. Catalogue all local media in [`provenance/media-catalogue.md`](provenance/media-catalogue.md).
- Pre-hardware lab authority: [`lab/README.md`](lab/README.md), [`lab/datasets.json`](lab/datasets.json), and [`lab/PLAN.md`](lab/PLAN.md). Defaults remain synthetic/no-install/no-device/no-download; held-out-session is the primary evaluation gate.
- Browser-rendered QA was unavailable for this release; never claim visual certification. Rehearse desktop, narrow and print/PDF before external circulation.

## Maintaining this file

Keep this file for knowledge useful to almost every future agent session in this project.
Do not repeat what the codebase already shows; point to the authoritative file or command instead.
Prefer rewriting or pruning existing entries over appending new ones.
When updating this file, preserve this bar for all agents and keep entries concise.
