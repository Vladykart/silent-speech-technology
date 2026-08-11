#!/usr/bin/env python3
"""Verify official archives and atomically prepare only frozen sEMG replay members.

The default path makes no network request. ``--download-missing`` is an explicit
operator action for preparation time only and is never called by the service.
"""
from __future__ import annotations

from argparse import ArgumentParser
from hashlib import md5, sha256
from pathlib import Path
from typing import BinaryIO
import json
import os
import shutil
import tarfile
import tempfile
import urllib.request
import zipfile

import numpy as np

ROOT = Path(__file__).resolve().parent
DEFAULT_LAB = Path("/root/.local/share/silent-speech-lab")
DEFAULT_ASSETS = ROOT / "local_assets"
ASSETS = json.loads((ROOT / "assets-manifest.json").read_text(encoding="utf-8"))
SAMPLES = json.loads((ROOT / "sample-manifest.json").read_text(encoding="utf-8"))


def digest(path: Path, algorithm: str) -> str:
    value = md5() if algorithm == "md5" else sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(4 * 1024 * 1024):
            value.update(chunk)
    return value.hexdigest()


def verify(path: Path, spec: dict) -> None:
    if not path.is_file():
        raise FileNotFoundError(path)
    if "bytes" in spec and path.stat().st_size != int(spec["bytes"]):
        raise RuntimeError(f"wrong byte size for approved asset: {path.name}")
    for algorithm in ("md5", "sha256"):
        if algorithm in spec and digest(path, algorithm) != spec[algorithm]:
            raise RuntimeError(f"{algorithm.upper()} mismatch for approved asset: {path.name}")


def download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as temporary:
        temporary_path = Path(temporary.name)
        with urllib.request.urlopen(url, timeout=300) as response:
            while chunk := response.read(4 * 1024 * 1024):
                temporary.write(chunk)
    temporary_path.replace(destination)


def locate_model(asset_dir: Path, lab_root: Path, allow_download: bool) -> Path:
    checkpoint = ASSETS["model"]["checkpoint"]
    destination = asset_dir / "model" / checkpoint["member"]
    candidates = (
        destination,
        lab_root / "model" / checkpoint["member"],
        lab_root / "models" / checkpoint["member"],
        lab_root / checkpoint["member"],
        lab_root / "src" / "silent_speech" / checkpoint["member"],
    )
    for candidate in candidates:
        if candidate.is_file():
            if candidate != destination:
                destination.parent.mkdir(parents=True, exist_ok=True)
                temporary_link = destination.with_name(destination.name + ".prepare")
                temporary_link.unlink(missing_ok=True)
                temporary_link.symlink_to(candidate.resolve())
                temporary_link.replace(destination)
            verify(destination, checkpoint)
            return destination
    if not allow_download:
        raise FileNotFoundError("official transduction checkpoint is not present in approved local storage")
    archive_spec = ASSETS["model"]["archive"]
    archive = asset_dir / "downloads" / "pretrained_models.zip"
    if not archive.is_file():
        download(archive_spec["url"], archive)
    verify(archive, archive_spec)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".prepare")
    temporary.unlink(missing_ok=True)
    with zipfile.ZipFile(archive) as package, package.open(checkpoint["member"]) as source, temporary.open("wb") as output:
        shutil.copyfileobj(source, output)
    verify(temporary, checkpoint)
    temporary.replace(destination)
    return destination


def locate_dataset(asset_dir: Path, lab_root: Path, allow_download: bool) -> Path:
    spec = ASSETS["dataset"]["archive"]
    candidates = (
        lab_root / "datasets" / "zenodo-4064408" / "emg_data.tar.gz",
        lab_root / "downloads" / "emg_data.tar.gz",
        asset_dir / "downloads" / "emg_data.tar.gz",
    )
    for candidate in candidates:
        if candidate.is_file():
            verify(candidate, spec)
            return candidate
    if not allow_download:
        raise FileNotFoundError("official dataset archive is not present in approved local storage")
    destination = candidates[-1]
    download(spec["url"], destination)
    verify(destination, spec)
    return destination


def extraction_targets() -> dict[str, list[tuple[str, str, str]]]:
    """Archive member -> [(public ID, role, expected digest)]."""
    result: dict[str, list[tuple[str, str, str]]] = {}
    for public_id, sample in SAMPLES["samples"].items():
        for role in ("selected", "context_before", "context_after", "metadata"):
            spec = sample[role]
            member = str(spec["member"])
            allowed = member.endswith("_emg.npy") if role != "metadata" else member.endswith("_info.json")
            if not allowed or any(token in member.lower() for token in ("audio", "button", "cleaned")):
                raise RuntimeError("sample manifest extraction allowlist contains a forbidden member")
            result.setdefault(member, []).append((public_id, role, str(spec["sha256"])))
    return result


