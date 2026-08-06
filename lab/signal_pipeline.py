#!/usr/bin/env python3
"""Synthetic-only sEMG preprocessing example with optional NumPy/SciPy execution."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import argparse
import json
import math
from typing import Sequence


@dataclass(frozen=True)
class FilterConfig:
    sample_rate_hz: float = 1000.0
    bandpass_low_hz: float = 20.0
    bandpass_high_hz: float = 450.0
    notch_hz: float = 50.0
    envelope_lowpass_hz: float = 8.0
    order: int = 4

    def validate(self) -> None:
        nyquist = self.sample_rate_hz / 2
        if not (0 < self.bandpass_low_hz < self.bandpass_high_hz < nyquist):
            raise ValueError("bandpass must be positive, ordered, and below Nyquist")
        if not (0 < self.notch_hz < nyquist):
            raise ValueError("notch must be below Nyquist")
        if not (0 < self.envelope_lowpass_hz < nyquist):
            raise ValueError("envelope cutoff must be below Nyquist")
        if self.order < 1:
            raise ValueError("filter order must be positive")


def synthetic_semg(sample_count: int = 256, sample_rate_hz: float = 1000.0) -> list[float]:
    """Original deterministic fixture; not biological or calibrated."""
    return [
        0.13 * math.sin(2 * math.pi * 71 * index / sample_rate_hz)
        + 0.05 * math.sin(2 * math.pi * 50 * index / sample_rate_hz)
        + (((index * 17) % 23) - 11) / 500
        for index in range(sample_count)
    ]


def rectified_moving_envelope(values: Sequence[float], window: int = 16) -> list[float]:
    if window <= 0:
        raise ValueError("window must be positive")
    rectified = [abs(float(value)) for value in values]
    return [sum(rectified[max(0, i - window + 1):i + 1]) / min(i + 1, window)
            for i in range(len(rectified))]


def dry_run(config: FilterConfig) -> dict[str, object]:
    config.validate()
    signal = synthetic_semg()
    envelope = rectified_moving_envelope(signal)
    return {
        "mode": "synthetic_dry_run",
        "config": asdict(config),
        "input": {"source": "authored_synthetic", "channels": 1, "samples": len(signal)},
        "plannedStages": ["bandpass", "notch", "rectify", "lowpass_envelope"],
        "standardLibraryEnvelope": {
            "first": round(envelope[0], 8),
            "last": round(envelope[-1], 8),
            "samples": len(envelope),
        },
        "scientificFilterExecuted": False,
        "note": "Defaults are a planning example, not a universal facial-sEMG protocol.",
    }


def scipy_smoke(config: FilterConfig) -> dict[str, object]:
    config.validate()
    try:
        import numpy as np
        from scipy import signal
    except ImportError as error:
        return {"mode": "optional_scipy_smoke", "status": "dependency_missing", "detail": str(error)}
    values = np.asarray(synthetic_semg(), dtype=np.float64)
    bandpass = signal.butter(config.order, [config.bandpass_low_hz, config.bandpass_high_hz],
                             btype="bandpass", fs=config.sample_rate_hz, output="sos")
    filtered = signal.sosfiltfilt(bandpass, values)
    notch_b, notch_a = signal.iirnotch(config.notch_hz, 30, fs=config.sample_rate_hz)
    filtered = signal.filtfilt(notch_b, notch_a, filtered)
    rectified = np.abs(filtered)
    envelope_sos = signal.butter(config.order, config.envelope_lowpass_hz, btype="lowpass",
                                  fs=config.sample_rate_hz, output="sos")
    envelope = signal.sosfiltfilt(envelope_sos, rectified)
    return {
        "mode": "optional_scipy_smoke", "status": "passed", "source": "authored_synthetic",
        "inputShape": list(values.shape), "outputShape": list(envelope.shape),
        "provenance": {"config": asdict(config), "numpy": np.__version__},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--with-scipy", action="store_true", help="run optional local NumPy/SciPy smoke path")
    args = parser.parse_args()
    config = FilterConfig()
    report = scipy_smoke(config) if args.with_scipy else dry_run(config)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
