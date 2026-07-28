# Quiet Channel Lab — 13-slide decision deck source

> **Release:** local decision deck, 2026-07-28.
> **Status:** concept/simulated interaction; no sensor, model, user study, customer, or product.
> **Captain decisions:** e& frontline retail advisors and field technicians; fixed-fee 90-day pilot → per-seat annual deployment as lead path; strategic IP/governed bilingual-dataset funding and acquisition/exit optionality as upside; pilot fee **AED 1,000,000**. Later prices/amounts remain `TBD`.
> **Claim rule:** IDs resolve in [`../research/claim-ledger.md`](../research/claim-ledger.md) and [`../research/references.md`](../research/references.md). Every external number stays attached to population, task, metric, evidence type, and non-transfer boundary.

## Slide 1 — A silent command channel

**Quiet Channel Lab**

A silent command channel into an existing assistant—confirmation-first, evidence-gated, and not presented as mind reading.

- Tomorrow: offline **CONCEPT / SIMULATED PIPELINE**.
- Proposed next proof: a fixed command grammar on a transparent surface-EMG research rig.
- Not: open-vocabulary conversation, assistive AAC, or a finished wearable.

**Speaker note:** Start with status. “Quiet Channel Lab” is a working name; brand owner, team and contact remain TBD. No relationship with e&, One Punch Solutions, Callevate, Apple, Meta, or named researchers is claimed.

**Trace:** C01–C06, C24–C30; R22–R25.

---

## Slide 2 — The problem is a hypothesis worth testing

**Hypothesis:** in some workflows, voice is socially/operationally costly while touch pulls eyes or hands away.

**Scenes to test, not assert:** busy service setting · work at a customer site · private lookup during a meeting.

**Current alternatives:** touch shortcut · keyboard · push-to-talk · ordinary voice · earpiece · whisper/contact mic · ask a colleague · no system.

**Missing today:** interviews, observed frequency, baseline task time/error, user preference, buyer, procurement, or willingness to pay.

> Win only if the alternate input improves the whole task—including setup, correction and fallback.

**Speaker note:** Keep the source deck’s strong scene-setting, remove “every assistant” and “speech is always fastest.” A non-biometric interaction proxy comes before biosignal collection.

**Trace:** C06, C24, C29; presentation review “Problem and user evidence.”

---

## Slide 3 — Why now, without claiming the decoder is solved

**Three signals; three different meanings**

1. **Wearable edge research:** SilentWear reports a 14-channel neckband and on-MCU command classifier—preprint, four participants, eight commands plus rest.
2. **Consumer sensor class:** Meta began selling a US$799 EMG wristband bundle in September 2025—for hand gestures, not speech.
3. **Optical category activity:** Apple’s Q.ai acquisition is reported/confirmed in company and press context; Q Cue’s patent uses coherent light, not electrodes.

> Sensors are entering wearables. Speech transfer across sessions is still research. That gap is the opportunity—and the risk.

**Speaker note:** Do not use another company’s release/acquisition as proof of this modality. Apple’s terms are undisclosed. Exact product/deal facts live in notes only.

**Trace:** C07–C12, C24; R26–R31.

---

## Slide 4 — Beachhead: e& frontline retail advisors and field technicians

**One opt-in, non-medical workforce beachhead:** retail advisors and field technicians; one controlled workflow at pilot start; low-consequence lookup/navigation/repeat/cancel commands; conventional fallback.

**Decision criteria**

- recurring private-input job that current controls do not solve;
- voluntary participation and no employment consequence;
- confirmation can contain error harm;
- calibration and contact are operationally acceptable;
- buyer and success measure are nameable.

**Out of first stage regardless of decision:** customer-record changes, payments, access control, performance scoring, emergency work, diagnosis, or replacement AAC.

**Speaker note:** The captain selected the two frontline roles. Stage 0 must still select one workflow and test role-specific differences rather than pooling them blindly. Assistive/clinical users remain a separate later track.

**Trace:** C06, C18–C21, C24–C25; `provenance/decisions.md`.

---

## Slide 5 — Capture → Decode → Reason → Reply

1. **Capture** — consent + explicit unlock; multi-channel sEMG research rig; signal-quality gate.
2. **Decode** — fixed grammar; candidate alternatives + abstain; named edge hardware only after profiling.
3. **Reason** — confirmed text/intent reaches an existing sandbox assistant; the decoder is the new AI.
4. **Reply** — visual/haptic/audio output remains a design choice; no “audible only” claim.

**Phase boundary:** in use, raw-signal egress/retention are design-off defaults. In calibration research, paired audio may be deliberately captured only under a separate explicit consent and retention rule.

