# Critical review of the captain-supplied presentation

**Source:** [`../provenance/source-record.md`](../provenance/source-record.md)
**Review date:** 2026-07-28
**Method:** bounded direct-HTTPS PPTX retrieval; package metadata and slide text inspection; no browser-rendered QA. Source statements below are paraphrased to avoid redistributing the confidential deck.

## Executive assessment

The four-slide source has a memorable interaction thesis—private, hands-free access to an existing assistant—but it collapses a difficult research program into a product form factor and acquisition story. Its strongest revision is not “a behind-the-ear device that reads words.” It is:

> **Test whether consented surface neuromuscular sensing can support a small, low-consequence, confirmation-first command set for one workflow—then stop if signal, transfer, user value, or governance gates fail.**

That revision keeps the useful product insight (an alternate input path to an existing system) while removing unsupported hardware, open-vocabulary, accessibility, privacy, timeline, and exit claims.

## Narrative and audience

**What the source does:** It opens with a compact product promise, expands to problem/solution, moves to business impact, and ends with a funded 90-day pilot ask. It is explicitly tailored to an e& innovation-pitch audience and frames integration with e&'s agent and CRM as the route to value.

**What works:**

- The four-stage capture → decode → reason → reply sequence is understandable.
- Reusing an existing assistant separates input research from general-agent development.
- The source asks for a sponsor, sandbox, cohort, and funded pilot rather than only money.
- “If it works” appears in the commercial model, which can become a real decision gate.

**What must change:**

- The title-level promise precedes feasibility evidence and makes a research prototype sound available.
- Two very different stories—frontline productivity and disability communication—are combined without shared requirements or evidence.
- The acquisition/exit frame displaces user value, scientific risk, clinical participation, and responsible data rights.
- No explicit evidence taxonomy distinguishes paper results, another company’s announcement, this team’s work, and future architecture.

## Problem and user evidence

| Source-deck position | Assessment | Defensible revision |
|---|---|---|
| Voice or screens fail in busy stores, homes, and meetings | Plausible workflow hypothesis; no interviews, observations, baseline error/time, or willingness-to-pay evidence supplied | “We need to test whether workers experience a recurring private-input job that existing voice, touch, shortcuts, or headsets do not solve.” |
| Speech is the fastest interface | Overbroad and context-dependent; speed is not the only measure | Compare task completion time, error, interruption, learnability, and accessibility against current input methods. |
| Frontline workers can answer without looking away | Desired outcome, not demonstrated behavior | Measure gaze interruption and task time in a non-biometric workflow study before sensing. |
| People with laryngectomy, ALS, dysphonia, post-stroke aphasia share the use case | Unsafe grouping. Needs, residual motor control, fatigue, language formulation, progression, and clinical context differ; aphasia is not simply loss of audible voice | Keep medical/assistive AAC out of the first commercial claim. Pursue only through participatory research with users, clinicians, ethics oversight, and a separate regulatory analysis. |

No customer, user interview, cohort, partner, deployment, or accessibility co-design evidence was present. The deck must not imply any.

## Technical mechanism and modality decision

The source specifies electrodes in a small behind-the-ear unit that decode mouthed words on device. The literature establishes that multiple biosignal modalities can carry articulatory or neural information; it does **not** establish that this placement/form factor can perform the promised task.

Key gaps:

- electrode count, anatomical placement, reference/ground, contact quality, sampling rate, front-end, artifact rejection, and electrical safety are unspecified;
- silent articulation is not equivalent to normal voiced speech with the audio removed; EMG distributions and timing can change;
- there is no vocabulary definition, calibration duration, personalization protocol, transfer test, error metric, rejection metric, latency budget, or hardware power/compute budget;
- “on device” is an architecture target, not an implemented or benchmarked property;
- motion, sweat, electrode shift, facial activity, fatigue, session drift, skin/hair differences, and ambient electromagnetic interference are absent;
- bone conduction is not inherently audible only to one wearer and does not solve the input problem;
- a behind-ear industrial design should follow signal feasibility, not be assumed before it.

**Recommended modality for the first study:** a transparent, research-grade surface-EMG rig at anatomically justified jaw/face/neck sites, constrained command vocabulary, per-user/session calibration, explicit rejection, and manual confirmation. Treat in-ear/intraoral, ultrasound, RF, EEG, and implants as comparison tracks, not interchangeable backups. Do not promise a wearable enclosure until placement ablations show what signal can be removed.

## Product promise and demo readiness

The source speaks in present tense (“device,” “reads,” “turns,” “returns”) but supplies no prototype evidence. No runnable artifact, hardware bill of materials, recording, code, model, dataset, protocol, test transcript, or result accompanies it.

Tomorrow’s repository demo therefore uses authored fixtures and labels itself **CONCEPT / SIMULATED PIPELINE** before interpretation. It demonstrates a product contract—candidate alternatives, rejection, human confirmation, and privacy state—not silent-speech capability. See [`../demo/README.md`](../demo/README.md).

## Evidence audit of load-bearing statements

