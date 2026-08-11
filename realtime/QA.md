# Rendered browser and network QA

**Date:** 2026-08-11

**Candidate surface:** exact runtime revision `4c0cb3d283ac5582181d83bfcb7bf75e9f9a85d0` on temporary loopback-only `127.0.0.1:8879`; no installed/shared service, Tailscale route, listener, or public endpoint was changed. A later evidence-record commit may differ only in release binding/QA records, per the no-self-reference release procedure.
**Product authority:** [`spec/INVESTOR_REAL_REPLAY_SPEC.md`](spec/INVESTOR_REAL_REPLAY_SPEC.md)

## Approved-tool attempt and fallback

A fresh named `chrome-devtools-axi` session opened only the loopback candidate and accepted a 1366×768 resize. Its first snapshot repeated the established harness failure:

```text
Protocol error (Target.setDiscoverTargets): Target closed
```

No retry, external origin, personal profile, install, or network/sandbox-policy change was made through that harness. Per the authorized fallback, rendered QA used the existing pinned Playwright-cache Chromium binary at the established project-local cache identity (Chromium `139.0.7258.5`) with:

- a fresh disposable profile under ignored `realtime/local_assets/` (not a personal profile);
- loopback-only remote debugging and page origin;
- background networking, sync, component updates, extensions, metrics upload, translation, and domain reliability disabled;
- host resolution set to fail every hostname except `127.0.0.1`;
- CDP network, log, accessibility, geometry, interaction, storage, cookie, and screenshot inspection;
- no downloaded browser/tool/package and no non-loopback navigation.

The durable harness is [`tests/rendered_browser_qa.mjs`](tests/rendered_browser_qa.mjs). Screenshots were transient ignored review aids only; they are not committed/retained as evidence or model output.

## Geometry matrix

| Requested viewport | Layout client width* | Initial overflow / clipped text | Visible enabled controls | Dynamic path |
|---:|---:|---:|---:|---|
| 320×568 | 305 | 0 / 0 | 17 | initial/truth/library geometry |
| 375×812 | 360 | 0 / 0 | 17 | initial/truth/library geometry |
| 768×1024 | 753 | 0 / 0 | 17 initial / 19 dynamic | all featured interaction paths |
| 1024×768 | 1009 | 0 / 0 | 17 | fully stacked initial geometry |
| 1366×768 | 1351 | 0 / 0 | 17 initial / 19 dynamic | all featured interaction paths |
| 1920×1080 | 1905 | 0 / 0 | 17 initial / 19 dynamic | all featured interaction paths |
| 3840×2160 | 3825 | 0 / 0 | 17 | capped projector initial geometry |

\* Headless Chromium reserved a 15 px vertical scrollbar. At every size, document and body scroll width equalled the actual layout client width exactly; there was no horizontal overflow. The audit checked every visible element boundary, text leaf clipping, one H1, named controls, control dimensions, external anchors, and sticky truth/limitation visibility after scrolling to the document end.

Transient visual inspection confirmed:

- the permanent three-part truth bar and complete limitation line remain legible at 320 px without truncation;
- the 1100 px stack produces readable tablet/narrow flow;
- 1366/1920 hero/proof hierarchy is presentation-ready;
- the ten-card library, all-eight-channel source/filtered views, architecture card, 112-feature heatmap, real 80-bin heatmap, 48-class view, separated timing, decoder gate, final no-actuation state, and footer have no overlap or chart spill;
- 3840 content is capped rather than stretched and uses the projector typography rule.

## Interaction, prompt, and human-policy matrix

At each of tablet (768), desktop (1366), and projector (1920), the harness executed:

1. `QC-R01`: exact ordered events, real output views, metadata only after model/decoder, candidate held, human reject → no result;
2. `QC-R02`: abstention → no result; `QC-R02-T2`: second official take through the same path, then human confirmation;
3. `QC-R03`: safety hold; confirmation disabled before acknowledgement; acknowledgement remained additional to confirmation; confirmed result stated no actuation;
4. evidence drawer open and Escape close without a focus trap.

Dynamic geometry repeated with zero overflow/clipping and all visible enabled controls named/sized. Reduced-motion, arrow-key heatmap inspection, skip/focus semantics, Space-confirm prevention, and exact event reducer are additionally deterministic contract tests.

## Network, persistence, and console result

- 75 page/API requests across seven reloads and nine complete operator paths; **0 external requests**. Every request stayed on the exact loopback origin. No WebSocket/WebRTC, beacon, font, external image, source map, service worker, or favicon request occurred.
- 0 cookies; 0 local/session storage entries; 0 IndexedDB databases; 0 Cache API entries; 0 service-worker registrations.
- 0 page console errors/warnings and 0 unexpected browser log errors/warnings.
- Accessibility tree: 0 unnamed exposed buttons.
- The pinned browser emitted one known security warning per reload because it does not recognize the still-present deny-only `bluetooth=()` Permissions-Policy directive (7 warnings total). Camera, microphone, geolocation, payment, USB, and serial deny directives were accepted. The Bluetooth declaration remains fail-closed in the header as required; the client contains no Bluetooth/capture API path. This runtime-specific warning is disclosed rather than suppressed or worked around.

## Release disposition

**Rendered/network QA passed** for exact runtime revision `4c0cb3d283ac5582181d83bfcb7bf75e9f9a85d0`. No source-only substitution is claimed. Re-run this matrix against the exact staged immutable release and authorized Tailnet client before any later owner-approved cutover. Any different request, overflow, clipping, inaccessible control, prompt-order failure, persistence, or warning beyond the one disclosed unsupported deny directive is a release block.
