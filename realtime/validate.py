#!/usr/bin/env python3
"""Zero-install structure, asset-manifest and replay-claim validation."""
from __future__ import annotations

from pathlib import Path
import ast
import json
import re

ROOT = Path(__file__).resolve().parent
REQUIRED = (
    "README.md",
    "THIRD_PARTY_NOTICES.md",
    "QA.md",
    "assets-manifest.json",
    "fetch_assets.py",
    "requirements.txt",
    "run-local.sh",
    "app/config.py",
    "app/signal_source.py",
    "app/preprocessing.py",
    "app/upstream_transformer.py",
    "app/model.py",
    "app/decoder.py",
    "app/pipeline.py",
    "app/service.py",
    "client/index.html",
    "client/styles.css",
    "client/app.js",
    "tests/test_realtime.py",
)


def main() -> int:
    errors: list[str] = []
    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            errors.append(f"missing {relative}")
    for path in [ROOT / "fetch_assets.py", ROOT / "validate.py", *(ROOT / "app").glob("*.py"), *(ROOT / "tests").glob("*.py")]:
        try:
            ast.parse(path.read_text(), filename=str(path))
        except SyntaxError as error:
            errors.append(f"Python syntax: {error}")
    manifest = json.loads((ROOT / "assets-manifest.json").read_text())
    expected = {
        "model DOI": (manifest["model"]["doi"], "10.5281/zenodo.6747411"),
        "model license": (manifest["model"]["license"], "CC BY 4.0"),
        "model bytes": (manifest["model"]["checkpoint"]["bytes"], 216_859_418),
        "model SHA-256": (
            manifest["model"]["checkpoint"]["sha256"],
            "67d40b64f7831ae15c3c24264e2d13cdff98a212953901048d2923b3db60171a",
        ),
        "dataset DOI": (manifest["dataset"]["version_doi"], "10.5281/zenodo.4064409"),
        "dataset license": (manifest["dataset"]["license"], "CC BY 4.0"),
        "dataset bytes": (manifest["dataset"]["archive"]["bytes"], 3_919_507_637),
        "dataset MD5": (manifest["dataset"]["archive"]["md5"], "7f97d2182b896652999b1b2d0c69fd7b"),
        "upstream commit": (
            manifest["code_reference"]["commit"],
            "a89357c2086609b432919b9d14ffc0be5d8983d5",
        ),
    }
    for label, (actual, wanted) in expected.items():
        if actual != wanted:
            errors.append(f"wrong {label}: {actual!r}")
    if manifest["dataset"].get("single_speaker") is not True:
        errors.append("dataset single-speaker boundary missing")
    for path in ROOT.rglob("*"):
        if not path.is_file() or "local_assets" in path.parts or ".venv" in path.parts or "__pycache__" in path.parts:
            continue
        if path.suffix.lower() in {".pt", ".pth", ".npy", ".h5", ".flac", ".gz", ".zip"}:
            errors.append(f"large/research asset must not be committed: {path.relative_to(ROOT)}")
    page = (ROOT / "client/index.html").read_text()
    docs = (ROOT / "README.md").read_text()
    combined = (page + docs).lower()
    for phrase in (
        "real recorded semg",
        "real released",
        "not live capture",
        "not measured project accuracy",
        "no mind reading",
        "not medical",
        "no new collection, accounts or telemetry",
        "non-commercial",
        "cc by 4.0",
        "10.5281/zenodo.4064409",
        "10.5281/zenodo.6747411",
        "dgaddy/silent_speech",
        "a89357c2086609b432919b9d14ffc0be5d8983d5",
    ):
        if phrase not in combined:
            errors.append(f"missing claim/source label: {phrase}")
    for pattern in (
        r"<script[^>]+src=[\"']https?://",
        r"<link[^>]+href=[\"']https?://[^>]+stylesheet",
    ):
        if re.search(pattern, page, re.I):
            errors.append(f"remote frontend dependency: {pattern}")
    service = (ROOT / "app/service.py").read_text()
    for route in ("/api/health", "/api/scenarios", "/api/sessions", "/stream", "/stop", "/decision", "/repair"):
        if route not in service:
            errors.append(f"missing API route {route}")
    source = (ROOT / "app/signal_source.py").read_text()
    for token in ("class SignalSource", "class RecordedEMGReplaySource", "class RealHardwareSignalSource", "class SimulatedSignalSource"):
        if token not in source:
            errors.append(f"signal contract missing: {token}")
    config_service = (ROOT / "app/config.py").read_text() + service
    if "SimulatedSignalSource(" in config_service:
        errors.append("default scenario/service must not instantiate simulated acquisition")
    if errors:
        print("realtime validation failed:", *[f"- {error}" for error in errors], sep="\n")
        return 1
    print(
        "realtime validation passed: official model/data identity and rights, no committed assets, "
        "recorded-replay default, hardware seam, local client and claim boundaries"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
