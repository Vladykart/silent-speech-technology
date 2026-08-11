# Evidence matrix

**Freeze:** 2026-07-28. Reference IDs resolve in [`references.md`](references.md). Empty or “not reported here” is preferable to an unsupported estimate.

## Technical evidence

| ID | Type | Modality / task | Participants & conditions | Reported result used here | Reproducibility / status | What it supports | What it does **not** support |
|---|---|---|---|---|---|---|---|
| E01 / R01 | peer-reviewed review | SSI field: EMG, articulatory, acoustic-adjacent, neural | heterogeneous literature through publication period | no performance number carried forward | DOI resolved; not independently replicated here | definitions, modality breadth, longstanding technical challenges | project feasibility or modern product maturity |
| E02 / R02 | peer-reviewed survey | biosignal-based spoken communication | heterogeneous studies | no performance number used | metadata verified | evaluation must be modality/task specific | a universal accuracy comparison |
| E03 / R03 | peer-reviewed conference paper | 8-channel facial/neck sEMG → synthesized audio; open/closed-vocabulary evaluation | single speaker, about 20 h total; silently articulated and vocalized/aligned conditions | ASR transcription WER of synthesized audio: 64%→4% in the paper’s easier condition and 88%→68% in its harder condition | official code/data/model fetched outside git on 2026-07-31; selected records and released mel/phoneme forward path run, but vocoder/ASR evaluation not reproduced | silent sEMG can synthesize intelligible speech in one personalized setup; exact released artifact path executes | direct command accuracy, cross-user/session, behind-ear, product, or project performance |
| E04 / R04 | peer-reviewed conference paper | improved facial sEMG → audio | same single-speaker corpus/research line; open-vocabulary intelligibility evaluation | abstract reports 25.8 percentage-point absolute improvement in paper-specific ASR intelligibility WER | official code line; not run | algorithmic progress in one setup | “25.8% accurate,” commercial readiness, transfer |
| E05 / R05, R16 | repository + model registry | sEMG synthesis/recognition code and pretrained artifact | exact commit; dependency stack names DeepSpeech 0.7 | README claims latest approx. 36% ASR-based WER; not a project result | code MIT; model/data records CC BY 4.0; strict checkpoint load/forward exercised; Python 3.12 adapter decodes trained phoneme head because legacy DeepSpeech is unavailable | artifact-level replay and licence-separation lesson | original full evaluation reproduction, turnkey product, maintained decoder, commercial rights bundle, project WER |
| E06 / R06 | peer-reviewed journal | under-chin ultrasound + lip video → speech | laboratory setup | no number used | DOI metadata | direct articulatory imaging is a serious SSI path | miniaturized/earable performance |
| E07 / R07–R09 | datasets + peer-reviewed papers | UTI/audio/lip video; UTI therapy; EMA/MRI/audio | multi-speaker/session corpora with different populations/tasks | corpus sizes not used as product evidence | landing pages/DOIs; data not downloaded | corpus/protocol exemplars and ground truth options | silent-only, clinical effectiveness, or licence equivalence |
| E08 / R10 | peer-reviewed review | imagined/attempted speech BCI | heterogeneous, often small/within-subject research | no number used | DOI registry metadata | neural speech is a distinct SSI branch | reliable consumer EEG mind reading |
| E09 / R11 | peer-reviewed journal | implanted intracortical attempted speech → text | one participant with ALS; two intracortical arrays; online decoder with LM; 50- and 125,000-word conditions | WER 9.1% / 23.8% vocal-attempt and 11.2% / 24.7% silent; average attempted rate 62 words/min | publisher + institutional full text checked; associated feasibility registry | leading individual implanted feasibility; vocabulary/condition materially affect WER | non-invasive sEMG expectation, population performance, approval, error-free throughput |
| E10 / R12 | peer-reviewed journal | implanted ECoG speech/avatar control | one clinical-research participant | no number used pending condition-level verification | DOI/Europe PMC metadata; associated registry | implanted ECoG can support high-bandwidth individual research | surface EMG, general clinical availability, approval |
| E11 / R13 | peer-reviewed journal | implanted speech neuroprosthesis | individual clinical research | no number used pending full-text condition verification | DOI/Europe PMC metadata | continued progress and calibration as explicit issue | a shipping product or this project’s timeline |
| E12 / R14–R15 | official clinical registries | intracortical/ECoG feasibility studies | BrainGate2: estimated 27; BRAVO: estimated 3; both Recruiting/Interventional at access | enrollment/status only, not performance | official APIs checked | trial/research-prototype status | regulatory approval or broad efficacy |
| E13 / R17 | repository/dataset, adjacent | bilateral wrist sEMG during touch typing | README: 1,135 sessions, 108 users, 346 hours | dataset scale only | exact commit; CC BY-NC-SA 4.0 / API `NOASSERTION`; no download | generic/personalized neuromotor HCI is an adjacent field | silent articulation, an sEMG speech product, a commercial licence |
| E14 / R21 | peer-reviewed demo paper | personalized facial/neck neuromuscular silent interface | paper-specific users/commands | no number used | DOI reached ACM access control | command-oriented personalized silent-interface precedent | independent replication, behind-ear/open-vocabulary/clinical product |
| E15 / R26, R35 | preprint + repository | 14-channel textile neck sEMG; 8 commands + rest; on-MCU top-1 classification | n=4; multi-day collection; global cross-validation vs leave-one-session-out; 15k-parameter CNN | silent accuracy 77.5±6.6% global CV and 59.3±2.2% held-out session. GAP9: 2.47 ms model inference, 63.9 µJ/inference; 20.5 mW system; 27.1 h estimated with 150 mAh | direct arXiv HTML checked; exact code commit Apache-2.0; not run/downloaded | closest command/wearable analogue; cross-session gap and edge feasibility under named setup | complete latency, all-day comfort, cross-user scale, behind-ear, open vocabulary, product or project performance |
| E16 / R27 | preprint + repository | open-vocabulary silent EMG with cross-modal model and LLM rescoring | Gaddy single-speaker benchmark | WER 28.8%→12.2% per abstract | exact code commit MIT; not run | research frontier and dependence on rescoring | streaming/on-device/cross-user/project result |
| E17 / R28–R29, R36 | peer-reviewed adjacent + company + repos | wrist sEMG gestures/handwriting; consumer wristband bundle | large-scale company research; not speech | no performance number carried into core deck | official product page and exact non-commercial code licences checked | sEMG sensor-class/product category context | silent speech, face/neck transfer, commercial code dependency |
| E18 / R30 | patent aggregator metadata | coherent-light facial micromovement sensing | patent application/grant family; no evaluated population | no performance number | application/grant event metadata checked; counsel required | optical category and FTO-review trigger | sEMG validation, product, infringement/validity/ownership-currentness |
| E19 / R38–R40 | peer-reviewed adjacent systems | ear-canal deformation / active acoustic eyewear / twin-IMU jaw-motion commands | paper-specific participants, tasks and sensing conditions | no performance number carried into the deck | DOI metadata/abstracts checked; not reproduced | named whole-task research comparators | product status, surface-EMG transfer, common-task ranking, or project performance |

