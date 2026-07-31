#!/usr/bin/env python3
"""Deterministically train the real CTC model on generated noisy sensor signals.

No participant, biometric, audio, upstream dataset or upstream checkpoint is used.
The resulting weights are real trained parameters for the synthetic acquisition
regime; their fit must never be presented as measured silent-speech accuracy.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import argparse
import json
import os
import random
import tempfile
import time

import numpy as np
import torch
from torch import nn

from .app.config import BLANK_ID, COMMANDS, MANIFEST_PATH, MODEL_PATH
from .app.model import SilentSpeechCTC, encode_text
from .app.preprocessing import preprocess
from .app.signal_source import NoiseProfile, inject_noise, synthesize_clean_signal

ARCHITECTURE = {"feature_count": 32, "hidden_size": 64, "layers": 2, "dropout": 0.10}
SEED = 24082020


def augmented_signal(text: str, rng: np.random.Generator) -> np.ndarray:
    clean = synthesize_clean_signal(text, rng=rng)
    profile = NoiseProfile(
        gaussian_std=float(rng.uniform(0.018, 0.085)),
        drift_amplitude=float(rng.uniform(0.015, 0.09)),
        mains_amplitude=float(rng.uniform(0.004, 0.025)),
        artifact_probability=float(rng.uniform(0.0, 0.004)),
        artifact_scale=float(rng.uniform(0.20, 0.70)),
    )
    return inject_noise(clean, profile, rng)


def build_batch(texts: list[str], rng: np.random.Generator):
    examples = [preprocess(augmented_signal(text, rng)) for text in texts]
    maximum = max(len(example.raw) for example in examples)
    if maximum % 8:
        maximum += 8 - maximum % 8
    maximum_steps = maximum // 8
    raw = np.zeros((len(examples), maximum, 8), dtype=np.float32)
    features = np.zeros((len(examples), maximum_steps, 32), dtype=np.float32)
    lengths: list[int] = []
    targets: list[int] = []
    target_lengths: list[int] = []
    for index, (text, example) in enumerate(zip(texts, examples, strict=True)):
        raw[index, : len(example.raw)] = example.raw
        features[index, : len(example.features)] = example.features
        lengths.append(len(example.raw))
        encoded = encode_text(text)
        targets.extend(encoded)
        target_lengths.append(len(encoded))
    return (
        torch.from_numpy(raw),
        torch.from_numpy(features),
        torch.tensor(lengths, dtype=torch.long),
        torch.tensor(targets, dtype=torch.long),
        torch.tensor(target_lengths, dtype=torch.long),
    )


def train(output: Path, manifest_path: Path, epochs: int = 42) -> dict:
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(max(1, min(4, os.cpu_count() or 1)))
    rng = np.random.default_rng(SEED)
    model = SilentSpeechCTC(**ARCHITECTURE)
    model.train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=1.7e-3, weight_decay=1e-4)
    criterion = nn.CTCLoss(blank=BLANK_ID, zero_infinity=True)
    started = time.perf_counter()
    final_loss = 0.0
    for epoch in range(epochs):
        order = list(COMMANDS) * 5
        random.Random(SEED + epoch).shuffle(order)
        losses: list[float] = []
        for start in range(0, len(order), 6):
            raw, features, lengths, targets, target_lengths = build_batch(order[start : start + 6], rng)
            optimizer.zero_grad(set_to_none=True)
            logits, output_lengths = model(raw, features, lengths)
            log_probs = torch.log_softmax(logits, dim=-1).transpose(0, 1)
            loss = criterion(log_probs, targets, output_lengths, target_lengths)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 3.0)
            optimizer.step()
            losses.append(float(loss.detach()))
        final_loss = sum(losses) / len(losses)
        if epoch % 6 == 0 or epoch == epochs - 1:
            print(f"epoch {epoch + 1:02d}/{epochs} synthetic_ctc_loss={final_loss:.4f}", flush=True)
    model.eval()
    output.parent.mkdir(parents=True, exist_ok=True)
    # Atomic save avoids a half-written production artifact.
    with tempfile.NamedTemporaryFile(dir=output.parent, suffix=".pt", delete=False) as temporary:
        temporary_path = Path(temporary.name)
    try:
        torch.save(model.state_dict(), temporary_path)
        temporary_path.replace(output)
    finally:
        temporary_path.unlink(missing_ok=True)
    digest = sha256(output.read_bytes()).hexdigest()
    parameter_count = sum(parameter.numel() for parameter in model.parameters())
    manifest = {
        "artifact": output.name,
        "sha256": digest,
        "format": "PyTorch state_dict",
        "model_kind": "residual temporal convolution + Transformer encoder + character CTC",
        "architecture": ARCHITECTURE,
        "parameter_count": parameter_count,
        "training": {
            "seed": SEED,
            "epochs": epochs,
            "examples_per_epoch": len(COMMANDS) * 5,
            "commands": list(COMMANDS),
            "source": "project-generated eight-channel signals with drift, Gaussian noise, mains pickup and sparse artifacts",
            "human_or_biometric_data": False,
            "final_synthetic_ctc_loss": round(final_loss, 6),
        },
        "claim_boundary": "Synthetic-regime training metadata is not measured silent-speech accuracy or evidence of hardware performance.",
        "reference": {
            "repository": "https://github.com/dgaddy/silent_speech",
            "commit": "a89357c2086609b432919b9d14ffc0be5d8983d5",
            "license": "MIT",
            "adaptation": "Residual raw-EMG front end and Transformer/CTC recognition pattern; implementation and weights are project-authored.",
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(
        f"saved {output} ({output.stat().st_size} bytes, {parameter_count} parameters) "
        f"in {time.perf_counter() - started:.1f}s"
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=MODEL_PATH)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--epochs", type=int, default=42)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if args.output.exists() and not args.force:
        print(f"model already exists: {args.output} (use --force to regenerate)")
        return 0
    train(args.output, args.manifest, args.epochs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
