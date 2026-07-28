# Media rights and provenance catalogue

**Catalogue date:** 2026-07-28
**Rule:** no third-party image, slide, video, logo, font, audio, model output, dataset visualization, or paper figure is vendored. A public URL establishes access, not reuse rights.

## Local authored assets

| Asset | Origin | Rights / status | Claim boundary |
|---|---|---|---|
| `pitch/assets/concept-research-rig.svg` | Original SVG authored for this local project, 2026-07-28 | No third-party source or embedded asset. Project-use clearance still subject to owner policy. | Concept schematic; no hardware, validated electrode sites, safety, comfort, enclosure, e& device, or product design. |
| `pitch/assets/pipeline-gates.svg` | Original SVG authored for this local project, 2026-07-28 | Same | Proposed architecture; not implemented data flow/security/integration. |
| `pitch/assets/evidence-gap.svg` | Original SVG authored for this local project from numeric values in SilentWear arXiv:2603.02847v2 | Graphic is original; underlying facts cited. No paper figure copied/traced. | External preprint values, n=4 / 8 commands + rest; not project results. |
| `pitch/assets/privacy-flow.svg` | Original SVG authored for this local project, 2026-07-28 | No third-party source or embedded asset. | Proposed state machine/prohibitions; not certification. |
| Demo waveform | Arrays authored in `demo/core.js`; SVG paths generated locally by `demo/script.js` | Original illustrative data; not biological or model output. | Normalized, not time/voltage calibrated, not measured accuracy. |
| `pitch/quiet-channel-evidence-deck.pptx` | Deterministic standard-library OOXML package built by `pitch/build_pptx.py` | Contains native project-authored DrawingML text/shapes and the four local SVGs above; no template or third-party media. Hash evidence: `pitch/pptx-build.json`. | Application opening/rendering remains unverified; artifact is not evidence of hardware or performance. |
| `pitch/quiet-channel-4-slide-deck.pptx` | Deterministic standard-library OOXML package built by `pitch/build_4_slide_pptx.py` | Contains native project-authored DrawingML text/shapes and reuses only `concept-research-rig.svg`; no template or third-party media. Hash evidence: `pitch/quiet-channel-4-slide-build.json`. | Application opening/rendering remains unverified; artifact is not evidence of hardware or performance. |
| Deck/demo UI | HTML/CSS/JS authored for this repository | TWPS commit `e3ce5a9` was inspected only for interaction/file-spirit reference; no TWPS identity, claims, media, CSS or branding is included. | Browser-rendered QA unavailable. |

## Captain-supplied deck

The source presentation and 14 embedded PNGs were inspected transiently but not retained or reused. The deck marks itself confidential and redistribution permission was not established. See [`source-record.md`](source-record.md).

## Third-party papers, repositories, datasets and models

No paper PDF, chart, screenshot, code, dataset, sample, model or weight is vendored. References and exact revisions appear in [`../research/references.md`](../research/references.md). Licences described there apply to the cited artifacts; they do not automatically license screenshots, trademarks, paper figures, participant data, dependencies, commercial use, or this project.

## Video and QR policy

Official video links may be listed as optional presenter references after source/rights review. They are not embedded, downloaded, auto-opened, or cached. A QR code is only a rendering of a URL; it does not grant permission to reproduce the destination video or its thumbnail. QR options, if included, must identify the destination domain in adjacent text, be generated as an original code graphic, and remain optional because the deck/demo must work offline.

## Media-rights report reconciliation

The 949-line parallel report `/root/kun-agent-workspace/data/silent-speech-media-s1/report.md` was read in full after the PPTX first passed validation (SHA-256 `708946cff9e17eb97ce536c01b31f76c26915279893430633bae28b94d2c6109`, access 2026-07-28). Its rights-layer analysis reinforces the conservative release:

- MIT Media Lab CC BY 4.0 photographs and ACL CC BY 4.0 figures may be reusable with attribution, but identifiable-person, endorsement, strategy and visual-review questions remain; **none is included**.
- SilentWear figures use arXiv's non-exclusive distribution licence—not a reuse licence; **none is included**.
- Meta's cited Nature figures are CC BY-NC-ND; commercial deck reuse is prohibited; **none is included**.
- MIT AlterEgo/TED video is link/QR-only or permission-controlled in this commercial context; no video/frame is embedded, played or copied.
- Corporate marks remain text-only. No e&, Meta, Apple, MIT, AlterEgo, Cornell, Whispp or other logo is present.

Three optional media choices remain captain decisions in the scout's decision lifecycle: AlterEgo competitor imagery, third-party logos, and outbound permission requests. Per the urgent delivery instruction, they do not block this release. Current resolution-by-omission is: original diagrams only, text-only corporate names, no outreach, no external video/QR. Future additions require a fresh catalogue entry, licence/likeness/trademark review and explicit captain approval.
