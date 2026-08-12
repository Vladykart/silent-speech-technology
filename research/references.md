# References and source register

**Access date:** 2026-07-28 for all entries unless stated.
**Legend:** peer reviewed (PR); clinical registry (REG); standard/framework (STD); repository (REPO); dataset/model registry (DATA); official institutional/project (INST); company material (MKT); captain-supplied source (SRC). `Checked` means bounded URL/metadata inspection succeeded; it does not mean independent replication.

## Foundational and modality evidence

**R01 · PR · Checked (DOI resolved).** Denby, B.; Schultz, T.; Honda, K.; Hueber, T.; Gilbert, J. M.; Brumberg, J. S. “Silent Speech Interfaces.” *Speech Communication* 52(4), 270–287 (2010). https://doi.org/10.1016/j.specom.2009.08.002
Boundary: field review; does not validate this project or a particular wearable placement.

**R02 · PR · Metadata checked.** Schultz, T.; Wand, M.; Hueber, T.; Krusienski, D. J.; Herff, C.; Brumberg, J. S. “Biosignal-Based Spoken Communication: A Survey.” *IEEE/ACM Transactions on Audio, Speech, and Language Processing* 25(12), 2257–2271 (2017). https://doi.org/10.1109/TASLP.2017.2752365
Boundary: survey across biosignals; maturity and metrics are heterogeneous.

**R03 · PR · Checked (ACL Anthology).** Gaddy, D.; Klein, D. “Digital Voicing of Silent Speech.” *EMNLP 2020*, 5521–5530. https://doi.org/10.18653/v1/2020.emnlp-main.445 and https://aclanthology.org/2020.emnlp-main.445/
Boundary: facial sEMG research and paper-specific ASR transcription WER; not a generic user, form-factor, or product result.

**R04 · PR · Checked (ACL Anthology).** Gaddy, D.; Klein, D. “An Improved Model for Voicing Silent Speech.” *ACL-IJCNLP 2021, Short Papers*, 175–181. https://doi.org/10.18653/v1/2021.acl-short.23 and https://aclanthology.org/2021.acl-short.23/
Boundary: same research line; an absolute improvement is not an accuracy claim for this project.

**R05 · REPO · Checked via `gh-axi`.** Gaddy, D. `dgaddy/silent_speech`, commit `a89357c2086609b432919b9d14ffc0be5d8983d5` (commit date 2023-12-11). https://github.com/dgaddy/silent_speech/tree/a89357c2086609b432919b9d14ffc0be5d8983d5
Repository reports MIT for code. README points to separate data/models and legacy DeepSpeech/CTC-language-model assets. Exact files, blob SHAs, commit metadata, architecture summary and retained notice: [`../provenance/upstream-reference.md`](../provenance/upstream-reference.md). No clone, submodule, data, model, sample, or dependency was downloaded; code reproducibility was not exercised.

**R06 · PR · DOI metadata checked.** Hueber, T.; Benaroya, E.-L.; Chollet, G.; Denby, B.; Dreyfus, G.; Stone, M. “Development of a Silent Speech Interface Driven by Ultrasound and Optical Images of the Tongue and Lips.” *Speech Communication* 52(4), 288–300 (2010). https://doi.org/10.1016/j.specom.2009.11.004
Boundary: laboratory UTI/lip imaging; does not support miniaturized or behind-ear sensing.

**R07 · DATA/PR · Dataset landing checked.** Ribeiro, M. S.; Sanger, J.; Zhang, J.-X.; Eshky, A.; Wrench, A.; Richmond, K. “TaL: a synchronised multi-speaker corpus of ultrasound tongue imaging, audio, and lip video.” *IEEE SLT 2021*. Dataset: https://doi.org/10.7488/ds/2992 ; paper: https://doi.org/10.1109/SLT48900.2021.9383532
Boundary: synchronized articulatory corpus; check item-level licenses and participant uses before reuse. Not downloaded.

**R08 · DATA/PR · Project page checked.** Eshky, A. et al. “UltraSuite: A Repository of Ultrasound and Acoustic Data from Child Speech Therapy Sessions.” *Interspeech 2018*. https://doi.org/10.21437/Interspeech.2018-1736 ; project: https://ultrasuite.github.io/
Boundary: clinical/therapy ultrasound + acoustic resource; not silent-only and not project performance. Not downloaded.

**R09 · DATA/PR · DOI listed.** Narayanan, S. et al. “Real-Time Magnetic Resonance Imaging and Electromagnetic Articulography Database for Speech Production Research (TC).” *IEEE Journal of Selected Topics in Signal Processing* 8(2), 242–251 (2014). https://doi.org/10.1109/JSTSP.2014.2304092
Boundary: synchronized research database/ground truth, not everyday EMA product evidence.

