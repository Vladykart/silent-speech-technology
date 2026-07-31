"""Hardware acquisition contract, real-recording replay, and optional simulator.

The default source replays CC BY 4.0 research recordings. It does not record a
person. ``SimulatedSignalSource`` remains an explicit acquisition-only fallback
for hardware integration tests and is never selected by the demo scenarios.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator
import json

import numpy as np

from .config import CHANNELS, CHUNK_SAMPLES, SAMPLE_RATE


@dataclass(frozen=True)
class SignalFrame:
    samples: np.ndarray
    sample_rate: int
    first_sample: int
    provenance: str


class SignalSource(ABC):
    sample_rate: int
    channels: int

    @abstractmethod
    def start(self) -> None:
        """Open/configure a device or recording replay."""

    @abstractmethod
    def frames(self) -> Iterator[SignalFrame]:
        """Yield contiguous float32 frames shaped time × channel."""

    @abstractmethod
    def stop(self) -> None:
        """Release promptly; safe after partial replay."""

    def filter_context(self) -> tuple[np.ndarray | None, np.ndarray | None]:
        """Optional neighboring samples used to avoid replay filter-edge effects."""
        return None, None


class RealHardwareSignalSource(SignalSource):
    """Reviewed-driver integration contract; no physical capture is configured."""

    sample_rate = SAMPLE_RATE
    channels = CHANNELS

    def start(self) -> None:
        raise NotImplementedError("no reviewed physical sensor driver is configured")

    def frames(self) -> Iterator[SignalFrame]:
        raise NotImplementedError("no reviewed physical sensor driver is configured")

    def stop(self) -> None:
        return None


class RecordedEMGReplaySource(SignalSource):
    """Replay one official dgaddy dataset sample without altering its raw values."""

    sample_rate = SAMPLE_RATE
    channels = CHANNELS

    def __init__(self, sample_directory: Path, index: int, chunk_samples: int = CHUNK_SAMPLES) -> None:
        self.sample_directory = sample_directory
        self.index = index
        self.chunk_samples = chunk_samples
        self._running = False
        self._samples: np.ndarray | None = None
        self._before: np.ndarray | None = None
        self._after: np.ndarray | None = None
        self.metadata: dict = {}
        self.alignment_frames: int | None = None

    def _load_array(self, index: int) -> np.ndarray:
        path = self.sample_directory / f"{index}_emg.npy"
        value = np.load(path, allow_pickle=False)
        if value.ndim != 2 or value.shape[1] != CHANNELS or not np.isfinite(value).all():
            raise ValueError(f"invalid official recording array: {path} shape={value.shape}")
        return np.asarray(value, dtype=np.float32)

    def start(self) -> None:
        info_path = self.sample_directory / f"{self.index}_info.json"
        self.metadata = json.loads(info_path.read_text())
        if int(self.metadata.get("sentence_index", -1)) < 0:
            raise ValueError("reference/silence records cannot be replayed as utterances")
        # Official chunk metadata includes paired 16 kHz audio sample counts used
        # upstream only to align raw EMG and mel-frame lengths. No audio is read.
        audio_samples = sum(int(chunk[1]) for chunk in self.metadata.get("chunks", ()))
        resampled_audio = int(np.ceil(audio_samples * 22_050 / 16_000))
        self.alignment_frames = 1 + (resampled_audio - 1_024) // 256
        if self.alignment_frames <= 0:
            raise ValueError("record metadata has no usable alignment frames")
        self._samples = self._load_array(self.index)
        self._before = self._load_array(self.index - 1)
        self._after = self._load_array(self.index + 1)
        self._running = True

    def frames(self) -> Iterator[SignalFrame]:
        if not self._running or self._samples is None:
            raise RuntimeError("source must be started before replay")
        for start in range(0, len(self._samples), self.chunk_samples):
            if not self._running:
                break
            yield SignalFrame(
                self._samples[start : start + self.chunk_samples].copy(),
                self.sample_rate,
                start,
                provenance="recorded_research_data_replay",
            )

    def filter_context(self) -> tuple[np.ndarray | None, np.ndarray | None]:
        return self._before, self._after

    def stop(self) -> None:
        self._running = False


class SimulatedSignalSource(SignalSource):
    """Explicit non-default acquisition fallback; never used for model claims."""

    sample_rate = SAMPLE_RATE
    channels = CHANNELS

    def __init__(self, duration_samples: int = 1_600, seed: int = 7) -> None:
        self.duration_samples = duration_samples
        self.seed = seed
        self._samples: np.ndarray | None = None
        self._running = False

    def start(self) -> None:
        generator = np.random.default_rng(self.seed)
        time = np.arange(self.duration_samples, dtype=np.float32) / self.sample_rate
        carrier = np.stack(
            [0.15 * np.sin(2 * np.pi * (45 + channel * 7) * time) for channel in range(CHANNELS)],
            axis=1,
        )
        drift = 0.04 * np.sin(2 * np.pi * 0.3 * time)[:, None]
        self._samples = (carrier + drift + generator.normal(0, 0.03, carrier.shape)).astype(np.float32)
        self._running = True

    def frames(self) -> Iterator[SignalFrame]:
        if not self._running or self._samples is None:
            raise RuntimeError("source must be started before reading")
        for start in range(0, len(self._samples), CHUNK_SAMPLES):
            if not self._running:
                break
            yield SignalFrame(
                self._samples[start : start + CHUNK_SAMPLES].copy(),
                self.sample_rate,
                start,
                provenance="explicit_simulator_fallback_not_default",
            )

    def stop(self) -> None:
        self._running = False
