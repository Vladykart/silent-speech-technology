"""Official recorded-sEMG preprocessing, released-model inference and decoding."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import json
import os
import time

import numpy as np
import torch

from .config import ASSET_MANIFEST_PATH, MODEL_PATH
from .decoder import DecodeResult, decode_phonemes
from .model import ReleasedGaddyTransductionModel
from .preprocessing import PreprocessedSignal, preprocess


@dataclass(frozen=True)
class InferenceResult:
    preprocessed: PreprocessedSignal
    decoded: DecodeResult
    mel_features: np.ndarray
    latency_ms: float
    output_steps: int


class InferencePipeline:
    """Loads checksum-verified CC BY 4.0 weights and executes their real path."""

    def __init__(self, model_path: Path = MODEL_PATH, device: str = "cpu") -> None:
        self.asset_manifest = json.loads(ASSET_MANIFEST_PATH.read_text())
        checkpoint = self.asset_manifest["model"]["checkpoint"]
        if not model_path.is_file():
            raise FileNotFoundError(
                f"official released checkpoint is missing ({model_path}); run `python realtime/fetch_assets.py`"
            )
        if model_path.stat().st_size != checkpoint["bytes"]:
            raise RuntimeError("released checkpoint byte size does not match assets-manifest.json")
        digest = sha256(model_path.read_bytes()).hexdigest()
        if digest != checkpoint["sha256"]:
            raise RuntimeError("released checkpoint SHA-256 does not match official asset manifest")
        self.model_path = model_path
        self.device = torch.device(device)
        torch.set_num_threads(max(1, min(int(os.getenv("TORCH_THREADS", "4")), os.cpu_count() or 1)))
        self.model = ReleasedGaddyTransductionModel()
        state = torch.load(model_path, map_location=self.device, weights_only=True)
        self.model.load_state_dict(state, strict=True)
        self.model.to(self.device).eval()
        self.parameter_count = sum(parameter.numel() for parameter in self.model.parameters())
        if self.parameter_count != checkpoint["trainable_parameters"]:
            raise RuntimeError("loaded model parameter count does not match manifest")

    def infer(
        self,
        recording: np.ndarray,
        before: np.ndarray | None = None,
        after: np.ndarray | None = None,
        max_frames: int | None = None,
    ) -> InferenceResult:
        processed = preprocess(recording, before, after, max_frames)
        raw = torch.from_numpy(processed.model_raw).unsqueeze(0).to(self.device)
        started = time.perf_counter()
        with torch.inference_mode():
            mel_features, phoneme_logits = self.model(raw)
            decoded = decode_phonemes(phoneme_logits[0].cpu())
        elapsed = (time.perf_counter() - started) * 1_000.0
        return InferenceResult(
            processed,
            decoded,
            mel_features[0].cpu().numpy(),
            round(elapsed, 3),
            phoneme_logits.shape[1],
        )
