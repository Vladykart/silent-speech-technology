"""Preprocessing faithful to dgaddy/silent_speech ``read_emg.py``/``data_utils.py``.

The released checkpoint consumes the 689.06 Hz raw branch. The 516.79 Hz,
112-dimensional feature branch is computed for inspection; upstream
``architecture.py`` accepts but does not use that branch in its forward pass.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import signal as scipy_signal

CHANNELS = 8
RECORDED_RATE = 1_000
MODEL_RAW_RATE = 689.06
FEATURE_RATE = 516.79
FEATURE_NAMES = tuple(
    f"ch{channel + 1}_{name}"
    for channel in range(CHANNELS)
    for name in (
        "low_frequency_mean",
        "low_frequency_rms",
        "rectified_rms",
        "zero_crossing_rate",
        "rectified_mean",
        "fft_0",
        "fft_1",
        "fft_2",
        "fft_3",
        "fft_4",
        "fft_5",
        "fft_6",
        "fft_7",
        "fft_8",
    )
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
    """NumPy equivalent of upstream ``get_emg_features`` (112 values/frame)."""
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
        # librosa.stft(center=False, n_fft=16, hop=6) uses a Hann window.
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
    """Run the released code's filtering, resampling, alignment and compression."""
    recorded = np.asarray(recorded, dtype=np.float64)
    if recorded.ndim != 2 or recorded.shape[1] != CHANNELS:
        raise ValueError(f"expected recorded (time, {CHANNELS}) sEMG, got {recorded.shape}")
    if not np.isfinite(recorded).all():
        raise ValueError("recording contains non-finite values")
    before = np.zeros((0, CHANNELS)) if before is None else np.asarray(before, dtype=np.float64)
    after = np.zeros((0, CHANNELS)) if after is None else np.asarray(after, dtype=np.float64)
    contextual = np.concatenate((before, recorded, after), axis=0)
    filtered = _apply_channels(_notch_harmonics, contextual, 60, RECORDED_RATE)
    filtered = _apply_channels(_remove_drift, filtered, RECORDED_RATE)
    filtered = filtered[len(before) : len(filtered) - len(after) if len(after) else None]

    feature_rate_signal = _apply_channels(_resample, filtered, FEATURE_RATE, RECORDED_RATE)
    features = extract_upstream_features(feature_rate_signal)
    model_rate_signal = _apply_channels(_resample, filtered, MODEL_RAW_RATE, RECORDED_RATE)
    # Upstream aligns eight raw samples to every feature frame after an 8-sample offset.
    available_frames = max(0, (len(model_rate_signal) - 8) // 8)
    frame_count = min(len(features), available_frames)
    if max_frames is not None:
        frame_count = min(frame_count, max_frames)
    features = features[:frame_count]
    model_rate_signal = model_rate_signal[8 : 8 + 8 * frame_count]
    model_raw = model_rate_signal / 20.0
    model_raw = 50.0 * np.tanh(model_raw / 50.0)
    return PreprocessedSignal(
        recorded=recorded.astype(np.float32),
        filtered=filtered.astype(np.float32),
        model_raw=model_raw.astype(np.float32),
        features=features,
        feature_names=FEATURE_NAMES,
        recorded_rate=RECORDED_RATE,
        model_rate=MODEL_RAW_RATE,
    )
