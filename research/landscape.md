# Silent-speech technology landscape

**Evidence freeze:** 2026-07-28 · **Status:** decision support, not a systematic review. See [`METHODS.md`](METHODS.md), [`evidence-matrix.md`](evidence-matrix.md), and [`references.md`](references.md).

## 1. Definitions and boundaries

“Silent speech” is not one signal or task. Denby et al. [R01] describe interfaces that enable speech communication without an audible acoustic signal. This repository uses the following operational boundaries:

| Term | Operational definition | Included signal | Common category error |
|---|---|---|---|
| **Silent speech interface (SSI)** | Converts non-acoustic or non-audible correlates of deliberate speech articulation into text or synthesized speech | articulatory movement, neuromuscular activity, tissue vibration, or neural activity | Calling every quiet input “silent speech” |
| **Subvocal / silently articulated speech** | The user deliberately forms or attempts speech with little/no audible output; muscle/articulator activity may remain | sEMG, in-ear/intraoral contact signals, ultrasound, EMA, optical, RF; sometimes neural | Equating it with private thought or assuming normal voiced-speech signals transfer unchanged |
| **Whispered speech** | Audible aperiodic airflow speech, normally without vocal-fold vibration | ordinary/contact microphones and acoustic ASR | Saying “no audio is recorded” when a microphone is used |
| **Imagined speech / inner speech** | Speech is mentally rehearsed without required peripheral articulation | EEG/MEG or implanted neural recording in research | Calling a system that senses articulation “thought reading,” or claiming robust open-vocabulary EEG decoding |
| **Speech neuroprosthesis** | Implanted or non-invasive BCI intended to decode attempted/imagined speech or drive speech output | ECoG, intracortical arrays; EEG/MEG research | Transferring a result from one implanted participant to a wearable EMG product |
| **Assistive AAC** | Tools/strategies that augment or replace communication for a person with communication disability | boards, switches, eye gaze, typing, acoustic or biosignal interfaces | Treating all diagnoses or access needs as interchangeable; removing reliable fallback |
| **Command/control** | Maps deliberate input to a bounded intent/action set | any modality, usually lower language burden | Advertising a closed grammar as open-vocabulary conversation |

A system can cross boundaries: a laryngectomy user may articulate silently or produce a whisper; a person with paralysis may attempt speech without visible movement; a contact microphone still captures mechanical/acoustic energy. Papers must be classified by what participants actually did.

## 2. Sensing modalities

### 2.1 Comparative decision matrix

