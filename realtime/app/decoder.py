"""Project bounded phoneme-edit algorithm; not a released or trained model.

Every run uses the same complete frozen grammar. The selected sample reference is
never an argument to this module.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import json
import re

import cmudict
import torch

from .config import DIAGNOSTIC_THRESHOLD, SAMPLE_MANIFEST_PATH
from .model import collapsed_phoneme_path

CMU_DICTIONARY = cmudict.dict()


@dataclass(frozen=True)
class Candidate:
    text: str
    diagnostic_score: float
    phoneme_distance: int
    phonemes: tuple[str, ...]


@dataclass(frozen=True)
class DecodeResult:
    raw_phonemes: tuple[str, ...]
    candidates: tuple[Candidate, ...]
    phoneme_alignment_score: float
    frame_top_class_diagnostic: float
    decoder_agreement: float
    status: str
    reason: str
    safety_sensitive: bool


@lru_cache(maxsize=1)
def frozen_grammar(path: Path = SAMPLE_MANIFEST_PATH) -> tuple[tuple[str, str], ...]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    result: list[tuple[str, str]] = []
    seen: set[str] = set()
    for public_id in [f"QC-R{index:02d}" for index in range(1, 11)]:
        sample = manifest["samples"][public_id]
        prompt = str(sample["prompt"])
        if prompt not in seen:
            result.append((prompt, str(sample["decoder_text"])))
            seen.add(prompt)
    if len(result) != 10:
        raise RuntimeError("frozen decoder grammar must contain ten catalogue prompts")
    return tuple(result)


@lru_cache(maxsize=1)
def safety_prompts(path: Path = SAMPLE_MANIFEST_PATH) -> frozenset[str]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    return frozenset(
        str(sample["prompt"])
        for sample in manifest["samples"].values()
        if sample.get("safety_sensitive")
    )


@lru_cache(maxsize=None)
def _pronunciation(text: str) -> tuple[str, ...]:
    result: list[str] = []
    for word in text.lower().split():
        pronunciations = CMU_DICTIONARY.get(word)
        if pronunciations:
            result.extend(re.sub(r"\d", "", phone).lower() for phone in pronunciations[0])
            continue
        # Generic, deterministic OOV handling spells alphabetic tokens with the
        # same dictionary. It is part of the project diagnostic, not a model.
        if not word.isalpha():
            raise ValueError(f"pronunciation dependency has no entry for frozen grammar token {word!r}")
        for letter in word:
            letter_pronunciations = CMU_DICTIONARY.get(letter)
            if not letter_pronunciations:
                raise ValueError(f"pronunciation dependency cannot spell frozen grammar token {word!r}")
            result.extend(re.sub(r"\d", "", phone).lower() for phone in letter_pronunciations[0])
    return tuple(result)


def _edit_distance(left: tuple[str, ...], right: tuple[str, ...]) -> int:
    previous = list(range(len(right) + 1))
    for left_index, left_phone in enumerate(left, start=1):
        current = [left_index]
        for right_index, right_phone in enumerate(right, start=1):
            current.append(min(
                current[-1] + 1,
                previous[right_index] + 1,
                previous[right_index - 1] + (left_phone != right_phone),
            ))
        previous = current
    return previous[-1]


def decode_phonemes(phoneme_logits: torch.Tensor) -> DecodeResult:
    """Rank the complete grammar from real auxiliary-head output."""
    if phoneme_logits.ndim != 2 or phoneme_logits.shape[1] != 48:
        raise ValueError("released auxiliary-head output must be [frames,48]")
    raw_path = collapsed_phoneme_path(phoneme_logits)
    rows: list[tuple[str, tuple[str, ...], int]] = []
    for display_text, decoder_text in frozen_grammar():
        pronunciation = _pronunciation(decoder_text)
        rows.append((display_text, pronunciation, _edit_distance(raw_path, pronunciation)))
    rows.sort(key=lambda row: (row[2], row[0]))
    distances = torch.tensor([-float(row[2]) for row in rows], dtype=torch.float64)
    candidate_diagnostics = torch.softmax(distances, dim=0)
    candidates = tuple(
        Candidate(
            text=row[0],
            diagnostic_score=round(float(candidate_diagnostics[index]), 6),
            phoneme_distance=row[2],
            phonemes=row[1],
        )
        for index, row in enumerate(rows[:3])
    )
    top = rows[0]
    agreement = max(0.0, 1.0 - top[2] / max(len(raw_path), len(top[1]), 1))
    probabilities = torch.softmax(phoneme_logits.float(), dim=-1)
    frame_diagnostic = float(probabilities.max(dim=-1).values.mean().item())
    alignment = agreement * (0.70 + 0.30 * frame_diagnostic)
    top_text = candidates[0].text
    if alignment < DIAGNOSTIC_THRESHOLD:
        status = "abstain"
        reason = "Phoneme alignment is below the bounded decoder threshold; no final result is available."
    else:
        status = "confirm_required"
        reason = "Candidate is held for mandatory human confirmation; no actuation is connected."
    return DecodeResult(
        raw_phonemes=raw_path,
        candidates=candidates,
        phoneme_alignment_score=round(alignment, 4),
        frame_top_class_diagnostic=round(frame_diagnostic, 4),
        decoder_agreement=round(agreement, 4),
        status=status,
        reason=reason,
        safety_sensitive=top_text in safety_prompts(),
    )
