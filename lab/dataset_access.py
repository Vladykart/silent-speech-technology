#!/usr/bin/env python3
"""Metadata-first dataset guard and checksum verifier; never downloads by default."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parent
REGISTRY = ROOT / "datasets.json"
REPOSITORY = ROOT.parent.resolve()
ACKNOWLEDGEMENT = "I_ACCEPT_BIOMETRIC_DATA_TERMS"


def dataset(dataset_id: str) -> dict[str, object]:
    entries = json.loads(REGISTRY.read_text())["datasets"]
    for entry in entries:
        if entry["id"] == dataset_id:
            return entry
    raise ValueError(f"unknown dataset: {dataset_id}")


def checksum(path: Path, algorithm: str) -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def guarded_download(entry: dict[str, object], destination: Path, accepted_license: str | None) -> None:
    if entry["id"] != "gaddy-klein-silent-speech-emg-v1" or not entry["access"]["downloadEligible"]:
        raise RuntimeError("this registry does not authorize a download path for that entry")
    expected_license = entry["recordLicense"]["identifier"]
    if accepted_license != expected_license:
        raise RuntimeError(f"explicit --accept-license {expected_license} is required")
    if os.environ.get("SILENT_SPEECH_DATA_ACK") != ACKNOWLEDGEMENT:
        raise RuntimeError(f"set SILENT_SPEECH_DATA_ACK={ACKNOWLEDGEMENT} after governance review")
    destination = destination.resolve()
    allowed_local_root = (ROOT / "data").resolve()
    if REPOSITORY in destination.parents and not (destination == allowed_local_root or allowed_local_root in destination.parents):
        raise RuntimeError("repository-local downloads are allowed only under gitignored lab/data/")
    destination.mkdir(parents=True, exist_ok=True)
    record = entry["files"][0]
    target = destination / record["name"]
    if target.exists():
        raise RuntimeError(f"refusing to overwrite {target}")
    url = "https://zenodo.org/api/records/4064409/files/emg_data.tar.gz/content"
    request = urllib.request.Request(url, headers={"User-Agent": "silent-speech-governed-download/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response, target.open("xb") as output:
        for chunk in iter(lambda: response.read(1024 * 1024), b""):
            output.write(chunk)
    actual = checksum(target, record["checksum"]["algorithm"])
    if actual != record["checksum"]["value"]:
        target.unlink()
        raise RuntimeError("checksum mismatch; downloaded file deleted")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset_id")
    parser.add_argument("--verify", type=Path, help="verify an existing file; never extracts it")
    parser.add_argument("--download-to", type=Path, help="explicit governed download destination")
    parser.add_argument("--accept-license")
    args = parser.parse_args()
    entry = dataset(args.dataset_id)
    if args.verify:
        record = entry.get("files", [None])[0]
        if not record:
            raise SystemExit("no verified file checksum is registered")
        actual = checksum(args.verify, record["checksum"]["algorithm"])
        print(json.dumps({"path": str(args.verify), "actual": actual, "expected": record["checksum"]["value"], "matches": actual == record["checksum"]["value"]}, indent=2))
        return 0 if actual == record["checksum"]["value"] else 1
    if args.download_to:
        guarded_download(entry, args.download_to, args.accept_license)
        print("download and checksum verification completed; data remains untracked")
        return 0
    print(json.dumps({"mode": "metadata_only", "downloadStarted": False, "entry": entry}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