def _copy_and_hash(source: BinaryIO, destinations: list[Path]) -> str:
    value = sha256()
    handles = [path.open("wb") for path in destinations]
    try:
        while chunk := source.read(1024 * 1024):
            value.update(chunk)
            for handle in handles:
                handle.write(chunk)
    finally:
        for handle in handles:
            handle.close()
    return value.hexdigest()


def verify_prepared(root: Path) -> None:
    for public_id, sample in SAMPLES["samples"].items():
        sample_root = root / public_id
        for role in ("selected", "context_before", "context_after", "metadata"):
            spec = sample[role]
            path = sample_root / Path(spec["member"]).name
            if digest(path, "sha256") != spec["sha256"]:
                raise RuntimeError(f"prepared member digest mismatch for {public_id}:{role}")
        selected = np.load(sample_root / Path(sample["selected"]["member"]).name, mmap_mode="r", allow_pickle=False)
        if selected.dtype != np.dtype("float64") or selected.shape != (int(sample["sample_count"]), 8):
            raise RuntimeError(f"selected member shape/dtype mismatch for {public_id}")
        if not np.isfinite(selected).all():
            raise RuntimeError(f"selected member is non-finite for {public_id}")
        for role in ("context_before", "context_after"):
            context = np.load(sample_root / Path(sample[role]["member"]).name, mmap_mode="r", allow_pickle=False)
            if context.dtype != np.dtype("float64") or context.ndim != 2 or context.shape[1] != 8 or not np.isfinite(context).all():
                raise RuntimeError(f"context shape/dtype mismatch for {public_id}:{role}")
        metadata = json.loads((sample_root / Path(sample["metadata"]["member"]).name).read_text(encoding="utf-8"))
        chunks = metadata.get("chunks", ())
        if sum(int(chunk[0]) for chunk in chunks) != int(sample["sample_count"]):
            raise RuntimeError(f"metadata chunk count mismatch for {public_id}")
        text = str(metadata.get("text", "")).strip().strip('"“”')
        if text != sample["prompt"]:
            raise RuntimeError(f"metadata prompt mismatch for {public_id}")


def extract_replays(archive: Path, asset_dir: Path) -> None:
    targets = extraction_targets()
    with tempfile.TemporaryDirectory(prefix=".prepare-replays-", dir=asset_dir) as temporary_name:
        staging = Path(temporary_name) / "replays"
        for entries in targets.values():
            for public_id, _, _ in entries:
                (staging / public_id).mkdir(parents=True, exist_ok=True)
        found: set[str] = set()
        with tarfile.open(archive, "r:gz") as package:
            for member in package:
                entries = targets.get(member.name)
                if entries is None:
                    continue
                source = package.extractfile(member)
                if source is None or not member.isfile():
                    raise RuntimeError("configured archive member is not a regular file")
                destinations = [staging / public_id / Path(member.name).name for public_id, _, _ in entries]
                actual = _copy_and_hash(source, destinations)
                if any(actual != expected for _, _, expected in entries):
                    raise RuntimeError("configured archive member digest mismatch")
                found.add(member.name)
        missing = set(targets) - found
        if missing:
            raise RuntimeError("official archive is missing one or more frozen allowlisted members")
        verify_prepared(staging)
        output = asset_dir / "replays"
        previous = asset_dir / ".replays-previous"
        if previous.exists():
            shutil.rmtree(previous)
        if output.exists():
            output.replace(previous)
        try:
            staging.replace(output)
        except Exception:
            if previous.exists() and not output.exists():
                previous.replace(output)
            raise
        if previous.exists():
            shutil.rmtree(previous)


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
        "schema_version": 2,
        "model_sha256": ASSETS["model"]["checkpoint"]["sha256"],
        "dataset_sha256": ASSETS["dataset"]["archive"]["sha256"],
        "catalogue_version": SAMPLES["catalogue_version"],
        "sample_count": len(SAMPLES["samples"]),
        "mode": "official_recorded_replay_one_official_released_checkpoint",
        "network_used": bool(args.download_missing),
    }
    temporary_ready = args.asset_dir / ".ready.prepare"
    temporary_ready.write_text(json.dumps(ready, indent=2) + "\n", encoding="utf-8")
    temporary_ready.replace(args.asset_dir / "ready.json")
    verify(checkpoint, ASSETS["model"]["checkpoint"])
    print("verified one official checkpoint and 11 frozen official recordings; no audio/button/synthetic member prepared")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
