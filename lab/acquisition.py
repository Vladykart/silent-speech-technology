#!/usr/bin/env python3
"""Default-safe deterministic acquisition contract. No device, audio, listener, or network."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import argparse
import json
from typing import Iterator


@dataclass(frozen=True)
class ChannelMetadata:
    index: int
    label: str
    unit: str = "synthetic_normalized"


@dataclass(frozen=True)
class Sample:
    session_id: str
    sequence: int
    timestamp_ns: int
    values: tuple[float, ...]


class MockBoard:
    """BrainFlow-shaped lifecycle concept using deterministic local constants only."""

    def __init__(self, session_id: str = "synthetic-session-001", sample_rate_hz: int = 1000,
                 channel_count: int = 8, sample_count: int = 32,
                 dropped_sequences: tuple[int, ...] = (7, 19)) -> None:
        if not session_id.startswith("synthetic-"):
            raise ValueError("mock session IDs must start with synthetic-")
        if sample_rate_hz <= 0 or channel_count <= 0 or sample_count <= 0:
            raise ValueError("sample rate, channels, and sample count must be positive")
        self.session_id = session_id
        self.sample_rate_hz = sample_rate_hz
        self.channel_count = channel_count
        self.sample_count = sample_count
        self.dropped_sequences = frozenset(dropped_sequences)
        self.channels = tuple(ChannelMetadata(i, f"S{i + 1}") for i in range(channel_count))
        self._running = False
        self._cursor = 0
        self.dropped_sample_count = 0
        self.shutdown_clean = False
        self._start_ns = 1_700_000_000_000_000_000

    def start(self) -> None:
        if self._running:
            raise RuntimeError("mock board already running")
        self._running = True
        self.shutdown_clean = False

    def samples(self) -> Iterator[Sample]:
        if not self._running:
            raise RuntimeError("mock board must be started before reading")
        period_ns = 1_000_000_000 // self.sample_rate_hz
        while self._cursor < self.sample_count:
            sequence = self._cursor
            self._cursor += 1
            if sequence in self.dropped_sequences:
                self.dropped_sample_count += 1
                continue
            values = tuple(round((((sequence + channel * 3) % 17) - 8) / 10, 3)
                           for channel in range(self.channel_count))
            yield Sample(self.session_id, sequence, self._start_ns + sequence * period_ns, values)

    def shutdown(self) -> None:
        self._running = False
        self.shutdown_clean = True

    def __enter__(self) -> "MockBoard":
        self.start()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.shutdown()


def smoke_summary() -> dict[str, object]:
    board = MockBoard()
    with board:
        samples = list(board.samples())
    return {
        "mode": "deterministic_mock_only",
        "sessionId": board.session_id,
        "sampleRateHz": board.sample_rate_hz,
        "channels": [asdict(channel) for channel in board.channels],
        "firstTimestampNs": samples[0].timestamp_ns,
        "lastTimestampNs": samples[-1].timestamp_ns,
        "samplesProduced": len(samples),
        "droppedSamples": board.dropped_sample_count,
        "shutdownClean": board.shutdown_clean,
        "realDeviceOpened": False,
        "audioCaptured": False,
        "listenerOpened": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("mock",), default="mock",
                        help="Only deterministic mock mode exists in this foundation")
    parser.parse_args()
    print(json.dumps(smoke_summary(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
