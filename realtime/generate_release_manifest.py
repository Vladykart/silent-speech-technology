#!/usr/bin/env python3
"""Generate deterministic runtime/source binding for an immutable release checkout."""
from __future__ import annotations

from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
import json
import os
import subprocess

ROOT = Path(__file__).resolve().parent
REPOSITORY = ROOT.parent
OUTPUT = ROOT / "release-manifest.json"


def digest(path: Path) -> str:
    value = sha256()
    value.update(path.read_bytes())
    return value.hexdigest()


def runtime_files() -> list[Path]:
    files = [
        ROOT / "assets-manifest.json",
        ROOT / "sample-manifest.json",
        ROOT / "model-registry.json",
        ROOT / "evaluation-protocol.json",
        ROOT / "requirements.txt",
        ROOT / "fetch_assets.py",
        ROOT / "run-local.sh",
    ]
    files.extend(sorted((ROOT / "app").glob("*.py")))
    files.extend(sorted((ROOT / "client").glob("*")))
    return sorted(path for path in files if path.is_file() and path != OUTPUT)


def current_revision() -> str:
    configured = os.getenv("QUIET_CHANNEL_RELEASE_REVISION")
    if configured:
        return configured
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPOSITORY, text=True).strip()


def build(revision: str) -> dict:
    if len(revision) != 40 or any(character not in "0123456789abcdef" for character in revision.lower()):
        raise ValueError("application revision must be a full 40-hex git commit")
    paths = runtime_files()
    return {
        "schema_version": 1,
        "application_revision": revision.lower(),
        "revision_semantics": "runtime-content source revision; deployment regenerates this file from the exact clean candidate commit",
        "asset_manifest_sha256": digest(ROOT / "assets-manifest.json"),
        "sample_manifest_sha256": digest(ROOT / "sample-manifest.json"),
        "dependency_lock_sha256": digest(ROOT / "requirements.txt"),
        "build_command": "python3 realtime/generate_release_manifest.py --revision <exact-clean-commit>",
        "files": {
            str(path.relative_to(REPOSITORY)): {"bytes": path.stat().st_size, "sha256": digest(path)}
            for path in paths
        },
    }


def verify(manifest: dict) -> None:
    for relative, expected in manifest["files"].items():
        path = REPOSITORY / relative
        if not path.is_file() or path.stat().st_size != expected["bytes"] or digest(path) != expected["sha256"]:
            raise RuntimeError(f"runtime release binding mismatch: {relative}")
    if digest(ROOT / "assets-manifest.json") != manifest["asset_manifest_sha256"]:
        raise RuntimeError("asset manifest release binding mismatch")
    if digest(ROOT / "sample-manifest.json") != manifest["sample_manifest_sha256"]:
        raise RuntimeError("sample manifest release binding mismatch")
    if digest(ROOT / "requirements.txt") != manifest["dependency_lock_sha256"]:
        raise RuntimeError("dependency lock release binding mismatch")


def main() -> int:
    parser = ArgumentParser()
    parser.add_argument("--revision", default=current_revision())
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        verify(json.loads(OUTPUT.read_text(encoding="utf-8")))
        print("release manifest matches runtime files")
        return 0
    manifest = build(args.revision)
    OUTPUT.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    verify(manifest)
    print(f"wrote deterministic release manifest for {len(manifest['files'])} runtime files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
