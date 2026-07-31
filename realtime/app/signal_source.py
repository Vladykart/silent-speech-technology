"""Hardware acquisition contract and the default noisy simulated source.

Only implementations in this module know whether samples came from a simulator or a
physical device. Preprocessing and every downstream stage consume SignalFrame.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterator

import numpy as np

from .config import CHANNELS, CHUNK_SAMPLES, SAMPLE_RATE


@dataclass(frozen=True)
class NoiseProfile:
    gaussian_std: float = 0.035
    drift_amplitude: float = 0.045
    mains_amplitude: float = 0.012
    artifact_probability: float = 0.0015
    artifact_scale: float = 0.55


@dataclass(frozen=True)
class SignalFrame:
    samples: np.ndarray
    sample_rate: int
    first_sample: int
    simulated: bool


class SignalSource(ABC):
    """Driver seam matching a start/read/stop acquisition lifecycle."""

    sample_rate: int
    channels: int

    @abstractmethod
    def start(self) -> None:
        """Open/configure a device or prepare a simulated acquisition."""

    @abstractmethod
    def frames(self) -> Iterator[SignalFrame]:
        """Yield contiguous float32 frames with shape ``(time, channel)``."""

    @abstractmethod
    def stop(self) -> None:
        """Release the source promptly. This must be safe after partial capture."""


class RealHardwareSignalSource(SignalSource):
    """Integration contract for a BrainFlow/LSL/device adapter.

    A real driver must convert its native timestamps/units to contiguous float32
    channel frames and set ``simulated=False``. It intentionally raises until an
    reviewed device-specific implementation is supplied; no capture is attempted.
    """

    sample_rate = SAMPLE_RATE
    channels = CHANNELS

    def start(self) -> None:
        raise NotImplementedError("no physical sensor driver is configured")

    def frames(self) -> Iterator[SignalFrame]:
        raise NotImplementedError("no physical sensor driver is configured")

    def stop(self) -> None:
        return None


def _character_code(character: str) -> np.ndarray:
    """Deterministic articulatory-like eight-channel activation code."""
    value = ord(character)
    channel = np.arange(CHANNELS, dtype=np.float32)
    primary = np.sin((value + 3) * (channel + 1) * 0.173)
    secondary = np.cos((value + 11) * (channel + 2) * 0.097)
    code = 0.62 * primary + 0.38 * secondary
    return (code / (np.max(np.abs(code)) + 1e-6)).astype(np.float32)


def synthesize_clean_signal(text: str, *, rng: np.random.Generator | None = None) -> np.ndarray:
    """Generate a representative *synthetic* 8-channel EMG-like utterance.

    This is acquisition simulation, not participant data and not a physiological
    claim. Character-dependent bursts make the synthetic training problem a real
    sequence-learning task rather than passing text to the decoder.
    """
    rng = rng or np.random.default_rng(0)
    parts: list[np.ndarray] = [np.zeros((56, CHANNELS), dtype=np.float32)]
    gains = rng.normal(1.0, 0.045, CHANNELS).astype(np.float32)
    for character in text:
        code = _character_code(character)
        phase = np.linspace(0.0, 1.0, 24, endpoint=False, dtype=np.float32)
        envelope = np.sin(np.pi * phase) ** 1.4
        carrier = 0.72 + 0.28 * np.sin(2 * np.pi * (2.0 + (ord(character) % 4)) * phase)
        burst = envelope[:, None] * carrier[:, None] * code[None, :] * gains[None, :]
        # Cross-channel motor-unit-like component; still entirely synthetic.
        burst += 0.10 * envelope[:, None] * np.roll(code, 1)[None, :]
        parts.extend((burst.astype(np.float32), np.zeros((8, CHANNELS), dtype=np.float32)))
    parts.append(np.zeros((56, CHANNELS), dtype=np.float32))
    return np.concatenate(parts, axis=0)


def inject_noise(signal: np.ndarray, profile: NoiseProfile, rng: np.random.Generator) -> np.ndarray:
    """Inject baseline drift, Gaussian noise, mains pickup and sparse artifacts."""
    count = signal.shape[0]
    time = np.arange(count, dtype=np.float32) / SAMPLE_RATE
    drift_frequency = rng.uniform(0.18, 0.42, CHANNELS)
    drift_phase = rng.uniform(0, 2 * np.pi, CHANNELS)
    drift = profile.drift_amplitude * np.sin(
        2 * np.pi * time[:, None] * drift_frequency[None, :] + drift_phase[None, :]
    )
    mains_phase = rng.uniform(0, 2 * np.pi, CHANNELS)
    mains = profile.mains_amplitude * np.sin(2 * np.pi * 50.0 * time[:, None] + mains_phase[None, :])
    gaussian = rng.normal(0.0, profile.gaussian_std, signal.shape)
    noisy = signal.astype(np.float64) + drift + mains + gaussian
    mask = rng.random(signal.shape) < profile.artifact_probability
    impulses = rng.normal(0.0, profile.artifact_scale, signal.shape) * mask
    # A one-sample impulse and its short decay approximate cable/electrode transients.
    noisy += impulses
    for lag, decay in ((1, 0.55), (2, 0.25)):
        noisy[lag:] += impulses[:-lag] * decay
    return np.clip(noisy, -2.5, 2.5).astype(np.float32)


class SimulatedSignalSource(SignalSource):
    """Default source: generated signal plus configurable realistic noise."""

    sample_rate = SAMPLE_RATE
    channels = CHANNELS

    def __init__(
        self,
        utterance: str,
        *,
        profile: NoiseProfile | None = None,
        seed: int = 7,
        alternate: str | None = None,
        blend: float = 0.50,
        chunk_samples: int = CHUNK_SAMPLES,
    ) -> None:
        self.utterance = utterance
        self.profile = profile or NoiseProfile()
        self.seed = seed
        self.alternate = alternate
        self.blend = blend
        self.chunk_samples = chunk_samples
        self._running = False
        self._samples: np.ndarray | None = None

    def start(self) -> None:
        rng = np.random.default_rng(self.seed)
        primary = synthesize_clean_signal(self.utterance, rng=rng)
        if self.alternate:
            alternate = synthesize_clean_signal(self.alternate, rng=np.random.default_rng(self.seed + 19))
            length = max(len(primary), len(alternate))
            left = np.pad(primary, ((0, length - len(primary)), (0, 0)))
            right = np.pad(alternate, ((0, length - len(alternate)), (0, 0)))
            primary = self.blend * left + (1.0 - self.blend) * right
        self._samples = inject_noise(primary, self.profile, rng)
        self._running = True

    def frames(self) -> Iterator[SignalFrame]:
        if not self._running or self._samples is None:
            raise RuntimeError("source must be started before reading")
        for start in range(0, len(self._samples), self.chunk_samples):
            if not self._running:
                break
            yield SignalFrame(
                self._samples[start : start + self.chunk_samples].copy(),
                self.sample_rate,
                start,
                simulated=True,
            )

    def stop(self) -> None:
        self._running = False


def profile_for_quality(quality: str) -> NoiseProfile:
    if quality == "ambiguous":
        return NoiseProfile(
            gaussian_std=0.19,
            drift_amplitude=0.13,
            mains_amplitude=0.045,
            artifact_probability=0.012,
            artifact_scale=1.10,
        )
    if quality == "repair":
        return NoiseProfile(
            gaussian_std=0.022,
            drift_amplitude=0.028,
            mains_amplitude=0.008,
            artifact_probability=0.0005,
            artifact_scale=0.35,
        )
    return NoiseProfile()
