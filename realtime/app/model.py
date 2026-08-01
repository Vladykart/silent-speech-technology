"""Exact architecture adapter for David Gaddy's released transduction weights.

The layer names and tensor shapes intentionally match ``architecture.py`` at
commit a89357c2086609b432919b9d14ffc0be5d8983d5. Code is MIT; the downloaded
model artifact is CC BY 4.0. See THIRD_PARTY_NOTICES.md.
"""
from __future__ import annotations

from copy import deepcopy

import torch
from torch import nn
import torch.nn.functional as functional

from .upstream_transformer import TransformerEncoderLayer

PHONEME_INVENTORY = (
    "aa", "ae", "ah", "ao", "aw", "ax", "axr", "ay", "b", "ch", "d", "dh",
    "dx", "eh", "el", "em", "en", "er", "ey", "f", "g", "hh", "hv", "ih",
    "iy", "jh", "k", "l", "m", "n", "nx", "ng", "ow", "oy", "p", "r",
    "s", "sh", "t", "th", "uh", "uw", "v", "w", "y", "z", "zh", "sil",
)


class ResidualBlock(nn.Module):
    """Raw-EMG residual block with upstream-compatible state names."""

    def __init__(self, inputs: int, outputs: int, stride: int = 1) -> None:
        super().__init__()
        self.conv1 = nn.Conv1d(inputs, outputs, 3, padding=1, stride=stride)
        self.bn1 = nn.BatchNorm1d(outputs)
        self.conv2 = nn.Conv1d(outputs, outputs, 3, padding=1)
        self.bn2 = nn.BatchNorm1d(outputs)
        if stride != 1 or inputs != outputs:
            self.residual_path = nn.Conv1d(inputs, outputs, 1, stride=stride)
            self.res_norm = nn.BatchNorm1d(outputs)
        else:
            self.residual_path = None

    def forward(self, value: torch.Tensor) -> torch.Tensor:
        input_value = value
        value = functional.relu(self.bn1(self.conv1(value)))
        value = self.bn2(self.conv2(value))
        residual = (
            self.res_norm(self.residual_path(input_value))
            if self.residual_path is not None
            else input_value
        )
        return functional.relu(value + residual)


class ReleasedTransformerEncoder(nn.Module):
    """Simple upstream-compatible stack avoiding modern nested-tensor rewrites."""

    def __init__(self, layer: nn.Module, count: int) -> None:
        super().__init__()
        self.layers = nn.ModuleList(deepcopy(layer) for _ in range(count))

    def forward(self, value: torch.Tensor) -> torch.Tensor:
        for layer in self.layers:
            value = layer(value)
        return value


class ReleasedGaddyTransductionModel(nn.Module):
    """54M-parameter raw EMG → mel features + phoneme emissions model."""

    def __init__(self) -> None:
        super().__init__()
        hidden = 768
        self.conv_blocks = nn.Sequential(
            ResidualBlock(8, hidden, 2),
            ResidualBlock(hidden, hidden, 2),
            ResidualBlock(hidden, hidden, 2),
        )
        self.w_raw_in = nn.Linear(hidden, hidden)
        layer = TransformerEncoderLayer(
            d_model=hidden,
            nhead=8,
            relative_positional=True,
            relative_positional_distance=100,
            dim_feedforward=3072,
            dropout=0.2,
        )
        self.transformer = ReleasedTransformerEncoder(layer, 6)
        self.w_out = nn.Linear(hidden, 80)
        self.w_aux = nn.Linear(hidden, len(PHONEME_INVENTORY))

    def forward(self, raw_emg: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """Run the released inference path on preprocessed raw EMG.

        ``raw_emg`` shape is batch × time × 8. The upstream feature and session
        arguments were unused by this checkpoint's architecture, so this adapter
        does not manufacture placeholder values for them.
        """
        value = self.conv_blocks(raw_emg.transpose(1, 2)).transpose(1, 2)
        value = self.w_raw_in(value).transpose(0, 1)
        value = self.transformer(value).transpose(0, 1)
        return self.w_out(value), self.w_aux(value)


def collapsed_phoneme_path(logits: torch.Tensor) -> tuple[str, ...]:
    """Collapse repeated framewise auxiliary-head predictions for inspection."""
    tokens = torch.argmax(logits, dim=-1).tolist()
    path: list[str] = []
    previous = None
    for token in tokens:
        phone = PHONEME_INVENTORY[token]
        if phone != previous and phone != "sil":
            path.append(phone)
        previous = phone
    return tuple(path)
