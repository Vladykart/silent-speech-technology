# Dataset registry and guarded access

Machine-readable authority: [`datasets.json`](datasets.json). This guide does not authorize human-subject collection or make dataset use ethically, legally, or commercially permissible.

## Registered sources

### Gaddy & Klein Silent Speech EMG

Zenodo concept DOI [`10.5281/zenodo.4064408`](https://doi.org/10.5281/zenodo.4064408) resolved on 2026-07-29 to version record [`10.5281/zenodo.4064409`](https://doi.org/10.5281/zenodo.4064409), “Silent Speech EMG,” v1.0, David Gaddy. Live Zenodo API metadata reported record license identifier `cc-by-4.0` (Creative Commons Attribution 4.0 International) and one file:

- `emg_data.tar.gz` — `3,919,507,637` bytes — MD5 `7f97d2182b896652999b1b2d0c69fd7b`

The source is described as eight-channel facial sEMG with silent/vocalized material from a single speaker. **Not downloaded.** The dataset record license does not supply code/model/dependency rights or resolve data-subject, patent, privacy, security, ethics, withdrawal/reuse, or intended-use obligations. Upstream code is separately MIT at the recorded commit; pretrained models are separate artifacts.

Metadata-only command:

```bash
python3 lab/dataset_access.py gaddy-klein-silent-speech-emg-v1
```

Checksum an already governed local copy without extraction:

```bash
python3 lab/dataset_access.py gaddy-klein-silent-speech-emg-v1 --verify /approved/untracked/path/emg_data.tar.gz
```

A download path exists only because exact record terms and checksum metadata were verified. It requires `--download-to`, exact `--accept-license cc-by-4.0`, and the explicit `SILENT_SPEECH_DATA_ACK` value printed by the script after governance review. Use a user-selected untracked location or gitignored `lab/data/`. Never use it during routine setup/CI and never commit/extract by default.

### SilentWear

The preprint reports n=4, 14 differential neck sEMG channels, and eight commands plus rest. Code at recorded commit is Apache-2.0; **dataset and model terms remain unverified**, so no download path is enabled. Reported `77.5±6.6%` global and `59.3±2.2%` held-out-session accuracy are external preprint results, not project evidence or expectations.

### EMG-UKA

Corpus access is described as by request from KIT. No request, automated access, or download is authorized. Obtain exact terms and accountable approval before any request.

### Arabic surface-EMG silent speech

A public Arabic surface-EMG silent-speech corpus was **not identified as of the source review date (2026-07-28)** in a bounded review. This is not proof that none exists. Refresh sources and terms before repeating the finding.

## Split and evaluation gate

Assign immutable subject/session/utterance IDs before feature generation. Fit normalization, vocabulary decisions, thresholds, augmentation, and hyperparameters on train data only. A subject/session pair may appear in exactly one split. Keep a final held-out session untouched until the decision evaluation; report session counts, personalization/calibration, text normalization, vocabulary/language model, abstentions, substitutions/deletions/insertions, uncertainty intervals, and failures.

Held-out-session performance is the primary week 9–12 gate. Global/random cross-validation alone is insufficient because it can obscure session/placement drift. A generalization drop is an honest result that informs redesign; never hide it by switching the primary split after seeing outcomes. Use [`split_rules.py`](split_rules.py) before training or metrics.