**Speaker note:** A 2.47 ms model inference result is not end-to-end latency; SilentWear uses 0.8–1.4 s windows. “On device” remains a project target until the complete path is measured.

**Trace:** C04–C08, C13–C17, C27; R03–R06, R26.

---

## Slide 6 — Demo the miss; make repair the product

1. Declare **CONCEPT / SIMULATED PIPELINE**—no sensor, model or measured project accuracy.
2. Unlock deliberately; inspect the illustrative 12-command grammar.
3. Advance authored signal → features → scripted alternatives.
4. Confirm a clear read-only candidate—or reject it anyway.
5. Run the scripted ambiguous case; automatic reject, then select an authored repair.
6. Show **what left the device**: confirmed text only; raw fixture transmission remains zero.

> The failure sequence, scores, threshold and timing are authored interaction fixtures—not a replay of a published error distribution.

**Speaker note:** Open `../demo/index.html`. The second scenario fails deterministically. Never mouth a command and imply the browser sensed it. Fallback: static rail + `demo/PRESENTER.md`.

**Trace:** C01–C03, C22–C23; demo runbook/tests.

---

## Slide 7 — What is real, partly proven, and missing

| Demonstrated elsewhere | Partial / disconfirming | Missing for this project |
|---|---|---|
| **2.47 ms model inference**, **20.5 mW system power**, **27.1 h estimated** battery on named hardware; preprint | **77.5±6.6%** cross-validated vs **59.3±2.2%** held-out-session silent accuracy; 4 people, 8 commands + rest, preprint | hardware, participant, command accuracy, transfer, latency, comfort, power, security |
| facial/neck sEMG peer-reviewed silent-speech precedent | open-vocabulary 12.2% WER is a preprint on one-speaker benchmark with LLM rescoring | open vocabulary, Arabic/Gulf transfer, all-day wear, user value, production form factor |

**Metric boundary:** accuracy is top-1 command classification in that study. WER is edit errors/reference words. Inference excludes sensing window, endpointing, confirmation and output.

> We would rather show the gap than have diligence find it.

**Speaker note:** These are SilentWear/MONA/Gaddy results—not this project. Battery is estimated with a 150 mAh battery; all-day comfort was not established.

**Trace:** C04, C07–C08, C13–C17, C22; R03–R06, R26–R27.

---

## Slide 8 — Privacy means a lock, a data flow, and a veto

**Before collection:** voluntary purpose-limited consent · non-biometric alternative · ethics/electrical-safety/labor/jurisdiction review · separate calibration consent.

**In system design:** explicit unlock/lock · contact required · raw retention/egress off by default · least privilege/encryption/deletion where data exists · confirm before state change · signed/fresh state.

**Architectural prohibitions:** no emotion/stress/engagement/health inference · no productivity scoring · no covert or bystander sensing · no unrelated model training.

**Why it matters:** no-air-audio is not anonymity; decoded text is still personal data. UAE PDPL applies to personal-data processing; EU AI Act Article 5 prohibits workplace emotion inference (medical/safety exception).

**Speaker note:** Framework/law references are not compliance certification. UAE Executive Regulations status remains counsel TBD. The demo’s switches show control intent only.

**Trace:** C18–C21, C28; R18–R20, R32–R33.

---

## Slide 9 — Competition is five categories, not a logo cloud

| Category | Status | Boundary |
|---|---|---|
| Gaddy/Klein, SilentWear, AlterEgo research lineage | papers/preprints/repositories/prototypes | closest modality evidence; no transfer to this project |
| Meta Neural Band / wrist sEMG | shipping gesture input | sensor-class precedent, explicitly not speech |
| Q Cue / Apple optical line | patent + acquisition context; unreleased capability | coherent light, not electrodes; no product performance |
| EarCommand, EchoSpeech, MuteIt | peer-reviewed ear-canal/acoustic-eyewear/IMU research systems [R38–R40] | tasks and sensing conditions differ; compare comfort, motion and whole-task value |
| Whispp/AAC/implanted BCI categories | Whispp company-described apps [R41]; other product or clinical statuses vary | acoustic/assistive/clinical paths separate; verify exact model, availability and approval |

**No evidence yet of:** regional leadership, moat, FTO, approved silent-speech product, customer win, or acquisition path.

**Speaker note:** Name AlterEgo first; do not repeat reported funding as fact. Q Cue grant publication is US12204627B2 per Google Patents; FTO requires counsel.

**Trace:** C09–C12, C26, C30–C32; R21, R28–R31, R38–R41, competitors matrix.

---

## Slide 10 — The governed corpus hypothesis

