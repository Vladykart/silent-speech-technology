# Live facial-sEMG prototype hardware and procurement guide

**Status:** sourcing and governance plan only — not purchase authority, a human-use approval, or evidence that this project owns hardware.

**Public-web snapshot:** **2026-08-05 UTC**. Prices, availability, software, support and conformity documents must be rechecked on the purchase-order date.

**Scope:** Silent Speech / facial surface electromyography (sEMG) only.

## 1. Truthful target

These are four different milestones:

1. **Live electrical-signal demo:** a signal generator or biopotential simulator drives a bench AFE and values move through a local display/recorder. No person is connected and no Silent Speech decoding is shown.
2. **Live participant-connected sEMG capture:** an approved participant is connected only to an exact, reviewed commercial system configuration; raw electrical activity is displayed and recorded. This is sensing, not decoding.
3. **Recorded-dataset pipeline:** immutable recorded files pass through provenance checks, display, quality control and optional preprocessing. The existing project path is still the separately labelled replay of official single-speaker research recordings.
4. **Real-model inference:** real weights execute on samples. Execution is not validation: hardware, units, channel sites, reference, bandwidth, calibration and population/session shift can all differ from the model's training conditions.

Every early participant-connected prototype must show this exact public label before traces or output:

> **REAL LIVE sEMG INPUT • MODEL UNVALIDATED ON THIS HARDWARE**

Keep it until the exact hardware/firmware, accessory and placement map, calibration, preprocessing, immutable data manifests and held-out person/session/day/device tests support a narrower upgraded claim. Buying hardware establishes none of Silent Speech decoding, transfer, accuracy, comfort, safety, wearability or product readiness.

## 2. Decision and ranked procurement routes

### Recommendation