| Source-deck statement | Evidence status at review | Use in revised deck |
|---|---|---|
| Meta shipped an sEMG wearable in 2025 | Requires exact product/release/availability evidence. A company announcement or developer product still would not validate this concept’s placement or performance. | Include only in notes if verified as company material and labelled accordingly; not a technical proof. |
| Apple acquired a silent-speech company in 2026 for about US$2B / about 100 people | Material transaction claim needs authoritative Apple filing/statement or high-quality financial reporting; “silent-speech company” may oversimplify the target. It supplies no product validation or repeatable exit model. | Omit from core investment logic. Record in competitor notes only if independently verified. |
| Nobody owns the category in the UAE | Undefined category and unsupported regional competitive claim | Remove. Run a registered competitor/patent/market scan before making geography claims. |
| Signal is decoded on device and only text leaves | Future architecture promise with no implementation, security model, or verification | “Design target: local processing; raw-signal egress off by default; verify with data-flow and network tests.” |
| A regional silent-speech dataset is an owned asset | Rights, consent, deletion, withdrawal, representation, labor, cross-border transfer, and model-inversion risks are ignored | Treat a dataset as a liability-bearing governed research record, not automatically a moat. No collection before protocol/consent/retention approval. |
| Shorter transactions and fewer escalations | No baseline or trial result | Pilot outcomes to test, never business impact already achieved. |
| A 90-day pilot yields real accuracy and an acquisition choice | 90 days might support discovery and initial within-session signal feasibility, not a validated wireless wearable, integration, longitudinal transfer, compliance, and exit decision | Stage 0 discovery → Stage 1 bench feasibility → Stage 2 consented study → Stage 3 workflow pilot, each with kill criteria. Timing/budget TBD. |

## Market, GTM, and business model

The source lists fixed-fee pilot, annual per-seat deployment, and revenue share. These are possible contract shapes, not a model supported by buyer research, deployment costs, support burden, pricing evidence, or unit economics.

The first commercial question is whether an alternative input creates enough incremental value over phone shortcuts, touch interfaces, push-to-talk headsets, and ordinary voice. A better GTM sequence is:

1. problem discovery with one role and one workflow;
2. non-biometric interaction test using a keyboard-triggered proxy;
3. signal feasibility study under consent;
4. limited evaluation under a research agreement;
5. paid low-consequence pilot only if pre-registered technical and workflow gates pass.

The captain subsequently approved a **fixed AED 1,000,000 fee for a 90-day pilot**, followed by annual per-seat deployment only if gates pass. Annual price, strategic IP/data funding, valuation, acquisition/exit amounts, seat count, revenue, market size, team, partners, and acquisition assumptions remain `TBD`.

## Privacy, safety, security, and regulatory exposure

“Private by design” is not established by the absence of audio. Neuromuscular and neural signals can be sensitive, linkable, health-relevant, and vulnerable to secondary inference. Decoded text can be more legible—and more actionable—than raw audio. Workplace power asymmetry, bystander expectations, covert use, and compelled enrollment matter.

Minimum controls before a human study:

- explicit purpose, lawful basis, voluntariness, withdrawal, and a non-biometric alternative;
- raw/feature/text data inventory; default non-retention; encryption and access controls where retention is approved;
- per-stage consent and visible recording state; no background or covert inference;
- subject/session separation in evaluation; no train/test leakage;
- user confirmation, reject/abstain, correction, timeout, and manual fallback;
- threat model covering device loss, model extraction, replay/injection, output spoofing, insiders, and update integrity;
- jurisdiction-specific data-protection and labor review;
- separate intended-use/regulatory analysis before any diagnosis, treatment, compensation-for-disability, or safety claim.

## Missing facts an owner must supply

- legal project name, brand rights, owners, inventors, team, contact, and authority to circulate;
- target buyer/user and evidence from discovery;
- any existing hardware/software/data, including provenance and test artifacts;
- modality/placement rationale and human-subject approvals;
- exact competitors and the sources behind corporate claims;
- budget, schedule, hiring plan, partner role, sandbox readiness, and procurement constraints;
- consent, retention, security, accessibility, incident, and regulatory owner;
- acceptance and kill thresholds agreed **before** collection.

## Strongest defensible revision

Position the project as an evidence-gated research and product-discovery program, not a finished wearable:

- **Thesis:** confirmation-first private-input commands may fill a narrow gap where voice and touch are operationally costly.
- **First users:** captain-selected e& frontline retail advisors and field technicians; Stage 0 selects one workflow and compares role-specific conditions; low-consequence lookup/navigation/repeat/cancel commands.
- **First modality:** multi-channel surface EMG research rig; form factor open.
- **First output:** candidate list → abstain/reject → human confirmation → sandbox action.
- **Evidence goal:** within-user/session feasibility plus failure characterization; no transfer or open-vocabulary claim.
- **Kill:** stop or change modality if signal does not beat a pre-agreed baseline, calibration/comfort is unacceptable, cross-session behavior is unstable, or users prefer existing controls.
- **Ask:** AED 1,000,000 for a fixed-fee 90-day gated pilot, plus workflow/data-governance owners and voluntary discovery access. Per-seat annual deployment follows only if gates pass; strategic IP/governed-dataset funding and acquisition/exit optionality are unpriced upside, not a promised return.