| Modality | What it senses / placement | Strengths | Load-bearing limits | Maturity for this project |
|---|---|---|---|---|
| **Surface EMG (sEMG)** | electrical activity at skin over face, jaw, chin, neck; wrist sEMG is adjacent HCI, not speech evidence | no air audio; deliberate articulation research; peer-reviewed/code/data exemplars [R03–R05]; a four-person neckband command preprint demonstrates named edge hardware [R26] | placement/contact, cross-talk, sweat, facial motion, fatigue, session drift; personalization; visible electrodes; electrical safety; literature setups do not prove behind-ear placement | **Selected for first feasibility rig**, not production form factor |
| **In-ear EMG / earable neuromuscular** | electrodes in/around ear canal or auricular/temporal region | potentially discreet and mechanically stable | limited access to speech muscles, ear anatomy/fit, skin contact, occlusion, hygiene; sparse evidence for speech compared with face/neck | comparison/placement-ablation track only |
| **Intraoral EMG / tongue/palate sensors** | electrodes or contact sensors inside mouth | proximity to tongue/jaw activity; less visual | saliva, comfort, hygiene, fit, materials, choking/electrical risk, dental variation, cleaning and regulatory burden | not tomorrow beachhead |
| **Ultrasound tongue imaging (UTI)** | transducer under chin images tongue surface; often paired with lip video | direct articulatory geometry; substantial laboratory literature and datasets [R06–R08] | probe stabilization, size/coupling, head motion, missing palate/hidden tongue surfaces, compute, speaker/session transfer; lip camera changes privacy profile | strong research comparator; poor first wearable form factor |
| **Electromagnetic articulography (EMA)** | tracked coils/sensors glued to tongue/lips/jaw in magnetic field | precise kinematic ground truth and alignment research [R09] | invasive setup, tethering, calibration, coil attachment and specialized field generator; not practical everyday input | ground-truth instrument, not product sensor |
| **Accelerometer / contact microphone / NAM** | skin vibration and structure-borne sound near throat/ear/mastoid | simple hardware; can capture whisper/non-audible murmur and speech vibration | often still speech audio/mechanical content; contact noise, motion, clothing, environmental coupling; “no microphone/audio” claim invalid | acoustic-adjacent baseline, not privacy shortcut |
| **Optical lip/tongue imaging** | camera, infrared, dental/oral optical sensor, or mouthpiece tracks articulators | rich movement signal; mature visual-speech research | line-of-sight, lighting, occlusion, camera acceptability, visible articulation, sensitive imagery; tongue requires intraoral view | benchmark/controlled research, not discreet beachhead |
| **RF / radar** | Doppler/range/phase changes from moving facial, throat, or tongue structures | contactless; can operate without visible light | weak small-motion returns, multipath, body/environment motion, placement, interference, privacy/bystander capture; research hardware/tasks vary widely | exploratory; no product claim or selected evidence baseline |
| **EEG** | scalp potentials during imagined/attempted speech | non-invasive neural access | low spatial resolution/SNR, artifacts, many electrodes/setup, small datasets, closed-set and within-subject evaluation common; semantic leakage claims need exceptional proof | research-only, not near-term decoder |
| **MEG** | external magnetic fields from neural activity | higher-quality research measurements than many scalp systems | shielded room, cryogenic/OPM infrastructure, head motion and cost; not wearable product path today | neuroscience instrument only |
| **ECoG** | cortical surface electrodes implanted surgically | high spatial/temporal signal; leading attempted-speech demonstrations [R11–R13] | neurosurgery and clinical risk; individual anatomy/tasks; long-term stability, access, clinical trial/regulatory burden | clinical research; non-transferable comparator |
| **Intracortical arrays** | penetrating microelectrodes record neural activity | high-resolution speech motor decoding; large-vocabulary individual demonstrations [R11, R13] | invasive surgery, array longevity, calibration, single/few participants, clinical infrastructure | clinical feasibility research, not competitor hardware for first beachhead |

### 2.2 Modality decision

**Decision:** start with multi-channel face/jaw/neck sEMG on a transparent research rig, for a bounded command set, with per-user and per-session calibration.

**Why:** it is the least implausible path to an offline, deliberate, non-audio command study using accessible research instrumentation; there are peer-reviewed speech studies and an exact-version open repository [R03–R05]. It also exposes the hard problem early: placement and transfer.

**Why not behind the ear yet:** form factor is an output of channel/placement ablation. The captain’s source supplies no evidence that auricular placement retains enough articulatory signal.

**Why not assistive AAC first:** communication failure is high consequence; intended users have heterogeneous motor/language needs; a co-designed clinical program and reliable fallback are required.

**Why not imagined-speech EEG:** the evidence/engineering gap to reliable open-vocabulary, low-setup communication is larger, and “thought reading” framing creates acute consent/surveillance risk.

**Fallback decision:** if opt-in sEMG does not satisfy pre-registered signal, comfort, calibration, cross-session, and workflow gates, compare a throat contact-signal baseline and UTI laboratory baseline before changing product claims.

## 3. End-to-end signal and product pipeline

A credible study reports each stage rather than only a final transcript:

1. **Intent and consent:** visible active state; deliberate start/stop; non-biometric input alternative; task prompt separated from ground truth.
2. **Acquisition:** sensor/AFE model, channel sites and photos/diagram, reference, gain, filters, sampling rate/bit depth, impedance/contact, synchronization, electrical isolation, device revision.
3. **Quality control:** saturation/dropout, mains/interference, channel contact, motion/chewing/swallowing/facial-expression confounds, session/environment labels.
4. **Preprocessing:** causal/non-causal filters, normalization scope, rectification/envelope or learned frontend, segmentation and end-pointing. Offline look-ahead must not be reported as live latency.
5. **Representation:** time/frequency EMG features or learned embeddings; articulatory/neural features as appropriate.
6. **Decoder:** closed command classifier, character/phoneme/token sequence model, or speech-feature synthesis. State whether the language model sees a constrained grammar.
7. **Calibration/personalization:** participant/session data and time, adaptation method, prompts, repetitions, and whether test utterances leak into training.
8. **Uncertainty:** calibrated score/coverage analysis, abstention threshold, alternative candidates, out-of-vocabulary behavior, artifact detector.
9. **Human gate:** user sees/hears candidates, confirms/corrects/rejects, times out, or switches input.
10. **Output:** text/synthesized speech/sandbox command; authorization remains separate from recognition.
11. **Audit and deletion:** event and error logs use minimum necessary data; raw retention off unless approved; withdrawal/deletion path tested.

