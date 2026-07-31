# Critical consumption of parallel evidence report

**Report read in full:** `/root/kun-agent-workspace/data/silent-speech-evidence-s1/report.md` (651 lines, SHA-256 `465ecdca024a3864e001f785124afb99a6ac1c1296b192e747d491c65a04dcee`)
**Consumed:** 2026-07-28, before research/deck finalization
**Role:** research input, not an authority. The external report is not required at runtime; durable accepted findings and boundaries are recorded in this repository.

## Accepted and independently checked load-bearing findings

1. **SilentWear is the closest published analogue.** Direct arXiv HTML for v2 (`2603.02847`, 2026-03-04) reports four participants, 14 differential neck EMG channels, eight commands plus rest, multi-day collection, a 15k-parameter CNN, and a proper held-out-session condition. It reports 77.5±6.6% average cross-validated silent accuracy and 59.3±2.2% inter-session silent accuracy. A GAP9 deployment reports 2.47 ms **model inference** and 63.9 µJ/inference at its energy-efficient operating point; total system power was 20.5 mW and battery life was **estimated** at 27.1 h with a 150 mAh battery. The repository exists at commit `b341c30b3a988e5ef871567f8a752084cefa1f7e` and its code license is Apache-2.0. These are preprint/system-specific results, not this project’s.
2. **Open-vocabulary non-invasive evidence remains narrow.** Direct arXiv metadata for MONA/LISA (`2403.05583`) reports WER reduced from 28.8% to 12.2% on the Gaddy 2020 open-vocabulary silent-speech benchmark using LLM-integrated rescoring. Gaddy’s peer-reviewed line and exact-commit repository were separately checked. The benchmark is a single-speaker corpus; this does not support cross-user/on-device claims.
3. **Meta’s sEMG work is adjacent, not speech.** Meta’s official product page says Meta Ray-Ban Display + Neural Band started at US$799 and became available 2025-09-30, describes EMG work with nearly 200,000 research participants, and describes gesture inputs—not speech-from-muscle decoding. The exact-commit `generic-neuromotor-interface` and `emg2qwerty` license files are non-commercial Creative Commons; they are not commercial product dependencies.
4. **Gaddy artifacts have separable terms.** Zenodo record `10.5281/zenodo.4064409` reports “Silent Speech EMG” v1.0, CC BY 4.0, one 3,919,507,637-byte archive (MD5 `7f97d2182b896652999b1b2d0c69fd7b`). At scout reconciliation it had not been downloaded. Updated 2026-07-31: official model/data assets were fetched to ignored local storage, checksum verified and selected records replayed under explicit attribution; code/data/model/dependency and intended-use terms remain separate.
5. **Cross-session drift is a first-order product risk.** SilentWear’s global-to-held-out-session gap was checked directly, and the companion neckband preprint (`2509.21964`) directly reports one participant, eight commands, 68±3% silent 5-fold CV and 54±7% silent leave-one-session-out after repositioning. The honest demo therefore needs rejection/repair—not a perfect transcript.
6. **Privacy claims need phase and purpose boundaries.** UAE’s official portal confirms Federal Decree-Law No.45 of 2021 and an in-force date of 2022-01-02. The official EU regulation text confirms the Article 5 prohibition on AI emotion inference in workplace/education (with medical/safety exception) and application of prohibitions from 2025-02-02. This project does not infer emotion and prohibits workplace scoring. Exact UAE Executive Regulations status was not established and is not claimed.
7. **The optical patent is real but needs precise wording.** Google Patents metadata identifies application publication `US20240119938A1`, assignee Q Cue Ltd, inventors Yonatan Wexler and Avi Barliya, and coherent-light sensing language. The page records grant publication `US12204627B2` on 2025-01-21 and labels status active while warning that Google’s legal status is not a legal conclusion. This supports an FTO/counsel gate—not an ownership, infringement, or product-performance conclusion.
8. **Clinical trials are not products.** ClinicalTrials.gov records for BrainGate2 and BRAVO were independently queried and remained recruiting interventional feasibility studies at access. Implanted results remain a separate clinical path.

## Useful findings retained with narrower wording

- **Arabic/Gulf corpus gap:** the scout found no public Arabic sEMG silent-speech corpus. A bounded negative search cannot prove non-existence. Safe wording is: “No public Arabic sEMG silent-speech corpus was identified in this bounded review; all sEMG performance exemplars cited here are English.” A future governed corpus is not automatically owned or a moat.
- **Apple/Q.ai:** the acquisition and reported transaction range are context, not technical validation. A Reuters URL returned 401 during independent retrieval; patent facts were independently checked. Core claims do not depend on deal price/headcount.
- **AlterEgo:** MIT’s official project page and IUI paper establish the research lineage and close modality/interaction similarity. Company funding/product-performance claims remain company/press evidence and are not load-bearing.
- **AAC populations:** the first stage must exclude medical claims. Aphasia is not a simple loss-of-phonation use case. ALS needs vary by stage and motor preservation; it is too broad to dismiss biologically or claim commercially without participatory clinical work.

## Scout recommendations deliberately not adopted as facts

1. **“Power/latency budget solved.”** SilentWear reports model inference, not end-to-end command latency. Its windows are 0.8–1.4 seconds, before endpointing/confirmation/output. Battery life is an estimate for the named platform/battery, and all-shift comfort was not established. The deck says “demonstrated in that preprint,” not “solved.”
2. **“A 59% first-pass channel is shippable.”** That is a product judgment with workflow/harm dependence. This project treats it as disconfirming evidence and requires rejection/repair and a no-go gate.
3. **Demo latency/error as ‘real numbers.’** No source was given for a 150–250 ms end-to-end delay, and replaying a deterministic miss does not reproduce a paper’s error distribution. The demo labels timing, candidates, scores, threshold, and failure sequence as authored fixtures. Published numbers appear only in the evidence panel/deck with conditions.
4. **Exact staged thresholds and cohort sizes in §12.1.** They are authored recommendations, not evidence. They are preserved as candidate planning inputs but remain `TBD` pending workflow owner, safety/ethics, statistician and captain approval.
5. **Exactly 12 commands as a validated beachhead.** The demo may display a 12-command illustrative grammar, but vocabulary size and chosen workflow remain a captain hold.
6. **Dataset ownership as a moat.** Consent, withdrawal, purpose limitation, representation, labor power, deletion and commercial rights come first. The project says “governed corpus hypothesis,” never that it already owns data.
7. **Clinical/regulatory classification conclusions from secondary sources.** Current pilot boundaries are non-medical; intended-use and jurisdiction counsel decide future classification. No clearance/exemption claim is made.
8. **Bone-conduction output.** No leakage measurement was verified and no hardware exists. The project keeps output modality open and does not claim private-only audio.

## Deck impact

The professional deck follows the scout’s **13-slide decision structure**: thesis; problem; why now; user/beachhead hold; mechanism; honest failure/repair demo; evidence status; privacy; competition; governed corpus hypothesis; business-model hold; ask with fee hold; go/no-go plan. It does not carry the scout’s proposed beachhead, pilot fee, exact threshold, timing, cohort, acquisition value, or dataset ownership as decided facts.

## Demo impact

The release adds a visible locked state, an illustrative 12-command grammar, deterministic second-scenario failure, explicit repair path, confirmation for staged actions, and a “what left the device” log. Every signal/score/timing behavior remains labelled authored/simulated. The demo never records a presenter mouthing a command, so the presenter script does not ask anyone to fake sensor input.
