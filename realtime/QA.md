# Rendered QA record

**Date:** 2026-08-05
**Surface:** three-stage official-model / recorded-sEMG replay on temporary loopback-only port `http://127.0.0.1:8877/`

## Completed

- A temporary service started on loopback with the checksum-verified released checkpoint. `/api/health` returned 54,187,136 parameters, official model/data identity, `official_recorded_semg_replay`, `live_capture: false`, and no telemetry. The temporary service was stopped after the browser attempt; no running service was mutated.
- Backend integration tests exercised untouched recorded arrays, source-faithful preprocessing, real mel/phoneme output, the exact recorded-example bindings, post-inference reference ordering, abstention, second-take repair, reject, safety acknowledgement/confirm, stop and no-output paths.
- The deterministic client contract test exercised the exact `Data collection → Model → Process result` reducer, rejected early metadata disclosure, classified three executable official-recorded examples versus eight authored non-executable future examples, and checked human-gate/safety/accessibility hooks.
- Static checks covered JavaScript syntax, three semantic stage panels/navigation entries, fieldset/legend, live/alert regions, score meter, focus-visible and reduced-motion rules, narrow/4K CSS breakpoints, local references, no external browser-asset URLs, and absence of telemetry, capture, WebSocket and browser-storage APIs.

## Rendered-browser limitation

`chrome-devtools-axi` was used only against that loopback service with a fresh named session (`silent-replay-ui-p6`). It opened the local URL and accepted a 1920×1080 resize, but `snapshot` returned:

```text
Protocol error (Target.setDiscoverTargets): Target closed
```

The harness therefore produced no trustworthy DOM snapshot or screenshot. No claim of rendered geometry, 1920×1080/3840×2160 visual polish, horizontal-overflow absence, focus traversal, or interactive Chromium QA is made. The agent did not bypass the approved browser harness, relax sandbox/network policy, or use BetterWright. Before presentation, manually rehearse current Chrome at 1920×1080, 3840×2160 and narrow widths; keyboard-test all three recorded paths and verify there is no horizontal scroll or obscured control. Deterministic API/HTML/CSS/JavaScript validation is not visual evidence.
