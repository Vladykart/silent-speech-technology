# Explicit claim ledger

**Release:** updated 2026-07-31. `C` IDs appear in the deck notes. **Green** means safe only with the wording/conditions shown. **Amber** is a hypothesis or external result requiring its qualifier. **Red** is prohibited for this project. `H` rows are captain holds and must not be silently decided.

## Project and demo

| ID | Verdict | Exact safe claim | Evidence / non-transfer boundary |
|---|---|---|---|
| C01 | Green | This repository has a runnable offline authored-fixture interaction demo. | `demo/`; local validators/tests. Keep distinct from `realtime/`. |
| C02 | Green | The locked static demo uses authored fixtures and no sensor, model, microphone, camera, biometric input, account, or network service. | `demo/` only; the separate `realtime/` client intentionally uses a loopback backend. |
| C03 | Green | The static demo exposes lock state, candidate alternatives, rejection, repair, confirmation, output, and a privacy log. | Interaction behavior only—not sensing performance. |
| C33 | Green | The separate local replay bench performs source-faithful preprocessing and strict PyTorch forward passes through David Gaddy's official 54,187,136-parameter released model, then decodes its trained phoneme head, abstains, replays a second real take and confirms. | `realtime/` exact hashes/manifests/tests/API; official model Zenodo 6747411, CC BY 4.0. Selected behavior proves local artifact execution only—not project accuracy or generalization. |
| C34 | Green | The default acquisition source replays untouched official single-speaker 1 kHz, eight-channel recorded sEMG from Silent Speech EMG v1.0; it is not live capture. A `SignalSource` contract isolates the unimplemented physical-driver seam. | Dataset Zenodo 4064409 (concept 4064408), CC BY 4.0. No project participant collection, device, electrical-safety review, calibration or cross-speaker evidence. An explicit simulator class remains non-default plumbing only. |
| C35 | Green | Large official data/model assets are fetched/checksummed outside git and attributed to David Gaddy; this project mode is non-commercial local research demonstration. | `realtime/assets-manifest.json`, fetch script and notices. Internal non-commercial scope does not rewrite MIT/CC BY 4.0 terms; no endorsement or project ownership. |
| C04 | Green | Facial/neck surface EMG is a plausible silent-speech research modality. | Peer-reviewed R01–R04; placement/task/participant specific. |
| C05 | Amber | Surface EMG is the proposed first feasibility modality. | Product decision for a transparent research rig; no hardware exists and form factor stays open. |
| C06 | Amber | The captain-selected beachhead is e& frontline retail advisors and field technicians, using fixed low-consequence commands with fallback. | Product decision, not demand evidence. Stage 0 must select/validate one workflow and compare current alternatives. |

## External technical evidence

| ID | Verdict | Exact safe claim | Conditions / source |
|---|---|---|---|
| C07 | Amber | SilentWear reports 77.5±6.6% average cross-validated silent-command accuracy and 59.3±2.2% held-out-session accuracy. | **Preprint**, v2 2026-03-04; n=4, 14 differential neck sEMG channels, 8 commands plus rest, SpeechNet; study result, not project expectation (R26). |
| C08 | Amber | SilentWear reports 2.47 ms model inference, 63.9 µJ/inference, 20.5 mW total system power and estimated 27.1 h operation. | Same preprint; GAP9 at 240 MHz/0.65 V, 150 mAh battery estimate. **Inference excludes 0.8–1.4 s sensing window, endpointing, confirmation and output.** Does not prove behind-ear/all-day comfort. |
| C09 | Amber | MONA/LISA reports open-vocabulary silent-speech WER reduced from 28.8% to 12.2%. | **Preprint**, Gaddy single-speaker benchmark, LLM-integrated rescoring; not on-device/cross-user/project performance (R27). |
| C10 | Green | Gaddy & Klein peer-reviewed work established end-to-end silent facial-EMG speech synthesis/recognition research. | Single-speaker research line; no transfer/product claim (R03–R05). |
| C11 | Amber | An implanted study reported 23.8% online WER at a 125,000-word vocabulary and 62 attempted words/minute. | Willett et al., peer-reviewed Nature 2023; n=1 participant with ALS, two intracortical arrays, language model; attempted rate is not error-free throughput (R11). |
| C12 | Amber | In Willett’s 50-word condition, online WER was 9.1% vocal-attempt / 11.2% silent; at 125,000 words 23.8% / 24.7%. | Same individual implanted study. Vocabulary/LM/condition materially change WER; no non-invasive transfer. |
| C13 | Green | Cross-session, participant, motion, placement, fatigue, language and calibration are necessary evaluation dimensions. | SilentWear/companion preprints plus surveys; no claim they are solved. |
| C14 | Green | WER is `(substitutions + deletions + insertions) / reference words`; command accuracy is not WER. | Metric definition. Text normalization, vocabulary, language model and split must be stated. |
| C15 | Green | Meta’s wrist sEMG work/product is gesture/handwriting evidence, not silent-speech evidence. | Official Meta page + exact-commit repository; no speech-from-muscle claim (R28–R29). |
| C16 | Amber | Meta’s official page says a US$799 Neural Band bundle became available 2025-09-30 and references nearly 200,000 sEMG research participants. | Company material establishes announcement/availability only; US bundle, gestures not speech (R28). |
| C17 | Amber | Q Cue’s US patent family describes coherent-light facial micromovement sensing for subvocalisation-related applications. | Google Patents metadata: application US20240119938A1, grant publication US12204627B2; legal status requires counsel. No performance/product/infringement conclusion (R30). |
| C31 | Green | EarCommand, EchoSpeech and MuteIt are peer-reviewed research comparators using ear-canal deformation, active acoustic eyewear and twin-IMU jaw-motion sensing respectively. | DOI metadata/abstracts; task and sensing conditions differ. No product, performance-transfer or project claim (R38–R40). |
| C32 | Amber | Whispp describes mobile/desktop apps and SDKs for acoustic voice reconstruction. | Company material only; whispered/atypical acoustic input, not no-audio silent articulation. Availability, approval, clinical benefit and performance remain unverified (R41). |

