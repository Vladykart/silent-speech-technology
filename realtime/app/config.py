"""Safe public configuration and bounded policy for the investor replay."""
from __future__ import annotations

from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = Path(os.getenv("SILENT_SPEECH_ASSET_DIR", ROOT / "local_assets"))
MODEL_PATH = ASSET_DIR / "model" / "pretrained_models" / "transduction_model.pt"
REPLAY_ROOT = ASSET_DIR / "replays"
ASSET_MANIFEST_PATH = ROOT / "assets-manifest.json"
SAMPLE_MANIFEST_PATH = ROOT / "sample-manifest.json"
MODEL_REGISTRY_PATH = ROOT / "model-registry.json"
EVALUATION_PROTOCOL_PATH = ROOT / "evaluation-protocol.json"
RELEASE_MANIFEST_PATH = ROOT / "release-manifest.json"
SAMPLE_RATE = 1_000
CHANNELS = 8
CHUNK_SAMPLES = 128
DIAGNOSTIC_THRESHOLD = 0.60
PUBLIC_SAMPLE_IDS = tuple(f"QC-R{index:02d}" for index in range(1, 11))
SECOND_TAKE_ID = "QC-R02-T2"
MAX_ACTIVE_RUNS = 4
RUN_TTL_SECONDS = 15 * 60
APP_REVISION = os.getenv("QUIET_CHANNEL_REVISION", "unbound")[:12]
TRUTH = "Replay of official single-speaker recorded sEMG through David Gaddy’s official released pretrained model; not live capture."
LIMITATION = (
    "No live hardware; no project accuracy/WER; no open-vocabulary, cross-speaker/session, customer, "
    "medical/AAC, safety-system, comfort, privacy, production, or deployment-performance evidence. "
    "Official source scope is single-speaker English research data."
)