**Bounded finding:** no public Arabic surface-EMG silent-speech corpus was identified in this review; cited performance exemplars are English.

**Licence reality:**

- Gaddy code: MIT; “Silent Speech EMG” data record: CC BY 4.0.
- SilentWear code at checked commit: Apache-2.0; dataset/participant terms still require separate review.
- Meta generic-neuromotor code: CC BY-NC 4.0; `emg2qwerty`: CC BY-NC-SA 4.0—no commercial dependency assumption.
- two implanted-BCI repositories checked have no LICENSE file.

**Asset only if governed:** bilingual command scope · representative consent · withdrawal/deletion · labor separation · reuse rights · encryption · no secondary licensing without new consent.

> A corpus is a liability-bearing research record before it is a moat.

**Speaker note:** Do not say “none exists” or “e& owns it.” Corpus scope, rights, language/dialect, collection, cost, and partner remain TBD.

**Trace:** C24, C26–C28, C30; R05, R07–R09, R16–R17, R26–R27, R34–R37.

---

## Slide 11 — Commercial model: operating path first; strategic upside second

**Lead path**

| Stage | Approved commercial shape | Decision delivered |
|---|---|---|
| 90-day pilot | fixed fee: **AED 1,000,000** | workflow + signal + transfer + comfort + privacy/security report; go/change/stop |
| deployment | per-seat annual pricing: `TBD` | only after pilot gates, operating cost and user value pass |

**Strategic upside—unpriced:** e& may fund and negotiate ownership of resulting foreground IP and a governed Gulf bilingual dataset, preserving acquisition/exit optionality. This is not a substitute for pilot evidence or a promised return.

**Terms still TBD:** background/foreground IP · contributor rights · data stewardship · model licence · publication/negative results · termination · later prices/amounts.

**Speaker note:** State the lead path before upside. “Ownership” is a proposed negotiated structure; participant withdrawal/deletion and applicable rights survive commercial rhetoric. Acquisition is optionality, not the business model.

**Trace:** C24–C30; `provenance/decisions.md`; presentation review “Market, GTM, and business model.”

---

## Slide 12 — The ask: fund a 90-day decision, not an enclosure

**Fixed 90-day pilot fee: AED 1,000,000**
**Later per-seat pricing: `TBD` · strategic funding: `TBD` · acquisition/exit amounts: `TBD`**

**Non-financial ask:** one workflow owner `TBD` · one data-governance owner `TBD` · voluntary access to retail-advisor/field-technician discovery participants (no biosignal collection before approvals) · sandbox only after discovery/protocol gates.

**Use-of-funds structure—all allocations `TBD`:**

- user discovery, accessibility and participant compensation;
- sensing/study engineering and calibration research;
- privacy, security, ethics, regulatory and IP/FTO work;
- evaluation, negative cases, fallback and operations;
- approved team roles and contingency.

**Release work by gate.** No cohort, partner, team, threshold, later price, strategic amount, acquisition value, or deployment is represented as agreed.

**Speaker note:** AED 1,000,000 is captain-approved for the fixed-fee 90-day pilot only. Do not reuse it as annual pricing, strategic funding, valuation, or acquisition/exit value.

**Trace:** C24–C30; `provenance/decisions.md`.

---

## Slide 13 — Pre-commit to go / change / stop

| Gate | Measure | GO threshold | Change / stop trigger |
|---|---|---|---|
| problem | whole task vs touch/voice/shortcut; voluntary preference | `TBD before study` | existing input wins / power risk unresolved |
| bench | false accept/reject, command accuracy, p50/p95 complete latency, comfort | `TBD before collection` | montage or grammar cannot contain error |
| transfer | remove/reapply, new day, motion/fatigue; adaptation time | `TBD before holdout` | personalisation burden defeats workflow |
| language | approved English/Arabic/dialect command grammar | `TBD with native users` | gap/corpus cost exceeds approved scope |
| field | retail/field task success, fallback, use, wear tolerance, security/privacy tests | `TBD before field work` | no net use/value; skin/control failure |

**90-day outcome:** go to deployment design · change modality/workflow · stop and retain the negative result. A stopped product can still be a successful evidence programme.

**Claim ledger:** safe now = offline simulated interaction + external evidence under conditions. Unknown = every project performance/commercial value. Prohibited = hardware/accuracy/AAC/privacy/traction claims.

**Speaker note:** The scout suggested example thresholds/cohorts, but they are not evidence and are not adopted without workflow, statistical, ethics and captain approval. This is the risk/kill-criteria slide.

**Trace:** C01–C30; full `research/claim-ledger.md` and `research/evidence-matrix.md`.
