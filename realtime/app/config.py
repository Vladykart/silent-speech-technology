"""Configuration and command policy for the local real-model service."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "silent_ctc_v1.pt"
MANIFEST_PATH = ROOT / "models" / "silent_ctc_v1.json"

SAMPLE_RATE = 1_000
CHANNELS = 8
CHUNK_SAMPLES = 64
ALPHABET = " abcdefghijklmnopqrstuvwxyz"
BLANK_ID = 0
COMMANDS = (
    "check stock",
    "open work order",
    "next step",
    "repeat instruction",
    "hold",
    "resume",
    "show parts list",
    "note issue",
    "request supervisor",
    "cancel request",
    "yes",
    "no",
)
SAFETY_SENSITIVE = frozenset({"cancel request"})
CONFIDENCE_THRESHOLD = 0.68


@dataclass(frozen=True)
class Scenario:
    id: str
    title: str
    description: str
    utterance: str
    alternate: str | None = None
    repair_utterance: str | None = None
    quality: str = "clear"


SCENARIOS = {
    "clear": Scenario(
        "clear",
        "Clear command",
        "A moderate-noise simulated eight-channel frame; confirmation still gates output.",
        "check stock",
    ),
    "ambiguous": Scenario(
        "ambiguous",
        "Ambiguous → abstain → repair",
        "A noisy blended simulated frame should be rejected; repair captures a cleaner frame.",
        "open work order",
        alternate="note issue",
        repair_utterance="open work order",
        quality="ambiguous",
    ),
    "safety": Scenario(
        "safety",
        "Safety-sensitive command",
        "A clear decode cannot execute until the operator explicitly confirms.",
        "cancel request",
        quality="clear",
    ),
}
