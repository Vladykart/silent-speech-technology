#!/usr/bin/env python3
"""Zero-download structural, claim, manifest, client, and deployment guard validation."""
from __future__ import annotations

from pathlib import Path
import ast
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parent
REQUIRED = (
    "spec/INVESTOR_REAL_REPLAY_SPEC.md", "README.md", "OPERATOR.md", "THIRD_PARTY_NOTICES.md", "QA.md",
    "assets-manifest.json", "sample-manifest.json", "model-registry.json", "evaluation-protocol.json", "release-manifest.json",
    "generate_release_manifest.py", "fetch_assets.py", "requirements.txt", "run-local.sh",
    "app/config.py", "app/asset_registry.py", "app/evaluation_protocol.py", "app/signal_source.py", "app/preprocessing.py",
    "app/upstream_transformer.py", "app/model.py", "app/decoder.py", "app/pipeline.py",
    "app/display_payload.py", "app/service.py", "client/index.html", "client/styles.css",
    "client/replay-contract.js", "client/app.js", "tests/test_assets.py", "tests/test_pipeline.py",
    "tests/test_api.py", "tests/test_evaluation_protocol.py", "tests/client_contract.test.js", "tests/responsive_contract.test.py", "tests/rendered_browser_qa.mjs",
    "deploy/README.md", "deploy/firstmate-silent-speech-demo.service", "deploy/preflight.sh",
    "deploy/deploy.sh", "deploy/rollback.sh", "deploy/verify.sh", "deploy/evidence/README.md",
)
PROMPTS = (
    "What news?", "09:48 AM", "Keep back!", "I myself heard nothing of that.", "I know I did.",
    "I could not credit it.", "I felt a tug at the reins.", "That was it!", "Are we far from Sunbury?",
    "Had they prepared pitfalls?",
)


