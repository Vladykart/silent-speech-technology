# Rendered QA record

**Date:** 2026-07-31
**Surface:** official-model / recorded-sEMG replay at alternate validation port `http://127.0.0.1:8876/` (the default 8765 was already occupied by an unrelated process and was not stopped)

## Completed

- The loopback service started with the checksum-verified released checkpoint and `/api/health` returned 54,187,136 parameters, official model/data identities, both CC BY 4.0 notices, `official_recorded_semg_replay`, and `live_capture: false`.
- API integration tests exercised untouched recorded-frame streams, source-faithful features, real mel/phoneme forward output, post-inference reference metadata ordering, abstention, a second real take, confirmation, mandatory safety acknowledgement and stop.
- HTML references, Python/JavaScript/shell syntax, local-only dependencies and visible replay/attribution/claim labels passed automated validation.

## Rendered-browser limitation

`chrome-devtools-axi` was available and used with a fresh named session (`silent-realdata-p1-current`) against the verified current service. Its bridge launched, opened the local URL and accepted resize/wait, but snapshot returned:

```text
Protocol error (Target.setDiscoverTargets): Target closed
```

The same harness limitation occurred in the earlier build. Therefore no claim of rendered geometry, responsive layout or interactive Chromium QA is made. Before presentation, manually rehearse current Chrome at desktop and narrow widths and run all three real-recording paths. API/DOM validation is not visual QA.
