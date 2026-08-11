#!/usr/bin/env python3
"""Locate/verify official assets and extract only the four configured replays.

Default behavior uses the captain-provided shared lab and performs no network
request. Pass ``--download-missing`` explicitly on another workstation.
Downloaded archives, checkpoint and replay arrays stay under ignored
``realtime/local_assets`` and are never committed or served.
"""
from __future__ import annotations

from argparse import ArgumentParser
from hashlib import md5, sha256
from pathlib import Path
import json
import os
import shutil
import tarfile
import tempfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent
DEFAULT_LAB = Path("/root/.local/share/silent-speech-lab")
DEFAULT_ASSETS = ROOT / "local_assets"
MANIFEST = json.loads((ROOT / "assets-manifest.json").read_text())


def digest(path: Path, algorithm: str) -> str:
    hasher = md5() if algorithm == "md5" else sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(4 * 1024 * 1024):
            hasher.update(chunk)
    return hasher.hexdigest()


def verify(path: Path, spec: dict, *, include_sha256: bool = False) -> None:
    if not path.is_file():
        raise FileNotFoundError(path)
    if path.stat().st_size != spec["bytes"]:
        raise RuntimeError(f"wrong byte size for {path}: {path.stat().st_size} != {spec['bytes']}")
    if "md5" in spec and digest(path, "md5") != spec["md5"]:
        raise RuntimeError(f"MD5 mismatch for {path}")
    if include_sha256 and "sha256" in spec and digest(path, "sha256") != spec["sha256"]:
        raise RuntimeError(f"SHA-256 mismatch for {path}")


def download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    print(f"downloading official asset to ignored local path: {destination}", flush=True)
    with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as temporary:
        temporary_path = Path(temporary.name)
        with urllib.request.urlopen(url, timeout=300) as response:
            while chunk := response.read(4 * 1024 * 1024):
                temporary.write(chunk)
    temporary_path.replace(destination)


def locate_model(asset_dir: Path, lab_root: Path, allow_download: bool) -> Path:
    checkpoint_spec = MANIFEST["model"]["checkpoint"]
    destination = asset_dir / "model" / checkpoint_spec["member"]
    candidates = (
        destination,
        lab_root / "models" / checkpoint_spec["member"],
        lab_root / checkpoint_spec["member"],
        lab_root / "src" / "silent_speech" / checkpoint_spec["member"],
    )
    for candidate in candidates:
        if candidate.is_file():
            if candidate != destination:
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.symlink_to(candidate)
            verify(destination, checkpoint_spec, include_sha256=True)
            return destination
    if not allow_download:
        raise FileNotFoundError(
            "official transduction_model.pt not found locally; supply the shared lab asset "
            "or rerun with --download-missing"
        )
    archive_spec = MANIFEST["model"]["archive"]
    archive = asset_dir / "downloads" / "pretrained_models.zip"
    if not archive.is_file():
        download(archive_spec["url"], archive)
    verify(archive, archive_spec)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as package, package.open(checkpoint_spec["member"]) as source:
        with destination.open("wb") as output:
            shutil.copyfileobj(source, output)
    verify(destination, checkpoint_spec, include_sha256=True)
    return destination


def locate_dataset(asset_dir: Path, lab_root: Path, allow_download: bool) -> Path:
    spec = MANIFEST["dataset"]["archive"]
    candidates = (
        lab_root / "datasets" / "zenodo-4064408" / "emg_data.tar.gz",
        asset_dir / "downloads" / "emg_data.tar.gz",
    )
    for candidate in candidates:
        if candidate.is_file():
            verify(candidate, spec, include_sha256=True)
            return candidate
    if not allow_download:
        raise FileNotFoundError(
            "official Zenodo 4064409 archive not found in shared lab; "
            "supply it or rerun with --download-missing (3.92 GB)"
        )
    destination = candidates[-1]
    download(spec["url"], destination)
    verify(destination, spec, include_sha256=True)
    return destination


def extract_replays(archive: Path, asset_dir: Path) -> None:
    targets: dict[str, tuple[str, str]] = {}
    for group, replay in MANIFEST["replays"].items():
        directory = replay["directory"]
        index = int(replay["index"])
        for neighbor in (index - 1, index, index + 1):
            targets[f"{directory}/{neighbor}_emg.npy"] = (group, f"{neighbor}_emg.npy")
        targets[f"{directory}/{index}_info.json"] = (group, f"{index}_info.json")
    output_root = asset_dir / "replays"
    found: set[str] = set()
    with tarfile.open(archive, "r:gz") as package:
        for member in package:
            target = targets.get(member.name)
            if target is None:
                continue
            source = package.extractfile(member)
            if source is None:
                raise RuntimeError(f"cannot read archive member {member.name}")
            group, filename = target
            destination = output_root / group / filename
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open("wb") as output:
                shutil.copyfileobj(source, output)
            found.add(member.name)
    missing = set(targets) - found
    if missing:
        raise RuntimeError(f"official archive is missing configured replay members: {sorted(missing)}")
    for group, replay in MANIFEST["replays"].items():
        info = json.loads((output_root / group / f"{replay['index']}_info.json").read_text())
        if info["book"] != replay["book"] or info["sentence_index"] != replay["sentence_index"]:
            raise RuntimeError(f"metadata identity mismatch for replay {group}")


def main() -> int:
    parser = ArgumentParser()
    parser.add_argument("--lab-root", type=Path, default=DEFAULT_LAB)
    parser.add_argument("--asset-dir", type=Path, default=DEFAULT_ASSETS)
    parser.add_argument("--download-missing", action="store_true")
    args = parser.parse_args()
    args.asset_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(args.asset_dir, 0o700)
    checkpoint = locate_model(args.asset_dir, args.lab_root, args.download_missing)
    archive = locate_dataset(args.asset_dir, args.lab_root, args.download_missing)
    extract_replays(archive, args.asset_dir)
    ready = {
        "model": str(checkpoint.resolve()),
        "model_sha256": MANIFEST["model"]["checkpoint"]["sha256"],
        "dataset_archive": str(archive.resolve()),
        "dataset_md5": MANIFEST["dataset"]["archive"]["md5"],
        "replay_root": str((args.asset_dir / "replays").resolve()),
        "license": "CC BY 4.0",
        "mode": "real_recorded_replay_real_released_model",
    }
    (args.asset_dir / "ready.json").write_text(json.dumps(ready, indent=2) + "\n")
    print("official real model and recorded replay assets verified; no synthetic asset selected")
    print("NON-COMMERCIAL LOCAL RESEARCH DEMO — attribution required; assets remain uncommitted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