### Performance-number notes

- **WER** is `(substitutions + deletions + insertions) / reference words`. It is decoder, normalization, vocabulary, language-model, and test-set dependent and can exceed 100%.
- Gaddy abstract numbers describe ASR transcription of synthesized audio under two paper-defined conditions; they are not two population accuracy estimates. They remain outside the core deck because full condition-level reproduction was not performed.
- Willett’s 62 words/minute is attempted speaking rate, not error-free throughput. The 23.8% online WER includes the 125,000-word language model and one participant’s evaluation.
- SilentWear’s 2.47 ms is model inference after an input window (0.8–1.4 s in the paper), not end-to-end command latency. Its 27.1 h value is an estimate with a named 150 mAh battery, not wear/comfort evidence.
- This project has **no measured project** WER, command accuracy, false accept/reject rate, calibration, participant, comfort, power or hardware number. The replay UI may show separate local model-forward and project-decoder times for one run only; both exclude recording duration, sensing, hardware, network, endpointing, confirmation and output and are not end-to-end product latency.

## Governance, product, and source evidence

| ID | Type | Evidence | Supports | Does not support |
|---|---|---|---|---|
| G01 / R18 | official framework | NIST Privacy Framework 1.0 | purpose/data-processing risk governance vocabulary | compliance, certification, or “private by design” |
| G02 / R19 | official framework | NIST AI RMF 1.0 | mapping/measuring/managing AI risks | model validation, legal compliance |
| G03 / R20 | official institutional report | WHO/UNICEF global assistive-technology report | access, systems, and user-centered assistive-technology importance | silent-speech clinical benefit |
| G04 / R14–R15 | official registry | recruiting interventional feasibility studies | strict distinction between study and approved product | approval, availability, efficacy |
| G05 / R22 | captain source | four-slide confidential pitch | what the prior narrative asserts | technical, customer, corporate, or financial truth |
| G06 / R23 | local repository | deterministic software tests and static validators | tomorrow interaction demo exists and is inspectable | sensors, models, accuracy, users, browser-rendered QA |
| G07 / R41 | official company page | Whispp describes mobile/desktop apps and SDKs using acoustic input | company-described offering category | independent performance, availability, approval, clinical benefit, or no-audio silent speech |

## Missing evidence register

| Question | Current value | Evidence required |
|---|---|---|
| Does the target workflow exist? | Unknown | consented discovery, alternatives, baseline and user preference |
| Which exact muscles/sites carry stable signal? | Unknown | protocol, research rig, placement/channel ablation, remove/reapply sessions |
| Command set / language | TBD | user co-design and error-harm grammar review |
| Within-user/session performance | Missing | frozen participant-level test and command/reject metrics |
| Cross-session/user transfer | Missing | day/session/participant holdouts; adaptation burden |
| End-to-end latency/power | Missing | named hardware/model profiling, p50/p95, battery/thermal |
| Comfort/accessibility | Missing | target-user co-design, adverse-event and abandonment measures |
| Privacy/security | Design targets only | approved data flow, threat model, controls and adversarial tests |
| Regulatory/clinical status | None | intended-use and jurisdiction review; participatory/clinical route if pursued |
| Customer/partner/traction | None | approved agreements and attributable evidence |
| Price/market/unit economics | TBD | buyer research and bottom-up operating model |
| Patent/FTO | Not assessed | counsel-led claim/territory/expiry/assignment search; no ownership inference from keywords |