**R10 · PR · Registry metadata checked.** Cooney, C.; Folli, R.; Coyle, D. “Neurolinguistics Research Advancing Development of a Direct-Speech Brain-Computer Interface.” *iScience* 8, 103–125 (2018). https://doi.org/10.1016/j.isci.2018.09.016
Boundary: BCI review; non-invasive imagined-speech findings require task/participant/confound scrutiny.

**R11 · PR · Publisher/Europe PMC full text checked.** Willett, F. R. et al. “A High-Performance Speech Neuroprosthesis.” *Nature* 620, 1031–1036 (2023). https://doi.org/10.1038/s41586-023-06377-x ; institutional full text identifier PMC10468393.
Exact number boundary: one participant with ALS, two intracortical arrays, attempted speech, language-model-assisted online decoding. Paper reports online WER 23.8% (125,000-word vocal-attempt), 24.7% (125,000 silent), 9.1% (50-word vocal-attempt), 11.2% (50-word silent), and average attempted rate 62 words/min. These are not non-invasive/product results.

**R12 · PR · Publisher/registry metadata checked.** Metzger, S. L. et al. “A High-Performance Neuroprosthesis for Speech Decoding and Avatar Control.” *Nature* 620, 1037–1046 (2023). https://doi.org/10.1038/s41586-023-06443-4 ; PMCID PMC10826467.
Boundary: implanted ECoG, an individual participant, clinical research; no number from this paper is used in the core deck.

**R13 · PR · Registry metadata checked.** Card, N. S. et al. “An Accurate and Rapidly Calibrating Speech Neuroprosthesis.” *New England Journal of Medicine* 391, 609–618 (2024). https://doi.org/10.1056/NEJMoa2314132 ; PMCID PMC11328962.
Boundary: implanted individual clinical research; “accurate” is the paper title, not a project claim. No result number is used here pending full-condition verification.

**R14 · REG · Checked.** ClinicalTrials.gov `NCT00912041`, “BrainGate2: Feasibility Study of an Intracortical Neural Interface System for Persons With Tetraplegia.” https://clinicaltrials.gov/study/NCT00912041
API showed Recruiting, Interventional, estimated enrollment 27, updated 2026-06-01. Registry status is not device approval or a commercial-product claim.

**R15 · REG · Checked.** ClinicalTrials.gov `NCT03698149`, “ECoG BMI for Motor and Speech Control.” https://clinicaltrials.gov/study/NCT03698149
API showed Recruiting, Interventional, estimated enrollment 3, updated 2026-05-05. Registry status is not approval.

**R16 · DATA · Checked (Zenodo metadata).** “Voicing Silent Speech Models.” Zenodo record/version DOI https://doi.org/10.5281/zenodo.6747411 (2022). Metadata labels CC BY 4.0; one `pretrained_models.zip`, 253,447,725 bytes, MD5 `2e172d2ff74126ca0e68d0f117d6466a`.
Not downloaded. Artifact license does not settle upstream dependency, training-data, patent, privacy, or intended-use rights.

**R17 · REPO/DATA · Checked via `gh-axi`.** Meta/Facebook Research `emg2qwerty`, commit `3200d91eeb952cbed1f278e47d0cc56928334fd1` (2025-06-11). https://github.com/facebookresearch/emg2qwerty/tree/3200d91eeb952cbed1f278e47d0cc56928334fd1
README describes wrist sEMG during QWERTY touch typing: 1,135 sessions, 108 users, 346 hours. Exact-commit LICENSE is CC BY-NC-SA 4.0; GitHub API reports `NOASSERTION`. Adjacent neuromotor HCI evidence only—not speech, silent speech, product availability, or a commercial-ready dependency. No data/model downloaded.

**R18 · STD · Checked (official NIST).** NIST, *Privacy Framework: A Tool for Improving Privacy through Enterprise Risk Management*, Version 1.0 (2020). https://www.nist.gov/privacy-framework
Governance aid, not certification or jurisdiction-specific legal advice.

**R19 · STD · DOI redirect checked with HTTPS limitation.** NIST, *Artificial Intelligence Risk Management Framework (AI RMF 1.0)*, NIST AI 100-1 (2023). https://doi.org/10.6028/NIST.AI.100-1
Risk framework, not validation or certification.

**R20 · INST · Checked (WHO).** WHO and UNICEF, *Global Report on Assistive Technology* (2022). https://www.who.int/publications/i/item/9789240049451
Supports the importance of access and user-centered assistive-technology systems; does not validate silent speech or this product.

