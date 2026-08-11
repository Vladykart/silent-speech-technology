"""Source-faithful preprocessing adapted from dgaddy/silent_speech.

The released checkpoint consumes only the 689.06 Hz raw branch. The 516.79 Hz,
112-value feature branch is real and inspectable, but is not model input.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy import signal as scipy_signal

CHANNELS = 8
RECORDED_RATE = 1_000
MODEL_RAW_RATE = 689.06
FEATURE_RATE = 516.79
FEATURE_COMPONENTS = (
    "low_frequency_mean", "low_frequency_rms", "rectified_rms", "zero_crossing_rate",
    "rectified_mean", "fft_0", "fft_1", "fft_2", "fft_3", "fft_4", "fft_5",
    "fft_6", "fft_7", "fft_8",
)
FEATURE_NAMES = tuple(
    f"ch{channel + 1}_{name}"
    for channel in range(CHANNELS)
    for name in FEATURE_COMPONENTS
)


@dataclass(frozen=True)
class PreprocessedSignal:
    recorded: np.ndarray
    filtered: np.ndarray
    model_raw: np.ndarray
    features: np.ndarray
    feature_names: tuple[str, ...]
    recorded_rate: int
    model_rate: float
    feature_rate: float
    provenance: tuple[dict[str, Any], ...]


def _apply_channels(function, values: np.ndarray, *args) -> np.ndarray:
    return np.stack([function(values[:, channel], *args) for channel in range(values.shape[1])], axis=1)


def _notch_harmonics(values: np.ndarray, frequency: float, sample_rate: int) -> np.ndarray:
    output = values
    for harmonic in range(1, 8):
        numerator, denominator = scipy_signal.iirnotch(frequency * harmonic, 30, sample_rate)
        output = scipy_signal.filtfilt(numerator, denominator, output)
    return output


def _remove_drift(values: np.ndarray, sample_rate: int) -> np.ndarray:
    numerator, denominator = scipy_signal.butter(3, 2, "highpass", fs=sample_rate)
    return scipy_signal.filtfilt(numerator, denominator, values)


def _resample(values: np.ndarray, new_rate: float, old_rate: float) -> np.ndarray:
    times = np.arange(len(values)) / old_rate
    sample_times = np.arange(0, times[-1], 1 / new_rate)
    return np.interp(sample_times, times, values)


def _frame(values: np.ndarray, length: int = 16, hop: int = 6) -> np.ndarray:
    if len(values) < length:
        raise ValueError("recording is too short for upstream feature window")
    count = 1 + (len(values) - length) // hop
    return np.stack([values[index * hop : index * hop + length] for index in range(count)])


def extract_upstream_features(emg: np.ndarray) -> np.ndarray:
    """NumPy equivalent of upstream get_emg_features (112 values/frame)."""
    centered = emg - emg.mean(axis=0, keepdims=True)
    channels: list[np.ndarray] = []
    averaging_filter = np.ones(9) / 9.0
    for channel in range(centered.shape[1]):
        values = centered[:, channel]
        average = np.convolve(np.convolve(values, averaging_filter, mode="same"), averaging_filter, mode="same")
        high = values - average
        rectified = np.abs(high)
        average_frames = _frame(average)
        high_frames = _frame(high)
        rectified_frames = _frame(rectified)
        time_features = np.stack(
            (
                average_frames.mean(axis=1),
                np.sqrt(np.mean(np.square(average_frames), axis=1)),
                np.sqrt(np.mean(np.square(rectified_frames), axis=1)),
                np.mean(np.signbit(high_frames[:, 1:]) != np.signbit(high_frames[:, :-1]), axis=1),
                rectified_frames.mean(axis=1),
            ),
            axis=1,
        )
        hann = scipy_signal.get_window("hann", 16, fftbins=True)
        spectrum = np.abs(np.fft.rfft(_frame(np.ascontiguousarray(values)) * hann, axis=1))
        channels.extend((time_features, spectrum))
    return np.concatenate(channels, axis=1).astype(np.float32)


def preprocess(
    recorded: np.ndarray,
    before: np.ndarray | None = None,
    after: np.ndarray | None = None,
    max_frames: int | None = None,
) -> PreprocessedSignal:
    """Filter native source arrays and explicitly create the float32 model boundary."""
    native = np.asarray(recorded)
    if native.dtype != np.dtype("float64"):
        raise ValueError(f"expected native float64 source, got {native.dtype}")
    if native.ndim != 2 or native.shape[1] != CHANNELS:
        raise ValueError(f"expected recorded (time, {CHANNELS}) sEMG, got {native.shape}")
    if not np.isfinite(native).all():
        raise ValueError("recording contains non-finite values")
    recorded_runtime = np.array(native, dtype=np.float64, copy=True)
    before_runtime = np.zeros((0, CHANNELS), dtype=np.float64) if before is None else np.asarray(before, dtype=np.float64)
    after_runtime = np.zeros((0, CHANNELS), dtype=np.float64) if after is None else np.asarray(after, dtype=np.float64)
    contextual = np.concatenate((before_runtime, recorded_runtime, after_runtime), axis=0)
    filtered = _apply_channels(_notch_harmonics, contextual, 60, RECORDED_RATE)
    filtered = _apply_channels(_remove_drift, filtered, RECORDED_RATE)
    filtered = filtered[len(before_runtime) : len(filtered) - len(after_runtime) if len(after_runtime) else None]

    feature_rate_signal = _apply_channels(_resample, filtered, FEATURE_RATE, RECORDED_RATE)
    features = extract_upstream_features(feature_rate_signal)
    model_rate_signal = _apply_channels(_resample, filtered, MODEL_RAW_RATE, RECORDED_RATE)
    available_frames = max(0, (len(model_rate_signal) - 8) // 8)
    frame_count = min(len(features), available_frames)
    if max_frames is not None:
        frame_count = min(frame_count, max_frames)
    if frame_count <= 0:
        raise ValueError("preprocessing produced no aligned model frames")
    features = features[:frame_count]
    model_rate_signal = model_rate_signal[8 : 8 + 8 * frame_count]
    model_raw_float64 = 50.0 * np.tanh((model_rate_signal / 20.0) / 50.0)
    model_raw = np.asarray(model_raw_float64, dtype=np.float32)
    if not all(np.isfinite(value).all() for value in (filtered, features, model_raw)):
        raise ValueError("preprocessing produced non-finite values")
    provenance = (
        {
            "operation": "native source load and runtime processing boundary",
            "input_rate_hz": 1000,
            "output_rate_hz": 1000,
            "input_shape": list(recorded_runtime.shape),
            "output_shape": list(recorded_runtime.shape),
            "input_dtype": "float64",
            "output_dtype": "float64",
            "lineage": "official checksum-bound NumPy member",
            "model_input": False,
        },
        {
            "operation": "60 Hz notch plus harmonics 2–7; 2 Hz third-order high-pass with immediate context",
            "input_rate_hz": 1000,
            "output_rate_hz": 1000,
            "input_shape": list(recorded_runtime.shape),
            "output_shape": list(filtered.shape),
            "input_dtype": "float64",
            "output_dtype": "float64",
            "lineage": "dgaddy/silent_speech read_emg.py adaptation",
            "model_input": False,
        },
        {
            "operation": "516.79 Hz resample; 16-sample windows / 6-sample hop; 112-value feature inspection",
            "input_rate_hz": 1000,
            "output_rate_hz": FEATURE_RATE,
            "input_shape": list(filtered.shape),
            "output_shape": list(features.shape),
            "input_dtype": "float64",
            "output_dtype": "float32",
            "lineage": "dgaddy/silent_speech data_utils.py adaptation",
            "model_input": False,
            "note": "inspectable / not consumed by released forward path",
        },
        {
            "operation": "689.06 Hz resample; 8-sample alignment/offset; divide by 20; 50*tanh(x/50); runtime float32 conversion",
            "input_rate_hz": 1000,
            "output_rate_hz": MODEL_RAW_RATE,
            "input_shape": list(filtered.shape),
            "output_shape": list(model_raw.shape),
            "input_dtype": "float64",
            "output_dtype": "float32",
            "lineage": "dgaddy/silent_speech architecture.py/read_emg.py adaptation",
            "model_input": True,
        },
    )
    recorded_runtime.flags.writeable = False
    filtered.flags.writeable = False
    return PreprocessedSignal(
        recorded=recorded_runtime,
        filtered=filtered,
        model_raw=model_raw,
        features=features,
        feature_names=FEATURE_NAMES,
        recorded_rate=RECORDED_RATE,
        model_rate=MODEL_RAW_RATE,
        feature_rate=FEATURE_RATE,
        provenance=provenance,
    )