### Realistic compute/hardware statement

Compute depends on channel count, sample rate, model, beam search, synthesis, and latency target. A small command classifier may fit on embedded hardware; open-vocabulary decoding plus language model/synthesis may need phone-class or larger compute. **No on-device claim is supportable until** a named hardware revision is profiled for end-to-end p50/p95 latency, memory, power/thermal behavior, reject logic, and quality loss. “On device” also needs network/data-flow verification and secure update/key design.

## 4. Evaluation that survives diligence

### 4.1 Metrics

| Metric | Definition / report requirement | Failure mode |
|---|---|---|
| Command accuracy | correct accepted commands / all in-vocabulary command trials; include confusion matrix | hiding rejected trials or class imbalance |
| False accept rate | unintended/out-of-vocabulary/artifact trials incorrectly emitted / such trials | evaluating only prompted valid commands |
| False reject rate | valid trials rejected / valid trials | claiming safety by rejecting everything |
| Coverage / selective risk | fraction accepted vs error among accepted across thresholds | selecting threshold on test set |
| WER | `(substitutions + deletions + insertions) / reference words` with text normalization and LM stated | calling `1-WER` “accuracy”; comparing vocabulary/LM/test sets |
| CER / phoneme error | same edit-distance construction over characters/phonemes | using an easier unit without disclosure |
| Intelligibility of synthesized speech | blinded human transcription WER and/or preregistered listening measure; ASR-WER named as proxy | treating one ASR engine as human intelligibility |
| Latency | acquisition window + endpointing + compute + candidate display + confirmed output; p50/p95 and hardware | reporting only model inference or using future context |
| Throughput | correctly completed task units/time including rejection/correction | reporting attempted articulation rate as effective rate |
| Calibration | calibration time, prompts, repetitions, and decay across sessions | excluding setup from user cost |
| Comfort/accessibility | validated/user-defined measures, adverse events, skin/hygiene burden, abandonment | “wearable” inferred from a short lab session |

### 4.2 Split design

Report at least:

- **within-session, within-user** (easiest; establishes only immediate feasibility);
- **new utterances**, with prompt/sentence duplication controlled;
- **cross-session within-user**, including remove/reapply and day separation;
- **cross-user zero-shot** and **adapted-user**, separately;
- **cross-language/dialect**, only where recruitment/training supports it;
- stationary/quiet vs motion/work-context; fresh vs sweat/fatigue/electrode-shift conditions.

Use participant-level separation for generalization claims. Sequence windows from one utterance/session must not straddle train/test. Report per-participant distributions, not only pooled frames. Freeze preprocessing, grammar, threshold, and exclusion rules before final test.

### 4.3 Disconfirming evidence and stressors

An honest pilot tries to break the decoder with:

- normal facial expressions, chewing, swallowing, coughing, head turns, walking, speaking aloud, and silence;
- electrode removal/reapplication, contact loss, sweat, dry skin, facial hair and varied anatomy;
- repeated use/fatigue, fast/slow articulation, corrections, code-switching and out-of-vocabulary phrases;
- identical/similar commands with asymmetric harm (“confirm” vs “cancel”);
- replay/injection, unplugged/swapped channels, corrupted packets, stale model/config, and lost output;
- user preference for touch, shortcut, whisper, gaze, switch, or no system at all.

A good negative result—e.g., unacceptable calibration or unstable cross-session rejection—is a roadmap decision, not a demo failure to hide.

## 5. Evidence state and reproducibility

### Leading exemplars, not a league table

