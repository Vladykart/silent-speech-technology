"""Production preprocessing and temporal feature extraction."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .config import CHANNELS, SAMPLE_RATE


@dataclass(frozen=True)
class PreprocessedSignal:
    raw: np.ndarray
    features: np.ndarray
    feature_names: tuple[str, ...]
    sample_rate: int


FEATURE_NAMES = tuple(
    f"ch{channel + 1}_{name}"
    for channel in range(CHANNELS)
    for name in ("mav", "rms", "waveform_length", "zero_crossings")
)


def high_pass(signal: np.ndarray, cutoff_hz: float = 8.0) -> np.ndarray:
    """First-order high-pass filter used unchanged for training and inference."""
    if signal.ndim != 2 or signal.shape[1] != CHANNELS:
        raise ValueError(f"expected (time, {CHANNELS}) signal, got {signal.shape}")
    if not np.isfinite(signal).all():
        raise ValueError("signal contains non-finite values")
    rc = 1.0 / (2.0 * np.pi * cutoff_hz)
    dt = 1.0 / SAMPLE_RATE
    alpha = rc / (rc + dt)
    output = np.zeros_like(signal, dtype=np.float32)
    for index in range(1, len(signal)):
        output[index] = alpha * (output[index - 1] + signal[index] - signal[index - 1])
    return output


def extract_features(filtered: np.ndarray, window: int = 16, hop: int = 8) -> np.ndarray:
    """Extract standard time-domain sEMG features at 125 frames/second."""
    remainder = len(filtered) % hop
    if remainder:
        filtered = np.pad(filtered, ((0, hop - remainder), (0, 0)))
    padded = np.pad(filtered, ((window // 4, window // 4), (0, 0)))
    frame_count = len(filtered) // hop
    frames = np.stack([padded[i * hop : i * hop + window] for i in range(frame_count)], axis=0)
    mav = np.mean(np.abs(frames), axis=1)
    rms = np.sqrt(np.mean(np.square(frames), axis=1) + 1e-7)
    waveform_length = np.mean(np.abs(np.diff(frames, axis=1)), axis=1)
    signs = np.signbit(frames)
    zero_crossings = np.mean(signs[:, 1:] != signs[:, :-1], axis=1)
    # Keep feature order channel-major to match FEATURE_NAMES.
    return np.stack((mav, rms, waveform_length, zero_crossings), axis=2).reshape(frame_count, -1).astype(np.float32)


def preprocess(signal: np.ndarray) -> PreprocessedSignal:
    filtered = high_pass(np.asarray(signal, dtype=np.float32))
    # Fixed calibration scale learned from the synthetic generator's unit convention.
    # A real driver supplies physical units and an approved calibration value here.
    normalized = np.clip(filtered / 0.55, -4.0, 4.0).astype(np.float32)
    features = extract_features(normalized)
    return PreprocessedSignal(normalized, features, FEATURE_NAMES, SAMPLE_RATE)
