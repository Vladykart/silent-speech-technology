# Quiet Channel Lab decision deck

A matched 13-slide HTML/editable PowerPoint evidence deck and a separate four-slide executive PowerPoint decision deck, with presenter notes, narrative sources, original diagrams, and zero-install validators. All formats are offline and contain no remote runtime dependency, tracker, telemetry, embedded video, or third-party slide asset.

## Status and decision boundary

- Tomorrow’s executable is a **concept / simulated interaction**, not silent-speech hardware or performance.
- Captain-selected beachhead: **e& frontline retail advisors and field technicians**.
- Lead business path: **AED 1,000,000 fixed-fee 90-day pilot**, then per-seat annual deployment only if gates pass.
- Strategic IP/governed bilingual-dataset funding and acquisition/exit optionality are unpriced upside. Later amounts remain `TBD`.
- Full claim ledger: [`../research/claim-ledger.md`](../research/claim-ledger.md).

## Files

- [`index.html`](index.html) — presentation.
- [`deck.md`](deck.md) — editable 13-slide source narrative, speaker notes and traces.
- [`deck-4-slide.md`](deck-4-slide.md) — authoritative four-slide executive narrative read by its builder.
- [`styles.css`](styles.css), [`script.js`](script.js) — local presentation assets.
- [`assets/`](assets/) — project-authored SVG schematics; rights/provenance in [`../provenance/media-catalogue.md`](../provenance/media-catalogue.md).
- [`validate.py`](validate.py) — HTML structure/claim/media checks.
- [`quiet-channel-evidence-deck.pptx`](quiet-channel-evidence-deck.pptx) — committed editable 13-slide PowerPoint artifact.
- [`quiet-channel-4-slide-deck.pptx`](quiet-channel-4-slide-deck.pptx) — editorial four-slide executive decision artifact using only native DrawingML.
- [`quiet-channel-4-slide-qa.md`](quiet-channel-4-slide-qa.md) — representative 1920×1080 Chromium geometry-QA record and exact-render limitation.
- [`build_pptx.py`](build_pptx.py) / [`build_4_slide_pptx.py`](build_4_slide_pptx.py) — deterministic Python standard-library OOXML builders; the latter can emit disposable SVG/HTML previews from its slide scene graph.
- [`validate_pptx.py`](validate_pptx.py) / [`validate_4_slide_pptx.py`](validate_4_slide_pptx.py) — ZIP/XML/relationship/content/notes/determinism validators.
- [`pptx-build.json`](pptx-build.json) / [`quiet-channel-4-slide-build.json`](quiet-channel-4-slide-build.json) — committed artifact hashes and build fingerprints.

## Present

Open `pitch/index.html` directly or run from repository root:

```bash
python3 -m http.server 8000 --bind 127.0.0.1
```

Then open `http://127.0.0.1:8000/pitch/`. Do not expose the rehearsal server beyond loopback.

Controls:

- `←` / `→`, Page Up / Page Down, or Space — navigate
- Home / End — first / last slide
- `N` — notes and sources
- `F` — fullscreen where supported
- `P` — print
- horizontal swipe — navigate on touch
- URL fragment `#slide-7` — deep link

Use slide 6 to open the offline demo. Follow [`../demo/PRESENTER.md`](../demo/PRESENTER.md); do not imply a presenter’s mouthed phrase is sensed.

## Rebuild and edit the PowerPoint

Rebuild from repository source without installing anything:

```bash
python3 pitch/build_pptx.py
python3 pitch/validate_pptx.py
python3 pitch/build_4_slide_pptx.py
python3 pitch/validate_4_slide_pptx.py
# Optional representative geometry QA (disposable output):
python3 pitch/build_4_slide_pptx.py --preview-dir .visual-qa-4slide
```

Both PPTX validators perform a second temporary rebuild and require byte-for-byte equality. The 13-slide validator covers package structure, notes, approved content, four catalogued SVGs and security boundaries. The four-slide validator additionally enforces its real source hash, strict word caps, room-readable type floors, bounded/non-overlapping text geometry, native connectors/chart primitives, a dominant ask, no embedded media, allowed source URL only, confidential-URL absence, and byte-stability of the 13-slide artifacts.

The 13-slide PPTX combines editable DrawingML with four project-authored SVGs. The four-slide deck contains only native editable text, shapes, connectors and chart primitives—no images, logos, charts from third parties, or device mockup. Both builders use a blank master and explicit Arial for portability.

**Exact application checks not performed:** PowerPoint, Keynote and LibreOffice remain unavailable, so application repair behavior, font substitution, notes-pane appearance and exact DrawingML rendering remain unverified. Geometry-matched SVG previews of the four-slide deck were rendered at 1920×1080 with installed headless Chromium and inspected; this is representative, not exact PowerPoint rendering. See [`quiet-channel-4-slide-qa.md`](quiet-channel-4-slide-qa.md). Open and rehearse the committed PPTX in the target application before circulation; if it repairs the file, retain the repair log and stop.

## Print / PDF

1. Open in the exact browser intended for the meeting.
2. Press `P`; choose landscape, background graphics, and zero/default browser margins.
3. Save to PDF; confirm 13 pages, source footers, no clipping, and readable notes separately.

Representative browser geometry QA is recorded for the four-slide deck; the 13-slide browser presentation still requires desktop/narrow/print rehearsal. Neither representative previews nor static checks replace exact target-application review before external circulation.

## Validate

From repository root:

```bash
python3 pitch/validate.py
python3 pitch/validate_pptx.py
python3 pitch/validate_4_slide_pptx.py
node --check pitch/script.js
python3 -m compileall -q pitch/validate.py pitch/build_pptx.py pitch/validate_pptx.py pitch/build_4_slide_pptx.py pitch/validate_4_slide_pptx.py
```

The validators check HTML/PPTX structure, local SVG parsing, decisions, notes, claim guardrails, OOXML relationships and deterministic rebuilds. They do **not** establish rendered visual quality, application compatibility, external-link truth, legal compliance, media permission beyond the catalogue, or device performance.

## Editing discipline

For the 13-slide deck, update `deck.md`, matching HTML slide/note and `build_pptx.py` together. For the executive deck, edit the fenced JSON in `deck-4-slide.md`; `build_4_slide_pptx.py` reads it directly. Rebuild and commit each PPTX with its hash evidence. External performance numbers require source, evidence type, participant/task/vocabulary, metric and non-transfer boundary. Do not add team, customer, partner, market, patent, approval, annual price, strategic funding, valuation or exit amounts without captain-approved evidence.