## Privacy, safety, medical and data

| ID | Verdict | Exact safe claim | Evidence / boundary |
|---|---|---|---|
| C18 | Green | “No audio” does not establish privacy; raw signals, features and decoded text can all be sensitive. | NIST/privacy threat analysis; legal data classification is fact/jurisdiction dependent. |
| C19 | Amber | Explicit lock, contact-required sensing, raw retention/egress off, and confirmation are design targets. | Demo/product architecture; not implemented device security or certification. |
| C20 | Green | The project prohibits covert/bystander sensing, workplace emotion/productivity scoring, authentication, and unrelated secondary model training. | Project policy. EU AI Act official text confirms workplace/education emotion-inference prohibition with medical/safety exception. |
| C21 | Green | Current scope is not AAC, medical, clinical, emergency, payment, access-control, employment or safety use. | No participatory/clinical/intended-use/regulatory evidence; conventional fallback required. |
| C22 | Green | The project has no measured project silent-speech accuracy, WER, end-to-end hardware latency, power, calibration, participant/cohort, comfort or hardware number. | `realtime/` may expose per-run local model-forward latency only as a software diagnostic. Its “single speaker” is attributed source scope, not a project participant count. External numbers remain attributed. |
| C23 | Green | Static-demo values 0.84, 0.54, 0.91 and threshold 0.72 are authored interaction fixtures. `realtime/` phoneme-alignment scores are computed from official model emissions but uncalibrated and selected for interaction paths. | Never translate either kind into accuracy, representative evaluation or calibrated probability. Reference metadata is revealed only after inference. |
| C24 | Amber | No public Arabic surface-EMG silent-speech corpus was identified in this bounded review; cited sEMG performance exemplars are English. | Negative search, not proof of non-existence. Refresh before external use. |
| C25 | Amber | A bilingual/Gulf corpus could be a research asset only if purpose, consent, withdrawal, representation, labor separation, deletion, security and reuse rights are governed. | Hypothesis; no corpus, rights or owner exists. |
| C26 | Green | Repository/data/model licenses are separate and commercially decisive. | Gaddy code MIT at exact commit; official Gaddy dataset 4064409 and model 6747411 deposits CC BY 4.0; SilentWear code/data Apache-2.0; Meta assets checked are CC BY-NC / BY-NC-SA; named BCI repos lack LICENSE. Gaddy model/data are fetched to ignored local storage, not committed/vendored or owned by this project. |
| C27 | Amber | In-use and calibration data claims must be separated. | A future study may require explicitly consented paired audio; current project captures none. No “audio is never recorded” blanket promise for future calibration. |
| C28 | Green | UAE’s official portal confirms Federal Decree-Law No.45 of 2021 and an in-force date of 2022-01-02. | No compliance claim; Executive Regulations status and legal interpretation remain counsel TBD. |

## Commercial/source claims

| ID | Verdict | Exact safe claim | Evidence / boundary |
|---|---|---|---|
| C29 | Red | Customers, partners, users, team credentials, patents owned, pilots, traction, revenue, market size, unit economics, regional leadership, approval and acquisition likelihood. | No evidence supplied. Only the captain-approved **AED 1,000,000 fixed 90-day pilot fee** may be stated; later pricing/funding/exit amounts remain TBD. |
| C30 | Green | The supplied four-slide presentation was recovered by bounded HTTPS, critically reviewed, and not retained. | `provenance/source-record.md`; confidential/rights boundary; SHA-256 recorded. Source assertions are not evidence. |

## Captain decisions (resolved)

| ID | Decision | Approved state | Boundary |
|---|---|---|---|
| H01 | Primary beachhead | **e& frontline retail advisors and field technicians** | One low-consequence workflow still must be selected/tested; not current demand or a customer. |
| H02 | Primary business model | **Fixed-fee 90-day pilot → per-seat annual deployment if gates pass; strategic e& IP/governed-dataset funding and acquisition/exit optionality as upside** | Later per-seat, strategic and exit amounts remain TBD; rights negotiated; no promised return. |
| H03 | Pilot fee | **AED 1,000,000** | Applies only to fixed-fee 90-day pilot; not annual pricing, strategic funding, valuation or exit amount. |

Authority/source: [`../provenance/decisions.md`](../provenance/decisions.md).

## Prohibited wording

Do not state or imply: reads thoughts; hears inner speech; works behind the ear; open vocabulary; speaker independent; real time (without complete latency); on device about this project; “only text leaves” as implemented; anonymous/private/secure/compliant/certified; audible only to wearer; supports aphasia/ALS/laryngectomy/dysphonia; approved/cleared/exempt; customer/partner/pilot; or that another organization’s result validates this project.

## Upgrade procedure

To upgrade a project claim, retain a dated evidence packet: owner/authority and consent; protocol; hardware/software revision; participant/session/task split; raw-artifact checksum or governed location; metric code/definition; negative cases; reviewer; and decision. A paper, preprint, repository, patent or company announcement can motivate a study; none upgrades this project on its own.
