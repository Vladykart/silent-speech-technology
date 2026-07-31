"""Gaddy-inspired residual-convolution + Transformer CTC recognizer."""
from __future__ import annotations

import math

import torch
from torch import nn
import torch.nn.functional as functional

from .config import ALPHABET, BLANK_ID, CHANNELS


class ResidualTemporalBlock(nn.Module):
    """Temporal residual block following dgaddy/silent_speech architecture.py."""

    def __init__(self, inputs: int, outputs: int, stride: int = 1) -> None:
        super().__init__()
        self.conv1 = nn.Conv1d(inputs, outputs, 3, padding=1, stride=stride)
        self.norm1 = nn.BatchNorm1d(outputs)
        self.conv2 = nn.Conv1d(outputs, outputs, 3, padding=1)
        self.norm2 = nn.BatchNorm1d(outputs)
        if stride != 1 or inputs != outputs:
            self.residual = nn.Sequential(
                nn.Conv1d(inputs, outputs, 1, stride=stride), nn.BatchNorm1d(outputs)
            )
        else:
            self.residual = nn.Identity()

    def forward(self, value: torch.Tensor) -> torch.Tensor:
        residual = self.residual(value)
        value = functional.gelu(self.norm1(self.conv1(value)))
        value = self.norm2(self.conv2(value))
        return functional.gelu(value + residual)


class SinusoidalPosition(nn.Module):
    def __init__(self, size: int, maximum: int = 512) -> None:
        super().__init__()
        position = torch.arange(maximum, dtype=torch.float32).unsqueeze(1)
        divisor = torch.exp(torch.arange(0, size, 2, dtype=torch.float32) * (-math.log(10_000.0) / size))
        encoding = torch.zeros(maximum, size)
        encoding[:, 0::2] = torch.sin(position * divisor)
        encoding[:, 1::2] = torch.cos(position * divisor)
        self.register_buffer("encoding", encoding, persistent=False)

    def forward(self, value: torch.Tensor) -> torch.Tensor:
        return value + self.encoding[: value.shape[1]].unsqueeze(0)


class SilentSpeechCTC(nn.Module):
    """Eight-channel signal-to-character sequence model with a CTC output head.

    The three stride-2 residual blocks mirror the raw-EMG front end in Gaddy's
    architecture. Unlike that reference implementation's recognition path, this
    model also fuses explicit sEMG features before a Transformer encoder.
    """

    def __init__(
        self,
        feature_count: int = CHANNELS * 4,
        hidden_size: int = 64,
        layers: int = 2,
        dropout: float = 0.10,
    ) -> None:
        super().__init__()
        self.hidden_size = hidden_size
        self.raw_encoder = nn.Sequential(
            ResidualTemporalBlock(CHANNELS, hidden_size, 2),
            ResidualTemporalBlock(hidden_size, hidden_size, 2),
            ResidualTemporalBlock(hidden_size, hidden_size, 2),
        )
        self.feature_projection = nn.Sequential(
            nn.Linear(feature_count, hidden_size), nn.LayerNorm(hidden_size), nn.GELU()
        )
        self.fusion = nn.Sequential(nn.Linear(hidden_size * 2, hidden_size), nn.LayerNorm(hidden_size))
        self.position = SinusoidalPosition(hidden_size)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_size,
            nhead=4,
            dim_feedforward=hidden_size * 4,
            dropout=dropout,
            activation="gelu",
            batch_first=True,
            norm_first=True,
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, layers, enable_nested_tensor=False)
        self.output = nn.Linear(hidden_size, len(ALPHABET) + 1)

    @staticmethod
    def output_lengths(raw_lengths: torch.Tensor) -> torch.Tensor:
        lengths = raw_lengths.clone()
        for _ in range(3):
            lengths = torch.div(lengths + 1, 2, rounding_mode="floor")
        return lengths

    def forward(
        self,
        raw: torch.Tensor,
        features: torch.Tensor,
        raw_lengths: torch.Tensor | None = None,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        # raw: batch, time, electrode; features: batch, time/8, feature
        encoded_raw = self.raw_encoder(raw.transpose(1, 2)).transpose(1, 2)
        encoded_features = self.feature_projection(features)
        steps = min(encoded_raw.shape[1], encoded_features.shape[1])
        fused = self.fusion(torch.cat((encoded_raw[:, :steps], encoded_features[:, :steps]), dim=-1))
        fused = self.position(fused)
        if raw_lengths is None:
            lengths = torch.full((raw.shape[0],), steps, dtype=torch.long, device=raw.device)
        else:
            lengths = torch.clamp(self.output_lengths(raw_lengths), max=steps)
        positions = torch.arange(steps, device=raw.device).unsqueeze(0)
        padding_mask = positions >= lengths.unsqueeze(1)
        encoded = self.transformer(fused, src_key_padding_mask=padding_mask)
        return self.output(encoded), lengths


def encode_text(text: str) -> list[int]:
    unknown = set(text) - set(ALPHABET)
    if unknown:
        raise ValueError(f"characters outside model alphabet: {sorted(unknown)!r}")
    return [ALPHABET.index(character) + 1 for character in text]


def greedy_decode(logits: torch.Tensor, length: int) -> str:
    best = torch.argmax(logits[:length], dim=-1).tolist()
    characters: list[str] = []
    previous = BLANK_ID
    for token in best:
        if token != BLANK_ID and token != previous:
            characters.append(ALPHABET[token - 1])
        previous = token
    return "".join(characters).strip()
