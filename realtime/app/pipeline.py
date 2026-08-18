"""Strict released-model execution with separately scoped model and decoder timing."""
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
    phoneme_logits: np.ndarray
    model_forward_ms: float
    project_decoder_ms: float
    output_steps: int


class InferencePipeline:
    """Verify, strict-load, and execute the one authorized released checkpoint."""

    def __init__(self, model_path: Path = MODEL_PATH, device: str = "cpu") -> None:
        self.asset_manifest = json.loads(ASSET_MANIFEST_PATH.read_text(encoding="utf-8"))
        checkpoint = self.asset_manifest["model"]["checkpoint"]
        if not model_path.is_file():
            raise FileNotFoundError("official released checkpoint is missing; prepare approved assets before startup")
        if model_path.stat().st_size != checkpoint["bytes"]:
            raise RuntimeError("released checkpoint byte size does not match the private asset manifest")
        value = sha256()
        with model_path.open("rb") as handle:
            while chunk := handle.read(4 * 1024 * 1024):
                value.update(chunk)
        if value.hexdigest() != checkpoint["sha256"]:
            raise RuntimeError("released checkpoint digest does not match the private asset manifest")
        self.model_path = model_path
        self.device = torch.device(device)
        torch.set_num_threads(max(1, min(int(os.getenv("TORCH_THREADS", "4")), os.cpu_count() or 1)))
        self.model = ReleasedGaddyTransductionModel()
        state = torch.load(model_path, map_location=self.device, weights_only=True)
        self.model.load_state_dict(state, strict=True)
        self.model.to(self.device).eval()
        self.parameter_count = sum(parameter.numel() for parameter in self.model.parameters())
        if self.parameter_count != checkpoint["trainable_parameters"]:
            raise RuntimeError("loaded model parameter count does not match the private manifest")

    def infer(
        self,
        recording: np.ndarray,
        before: np.ndarray | None = None,
        after: np.ndarray | None = None,
        max_frames: int | None = None,
    ) -> InferenceResult:
        processed = preprocess(recording, before, after, max_frames)
        if processed.model_raw.dtype != np.float32 or processed.model_raw.shape[1] != 8:
            raise RuntimeError("documented model-input conversion boundary failed")
        raw = torch.from_numpy(processed.model_raw).unsqueeze(0).to(self.device)
        model_started = time.perf_counter()
        with torch.inference_mode():
            mel_tensor, logits_tensor = self.model(raw)
        model_finished = time.perf_counter()
        logits_cpu = logits_tensor[0].detach().cpu()
        decoder_started = time.perf_counter()
        decoded = decode_phonemes(logits_cpu)
        decoder_finished = time.perf_counter()
        mel = mel_tensor[0].detach().cpu().numpy()
        logits = logits_cpu.numpy()
        if mel.ndim != 2 or mel.shape[1] != 80 or logits.ndim != 2 or logits.shape[1] != 48:
            raise RuntimeError("released output-head shape differs from the execution contract")
        if len(mel) != len(logits) or len(mel) != len(processed.features):
            raise RuntimeError("released output and preprocessing frames are not aligned")
        if not np.isfinite(mel).all() or not np.isfinite(logits).all():
            raise RuntimeError("released model produced non-finite output")
        if float(np.std(mel)) <= 1e-8 or float(np.std(logits)) <= 1e-8:
            raise RuntimeError("released model produced constant output")
        return InferenceResult(
            preprocessed=processed,
            decoded=decoded,
            mel_features=mel,
            phoneme_logits=logits,
            model_forward_ms=round((model_finished - model_started) * 1_000.0, 3),
            project_decoder_ms=round((decoder_finished - decoder_started) * 1_000.0, 3),
            output_steps=logits.shape[0],
        )
