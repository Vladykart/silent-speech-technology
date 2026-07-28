# Quiet Channel Lab decision deck

A matched 13-slide HTML and editable PowerPoint decision deck with presenter notes, source Markdown, original SVG diagrams, and zero-install validators. Both formats are offline and contain no remote runtime dependency, tracker, telemetry, embedded video, or third-party slide asset.

## Status and decision boundary

- Tomorrow’s executable is a **concept / simulated interaction**, not silent-speech hardware or performance.
- Captain-selected beachhead: **e& frontline retail advisors and field technicians**.
- Lead business path: **AED 1,000,000 fixed-fee 90-day pilot**, then per-seat annual deployment only if gates pass.
- Strategic IP/governed bilingual-dataset funding and acquisition/exit optionality are unpriced upside. Later amounts remain `TBD`.
- Full claim ledger: [`../research/claim-ledger.md`](../research/claim-ledger.md).

## Files

- [`index.html`](index.html) — presentation.
- [`deck.md`](deck.md) — editable source narrative, speaker notes and traces.
- [`styles.css`](styles.css), [`script.js`](script.js) — local presentation assets.
- [`assets/`](assets/) — project-authored SVG schematics; rights/provenance in [`../provenance/media-catalogue.md`](../provenance/media-catalogue.md).
- [`validate.py`](validate.py) — HTML structure/claim/media checks.
- [`quiet-channel-evidence-deck.pptx`](quiet-channel-evidence-deck.pptx) — committed editable 13-slide PowerPoint artifact.
- [`quiet-channel-4-slide-deck.pptx`](quiet-channel-4-slide-deck.pptx) — focused editable four-slide PowerPoint artifact.
- [`build_pptx.py`](build_pptx.py) / [`build_4_slide_pptx.py`](build_4_slide_pptx.py) — deterministic Python standard-library OOXML builders.
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
```

The validator performs a second temporary rebuild and requires byte-for-byte equality with the committed artifact. It also checks ZIP CRC/integrity, deterministic timestamps/order, XML well-formedness, required OPC parts and relationships, 13-slide order, 13 speaker-note parts, approved decision text, editable DrawingML shape count, four embedded project-authored SVGs, required evidence qualifiers, artifact/source hashes, and absence of remote relationships or macros.

Most copy, citations, cards, tables and diagrams are native editable PowerPoint text/shapes. Four project-authored SVG visuals are embedded as local images; edit their source under `pitch/assets/` and rebuild. The builder intentionally uses a single blank master and Arial for portability—advanced PowerPoint theme/layout tooling is outside this no-install build.

**Opening checks not performed:** PowerPoint, Keynote and LibreOffice are unavailable in this environment, so actual application opening, SVG compatibility/fallback, notes-pane appearance, font substitution, transitions, edit behavior and rendered layout remain unverified. Open and inspect the committed PPTX in the target application before tomorrow's presentation. If an application repairs the file, retain the repair log and do not present until reviewed. The HTML deck remains the validated offline fallback.

## Print / PDF

1. Open in the exact browser intended for the meeting.
2. Press `P`; choose landscape, background graphics, and zero/default browser margins.
3. Save to PDF; confirm 13 pages, source footers, no clipping, and readable notes separately.

Browser-rendered QA was unavailable during build. Static structure/accessibility/parser checks are strong but do not replace a desktop/narrow/print rehearsal. Rendered QA remains a release gate before external circulation.

## Validate

From repository root:

```bash
python3 pitch/validate.py
python3 pitch/validate_pptx.py
node --check pitch/script.js
python3 -m compileall -q pitch/validate.py pitch/build_pptx.py pitch/validate_pptx.py
```

The validators check HTML/PPTX structure, local SVG parsing, decisions, notes, claim guardrails, OOXML relationships and deterministic rebuilds. They do **not** establish rendered visual quality, application compatibility, external-link truth, legal compliance, media permission beyond the catalogue, or device performance.

## Editing discipline

Update `deck.md`, the matching HTML slide/note, `build_pptx.py`, the claim ledger, and references together; rebuild and commit the PPTX/hash evidence. External performance numbers require source, evidence type, participant/task/vocabulary, metric and non-transfer boundary. Do not add team, customer, partner, market, patent, approval, annual price, strategic funding, valuation or exit amounts without captain-approved evidence.
