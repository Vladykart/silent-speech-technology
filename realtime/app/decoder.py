"""Modern phoneme-grammar decoder for the released model's auxiliary head.

The checkpoint's text path in the original repository synthesized speech and
used legacy DeepSpeech 0.7. That binary stack is unavailable on Python 3.12.
This adapter decodes the model's *real trained phoneme emissions* directly with
CMUdict pronunciations and phoneme edit distance. It does not use reference
labels from the selected replay.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import re

import cmudict
import torch

from .config import CONFIDENCE_THRESHOLD, REPLAY_GRAMMAR, SAFETY_SENSITIVE
from .model import collapsed_phoneme_path

CMU_DICTIONARY = cmudict.dict()


@dataclass(frozen=True)
class Candidate:
    text: str
    score: float
    phoneme_distance: int
    phonemes: tuple[str, ...]


@dataclass(frozen=True)
class DecodeResult:
    raw_phonemes: tuple[str, ...]
    candidates: tuple[Candidate, ...]
    confidence: float
    frame_certainty: float
    decoder_agreement: float
    status: str
    reason: str
    safety_sensitive: bool


@lru_cache(maxsize=None)
def _pronunciation(text: str) -> tuple[str, ...]:
    dictionary = CMU_DICTIONARY
    result: list[str] = []
    for word in text.lower().split():
        pronunciations = dictionary.get(word)
        if not pronunciations:
            raise ValueError(f"CMUdict has no pronunciation for grammar word {word!r}")
        result.extend(re.sub(r"\d", "", phone).lower() for phone in pronunciations[0])
    return tuple(result)


def _edit_distance(left: tuple[str, ...], right: tuple[str, ...]) -> int:
    previous = list(range(len(right) + 1))
    for left_index, left_phone in enumerate(left, start=1):
        current = [left_index]
        for right_index, right_phone in enumerate(right, start=1):
            current.append(
                min(
                    current[-1] + 1,
                    previous[right_index] + 1,
                    previous[right_index - 1] + (left_phone != right_phone),
                )
            )
        previous = current
    return previous[-1]


def decode_phonemes(phoneme_logits: torch.Tensor) -> DecodeResult:
    """Decode free phoneme emissions against the bounded real-prompt grammar."""
    raw_path = collapsed_phoneme_path(phoneme_logits)
    rows: list[tuple[str, tuple[str, ...], int]] = []
    for display_text, decoder_text in REPLAY_GRAMMAR:
        pronunciation = _pronunciation(decoder_text)
        rows.append((display_text, pronunciation, _edit_distance(raw_path, pronunciation)))
    rows.sort(key=lambda row: row[2])
    # Scores compare grammar candidates only; they are not calibrated probabilities.
    distances = torch.tensor([-float(row[2]) for row in rows], dtype=torch.float64)
    candidate_scores = torch.softmax(distances, dim=0)
    candidates = tuple(
        Candidate(
            text=row[0],
            score=round(float(candidate_scores[index]), 6),
            phoneme_distance=row[2],
            phonemes=row[1],
        )
        for index, row in enumerate(rows[:3])
    )
    top = rows[0]
    agreement = max(0.0, 1.0 - top[2] / max(len(raw_path), len(top[1]), 1))
    probabilities = torch.softmax(phoneme_logits.float(), dim=-1)
    frame_certainty = float(probabilities.max(dim=-1).values.mean().item())
    confidence = agreement * (0.70 + 0.30 * frame_certainty)
    top_text = candidates[0].text
    if confidence < CONFIDENCE_THRESHOLD:
        status = "abstain"
        reason = "Free phoneme path is below the bounded replay-decoder threshold; no output is available."
    else:
        status = "confirm_required"
        reason = (
            "Safety-sensitive replay candidate: explicit confirmation is mandatory."
            if top_text in SAFETY_SENSITIVE
            else "Decoded replay candidate is held for human confirmation."
        )
    return DecodeResult(
        raw_phonemes=raw_path,
        candidates=candidates,
        confidence=round(confidence, 4),
        frame_certainty=round(frame_certainty, 4),
        decoder_agreement=round(agreement, 4),
        status=status,
        reason=reason,
        safety_sensitive=top_text in SAFETY_SENSITIVE,
    )
