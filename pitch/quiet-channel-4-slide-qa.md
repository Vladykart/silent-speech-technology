# Four-slide representative visual QA

- **Artifact:** `quiet-channel-4-slide-deck.pptx`
- **Artifact SHA-256:** `60810db66994a34dc6a7962c8866eb2e149abb70e99a522940d177a5766c5fd1`
- **QA date:** 2026-07-28
- **Renderer:** installed headless Chromium 150.0.7871.128 at 1920×1080
- **Status:** representative geometry QA passed; exact PowerPoint rendering remains a release gate.

## Method

`build_4_slide_pptx.py` emits disposable SVG/HTML previews from the same slide scene graph, coordinates, colours, type sizes, and line breaks used for DrawingML:

```bash
python3 pitch/build_4_slide_pptx.py --preview-dir .visual-qa-4slide
python3 -m http.server 8765 --bind 127.0.0.1 --directory .visual-qa-4slide
chromium --headless --no-sandbox --disable-gpu --hide-scrollbars \
  --force-device-scale-factor=1 --window-size=1920,1080 \
  --screenshot=slide-1.png http://127.0.0.1:8765/slide-1.svg
```

All four slides and `contact-sheet.html` were rendered. The generated SVG, HTML, and PNG files were disposable and are not committed.

Final representative PNG hashes:

```text
slide-1.png       b9023a2fb6c8a384238d15cfc1b077bfbca915c4d83cadf38b0ca8b6f7888dc0
slide-2.png       2841210b7163ebc2e18711bb80beba87d76e6b3e78c4d5cbc65f4ba7186c5ac2
slide-3.png       f5f5b122cef6ad453b64e8314ceeb22edc424c6946e3099bf2848824d8866d98
slide-4.png       713b5a063c7d6ad6bca9283a4f4e361a43a1c2af5d23712a31772a5ef9d4fc8e
contact-sheet.png 266fff18f0a9dae0e142e7e345b67431eba2ac11ed0aeb9a9081969aad5752db
```

## Inspected result

- Four distinct focal compositions are clear at contact-sheet scale.
- Assertion headlines remain inside their editorial columns with no observed preview clipping.
- Slide 1 uses an abstract retail/field command flow; no device or hardware mockup appears.
- Slide 2 uses explicit connectors, a dominant human gate, repair loop, and raw-signal boundary.
- Slide 3's native evidence bars, values, transfer-gap annotation, conditions, and proof obligations are separated and legible.
- Slide 4 makes `AED 1,000,000` the dominant type and clearly terminates in `GO / CHANGE / STOP`.
- No observed preview text collisions, object overflow, distorted media, third-party media, or logo use.

## Limitation

This preview is **representative, not exact PowerPoint rendering**. Chromium substitutes its available Arial-compatible font and does not exercise PowerPoint's DrawingML renderer, notes pane, edit behavior, or file-repair path. Open and rehearse the committed PPTX in the exact target PowerPoint environment before external circulation.
