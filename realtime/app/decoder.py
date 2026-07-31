"""CTC sequence scoring, grammar decoding and abstention policy."""
from __future__ import annotations

from dataclasses import dataclass

import torch

from .config import COMMANDS, CONFIDENCE_THRESHOLD, SAFETY_SENSITIVE
from .model import encode_text, greedy_decode


@dataclass(frozen=True)
class Candidate:
    text: str
    score: float
    ctc_log_score: float


@dataclass(frozen=True)
class DecodeResult:
    raw_ctc: str
    candidates: tuple[Candidate, ...]
    confidence: float
    frame_certainty: float
    decoder_agreement: float
    status: str
    reason: str
    safety_sensitive: bool


def _logadd(values: list[torch.Tensor]) -> torch.Tensor:
    return torch.logsumexp(torch.stack(values), dim=0)


def ctc_sequence_log_probability(log_probs: torch.Tensor, tokens: list[int]) -> torch.Tensor:
    """Forward-algorithm probability of a label sequence under CTC."""
    blank = 0
    extended: list[int] = [blank]
    for token in tokens:
        extended.extend((token, blank))
    states = len(extended)
    negative = torch.tensor(float("-inf"), dtype=log_probs.dtype, device=log_probs.device)
    alpha = torch.full((states,), negative, dtype=log_probs.dtype, device=log_probs.device)
    alpha[0] = log_probs[0, blank]
    if states > 1:
        alpha[1] = log_probs[0, extended[1]]
    for time_index in range(1, log_probs.shape[0]):
        updated = torch.full_like(alpha, negative)
        for state, token in enumerate(extended):
            sources = [alpha[state]]
            if state > 0:
                sources.append(alpha[state - 1])
            if state > 1 and token != blank and token != extended[state - 2]:
                sources.append(alpha[state - 2])
            updated[state] = _logadd(sources) + log_probs[time_index, token]
        alpha = updated
    if states == 1:
        return alpha[0]
    return torch.logsumexp(alpha[-2:], dim=0)


def _sequence_agreement(left: str, right: str) -> float:
    """Normalized character agreement between free and grammar-constrained CTC."""
    if not left and not right:
        return 1.0
    previous = list(range(len(right) + 1))
    for left_index, left_character in enumerate(left, start=1):
        current = [left_index]
        for right_index, right_character in enumerate(right, start=1):
            current.append(
                min(
                    current[-1] + 1,
                    previous[right_index] + 1,
                    previous[right_index - 1] + (left_character != right_character),
                )
            )
        previous = current
    return max(0.0, 1.0 - previous[-1] / max(len(left), len(right), 1))


def decode_logits(logits: torch.Tensor, length: int) -> DecodeResult:
    """Decode model emissions against the approved low-consequence grammar."""
    active = logits[:length].float()
    log_probs = torch.log_softmax(active, dim=-1)
    raw_ctc = greedy_decode(active, length)
    scored = [
        (command, float(ctc_sequence_log_probability(log_probs, encode_text(command)).item()))
        for command in COMMANDS
    ]
    scored.sort(key=lambda item: item[1], reverse=True)
    top_values = torch.tensor([value for _, value in scored], dtype=torch.float64)
    # Grammar posterior is a decoder score, not a calibrated real-world probability.
    grammar_scores = torch.softmax(top_values, dim=0)
    candidates = tuple(
        Candidate(command, round(float(grammar_scores[index]), 6), round(value, 4))
        for index, (command, value) in enumerate(scored[:3])
    )
    frame_certainty = float(torch.exp(torch.mean(torch.max(log_probs, dim=-1).values)).item())
    top_grammar = float(grammar_scores[0])
    confidence = max(0.0, min(1.0, 0.55 * frame_certainty + 0.45 * top_grammar))
    top_text = candidates[0].text
    agreement = _sequence_agreement(raw_ctc, top_text)
    # Free-path/grammar disagreement catches confidently malformed emissions that a
    # closed grammar would otherwise force onto an unrelated short command.
    confidence *= 0.30 + 0.70 * agreement
    if confidence < CONFIDENCE_THRESHOLD:
        status = "abstain"
        reason = "Model score is below the command-channel threshold; no output is available."
    else:
        status = "confirm_required"
        reason = (
            "Safety-sensitive command: explicit confirmation is mandatory."
            if top_text in SAFETY_SENSITIVE
            else "Decoded command is held for human confirmation."
        )
    return DecodeResult(
        raw_ctc=raw_ctc,
        candidates=candidates,
        confidence=round(confidence, 4),
        frame_certainty=round(frame_certainty, 4),
        decoder_agreement=round(agreement, 4),
        status=status,
        reason=reason,
        safety_sensitive=top_text in SAFETY_SENSITIVE,
    )
