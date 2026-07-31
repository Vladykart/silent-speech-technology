# Claim boundary

**Release status:** local research package, locked static concept, and separate synthetic-signal/real-model bench, updated 2026-07-31.
**Authority:** this file governs README, demo, deck, scripts, and spoken narrative. When wording conflicts, use the more conservative statement.

## One-sentence safe claim

> We have a locked authored-fixture **concept / simulated pipeline** and a separate local bench where noisy **simulated sensor signals** pass through a genuine synthetic-trained CTC decoder; we have not built or validated a physical silent-speech sensor, real-EMG decoder, wearable, clinical system, or product.

## Current capability ledger

| Status | Supportable statement |
|---|---|
| Exercised locally | The locked static demo deterministically replays authored candidate/uncertainty fixtures. Separately, `realtime/` generates noisy eight-channel signals, performs real preprocessing/features and a forward pass through 185,820 learned PyTorch parameters, CTC-decodes emissions, abstains/repairs/confirms, and exposes/tests a loopback API. This establishes executable synthetic-bench software only. |
| Design decision | The captain-selected beachhead is e& frontline retail advisors and field technicians. A first research track would evaluate opt-in multi-channel surface EMG for one low-consequence workflow, with a fixed command grammar, calibration, abstention, repair and confirmation. |
| Research support | Peer-reviewed work shows several articulatory/neuromuscular and implanted-neural approaches can decode or synthesize speech under specific study conditions. Those results do not transfer to this project. |
| Unknown | User demand, electrode placement, signal quality, calibration burden, vocabulary, within/cross-session performance, subject transfer, latency, comfort, power, compute, cost, security, regulatory status, pricing, team, partners, and funding. |
| Not present | Physical hardware/capture, real-EMG- or participant-trained weights, collected/human/biometric data, measured silent-speech performance, prototype enclosure, customer discovery, users, trial, approval, certification, patent opinion, production integration, remote service, or deployment. |

## Approved wording

Use these phrases with their qualifiers intact:

- “silent-speech **research**” — umbrella field, not this product’s capability;
- “surface EMG **proposed first study modality**” — not selected production hardware;
- “small command vocabulary **to be defined with users**” — not open vocabulary;
- “local processing **design target**” — not an implemented security guarantee;
- “confirmation-first **interaction prototype**” — what the demo actually supports;
- static demo: “confidence **fixture value**” or “scripted candidate score”; real-model bench: “**uncalibrated decoder score**”—neither is accuracy or a calibrated probability;
- “**simulated signal with injected noise; real synthetic-trained model and inference**” — keep every qualifier and do not shorten this to a hardware capability;
- “assistive AAC **future participatory research track**” — not an indicated use;
- “e& frontline retail advisors and field technicians” — captain-selected beachhead, not traction or validated demand;
- “AED 1,000,000 fixed-fee 90-day pilot” — captain-approved ask only; per-seat annual pricing, strategic funding and acquisition/exit amounts remain **TBD**.

## Prohibited or unsupported wording

Do not state or imply:

- reads thoughts, hears inner speech, telepathy, mind reading, or imagined-speech capability;
- “works,” “reads words,” “decodes speech,” “real time,” “open vocabulary,” “speaker independent,” or “on device” about this project;
- measured accuracy, WER, CER, information-transfer rate, end-to-end hardware latency, words/minute, confidence calibration, or transfer performance for this project; backend forward-pass timing may be shown only as a per-run local software diagnostic and not a hardware/product guarantee;
- behind-the-ear, invisible, wireless, bone-conduction-only, safe, comfortable, all-day, or manufacturable form factor;
- no audio means anonymous/private; “only text leaves”; compliant, secure, encrypted, certified, or privacy-preserving by default;
- laryngectomy, ALS, dysarthria, dysphonia, aphasia, stroke, locked-in syndrome, or other diagnosis as a supported user indication;
- FDA cleared/approved, CE-marked, exempt, non-medical, or outside regulation without intended-use and jurisdiction review;
- customer, design partner, sponsor, cohort, agreed pilot, integration, traction, revenue, market size, moat, owned dataset, team credentials, partnership, patent, acquisition likelihood, or regional leadership;
- any price other than the captain-approved AED 1,000,000 fixed 90-day pilot fee; annual seats, strategic IP/data funding, valuation and acquisition/exit amounts are TBD;
- Meta, Apple, or another organization’s research/product/transaction as proof that this project can work;
- the demo’s `0.84`, `0.54`, `0.91`, or `0.72` values as measurements. They are authored interaction fixtures.

## Demo labels

The locked static `demo/` must show before traces or candidate values:

> **CONCEPT / SIMULATED PIPELINE — authored fixture data; no sensor, recording, model, or measured accuracy.**

Its illustrative 12-command grammar, egress counters, scores, threshold, delay, miss and manual repair remain authored interaction behavior.

The separate `realtime/` client must keep this visible throughout:

> **SIMULATED SIGNAL + NOISE / REAL MODEL + REAL INFERENCE.**

It must explain that weights were trained only on generated signals, model/decoder scores are uncalibrated and no physical/participant data or measured real-world accuracy exists. A “live” label describes browser-to-local-service execution, never live sensing.

If either demo fails, never describe the broken interaction as sensing. The static five-stage rail and presenter script remain the fallback for the locked concept experience.

## Research-performance citation rule

A number from literature may appear only with:

1. named source and stable URL/DOI;
2. evidence type (peer-reviewed, preprint, company material, repository, dataset, etc.);
3. participants and modality;
4. vocabulary/task and personalization/calibration condition;
5. metric definition and evaluation split where available;
6. an explicit statement that it is not this project’s result.

Example allowed wording:

> In one participant with ALS implanted with intracortical arrays, Willett et al. reported online WER of 23.8% for a 125,000-word vocabulary and an attempted-speech rate of 62 words/minute; WER includes language-model output and the result does not transfer to non-invasive EMG or this project (Nature 2023, DOI 10.1038/s41586-023-06377-x).

## Privacy and human-subject gate

No human recording begins until an accountable owner approves: protocol/ethics route, voluntariness and non-biometric alternative, recruitment, sensor electrical safety, consent, compensation, data inventory, retention/deletion, access, export, incident response, publication/reuse, withdrawal handling, accessibility, and jurisdiction/labor review. Workplace enrollment must not be tied to performance scoring or employment consequence.

## Medical and safety boundary

Tomorrow’s concept is low-consequence command/control with human confirmation. It is not assistive AAC, diagnosis, treatment, emergency communication, authentication, access control, payment authorization, safety automation, or a substitute for a reliable communication method. A future assistive track requires co-design with intended users and clinicians, an always-available fallback, failure-harm analysis, and intended-use regulatory review before claims or trials.