- **Silent facial EMG:** Gaddy & Klein’s peer-reviewed EMNLP 2020 and ACL 2021 work [R03, R04] reports open-vocabulary synthesis/recognition research in a single-speaker line. The official MIT-licensed code at commit `a89357c2086609b432919b9d14ffc0be5d8983d5` points to separate Zenodo data/model records [R05, R34]. Reproduction requires legacy assets and substantial dependencies; this project did not download or run them.
- **Wearable command sEMG:** SilentWear v2 [R26] is the closest analogue found: preprint, n=4, 14 differential neck channels, eight commands plus rest. Average silent top-1 accuracy was 77.5±6.6% in global cross-validation and 59.3±2.2% with a held-out session. GAP9 model inference was 2.47 ms / 63.9 µJ; total system power 20.5 mW and 27.1 h battery life was estimated with 150 mAh. Its 0.8–1.4 s windows mean 2.47 ms is not complete latency. This exposes cross-session drift; it does not prove all-day comfort, cross-user transfer, behind-ear placement, a product, or this project.
- **Open-vocabulary preprint frontier:** MONA/LISA [R27] reports 12.2% WER on the Gaddy single-speaker benchmark with LLM-integrated rescoring. It is not cross-user, streaming/on-device or product evidence.
- **Ultrasound/lip imaging:** Hueber et al. [R06] demonstrates a laboratory articulatory route. TaL [R07] and UltraSuite [R08] are useful corpus exemplars; they are not behind-ear, silent-only, product, or clinical validations.
- **EMA:** USC-TIMIT [R09] is a synchronized acoustic/articulatory corpus and ground-truth resource, not proof of silent wearable use.
- **Non-invasive neural:** reviews [R10] show imagined/attempted speech decoding is an active BCI topic; small, within-subject, closed-set studies and artifact/confound risks limit product inference.
- **Implanted neural:** Willett et al. [R11], Metzger et al. [R12], and Card et al. [R13] are leading individual clinical-research demonstrations. ClinicalTrials.gov lists the associated BrainGate2 and BRAVO studies as recruiting interventional feasibility studies, not approved speech products [R14, R15].

### One carefully bounded frontier number

Willett et al. [R11] studied **one participant with ALS** using **two implanted intracortical microelectrode arrays** and a language-model-assisted decoder. Online results included:

- 23.8% WER for a 125,000-word vocabulary in the paper’s vocal-attempt condition (24.7% in its silent condition);
- 9.1% WER for a 50-word vocabulary in the vocal-attempt condition (11.2% silent);
- average attempted-speech rate of 62 words/minute.

WER is edit errors divided by reference words. The speaking rate is not error-free throughput. These results are participant-, implant-, corpus-, decoder-, and language-model-specific and provide **no performance expectation** for non-invasive sEMG or this project.

### Dataset/software licence rules

Before use, record separately: code license, dataset license/terms, model license, pretrained dependency terms, consented uses, commercial restriction, attribution/share-alike, and withdrawal obligations. Examples:

- `dgaddy/silent_speech` code is MIT at the exact commit above [R05]. Its README points to Zenodo data; the data terms must be checked at the record, not inferred from the code license.
- Zenodo record 6747411 labels pretrained model artifacts CC BY 4.0 [R16]; dependencies and training-data rights still require review. The 253,447,725-byte model archive was **not downloaded**.
- `pulp-bio/SilentWear` code is Apache-2.0 at commit `b341c30b3a988e5ef871567f8a752084cefa1f7e`; paper/data/image/dependency terms remain separate [R35]. It was not cloned or run.
- `facebookresearch/generic-neuromotor-interface` and `emg2qwerty` are adjacent wrist HCI, not silent speech. Exact-commit licenses are CC BY-NC and CC BY-NC-SA respectively, so they are not drop-in commercial dependencies [R36]. No data/models were downloaded.
- Two named implanted-BCI repositories lacked root LICENSE files at checked commits; no default permission is assumed [R37].

## 6. Privacy, security, accessibility, and misuse

### Data sensitivity

Raw signals, features, calibration templates, decoded text, prompts, corrections, device identifiers, and linked workflow records have different risks. “No air audio” does not make them anonymous. Depending on purpose and jurisdiction, they may expose identity-linked patterns, health/motor characteristics, communication content, or inferred behavior. Do not call every biosignal legally “biometric”; obtain fact-specific advice.

### Required controls

