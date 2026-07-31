# Rendered QA record

**Date:** 2026-07-31
**Surface:** local FastAPI client at `http://127.0.0.1:8765/`

## Completed

- The loopback service started and `/api/health` returned the loaded checkpoint checksum, 185,820 parameters, `synthetic_only` training provenance, and the simulated-signal/real-inference truth label.
- API integration tests exercised both NDJSON stream attempts, raw-frame events, feature payload, actual model inference, abstention, repair, confirmation, mandatory safety acknowledgement and stop.
- HTML references, Python/JavaScript/shell syntax, local-only dependencies and required visible claim labels passed automated validation.

## Rendered-browser limitation

`chrome-devtools-axi` was available and was used as required. Two fresh named sessions (`silent-realmodel-p1` and `silent-realmodel-p1b`) successfully launched the bridge and opened the URL, but both returned:

```text
Protocol error (Target.setDiscoverTargets): Target closed
```

before snapshot or screenshot capture. Therefore no claim of rendered geometry, responsive layout or interactive Chromium QA is made. Before presentation, manually rehearse the page in current Chrome at desktop and narrow widths and run all three scenario paths. Do not treat API/DOM validation as visual QA.
