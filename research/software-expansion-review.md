# Software-only model and sample expansion review

**Date:** 2026-08-12

**Method:** independent read-only senior-agent review of committed claim, evidence, replay, registry, provenance, QA, and test authorities; no network, downloads, service action, deployment, training, or new execution.

## Conclusion

The project can move forward without new hardware as a stronger **reproducibility and evidence-discipline demonstration**. Adding model names, parameters, or hand-picked replay cards does not itself strengthen project performance evidence.

The Gaddy transduction checkpoint is the **only currently approved, checksum-bound, and executable checkpoint** in this repository. That is an artifact-readiness statement. It is not evidence that this is the field's best, most accurate, state-of-the-art, most wearable, or most transferable model.

## Why the evidence-only rows are not interchangeable

| Entry | Actual pipeline role | Main blocker | Comparability boundary |
|---|---|---|---|
| HiFi-GAN | downstream predicted-mel-to-audio vocoder | compressed/unapproved runtime and audio prohibited | not an alternative sEMG recognizer |
| Recognition DOI 7183877 | direct character-CTC recognizer | checkpoint, checksum, complete rights/runtime, overlap, and evaluation contract absent | closest meaningful next checkpoint, but incompatible with the current 48-class phoneme decoder |
| DeepSpeech 0.7 + KenLM | legacy synthesized-audio ASR evaluation stack | external assets and legacy dependency path absent | WER would cover synthesis + ASR, not direct sEMG or command accuracy |
| SilentWear SpeechNet | fixed-command 14-channel neck-sEMG classifier | no approved checkpoint; different channels, placement, participants, labels, and windows | external-system reproduction, not a model for current 8-channel sentence samples |
| MONA/LISA | cross-modal recognition system with LLM rescoring | exact approved weights, LM assets, rights, checksums, runtime, and evaluation absent | reported rescored WER is not comparable with the bounded ten-phrase diagnostic |

A vocoder, recognizer, language model, evaluation stack, classifier, decoder algorithm, and complete research system solve different tasks. Counting all of them as “models” would mislead.

## Recommended proof ladder

1. **Artifact integrity:** exact rights, bytes, manifests, strict load, and finite outputs.
2. **Reproducible execution:** deterministic replay and complete failure retention.
3. **Explicit failure:** mismatch, abstention, error, and asset failure stay visible.
4. **Human control:** confirmation, safety acknowledgement, rejection, and no actuation.
5. **Pre-registered next evidence:** freeze selection and metrics before any new output is observed.

This ladder is more valuable for an investor presentation than a larger model carousel.

## Defensible sample expansion

Keep the ten cards as a visibly curated presentation cohort. Create a separate evaluation track:

- define the question, source universe, exclusions, seed, stratification, decoder, threshold, normalization, outcomes, and metrics before execution;
- mechanically rank eligible records and freeze disjoint development/evaluation cohorts before observing outputs;
- never call records held out while checkpoint training overlap is unknown;
- retain every selected execution, abstention, error, and asset failure in the denominator;
- prohibit replacement after freeze;
- keep artifact reliability, direct-recognition WER/CER, fixed-command accuracy, and project bounded-decoder descriptions separate;
- keep any SilentWear or MONA/LISA reproduction in an external-system section, never averaged into a project score.

## Implemented response to this review

- [`../realtime/model-registry.json`](../realtime/model-registry.json) now records each component's role, modality, channel geometry, task, output, metric family, readiness gates, evaluation status, and comparability boundary.
- [`../realtime/evaluation-protocol.json`](../realtime/evaluation-protocol.json) is a protocol-only, no-result, no-execution plan.
- [`../realtime/app/evaluation_protocol.py`](../realtime/app/evaluation_protocol.py) makes deterministic output-blind ranking, disjoint cohort planning, and complete denominators testable with synthetic IDs only.
- The diligence drawer exposes the readiness matrix and next proof plan without adding weights, samples, outputs, scores, or claims.

## Separate-cycle stop conditions

A new research/rights/implementation authorization is required before obtaining or executing another checkpoint/dataset/LM/vocoder/dependency, enabling audio, selecting or running new official samples, changing grammar/threshold after output observation, reporting WER/CER/accuracy or comparative rankings, reproducing another research system, training/fine-tuning/calibrating, collecting participants, adding hardware, or changing deployment.

Authority remains [`claim-boundary.md`](claim-boundary.md), [`claim-ledger.md`](claim-ledger.md), and [`../realtime/spec/INVESTOR_REAL_REPLAY_SPEC.md`](../realtime/spec/INVESTOR_REAL_REPLAY_SPEC.md).
