"""Acquisition-independent preprocessing, model inference, decoding and policy."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import json
import time

import numpy as np
import torch

from .config import MANIFEST_PATH, MODEL_PATH
from .decoder import DecodeResult, decode_logits
from .model import SilentSpeechCTC
from .preprocessing import PreprocessedSignal, preprocess


@dataclass(frozen=True)
class InferenceResult:
    preprocessed: PreprocessedSignal
    decoded: DecodeResult
    latency_ms: float
    output_steps: int


class InferencePipeline:
    """Owns a verified trained model and runs the genuine downstream path."""

    def __init__(
        self,
        model_path: Path = MODEL_PATH,
        manifest_path: Path = MANIFEST_PATH,
        device: str = "cpu",
    ) -> None:
        if not model_path.is_file() or not manifest_path.is_file():
            raise FileNotFoundError(
                f"trained model is missing ({model_path}); run `python -m realtime.train`"
            )
        self.model_path = model_path
        self.manifest = json.loads(manifest_path.read_text())
        digest = sha256(model_path.read_bytes()).hexdigest()
        if digest != self.manifest["sha256"]:
            raise RuntimeError("model checksum does not match its training manifest")
        self.device = torch.device(device)
        self.model = SilentSpeechCTC(**self.manifest["architecture"])
        state = torch.load(model_path, map_location=self.device, weights_only=True)
        self.model.load_state_dict(state)
        self.model.to(self.device).eval()

    def infer(self, signal: np.ndarray) -> InferenceResult:
        processed = preprocess(signal)
        raw = torch.from_numpy(processed.raw).unsqueeze(0).to(self.device)
        features = torch.from_numpy(processed.features).unsqueeze(0).to(self.device)
        lengths = torch.tensor([len(processed.raw)], dtype=torch.long, device=self.device)
        started = time.perf_counter()
        with torch.inference_mode():
            logits, output_lengths = self.model(raw, features, lengths)
            decoded = decode_logits(logits[0].cpu(), int(output_lengths[0].item()))
        elapsed = (time.perf_counter() - started) * 1_000.0
        return InferenceResult(processed, decoded, round(elapsed, 3), int(output_lengths[0].item()))