**Preferred fastest truthful live-demo route:** obtain a manufacturer quote for **one Delsys Trigno Centro system, at least eight Trigno Avanti sensors, the supported receiver/base and host software, and Trigno SDK access**. The current [Avanti page](https://delsys.com/product/trigno-avanti/) identifies Centro as its research system; the current [Trigno SDK page](https://delsys.com/support/trigno-sdk/) documents 16 EMG streams at fixed 2,000 Hz, TCP/IP delivery of scaled IEEE-754 samples, triggering, and a licence-free control server. Require the quote to bind those facts to the exact Centro/firmware configuration. Use only Delsys's exact [Trigno Sensor Adhesive Interface](https://delsys.com/product/trigno-sensor-adhesive-interface/) if confirmed for the quoted sensor revision.

**Fallback:** **PLUX 8-Channel biosignalsplux Kit `820201027` plus eight biosignalsplux EMG sensors `820201201`**. Its official pages expose a direct order route, eight simultaneous inputs, up to 3 kHz/16-bit acquisition, three desktop OSs, raw exports and free APIs. It is the clearest low-friction integration purchase, but wireless/battery operation and a vendor-described charger do **not** prove complete-system isolation, certification or approval for this protocol.

Neither route may be connected to a person before the gates in section 6. If the preferred quote does not guarantee raw programmatic access, eight simultaneous EMG channels, stable timing, included software entitlement and the reviewed participant-side configuration, reject it and evaluate the fallback rather than improvising accessories.

### Ranked routes

1. **Commercial participant-research system — first choice.** Delsys first; Noraxon Ultium EMG, g.tec g.USBamp Research, PLUX and Shimmer are credible comparators below. Approval applies to the complete quoted configuration, not the brand or AFE.
2. **Research-maker board — plumbing/bench first.** OpenBCI Cyton exposes raw eight-channel ADS1299 data, but its 250 Hz stream cannot reproduce the current 1 kHz input and its official disclaimer calls it an engineering evaluation board, not a medical device or finished product. Battery power is not a safety finding.
3. **TI EVM bench — signal-generator/electrical evaluation only.** `ADS1299EEGFE-PDK` is the preferred eight-channel AFE bench kit; `ADS1298ECGFE-PDK` is an alternate family evaluation. Never connect either to a participant.
4. **Custom ADS129x board — slowest and highest safety-engineering burden.** Bare AFEs require protection, isolation, power, reference/clock, layout, firmware, EMC and complete-system review. Treat every custom revision as non-human until separately reviewed and approved.

**Investigated, not shortlisted:** [g.Nautilus Research](https://www.gtec.at/product/gnautilus-research-wireless-eeg-system/) is a current wireless 8/16/32/64-channel EEG system, but its official page specifies at most 500 Hz for 8/16/32 channels (250 Hz for 64) and EEG electrode configurations. That misses the current 1 kHz sEMG contract, so no facial-sEMG compatibility is assumed.

## 3. Commercial and maker comparison

The compatibility reference is the project's current Gaddy replay/model path: recorded `float32 [time, 8]` facial/neck-region sEMG at 1,000 Hz. Matching shape and rate alone does not match channel sites, reference, units, bandwidth, artifacts or training distribution.

“Vendor boundary” reports only what the linked manufacturer page establishes. It is not this project's safety or medical claim. “Quote required” also means stock, lead time and landed price were not public.

### Acquisition and electrical boundary

| Rank | Manufacturer / exact system and official order route | Public signal specification | Connection, power and participant-use boundary | Gap versus current 8-channel, 1 kHz Gaddy input/model |
|---:|---|---|---|---|
| 1 | Delsys [Trigno Centro](https://delsys.com/product/trigno-centro/) + **≥8 [Trigno Avanti](https://delsys.com/product/trigno-avanti/)** sensors; request quote on product page | Current SDK specification: 16 EMG streams, fixed 2,000 Hz; output is scaled single-precision float. Sensor ADC resolution/range/noise were not specified on the checked public pages. | Wireless, body-worn sensor path; exact receiver, battery/charging boundary and current conformity documents must be in quote and reviewed. No charging while worn unless the exact manual and safety owner expressly allow it. Commercial research hardware reduces, but does not remove, protocol/electrical review. | Eight channels can be selected; needs a fixed placement/reference map and validated anti-alias downsample 2 kHz→1 kHz. No model transfer assumed. |
| 2 | Noraxon [Ultium EMG](https://www.noraxon.com/our-products/ultium-emg/), quote an exact **8-sensor** system | 2,000 or 4,000 Hz; 24-bit; ±24,000 µV; baseline noise <1 µV; CMRR >100 dB; input >100 MΩ; selectable 5/10/20 Hz high-pass and 500/1,000/1,500 Hz low-pass. Public page says analog output up to 32 channels; exact receiver capacity must be quoted. | Wireless sensors, 8 h stated runtime, integrated impedance test, 250 MB recovery memory. Exact charging state, isolation/conformity and participant accessories still require accountable review. | Plausible eight-sensor route, but needs deterministic 2/4 kHz→1 kHz conversion, placement/calibration and proof that the paid data path exposes unprocessed samples. |
| 3 | g.tec [g.USBamp Research](https://www.gtec.at/product/gusbamp-research-16-channel-biosignal-amplifier/); [official configurator](https://www.gtec.at/product-configurator/g-usbamp-research/) | 16 monopolar or 8 bipolar simultaneous channels; 24-bit; up to 38.4 kHz/channel; <0.4 µV RMS (1–30 Hz); ±250 mV sensitivity range stated on page. | Wired USB 2.0. Manufacturer page states Safety Class II and Applied Part CF; obtain the exact current declaration/certificate and approved sEMG leads before review. Component labels do not authorize the study. | Exactly eight bipolar paths are plausible. Confirm an exact 1 kHz mode or validate conversion, channel reference, accessory bandwidth and calibrated units. |
| 4 | PLUX **[8-Channel biosignalsplux Kit `820201027`](https://www.pluxbiosignals.com/products/8-channel-biosignals-kit)** + 8 × **[EMG sensor `820201201`](https://www.pluxbiosignals.com/products/electromyography-emg)** | Eight generic analog inputs, up to 3,000 Hz and 16-bit/channel. EMG sensor: gain 1,000, 25–500 Hz, ±1.5 mV at 3 V, CMRR 100 dB, input >100 GΩ. | Bluetooth Class II; hub battery states ~10 h streaming/~24 h logging. Kit includes charger and 24 vendor electrodes, but no sensors. The checked page did not establish complete-system isolation or certification; review exact use/charge boundary. | Exact channel count; acceptance must demonstrate a supported 1 kHz mode, common timing and channel order. Sensor's 25 Hz high-pass and placement differ from current recordings and may affect inference. |
| 5 | 4 × Shimmer **[Shimmer3R EMG Unit](https://www.shimmersensing.com/product/shimmer3-emg-unit/)** or an exact [Consensys EMG Development Kit](https://www.shimmersensing.com/product/consensys-emg-development-kits/) configuration | Two differential EMG channels/unit with common reference; configurable 125–8,000 SPS including 1,000; configurable gain 1–12; about 800 mV range at gain 6. Resolution/noise were not stated on the checked product page. | Bluetooth, rechargeable Li-ion and on-device SD. Page identifies input protection and touchproof jack type; those component/connector facts are not complete-system IEC certification. Four-unit clock synchronization and charging isolation require acceptance evidence. | Four devices yield eight channels at 1 kHz, but cross-device synchronization, shared reference differences, units and dropped packets are material unproven gaps. |
| 6 | OpenBCI [Cyton Biosensing Board (8-channel)](https://shop.openbci.com/products/cyton-biosensing-board-8-channel) | 8 differential channels; ADS1299; 24-bit; gain 1–24; **250 Hz/channel**; microSD and wireless link to USB dongle. | Official docs say [battery only](https://docs.openbci.com/Cyton/CytonSpecs/); current shop bundle says lithium battery/charger included and electrodes excluded. No public isolation evidence was established. Official disclaimer: engineering evaluation only, not a finished product or medical device, and not represented as meeting CE/UL/FCC/EMC requirements. | **Not input-compatible:** 250 Hz is one quarter of the recorded 1 kHz stream and cannot recover omitted bandwidth. Requires a separate hardware/model study, not upsampling and a transfer claim. |

### Data path, software and commercial snapshot

| System | Raw export, SDK/API, files and timing | Host/software and licence/support caveat | Public price / availability snapshot, 2026-08-05 UTC |
|---|---|---|---|
| Delsys Trigno | [SDK](https://delsys.com/support/trigno-sdk/): continuous digital samples over local/remote TCP/IP, multiple clients, selectable start/stop trigger; 16 multiplexed EMG values formatted as scaled IEEE-754 floats. Device timestamp/drop-counter semantics and archival format were not established publicly. | Licence-free SDK server; documented reusable samples for MATLAB, LabVIEW, Go, Android, Windows C#/C and Linux. Current server download is a Windows `.exe`; client examples do not prove a native non-Windows device server. Bind EMGworks/version, API entitlement, updates and support to quote. | **Quote required**; no public system stock/lead time. Exact adhesive interface page showed USD 40 per 80-pack below 20 packs (regional invoice outside North America). |
| Noraxon Ultium | Public product page establishes synchronized sensors, loss recovery/internal memory and analog output, but not a documented raw SDK/API, timestamp contract or file format. Require a sample raw export and programmatic-stream specification before PO. | Proprietary MR4/software EULA and support from an Approved Source are indicated; supported OS, export entitlement and SDK terms were not public on the checked product page. Closed/raw-inaccessible delivery is a stop condition. | **Quote required**; no public core-system stock/lead time. Official shop listed accessories, not the core system. |
| g.USBamp Research | Product page advertises real-time integration and APIs for Python (g.Pype), MATLAB, Simulink, C, C#/.NET and LSL plus synchronized triggers. Require raw units, device timestamps, packet-loss behavior and recording format in configuration acceptance. | g.HIsys/g.Recorder/g.Pype are separate software choices; API wording does not prove a free licence. Supported host OS and current version/support term must be quoted. | Page displayed amplifier **€15,724**, g.HIsys **€6,542**, g.Recorder **€3,899**; configuration, tax, stock and lead time unknown. |
| PLUX biosignalsplux | [OpenSignals](https://www.pluxbiosignals.com/pages/opensignals) exports TXT, H5 and EDF and streams LSL/TCP; official [API support](https://support.pluxbiosignals.com/article-categories/apis/) says APIs/sample code are free. Device timestamp and dropped-packet semantics still need acceptance tests. | OpenSignals listed for Windows/macOS/Linux; Android mobile app. APIs bundled; analysis add-ons may be separately licensed. Record versions and support status at PO. | Kit **€3,950** + eight sensors at **€140 each** = **€5,070 displayed component subtotal**, before tax/shipping/options. Add-to-cart rendered; numeric stock and lead time were not visible. |
| Shimmer3R EMG | Raw data can stream through Consensys and log to SD; page states accurate inter-sensor synchronization. Official software catalogue lists C#, Swift (macOS/iOS), Java/Android, MATLAB and LabVIEW APIs. Exact file/timestamp/drop-counter semantics require a sample export. | ConsensysBASIC free; ConsensysPRO displayed as €199 annual; firmware described as open source. Consensys unified GUI is listed for Windows; API support varies by platform and licence. | Individual unit **€680**; four-unit component subtotal **€2,720**. EMG development-kit selector displayed **€799–€8,969**, so exact four-unit base/dock/leads configuration and lead time require confirmation. |
| OpenBCI Cyton | OpenBCI GUI records raw text/CSV and markers and can stream LSL; [developer docs](https://docs.openbci.com/ForDevelopers/SoftwareDevelopment/) list BrainFlow APIs for C++, Python, C#, Java, R, MATLAB, Julia, Rust and Node.js. Cyton packet/sample counters and host timestamps must not be relabelled as verified device time. | [GUI docs](https://docs.openbci.com/Software/OpenBCISoftware/GUIWidgets/) list macOS, Windows 10 and Linux. Public GUI/BrainFlow tooling exists, but preserve exact software/firmware licences and support versions in the manifest; no medical/support inference. | **USD 1,249; “Sold out”** on the official shop. No stock count or replenishment date. |

## 4. TI bench and custom-board routes

The TI facts and public prices below were rechecked in the completed bounded sourcing review at **2026-08-05 11:38–11:56 UTC**. TI-direct prices exclude tax, shipping, import, accessories and simulator. Inventory quantities and EVM delivery were login-gated; no login was attempted.

### Official EVMs — never participant-connected

| Exact kit / official route | Established capability and data path | Price/availability and host caveat | Hard boundary / 1 kHz fit |
|---|---|---|---|
| TI [`ADS1299EEGFE-PDK`](https://www.ti.com/tool/ADS1299EEGFE-PDK) ([user guide](https://www.ti.com/lit/pdf/SLAU443)) | 8 simultaneous 24-bit channels; ADS1299 supports 250 SPS–16 kSPS. GUI scope/FFT/histogram and text export of raw unfiltered data; no real-time-processing flow. | **USD 208.95** advertised; stock/delivery login-gated. Public page says Windows XP/7 while the 2016 guide says Windows 7 was unsupported at that time; Windows 10/11 unknown. Firmware/source downloads require export approval and were not accessed. | **Signal generator/simulator only.** MMB0 connects to PC over USB; the EVM is not a direct participant interface, isolated recorder, reference design or medical device. A 1 kHz bench configuration is plausible but must be measured. |
| TI [`ADS1298ECGFE-PDK`](https://www.ti.com/tool/ADS1298ECGFE-PDK) ([user guide](https://www.ti.com/lit/pdf/SBAU171)) | 8 simultaneous 24-bit channels; ADS1298 HR 500 SPS–32 kSPS / LP 250 SPS–16 kSPS. GUI analysis and text export; no real-time-processing flow. | **USD 208.95** advertised; stock/delivery login-gated. Windows XP/7 stated; current Windows support unknown. Source/firmware export approval required. | **Signal generator/simulator only.** Same USB/non-patient boundary. Do not infer suitability because the IC supports biopotential applications. |

Do not order electrodes or participant leads for either EVM. For electrical acceptance use only an approved lab signal generator/simulator and segregated bench setup selected by the lab owner.

### Bare TI parts — custom, non-human until separately reviewed

TI-direct is the manufacturer purchase route; recheck lifecycle and the [TI authorized-distributor list](https://www.ti.com/ordering-resources/faqs/purchasing-online/authorized-distributors.html) on PO day. The report found Arrow (except Japan), Digi-Key and Mouser on TI's current list, but their dynamic price/stock pages were blocked; no distributor availability is claimed.

| Family / exact tray orderable | Channels; stable datasheet facts | TI qty-1 public price / stock-category snapshot |
|---|---|---:|
| [`ADS1299IPAG`](https://www.ti.com/product/ADS1299/part-details/ADS1299IPAG) | 8; simultaneous 24-bit; 250 SPS–16 kSPS; gain 1–24; [ADS1299-x datasheet](https://www.ti.com/lit/ds/symlink/ads1299.pdf) | USD **69.82** / “In stock”; quantity and lead time hidden |
| [`ADS1299-6PAG`](https://www.ti.com/product/ADS1299-6/part-details/ADS1299-6PAG) | 6; same rate/resolution family | USD **60.583** / “In stock”; quantity and lead time hidden |
| [`ADS1299-4PAG`](https://www.ti.com/product/ADS1299-4/part-details/ADS1299-4PAG) | 4; same rate/resolution family | USD **40.545** / “In stock”; quantity and lead time hidden |
| [`ADS1298IPAG`](https://www.ti.com/product/ADS1298/part-details/ADS1298IPAG) | 8; simultaneous 24-bit through 8 kSPS; HR 500 SPS–32 kSPS / LP 250 SPS–16 kSPS; [ADS129x datasheet](https://www.ti.com/lit/ds/symlink/ads1298.pdf) | USD **42.506** / “In stock”; quantity and lead time hidden |
| [`ADS1296IPAG`](https://www.ti.com/product/ADS1296/part-details/ADS1296IPAG) | 6; same rate family | USD **35.882** / “In stock”; quantity and lead time hidden |
| [`ADS1294IPAG`](https://www.ti.com/product/ADS1294/part-details/ADS1294IPAG) | 4; same rate family | USD **26.914** / “In stock”; quantity and lead time hidden |

A lower channel-count AFE is not equivalent to the eight-channel recordings/model. A bare “medical/biosensing” AFE, a battery, or a connector standard is not complete-system isolation, certification or human-use evidence. Follow TI's [anti-counterfeit policy](https://www.ti.com/quality-reliability/quality/anti-counterfeit.html); do not substitute a marketplace board, clone, broker part, reel suffix or BGA package for an approved exact orderable.

## 5. Prototype architecture and acceptance contract

Do not implement a driver as part of procurement. After bench acceptance and approvals, add a vendor adapter behind [`SignalSource` / `RealHardwareSignalSource`](../realtime/app/signal_source.py):

```text
reviewed vendor device + exact accessories
  → vendor SDK/API adapter (no inference)
  → immutable raw recorder + acquisition manifest
  → calibrated canonical frame contract
  → separately enabled live display
  → separately approved preprocessing
  → separately enabled model inference
  → abstain/repair + human confirmation
```

For the preferred Delsys path, configure and record the native 2 kHz SDK stream, verify sequence/timing, map the selected eight channels, and create an evidence-backed anti-alias/downsample stage to the current 1 kHz contract. `SignalFrame.samples` remains `float32 [time, 8]`, `sample_rate=1000`, and `first_sample` remains contiguous only after conversion proves no gaps. Never silently interpolate a dropout. The same rules apply to a fallback adapter.

The canonical source record must carry, either in an expanded frame envelope or adjacent immutable metadata:

- calibrated physical units and conversion formula; native raw integer/float representation retained;
- eight channels in declared order, or an explicit source→canonical channel map with unfilled channels rejected rather than invented;
- device clock/sample counter plus monotonic host receive timestamp, clock-domain and synchronization evidence;
- configured and measured native/canonical sample rates, anti-alias/resampling revision and duration/sample-count cross-check;
- packet sequence, cumulative dropped/late/duplicate sample counters, and an explicit gap mask;
- per-channel contact/impedance/rail/saturation/quality state without treating a proprietary score as ground truth;
- session ID; device/base/sensor serials; hardware, firmware, SDK, OS and configuration profile; calibration record;
- an append-only manifest with raw file path, bytes, cryptographic digest, creation/close times, operator, consent/protocol scope, access class and transformation parent hashes.

**Stage gates:** live display may consume canonical frames without recording; recording requires governance; preprocessing requires frozen configuration tests; inference requires a declared hardware-transfer evaluation; any presented output still requires abstention/repair policy and human confirmation. A failure in one stage must not be hidden by another.

## 6. Governed data-collection plan

### Before any human connection

1. **No-human bench acceptance:** inspect shipment/configuration, serials and conformity documents; use a lab-approved signal generator/simulator to test all channels, range, rate, filters, timestamps/triggers, disconnects, packet loss/recovery, raw export and repeatable calibration. Test receiver/host failure and any cable/charger/debug path. Quarantine unexplained gaps or gain/filter behavior.
2. Freeze the **exact inventory**: base/receiver, every sensor and serial, electrode/adhesive/lead SKU and lot, charger/power supply/cable, host, OS, firmware, SDK/application and licence. Photograph/diagram configuration without participant identity.
3. Obtain an accountable **electrical-safety review** of the complete assembled configuration and intended environment, including isolation, leakage/touch and auxiliary current as applicable, single-fault behavior, charging/USB/debug paths, protection, cable strain, EMC, emergency disconnect and local intended-use/regulatory analysis. A vendor statement about one component is insufficient.
4. Approve protocol and ethics/IRB or local equivalent: purpose, recruitment, eligibility, compensation, voluntariness, no employment consequence, informed consent, withdrawal handling, adverse-event process and owner. Maintain a conventional communication fallback and a non-biometric alternative.
5. Approve a skin-contact/sanitation process for only the exact vendor-supported accessories: material/adhesive and allergy review, preparation/removal, wear limits, single-use/reuse rules, cleaning/disinfection, inspection and disposal. This guide gives no body-connection instructions.
6. Approve the placement-map method, session calibration, signal-quality thresholds, stop criteria and a physical emergency disconnect that does not depend on software. Stop for discomfort, skin reaction, damaged equipment, unexpected current/heat, loss of supervision, unacceptable contact/quality, repeated dropouts or protocol deviation.
7. Approve privacy/security: data minimization, pseudonymous IDs, access roles, encryption and key owner, transfer/jurisdiction, incident response, retention/deletion schedule, consent-scoped publication/reuse, withdrawal limits after de-identification/publication, and verified deletion. Raw sEMG, metadata, calibration signals and decoded text remain sensitive.

### Pilot progression and leakage control

1. **No-human bench** with synthetic electrical input; no model claim.
2. **One approved operator dry run** only after all human-use gates; test procedure and stop/disconnect, not performance.
3. **Bounded approved participants** under the frozen protocol; pause on deviations and version every hardware/accessory/configuration change.
4. Predeclare evaluation splits grouped by **person, session, day and device** as required by the question. Never randomly split overlapping or neighboring windows across train/validation/test. Keep a truly held-out test manifest inaccessible to tuning.

For every session, preserve acquisition provenance, protocol/consent scope, device/software licences, immutable raw and derived hashes, placement/configuration revision and quality events. Freeze train/validation/test manifests. Fit normalization, feature statistics, augmentation parameters, vocabulary/thresholds and calibration models on training data only; apply frozen values to validation/test. Report exclusions and missingness rather than silently deleting difficult windows.

## 7. Purchase checklist

Before an authorized owner signs a PO or quote:

- [ ] Exact manufacturer SKU/configuration and selling legal entity; authorized manufacturer/distributor verified on that date.
- [ ] Exact number/revision of sensors, receiver/base/dongle, charging dock/power supply, carrying/storage items and every cable.
- [ ] Exact vendor-supported participant accessory SKU, quantities/lots, compatibility and included versus separately ordered status.
- [ ] Eight simultaneous differential channels (or explicit approved map), native sample-rate option, resolution/range, gain, hardware/software filters and synchronization/trigger option.
- [ ] Unprocessed/calibrated raw access, units, timestamp/sample-counter/drop semantics, sample export, archival format and a supplied acceptance file.
- [ ] SDK/API and recording-software entitlement, licence term, permitted deployment, seats/hosts, offline operation, version pinning, update access and source/sample-code terms.
- [ ] Supported host OS/architecture and tested driver/firmware matrix; no assumption from an old manual or cross-platform client example.
- [ ] Included warranty, calibration certificate/service, battery replacement, technical support/SLA, repair/RMA and end-of-support policy.
- [ ] Numeric stock, promised ship date, lead time/backorder/cancellation, return/restocking terms and whether opened body-contact/electronic items remain returnable.
- [ ] Shipping, dangerous-goods handling, insurance, import/export, duty, tax, brokerage and landed currency cost; no checkout or export acceptance based on this guide.
- [ ] Current complete-system declaration/certificates and intended-use statements supplied for the exact revision; institutional safety/ethics owners still approve use.
- [ ] Receiving plan for serial/lot traceability, damage/counterfeit inspection, calibration/bench acceptance and quarantine.

### Stop / red flags

Stop procurement or use on any marketplace clone, counterfeit-risk seller, shortened/substituted SKU, unsupported OS, closed or preprocessed-only/raw-inaccessible stream, missing isolation evidence, ambiguous USB/charging/debug path, unclear SDK licence, unavailable calibration/support, unexplained packet loss, generic unaudited body-contact accessory, or no accountable human-use review. Do not treat “battery powered,” “wireless,” “medical-grade,” “Applied Part,” a connector standard or an ADS1299/ADS1298 component as complete-system approval.

## Evidence limitations

This was a bounded read-only check of public manufacturer product/support pages and public manuals, plus the completed TI sourcing report. No account/login, quote request, supplier contact, order, cart, reservation, credential, proprietary-software download, export acceptance, device, participant, dataset, weights or private endpoint was used. Dynamic quote/login pages leave configuration, numeric stock, lead time, shipping and some licence/OS details unknown; those unknowns are explicit above.
