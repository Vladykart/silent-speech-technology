"""Configuration and bounded replay policy for the local research service."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = Path(os.getenv("SILENT_SPEECH_ASSET_DIR", ROOT / "local_assets"))
MODEL_PATH = ASSET_DIR / "model" / "pretrained_models" / "transduction_model.pt"
REPLAY_ROOT = ASSET_DIR / "replays"
ASSET_MANIFEST_PATH = ROOT / "assets-manifest.json"
SAMPLE_RATE = 1_000
CHANNELS = 8
CHUNK_SAMPLES = 128
CONFIDENCE_THRESHOLD = 0.60


@dataclass(frozen=True)
class Scenario:
    id: str
    title: str
    description: str
    sample_group: str
    sample_index: int
    reference_prompt: str
    decoder_text: str
    evaluation_split: str
    safety_sensitive: bool = False
    repair_group: str | None = None
    repair_index: int | None = None


SCENARIOS = {
    "clear": Scenario(
        "clear",
        "Held-out research replay",
        "Real silent facial-sEMG recording from the source's large development split.",
        "clear",
        314,
        "What news?",
        "what news",
        "largedev/dev",
    ),
    "ambiguous": Scenario(
        "ambiguous",
        "Recorded replay → abstain → repair",
        "A real closed-vocabulary recording; repair replays a second real take of the same prompt.",
        "ambiguous",
        379,
        "09:48 AM",
        "nine forty eight a m",
        "closed-vocabulary research set",
        repair_group="repair",
        repair_index=310,
    ),
    "safety": Scenario(
        "safety",
        "Safety-sensitive prompt replay",
        "Real silent facial-sEMG for “Keep back!”; no actuation is connected.",
        "safety",
        91,
        "Keep back!",
        "keep back",
        "largedev/dev",
        safety_sensitive=True,
    ),
}

# Every grammar entry is a prompt that occurs in the official dataset. The
# reference prompt is never passed into model.forward; all entries compete in
# the phoneme alignment decoder.
REPLAY_GRAMMAR = (
    ("What news?", "what news"),
    ("09:48 AM", "nine forty eight a m"),
    ("Keep back!", "keep back"),
    ("That was it!", "that was it"),
    ("I know I did.", "i know i did"),
    ("To get under water!", "to get under water"),
)
SAFETY_SENSITIVE = frozenset({"Keep back!"})
