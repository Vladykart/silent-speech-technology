# Non-purchasing equipment and study plan

All prices are rough **USD planning classes**, not quotes or budgets. Refresh authorized supplier quotes, shipping, tax, lead time, calibration, warranty, licenses, consumables, and local availability before a decision. No order, vendor contact, device suitability claim, or human connection is authorized here.

## Procurement tiers

### Tier 0 — learning/bench rig (roughly USD 250–700)

Three MyoWare 2.0 sensors with cable shields; Arduino Nano 33 BLE Sense Rev2 or a reusable ESP32-S3 board; disposable small Ag/AgCl electrodes; skin prep; tape; breadboard/jumpers; and isolated battery power. Purpose: learn channel handling and motion/artifact behavior on electrical phantoms/bench signals first. Three channels do not reproduce eight-channel research. Board analog range, simultaneous sampling, isolation, noise, electrode use, and body-contact suitability require engineering/safety review.

### Tier 1 — research rig (roughly USD 5,000–25,000 all-in; quote required)

Compare rather than assume:

- **OpenBCI Cyton + Daisy** (roughly USD 2,000–4,000 equipment class): accessible ecosystem/BrainFlow path; confirm channel simultaneity, sample rate, input protection, gain, radio/drop behavior, and research-use constraints.
- **TI ADS1299EEGFE-PDK** (roughly USD 300–1,000 board-only class): evaluation front end, not a participant-ready recorder; substantial isolated acquisition, enclosure, firmware, protection, verification, and engineering are required.
- **OT Bioelettronica Muovi** (research-vendor quote): higher-density/research workflow option; verify API/data access, electrodes/accessories, lead time, service, and license terms.

Budget separately for appropriate electrodes, skin-impedance measurement, touchproof shielded leads/connectors, **mandatory medical-grade USB isolation where applicable**, battery operation, repeatable placement jig, reference microphone/audio interface for explicitly consented paired calibration only, and adequate local compute/storage. A reference microphone is future protocol equipment—not part of the web demo or default lab smoke tests.

### Tier 2 — wearable research path (roughly USD 20,000–100,000+ NRE)

BioGAP-Ultra/GAP9 evaluation hardware and reviewed GAPflow toolchain; multiple flex-PCB spins; dry-electrode material/geometry trials; housings and placement fixtures; battery/power profiler; oscilloscope and isolated bench equipment; test jigs; and explicit EMC/pre-compliance budget. This is an R&D path, not a product bill of materials. Verify tool/board availability, licenses, export flow, analog front end, memory, power, thermal, EMC, skin contact, cleaning, and manufacturing constraints.

## Non-negotiable gates before any person recording

- Accountable protocol/ethics and jurisdiction/labor review; informed consent; voluntariness; non-biometric alternative; withdrawal/deletion; compensation; accessibility and incident plan.
- Intended-use/failure-harm review, skin-contact and irritation procedure, electrode/skin-prep instructions, stop criteria, trained operator, and adverse-event route.
- Independent electrical review of current paths, input protection, isolation, battery state, enclosure, cables, leakage, and emergency disconnect.
- Data inventory, purpose, retention, encryption/access, export/publication/reuse, de-identification limits, and deletion owner.
- Approved reference-audio wording and controls if paired calibration is scientifically necessary. No covert or default audio.

**Never connect a person to a mains-referenced experimental rig.** Battery power does not by itself prove isolation or safety. No participant recording begins from this repository’s defaults.

## Evidence-gated sequence

| Window | Work | Objective exit gate |
|---|---|---|
| Weeks 1–2 | Select one low-consequence workflow/grammar; freeze consent/governance and split plan; run synthetic acquisition/signal/model contracts; decide board evaluation criteria. | Named owners; approved protocol route; threat/failure analysis; deterministic mocks and validators pass; no human recording. |
| Weeks 3–4 | Procure only after approval; bench/phantom evaluation of noise, timestamps, drops, disconnect and isolation; freeze channel map/filter candidates and raw provenance schema. | Electrical reviewer sign-off for next step; board comparison evidence; safe shutdown/drop accounting; still no person if any gate is open. |
| Weeks 5–8 | If all gates pass, small consented feasibility capture with session-separated IDs and fallback; quantify signal quality, placement/calibration burden, abstention/repair and operator burden. | Auditable governed dataset; immutable split manifest; within-session baseline clearly secondary; predefined stop/continue criteria. |
| Weeks 9–12 | Keep final session untouched; run primary held-out-session evaluation and complete latency/abstention/failure analysis. | **Held-out-session decision gate** with WER/command metric definitions, uncertainty and negative cases. Global CV alone cannot pass. A generalization drop is an honest redesign result, not failure. |
| Week 13+ | Only after evidence: repeat sessions/participants/languages, compare hardware/form factors, participatory workflow research, and separately reviewed edge export experiments. | Each claim upgraded only from retained protocol, revision, split, metric code, checksum, reviewer, and decision evidence; no production/medical/safety leap. |

Stop or redesign if isolation, voluntariness, signal quality, session generalization, fallback burden, privacy, or harm gates fail. Do not tune the test split, hide abstentions, or convert an external result into a project target.