**R21 · PR · DOI reached publisher access control.** Kapur, A.; Kapur, S.; Maes, P. “AlterEgo: A Personalized Wearable Silent Speech Interface.” *ACM IUI 2018*. https://doi.org/10.1145/3172944.3172977
Personalized research prototype; title does not mean a shipping, clinically approved, or independently replicated product.

## Project/source evidence

**R22 · SRC · Checked and not retained.** Captain-supplied “The Quiet Channel” four-slide PPTX, retrieved 2026-07-28 through a confidential capability URL that is intentionally omitted. Provenance, SHA-256, rights boundary, and critical review: [`../provenance/source-record.md`](../provenance/source-record.md).
Confidential source-deck assertions are not independent evidence.

**R23 · REPO · Local.** This repository, tomorrow demo and validators. See [`../demo/README.md`](../demo/README.md), [`claim-boundary.md`](claim-boundary.md), and [`claim-ledger.md`](claim-ledger.md).
Supports only interaction/software behavior and documentation status.

**R24 · REPORT · Critically consumed.** Parallel evidence scout report, 2026-07-28, SHA-256 `465ecdca024a3864e001f785124afb99a6ac1c1296b192e747d491c65a04dcee`. Critical acceptance/rejection record: [`scout-review.md`](scout-review.md).
Not an authority; load-bearing findings were independently checked where feasible.

**R25 · DECISION · Captain.** Beachhead/business/fee decisions, 2026-07-28. Durable repository record: [`../provenance/decisions.md`](../provenance/decisions.md).
Decision evidence, not customer, price-discovery, traction, or technical validation.

**R26 · PREPRINT/REPO · Direct full HTML + exact commit checked.** Spacone, G. et al. “SilentWear: an Ultra-Low Power Wearable System for EMG-based Silent Speech Recognition.” arXiv:2603.02847v2 (2026-03-04). https://arxiv.org/abs/2603.02847 and https://arxiv.org/html/2603.02847v2 . Code: `pulp-bio/SilentWear` commit `b341c30b3a988e5ef871567f8a752084cefa1f7e`, Apache-2.0.
Numbers used: n=4, 14 differential neck channels, 8 commands plus rest, 15k-parameter SpeechNet; average silent accuracy 77.5±6.6% global cross-validation and 59.3±2.2% leave-one-session-out. GAP9 at 240 MHz/0.65 V: 2.47 ms **inference**, 63.9 µJ/inference; 20.5 mW total and estimated 27.1 h with 150 mAh battery. Windows are 0.8–1.4 s; inference is not complete latency. Preprint, not project expectation; comfort/production not established.

**R27 · PREPRINT/REPO · Direct abstract + exact commit checked.** Benster, T. et al. “A Cross-Modal Approach to Silent Speech with LLM-Enhanced Recognition.” arXiv:2403.05583 (2024). https://arxiv.org/abs/2403.05583 . Code: `tbenst/silent_speech` commit `177a844aec78171bf8c255824756687efbff1e09`, MIT.
Abstract reports open-vocabulary silent WER 28.8%→12.2% on the Gaddy 2020 benchmark using LLM-integrated scoring. Single-speaker benchmark; preprint; not on-device/cross-user/project performance.

**R28 · MKT · Official company material checked.** Meta, “Meta Ray-Ban Display: AI Glasses With an EMG Wristband,” published 2025-09-17, updated 2025-09-30. https://about.fb.com/news/2025/09/meta-ray-ban-display-ai-glasses-emg-wristband/
Says the US$799 bundle became available 2025-09-30 and Neural Band follows EMG research with nearly 200,000 participants. Inputs described are hand/finger gestures; this is not a silent-speech performance source.

**R29 · PR/REPO · DOI/repository checked.** “A generic non-invasive neuromotor interface for human-computer interaction.” *Nature* (2025). https://doi.org/10.1038/s41586-025-09255-w . Code: `facebookresearch/generic-neuromotor-interface` commit `b6bf250e2be5a67b23488104335373cdb87a15c9`; exact-commit LICENSE is CC BY-NC 4.0.
Wrist neuromotor/gesture HCI, not speech. Non-commercial code terms mean no commercial dependency assumption.

**R30 · PATENT AGGREGATOR · Metadata checked; counsel required.** Q Cue Ltd, “Using a wearable to interpret facial skin micromovements.” Application publication `US20240119938A1`; Google Patents records grant publication `US12204627B2` on 2025-01-21 and labels status active with an explicit no-legal-conclusion warning. https://patents.google.com/patent/US20240119938A1/en
Metadata identifies Q Cue Ltd, inventors Yonatan Wexler and Avi Barliya, and coherent-light sensing. Supports an FTO gate only; no infringement, ownership-currentness, validity, product, or performance conclusion.

