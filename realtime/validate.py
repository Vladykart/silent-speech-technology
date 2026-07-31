#!/usr/bin/env python3
"""Zero-install structural and claim-boundary validation for realtime/."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import ast
import json
import re

ROOT = Path(__file__).resolve().parent
REQUIRED = (
    "README.md",
    "THIRD_PARTY_NOTICES.md",
    "QA.md",
    "requirements.txt",
    "run-local.sh",
    "train.py",
    "app/config.py",
    "app/signal_source.py",
    "app/preprocessing.py",
    "app/model.py",
    "app/decoder.py",
    "app/pipeline.py",
    "app/service.py",
    "client/index.html",
    "client/styles.css",
    "client/app.js",
    "models/silent_ctc_v1.pt",
    "models/silent_ctc_v1.json",
    "tests/test_realtime.py",
)


def main() -> int:
    errors: list[str] = []
    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            errors.append(f"missing {relative}")
    for path in [ROOT / "train.py", *(ROOT / "app").glob("*.py"), *(ROOT / "tests").glob("*.py")]:
        try:
            ast.parse(path.read_text(), filename=str(path))
        except SyntaxError as error:
            errors.append(f"Python syntax: {error}")
    manifest = json.loads((ROOT / "models/silent_ctc_v1.json").read_text())
    model = ROOT / "models/silent_ctc_v1.pt"
    if sha256(model.read_bytes()).hexdigest() != manifest.get("sha256"):
        errors.append("checkpoint does not match manifest sha256")
    if not 100_000 <= manifest.get("parameter_count", 0) <= 500_000:
        errors.append("unexpected model parameter count")
    if manifest.get("training", {}).get("human_or_biometric_data") is not False:
        errors.append("manifest must deny human/biometric training data")
    if model.stat().st_size >= 1_000_000:
        errors.append("checkpoint exceeds 1 MB repository limit")
    page = (ROOT / "client/index.html").read_text()
    docs = (ROOT / "README.md").read_text()
    combined = (page + docs).lower()
    for phrase in (
        "simulated signal + noise",
        "real model / real inference",
        "not measured accuracy",
        "no mind reading",
        "not medical",
        "no collection, accounts or telemetry",
        "dgaddy/silent_speech",
        "a89357c2086609b432919b9d14ffc0be5d8983d5",
    ):
        if phrase not in combined:
            errors.append(f"missing claim/source label: {phrase}")
    for pattern in (
        r"https?://[^\"']+\.(?:js|css)",
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
    for token in ("class SignalSource", "class SimulatedSignalSource", "class RealHardwareSignalSource", "gaussian", "drift", "artifact"):
        if token not in source:
            errors.append(f"signal contract/noise missing: {token}")
    if errors:
        print("realtime validation failed:", *[f"- {error}" for error in errors], sep="\n")
        return 1
    print(
        "realtime validation passed: real checkpoint hash/size/provenance, Python structure, "
        "API stages, hardware seam, noise components, local client and claim boundaries"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