- opt-in purpose-limited enrollment, layered consent, withdrawal, non-biometric alternative, and no employment penalty;
- obvious active/paused state and physical/software stop; no background collection;
- raw-signal egress and retention off by default; approved retention windows and tested deletion;
- encryption in transit/at rest where data exists, least privilege, device/user binding, access logs, secrets/key rotation and secure updates;
- confirmation and action authorization separated; safer command grammar; lockout/rate limits; correction and manual fallback;
- signed/config-versioned models; replay/injection and rollback defense; integrity/freshness checks;
- data/model cards covering population gaps, sessions, languages, exclusions, harms, and prohibited uses;
- accessibility testing with target users; avoid forcing silent articulation, earbuds, touch, vision, hearing, fine motor control, or one language.

NIST’s Privacy Framework is a governance aid, not certification [R18]. Medical, employment, data-protection, accessibility, telecom, and AI obligations depend on intended use and jurisdiction.

### Prohibited uses for this roadmap

Covert inference; bystander capture; workplace productivity/emotion scoring; lie detection; authentication; law-enforcement interrogation; advertising inference; compelled accessibility enrollment; diagnosis; unattended emergency/safety actions; weapon/access/payment control; or training unrelated models from raw signals without new consent.

## 7. Practical beachhead and staged roadmap

### Captain-selected beachhead

The selected first commercial audience is **e& frontline retail advisors and field technicians**. Stage 0 still must choose one controlled workflow and test role-specific differences rather than pool two jobs. Start with a to-be-defined low-consequence lookup/navigation/repeat/cancel grammar where voice and touch are demonstrably costly. Every action is previewed/confirmed; a conventional input remains. The demo’s twelve-command list is illustrative product copy, **not** a validated vocabulary size or performance condition.

Candidate workflow examples for discovery: inventory lookup, internal checklist navigation, repeat/hold a displayed instruction, or cancel a staged request. Do not start with customer-record changes, payments, access control, employment decisions, emergency work, or medical communication.

### Roadmap and kill gates

| Stage | Work | Evidence gate | Kill / change condition |
|---|---|---|---|
| 0 — discovery | 10–15 **TBD/owner-approved** interviews/observations; compare voice/touch/shortcuts; non-biometric proxy | one recurring job, measurable baseline, voluntary context, user preference | no unmet job; ordinary controls preferred; surveillance/power risk cannot be mitigated |
| 1 — bench feasibility | safety-reviewed sEMG rig; placement/channel ablation; within-session commands + confounds | pre-registered command/reject/latency/comfort thresholds, raw protocol and negative cases | no separable signal; false accepts unacceptable; setup/comfort fails |
| 2 — cross-session study | remove/reapply, days, motion/fatigue, new phrases/users; fixed holdout | cross-session selective-risk and calibration burden pass | performance collapses, exclusions inequitable, adaptation burden too high |
| 3 — workflow evaluation | offline/on-device candidate on named hardware; confirmation; sandbox only | task benefit vs baseline, p50/p95 latency, preference, privacy/security test | no workflow gain; users bypass; privacy/security controls fail |
| 4 — limited paid pilot | governed device ops, support, incident/fallback, retention/deletion audit | renewal/value and reliability evidence under agreed thresholds | unit support burden or harm exceeds value |
| separate assistive track | participatory co-design, clinical/ethics/regulatory path and reliable AAC fallback | user-defined communication outcomes and safety evidence | never displace reliable communication on lab performance |

Commercial decision: the captain approved a **fixed-fee AED 1,000,000 90-day pilot**, followed by annual per-seat deployment at `TBD` pricing only if evidence gates pass. Strategic e& funding/negotiated ownership of foreground IP and a governed Gulf bilingual corpus, with acquisition/exit optionality, is unpriced upside—not a promised outcome or a substitute for evidence. All cohort sizes, thresholds, detailed schedule, hardware, owners, fund allocation, later pricing/funding, rights terms and exit amounts remain `TBD` until protocol/contract approval.

## 8. Decision summary

Fund learning only if decision-makers accept four truths:

1. tomorrow’s demo is interaction design, not sensing evidence;
2. form factor follows signal evidence;
3. low-consequence command/control is the first hypothesis, not open-vocabulary AAC;
4. abstention, consent, fallback, and kill criteria are product features—not research footnotes.
