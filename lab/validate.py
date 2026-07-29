#!/usr/bin/env python3
"""Fast no-install validation for the pre-hardware lab foundation."""
from __future__ import annotations

import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from acquisition import smoke_summary
from model_contract import dry_run as model_dry_run
from signal_pipeline import FilterConfig, dry_run as signal_dry_run
from split_rules import validate_manifest

ROOT = Path(__file__).resolve().parent
REPOSITORY = ROOT.parent

REQUIRED = [
    "README.md", "PLAN.md", "DATASETS.md", "software-profiles.json", "datasets.json",
    "acquisition.py", "signal_pipeline.py", "model_contract.py", "bootstrap_plan.py",
    "dataset_access.py", "split_rules.py", "examples/split-manifest.json", "tests/test_lab.py",
]
FORBIDDEN_SUFFIXES = {".npy", ".npz", ".wav", ".flac", ".mp3", ".ogg", ".pt", ".pth", ".ckpt", ".onnx", ".tflite", ".pkl"}
FORBIDDEN_NAMES = {"emg_data.tar.gz", "lm.binary", ".env", "credentials.json"}


def main() -> int:
    errors: list[str] = []
    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            errors.append(f"missing {relative}")

    profiles = json.loads((ROOT / "software-profiles.json").read_text())
    if set(profiles.get("groups", {})) != {"core", "acquisition", "signal", "model", "edge"}:
        errors.append("software groups must be core/acquisition/signal/model/edge")
    if profiles.get("policy", {}).get("installByDefault") is not False:
        errors.append("software profile must default to no install")
    if profiles.get("policy", {}).get("noGlobalMutation") is not True:
        errors.append("global mutation prohibition missing")

    registry = json.loads((ROOT / "datasets.json").read_text())
    policy = registry.get("policy", {})
    if policy.get("downloadByDefault") is not False or policy.get("trackedDataAllowed") is not False:
        errors.append("dataset registry default/tracking guard missing")
    if policy.get("primaryEvaluationGate") != "held-out-session":
        errors.append("held-out-session must be primary evaluation gate")
    expected_ids = {"gaddy-klein-silent-speech-emg-v1", "silentwear", "emg-uka", "arabic-surface-emg-negative-search"}
    entries = registry.get("datasets", [])
    if {entry.get("id") for entry in entries} != expected_ids:
        errors.append("dataset registry IDs do not match bounded registry")
    for entry in entries:
        for field in ("recordLicense", "codeLicense", "modelLicense", "access"):
            if field not in entry:
                errors.append(f"dataset {entry.get('id')} missing separate {field}")
    gaddy = next(entry for entry in entries if entry.get("id") == "gaddy-klein-silent-speech-emg-v1")
    file_record = gaddy.get("files", [{}])[0]
    if (gaddy.get("conceptDoi"), gaddy.get("versionDoi"), file_record.get("bytes"), file_record.get("checksum", {}).get("value")) != (
        "10.5281/zenodo.4064408", "10.5281/zenodo.4064409", 3919507637, "7f97d2182b896652999b1b2d0c69fd7b"
    ):
        errors.append("verified Gaddy Zenodo metadata drift")

    acquisition = smoke_summary()
    if acquisition["realDeviceOpened"] or acquisition["audioCaptured"] or acquisition["listenerOpened"]:
        errors.append("mock acquisition crossed a default-safe boundary")
    if not acquisition["shutdownClean"] or acquisition["droppedSamples"] != 2 or len(acquisition["channels"]) != 8:
        errors.append("mock acquisition lifecycle/drop/channel invariant failed")
    signal = signal_dry_run(FilterConfig())
    if signal["input"]["source"] != "authored_synthetic" or signal["scientificFilterExecuted"]:
        errors.append("signal dry-run boundary failed")
    model = model_dry_run()
    if model["inputShape"] != [2, 96, 8] or model["checkpointLoaded"] or not model["outputSchema"]["requiresConfirmation"]:
        errors.append("model contract shape/checkpoint/confirmation invariant failed")

    split_errors = validate_manifest(json.loads((ROOT / "examples/split-manifest.json").read_text()))
    errors.extend(f"split example: {error}" for error in split_errors)

    for path in REPOSITORY.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() in FORBIDDEN_SUFFIXES or path.name in FORBIDDEN_NAMES:
            errors.append(f"forbidden tracked-like data/model/credential artifact: {path.relative_to(REPOSITORY)}")
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            errors.append(f"generated cache present: {path.relative_to(REPOSITORY)}")
    source = (ROOT / "acquisition.py").read_text()
    for forbidden in ("import brainflow", "import pylsl", "import socket", "getUserMedia", "microphone"):
        if forbidden in source:
            errors.append(f"default mock acquisition contains forbidden real path: {forbidden}")
    downloader = (ROOT / "dataset_access.py").read_text()
    for guard in ("--download-to", "--accept-license", "SILENT_SPEECH_DATA_ACK", "refusing to overwrite", "checksum mismatch"):
        if guard not in downloader:
            errors.append(f"dataset access guard missing: {guard}")

    docs = "\n".join((ROOT / name).read_text() for name in ("README.md", "PLAN.md", "DATASETS.md"))
    for phrase in ("Never connect a person to a mains-referenced experimental rig", "held-out-session", "not identified as of", "OpenBCI GUI", "GAP9/GAPflow", "No participant recording"):
        if phrase.lower() not in docs.lower():
            errors.append(f"documentation boundary missing: {phrase}")

    if errors:
        print("lab validation failed:", *[f"- {error}" for error in errors], sep="\n")
        return 1
    print("lab validation passed: safe mock acquisition, synthetic signal/model contracts, registries, leakage rules, and tracked-artifact guards")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
