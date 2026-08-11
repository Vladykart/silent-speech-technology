# Real-replay artifact provenance and change record

Machine authority: [`../realtime/assets-manifest.json`](../realtime/assets-manifest.json), [`../realtime/sample-manifest.json`](../realtime/sample-manifest.json), and [`../realtime/model-registry.json`](../realtime/model-registry.json). Product/payload authority: [`../realtime/spec/INVESTOR_REAL_REPLAY_SPEC.md`](../realtime/spec/INVESTOR_REAL_REPLAY_SPEC.md).

## Executed source and checkpoint

| Artifact | Authority / local treatment | Rights and non-transfer boundary |
|---|---|---|
| Silent Speech EMG v1.0 | David Gaddy / UC Berkeley; version DOI `10.5281/zenodo.4064409`, concept DOI `10.5281/zenodo.4064408`; one official 3,919,507,637-byte archive; outer and frozen-member hashes remain in unserved manifests | Zenodo deposit records CC BY 4.0. Exactly 11 selected native `float64 [time,8]` recordings, immediate context, and selected metadata are atomically prepared under ignored owner-controlled storage. No audio/buttons/full extraction. Single-speaker research scope does not transfer to project performance, diversity, privacy, consent, endorsement, patent, or intended-use conclusions. |
| Voicing Silent Speech Models | David Gaddy; DOI `10.5281/zenodo.6747411`; official 253,447,725-byte ZIP and 216,859,418-byte `transduction_model.pt`; checkpoint full hash remains unserved | Zenodo deposit records CC BY 4.0. One 54,187,136-parameter checkpoint strict-loads and executes. The model is not redistributed/downloadable and is not project-owned. Adapted runtime and direct phoneme-head postprocessing are disclosed changes. |
| dgaddy/silent_speech code lineage | Repository commit `a89357c2086609b432919b9d14ffc0be5d8983d5`; adapted architecture/transformer/preprocessing only | MIT, Copyright © 2021 David Gaddy. External paper/repository performance does not become a project result. |

## Runtime pronunciation dependency

`cmudict==1.0.32` has two separately recorded layers:

- Python package/distribution metadata and top-level packaged license: **GPL-3.0-or-later**;
- CMU Pronouncing Dictionary data: separate Carnegie Mellon redistribution notice and disclaimer in `cmudict/data/LICENSE`.

The project does not vendor either payload. The complete dependency bundle needs review before broader distribution; it is not permissive-only.

## Not executed

The model registry visually and mechanically separates HiFi-GAN, recognition DOI 7183877, DeepSpeech/KenLM, SilentWear SpeechNet, and MONA/LISA as **NOT EXECUTED HERE**. HiFi-GAN remains compressed and audio is prohibited. Other checkpoints/runtime assets are absent or unapproved. Papers, architectures, datasets, decoders, and authored fixtures are not counted as additional executed models.

## Display changes and privacy boundary

Source traces, source/filtered comparison, 112-feature and 80-bin heatmaps, and 48-class top-output inspection are generated per active run by project-authored code. They are min/max decimated, robustly centered/scaled, time-binned, normalized, and/or signed-8-bit quantized under explicit labels. They are not untouched source, ground truth, audio, full tensors, or integrity proofs. No center/scale values, full hash/path, source session/book/sentence identity, participant field, download, screenshot, or retained output is exposed.

CC BY 4.0 attribution is visible. The captain’s private non-commercial research-demo limit is stricter project policy, not a reinterpretation of upstream rights. No public/customer deployment, endorsement, accuracy transfer, medical/AAC, identity/emotion, or redistribution claim is made.

## Change record

- **2026-08-11 / manifest v1:** froze `QC-R01`–`QC-R10` plus `QC-R02-T2` before added-recording execution; added selected/context/metadata digests, selection disclosure, one-executed-model registry, bounded display derivatives, corrected native dtype/timing claims, and separated cmudict package/data rights.
- Catalogue changes require a new manifest/spec version, rationale, and disclosed selection policy. Mismatch, error, or abstention outcomes remain; no post-execution sample substitution for presentation quality.