**R31 · MKT/PRESS · Partially checked.** Apple/Q.ai acquisition context (2026-01-29) was reported by reputable press and captured in the scout report; direct Reuters retrieval returned HTTP 401 during independent check. Apple terms were not disclosed.
Core technical claims do not depend on price/headcount. Deck says optical category activity/acquisition context only and cites R30 for mechanism.

**R32 · GOV · Official UAE portal checked.** UAE, “Data protection laws.” https://u.ae/en/about-the-uae/digital-uae/data/data-protection-laws
Confirms Federal Decree-Law No.45 of 2021 and in-force date 2022-01-02. Does not establish project compliance or resolve Executive Regulations status.

**R33 · LAW · Official Journal text checked.** Regulation (EU) 2024/1689 (AI Act), Article 5(1)(f). https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng
Official text prohibits specified AI emotion inference in workplace/education except medical/safety reasons; prohibitions apply from 2025-02-02. Legal applicability still requires counsel.

**R34 · DATA · Zenodo API metadata checked.** Gaddy, D. “Silent Speech EMG,” v1.0. https://doi.org/10.5281/zenodo.4064409 . Metadata: CC BY 4.0; archive 3,919,507,637 bytes; MD5 `7f97d2182b896652999b1b2d0c69fd7b`.
Not downloaded. Data license does not settle dependencies, data-subject rights, patents, intended use, or this project.

**R35 · REPO · Checked via `gh-axi`.** `pulp-bio/SilentWear`, commit `b341c30b3a988e5ef871567f8a752084cefa1f7e`, Apache-2.0 code. https://github.com/pulp-bio/SilentWear/tree/b341c30b3a988e5ef871567f8a752084cefa1f7e
No clone/model/data download or reproduction. Images have a separate license file; no media reused.

**R36 · REPO · Checked via `gh-axi`.** Meta repositories: `generic-neuromotor-interface` commit `b6bf250e2be5a67b23488104335373cdb87a15c9`, CC BY-NC 4.0; `emg2qwerty` commit `3200d91eeb952cbed1f278e47d0cc56928334fd1`, CC BY-NC-SA 4.0.
Non-commercial terms; adjacent wrist HCI, not speech.

**R37 · REPO · Checked via `gh-axi`.** `fwillett/speechBCI` commit `522a9605ccf0818def80b6fd80007598e790408e` and `Neuroprosthetics-Lab/nejm-brain-to-text` commit `980a5b7e96392210edf976d76bdb5d15d2e0e62b` had no LICENSE file in root at access.
No default reuse permission is assumed; neither was downloaded or used.

**R38 · PR · Crossref metadata/abstract checked.** Jin, Y. et al. “EarCommand: ‘Hearing’ Your Silent Speech Commands In Ear.” *Proceedings of the ACM on Interactive, Mobile, Wearable and Ubiquitous Technologies* (2022). https://doi.org/10.1145/3534613
Earphone-based ear-canal deformation command research; not a shipping product, surface-EMG result, independent replication, or project result. No performance number is carried into the deck.

**R39 · PR · Crossref metadata checked.** Zhang, R. et al. “EchoSpeech: Continuous Silent Speech Recognition on Minimally-obtrusive Eyewear Powered by Acoustic Sensing.” *CHI 2023*. https://doi.org/10.1145/3544548.3580801
Active acoustic sensing on research eyewear; not a no-audio system, product-availability source, surface-EMG result, or project result. No performance number is carried into the deck.

**R40 · PR · Crossref metadata/abstract checked.** Srivastava, T. et al. “MuteIt: Jaw Motion Based Unvoiced Command Recognition Using Earable.” *Proceedings of the ACM on Interactive, Mobile, Wearable and Ubiquitous Technologies* (2022). https://doi.org/10.1145/3550281
Twin-IMU jaw-motion command research; not a shipping product, full speech system, surface-EMG result, or project result. No performance number is carried into the deck.

**R41 · MKT · Official company page checked.** Whispp, product overview. https://whispp.com/
The company describes mobile/desktop apps and SDK offerings for reconstructing voice from whispered or atypical acoustic input. This establishes company-described offering status only—not independent performance, target-jurisdiction availability, approval, clinical benefit, or a no-audio silent-speech system.

## Corporate and market-source rule

Specific company shipping, acquisition, price, headcount, approval, customer, and regional-leadership statements from the supplied deck are omitted from the core evidence story unless an authoritative or reputable source and exact status are recorded. Corporate claims—when added—must be tagged `MKT` and may establish only what the organization announced, not independent technical performance. No patent freedom-to-operate or ownership search has been completed.
