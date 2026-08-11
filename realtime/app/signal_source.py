"""Production acquisition path: read-only replay of one verified official recording."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterator
import json

import numpy as np

from .asset_registry import SampleRecord
from .config import CHANNELS, CHUNK_SAMPLES, SAMPLE_RATE


@dataclass(frozen=True)
class SignalFrame:
    samples: np.ndarray
    sample_rate: int
    first_sample: int
    provenance: str
    native_dtype: str


class SignalSource(ABC):
    sample_rate: int
    channels: int

    @abstractmethod
    def start(self) -> None: ...

    @abstractmethod
    def frames(self) -> Iterator[SignalFrame]: ...

    @abstractmethod
    def stop(self) -> None: ...

    def filter_context(self) -> tuple[np.ndarray | None, np.ndarray | None]:
        return None, None


class RecordedEMGReplaySource(SignalSource):
    """Preserve official native float64 values through the acquisition boundary."""

    sample_rate = SAMPLE_RATE
    channels = CHANNELS

    def __init__(self, sample: SampleRecord, chunk_samples: int = CHUNK_SAMPLES) -> None:
        self.sample = sample
        self.chunk_samples = chunk_samples
        self._running = False
        self._samples: np.ndarray | None = None
        self._before: np.ndarray | None = None
        self._after: np.ndarray | None = None
        self.metadata: dict = {}
        self.alignment_frames: int | None = None

    def _load_array(self, role: str) -> np.ndarray:
        value = np.load(self.sample.path_for(role), mmap_mode="r", allow_pickle=False)
        if value.dtype != np.dtype("float64") or value.ndim != 2 or value.shape[1] != CHANNELS:
            raise ValueError("official recording has an invalid native dtype or shape")
        if not np.isfinite(value).all():
            raise ValueError("official recording contains non-finite values")
        value.flags.writeable = False
        return value

    def start(self) -> None:
        self.metadata = json.loads(self.sample.path_for("metadata").read_text(encoding="utf-8"))
        chunks = self.metadata.get("chunks", ())
        # The second count is used only for source-compatible frame alignment.
        # No audio member is opened or prepared.
        audio_samples = sum(int(chunk[1]) for chunk in chunks)
        resampled_audio = int(np.ceil(audio_samples * 22_050 / 16_000))
        self.alignment_frames = 1 + (resampled_audio - 1_024) // 256
        if self.alignment_frames <= 0:
            raise ValueError("official metadata has no usable alignment frames")
        self._samples = self._load_array("selected")
        self._before = self._load_array("context_before")
        self._after = self._load_array("context_after")
        if len(self._samples) != int(self.sample.spec["sample_count"]):
            raise ValueError("official recording count differs from frozen registry")
        self._running = True

    def frames(self) -> Iterator[SignalFrame]:
        if not self._running or self._samples is None:
            raise RuntimeError("source must be started before replay")
        for start in range(0, len(self._samples), self.chunk_samples):
            if not self._running:
                break
            frame = np.array(self._samples[start : start + self.chunk_samples], dtype=np.float64, copy=True)
            frame.flags.writeable = False
            yield SignalFrame(
                samples=frame,
                sample_rate=self.sample_rate,
                first_sample=start,
                provenance="checksum_bound_official_recording_native_float64",
                native_dtype="float64",
            )

    def filter_context(self) -> tuple[np.ndarray | None, np.ndarray | None]:
        return self._before, self._after

    def stop(self) -> None:
        self._running = False
        self._samples = None
        self._before = None
        self._after = None