def load(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    for relative in REQUIRED:
        if not (ROOT / relative).is_file(): errors.append(f"missing {relative}")
    if errors:
        print("realtime validation failed:", *[f"- {item}" for item in errors], sep="\n"); return 1

    for path in [ROOT / "fetch_assets.py", ROOT / "validate.py", ROOT / "generate_release_manifest.py", *(ROOT / "app").glob("*.py"), *(ROOT / "tests").glob("*.py")]:
        try: ast.parse(path.read_text(), filename=str(path))
        except SyntaxError as error: errors.append(f"Python syntax: {error}")
    for path in (ROOT / "deploy").glob("*.sh"):
        result = subprocess.run(["bash", "-n", str(path)], capture_output=True, text=True)
        if result.returncode: errors.append(f"shell syntax {path.name}: {result.stderr.strip()}")
    for path in (ROOT / "client").glob("*.js"):
        result = subprocess.run(["node", "--check", str(path)], capture_output=True, text=True)
        if result.returncode: errors.append(f"JavaScript syntax {path.name}: {result.stderr.strip()}")

    assets, samples, models, evaluation = load("assets-manifest.json"), load("sample-manifest.json"), load("model-registry.json"), load("evaluation-protocol.json")
    if assets.get("schema_version") != 2: errors.append("assets manifest schema must be 2")
    expected_assets = {
        "model archive SHA": (assets["model"]["archive"].get("sha256"), "be370313ffc53e4d9c118032d7eededd9c807f8b8449fadcb2eb2008379a3f54"),
        "checkpoint SHA": (assets["model"]["checkpoint"].get("sha256"), "67d40b64f7831ae15c3c24264e2d13cdff98a212953901048d2923b3db60171a"),
        "parameters": (assets["model"]["checkpoint"].get("trainable_parameters"), 54_187_136),
        "dataset SHA": (assets["dataset"]["archive"].get("sha256"), "1a4b205195185d2972923ed4fdaa71bb51cc01462c6b1ab279ed4d00acbd0089"),
        "code commit": (assets["code_reference"].get("commit"), "a89357c2086609b432919b9d14ffc0be5d8983d5"),
        "cmudict package": (assets["dependencies"]["cmudict_python_package"].get("license"), "GPL-3.0-or-later"),
    }
    for label, (actual, expected) in expected_assets.items():
        if actual != expected: errors.append(f"wrong {label}: {actual!r}")
    expected_ids = {*(f"QC-R{index:02d}" for index in range(1, 11)), "QC-R02-T2"}
    if set(samples.get("samples", {})) != expected_ids: errors.append("frozen sample IDs differ")
    if sum(bool(item.get("catalogue_card")) for item in samples["samples"].values()) != 10: errors.append("catalogue must expose ten cards")
    if samples["samples"]["QC-R02"].get("second_take_id") != "QC-R02-T2": errors.append("second take binding differs")
    for public_id, sample in samples["samples"].items():
        if sample.get("prompt") not in PROMPTS: errors.append(f"unknown frozen prompt: {public_id}")
        if sample.get("native_dtype") not in (None, "float64"): errors.append(f"wrong source dtype: {public_id}")
        for role in ("selected", "metadata", "context_before", "context_after"):
            if not re.fullmatch(r"[0-9a-f]{64}", sample.get(role, {}).get("sha256", "")): errors.append(f"bad member digest: {public_id}:{role}")
    if models.get("schema_version") != 2: errors.append("model registry schema must be 2")
    readiness = set(models.get("required_readiness_fields", ()))
    executed = [item for item in models.get("entries", []) if item.get("status") == "executed"]
    evidence = [item for item in models.get("entries", []) if item.get("status") == "evidence_only"]
    gate_fields = ("weights_available", "rights_verified", "checksum_verified", "runtime_approved")
    if len(executed) != 1 or executed[0].get("parameters") != 54_187_136: errors.append("registry must have one exact executed model")
    if executed and (executed[0].get("type") != "checkpoint" or not all(executed[0].get(field) is True for field in gate_fields)): errors.append("executed checkpoint has not passed every readiness gate")
    if not readiness or any(not readiness.issubset(item) for item in models.get("entries", [])): errors.append("model registry readiness matrix is incomplete")
    if not evidence or any(item.get("badge") != "NOT EXECUTED HERE" or not item.get("not_executed_reason") for item in evidence): errors.append("evidence-only registry lacks explicit status/reason")
    if any(item.get("runtime_approved") is not False or not item.get("comparability_notes") for item in evidence): errors.append("evidence-only registry lacks runtime/comparability boundary")
    if evaluation.get("status") != "protocol_only_no_results" or evaluation.get("execution_authorized") is not False or evaluation.get("results") is not None: errors.append("evaluation plan must remain protocol-only with no results or execution authority")
    if "unknown" not in evaluation.get("source_scope", {}).get("training_overlap", "").lower(): errors.append("evaluation plan overstates training overlap")
    if evaluation.get("selection", {}).get("replacement_after_freeze") != "prohibited": errors.append("evaluation plan permits post-freeze replacement")
    decoder = next((item for item in models.get("entries", []) if item.get("id") == "project-phoneme-edit-decoder"), {})
    if decoder.get("type") != "algorithm" or not decoder.get("not_a_model"): errors.append("decoder is not typed as a non-model algorithm")

    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in {"local_assets", ".venv", "__pycache__"} for part in path.parts): continue
        if path.suffix.lower() in {".pt", ".pth", ".npy", ".h5", ".flac", ".wav", ".gz", ".zip"}: errors.append(f"research asset must not be committed: {path.relative_to(ROOT)}")

    html = (ROOT / "client/index.html").read_text()
    css = (ROOT / "client/styles.css").read_text()
    app_js = (ROOT / "client/app.js").read_text()
    reducer = (ROOT / "client/replay-contract.js").read_text()
    browser = html + css + app_js + reducer
    if re.search(r"https?://", browser, re.I): errors.append("browser assets contain an external URL")
    for prompt in PROMPTS:
        if prompt in browser: errors.append(f"browser prompt leak: {prompt}")
    for token in ("sendBeacon", "localStorage", "sessionStorage", "indexedDB", "serviceWorker", "WebSocket", "EventSource", "RTCPeerConnection", "getUserMedia", "mediaDevices"):
        if token in browser: errors.append(f"browser uses prohibited API: {token}")
    if re.search(r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])", browser): errors.append("browser assets contain a full digest")
    if re.findall(r'data-stage-panel="([^"]+)"', html) != ["recorded-source", "released-model", "human-decision"]: errors.append("workspace must have exactly three ordered stages")
    if len(re.findall(r'data-sample-id="QC-R', html)) != 10: errors.append("client must contain ten cards")
    for phrase in (
        "ONE REAL RELEASED PRETRAINED MODEL", "NOT LIVE CAPTURE", "RECORDED SOURCE TRACE · TRANSFORMED DISPLAY ENVELOPE",
        "EXECUTED MODEL 1 OF 1", "PROJECT BOUNDED DECODER · NOT THE RELEASED MODEL", "NOT EXECUTED HERE",
        "Bounded transformed evidence is sent to this authorized browser", "No live hardware; no project accuracy/WER",
        "only currently approved, checksum-bound, and executable checkpoint", "PROTOCOL ONLY · NO RESULTS",
    ):
        if phrase not in html: errors.append(f"missing browser truth/evidence label: {phrase}")
    for misleading in ("NO EGRESS", "forward-pass time", "unchanged raw values", "untouched official"):
        if misleading.lower() in browser.lower(): errors.append(f"misleading browser label: {misleading}")
    if ":focus-visible" not in css or "prefers-reduced-motion: reduce" not in css or "max-width: 1100px" not in css: errors.append("responsive/focus/reduced-motion contract missing")
    if re.search(r"overflow-x:\s*(?:hidden|clip)", css): errors.append("CSS masks horizontal overflow")

    production = "\n".join(path.read_text() for path in (ROOT / "app").glob("*.py"))
    if "SimulatedSignalSource" in production: errors.append("production import graph contains simulator")
    if "docs_url=None" not in production or "openapi_url=None" not in production: errors.append("OpenAPI/docs are not disabled")
    service = (ROOT / "app/service.py").read_text()
    for route in ("/api/v1/manifest", "/api/v1/runs", "/events", "/stop", "/decision", "/second-take"):
        if route not in service: errors.append(f"missing safe API route: {route}")
    for old in ('@app.get("/api/health")', '"/api/scenarios"', '"/api/sessions"'):
        if old in service: errors.append(f"old API route remains: {old}")

    notice = (ROOT / "THIRD_PARTY_NOTICES.md").read_text()
    if "GPL-3.0-or-later" not in notice or "CMU Pronouncing Dictionary data" not in notice: errors.append("cmudict package/data rights separation missing")
    if "permissive 3-clause BSD-style license; package" in notice: errors.append("false permissive-only cmudict notice remains")
    deploy_scripts = "\n".join(path.read_text() for path in (ROOT / "deploy").glob("*.sh"))
    if re.search(r"tailscale\s+serve\s+(?:--|https|tcp|set)", deploy_scripts) or re.search(r"tailscale\s+funnel\s+(?:--|on|off|set)", deploy_scripts): errors.append("deployment script mutates Tailscale")
    if "--host 127.0.0.1 --port 8765 --no-access-log" not in (ROOT / "deploy/firstmate-silent-speech-demo.service").read_text(): errors.append("service template is not loopback/no-access-log")

    for command in (["node", str(ROOT / "tests/client_contract.test.js")], ["python3", str(ROOT / "tests/responsive_contract.test.py")]):
        result = subprocess.run(command, cwd=ROOT.parent, capture_output=True, text=True)
        if result.returncode: errors.append(f"contract test failed ({' '.join(command)}): {result.stdout}{result.stderr}")

    if errors:
        print("realtime validation failed:", *[f"- {item}" for item in errors], sep="\n"); return 1
    print("realtime validation passed: frozen official assets, one executed model, sealed ordered API, bounded evidence client, claims, accessibility, and private deployment templates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
