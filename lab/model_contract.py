#!/usr/bin/env python3
"""CNN/Transformer/CTC-style model contract; dry-run by default, no checkpoint."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import argparse
import importlib.util
import json


@dataclass(frozen=True)
class ModelConfig:
    input_channels: int = 8
    hidden_size: int = 64
    transformer_layers: int = 2
    attention_heads: int = 4
    vocabulary_size: int = 32
    blank_index: int = 31
    abstention_threshold: float = 0.72

    def validate(self) -> None:
        if self.input_channels <= 0 or self.hidden_size % self.attention_heads:
            raise ValueError("channels must be positive and hidden size divisible by heads")
        if not (0 <= self.blank_index < self.vocabulary_size):
            raise ValueError("blank index must be in vocabulary")
        if not (0 <= self.abstention_threshold <= 1):
            raise ValueError("abstention threshold must be in [0,1]")


def dry_run() -> dict[str, object]:
    config = ModelConfig()
    config.validate()
    batch, timesteps = 2, 96
    lengths = [96, 73]
    output_timesteps = (timesteps + 1) // 2
    mask = [[position >= (length + 1) // 2 for position in range(output_timesteps)] for length in lengths]
    return {
        "mode": "standard_library_contract",
        "config": asdict(config),
        "inputShape": [batch, timesteps, config.input_channels],
        "logitShape": [batch, output_timesteps, config.vocabulary_size],
        "paddingMaskShape": [len(mask), len(mask[0])],
        "maskedPositions": [sum(row) for row in mask],
        "split": {"policy": "held-out-session", "trainSessions": ["synthetic-s01"], "testSessions": ["synthetic-s02"]},
        "outputSchema": {"candidates": "array", "topScore": "authored_or_model_score", "abstained": "boolean", "requiresConfirmation": True},
        "checkpointLoaded": False,
        "dependencies": {name: importlib.util.find_spec(name) is not None for name in ("torch", "numpy")},
    }


def torch_smoke() -> dict[str, object]:
    try:
        import torch
        from torch import nn
    except ImportError as error:
        return {"mode": "optional_torch_smoke", "status": "dependency_missing", "detail": str(error)}
    config = ModelConfig()
    config.validate()
    torch.manual_seed(7)

    class Scaffold(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.features = nn.Conv1d(config.input_channels, config.hidden_size, 3, stride=2, padding=1)
            layer = nn.TransformerEncoderLayer(config.hidden_size, config.attention_heads, batch_first=True)
            self.sequence = nn.TransformerEncoder(layer, config.transformer_layers)
            self.output = nn.Linear(config.hidden_size, config.vocabulary_size)

        def forward(self, inputs, padding_mask):
            features = self.features(inputs.transpose(1, 2)).transpose(1, 2)
            encoded = self.sequence(features, src_key_padding_mask=padding_mask)
            return self.output(encoded)

    inputs = torch.zeros((2, 96, config.input_channels), dtype=torch.float32)
    lengths = torch.tensor([96, 73])
    output_length = 48
    reduced_lengths = torch.div(lengths + 1, 2, rounding_mode="floor")
    mask = torch.arange(output_length).unsqueeze(0) >= reduced_lengths.unsqueeze(1)
    model = Scaffold().eval()
    with torch.no_grad():
        logits = model(inputs, mask)
    assert tuple(logits.shape) == (2, 48, config.vocabulary_size)
    return {"mode": "optional_torch_smoke", "status": "passed", "inputShape": list(inputs.shape),
            "logitShape": list(logits.shape), "maskShape": list(mask.shape), "checkpointLoaded": False,
            "torch": torch.__version__}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--with-torch", action="store_true", help="exercise optional project-local PyTorch")
    args = parser.parse_args()
    print(json.dumps(torch_smoke() if args.with_torch else dry_run(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
