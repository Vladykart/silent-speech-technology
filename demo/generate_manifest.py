#!/usr/bin/env python3
"""Generate or verify the deterministic SHA-256 manifest for the demo tree."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "artifact-manifest.json"
EXCLUDED = {MANIFEST.name}


def public_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.name in EXCLUDED:
            continue
        relative = path.relative_to(ROOT)
        if "__pycache__" in relative.parts or path.suffix == ".pyc":
            raise RuntimeError(f"generated cache is not a public artifact: {relative.as_posix()}")
        if path.is_symlink():
            raise RuntimeError(f"symbolic links are not allowed in the demo artifact: {relative.as_posix()}")
        files.append(path)
    return sorted(files, key=lambda item: item.relative_to(ROOT).as_posix())


def build_manifest() -> dict[str, object]:
    records = []
    for path in public_files():
        payload = path.read_bytes()
        records.append({
            "path": path.relative_to(ROOT).as_posix(),
            "bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
        })
    return {
        "schema": "quiet-channel-static-artifact/v1",
        "algorithm": "sha256",
        "base": "demo/",
        "selfHashExcluded": MANIFEST.name,
        "files": records,
    }


def encoded_manifest() -> bytes:
    return (json.dumps(build_manifest(), indent=2, ensure_ascii=True) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="replace artifact-manifest.json")
    args = parser.parse_args()
    expected = encoded_manifest()
    if args.write:
        MANIFEST.write_bytes(expected)
        print(f"wrote {MANIFEST.relative_to(ROOT.parent)} with {len(build_manifest()['files'])} file hashes")
        return 0
    if not MANIFEST.is_file():
        print("manifest check failed: artifact-manifest.json is missing")
        return 1
    if MANIFEST.read_bytes() != expected:
        print("manifest check failed: run python3 demo/generate_manifest.py --write")
        return 1
    print(f"manifest check passed: {len(build_manifest()['files'])} files match SHA-256 evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
