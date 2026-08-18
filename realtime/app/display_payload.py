"""The sole deterministic builder for bounded transformed browser evidence."""
from __future__ import annotations

from hashlib import sha256
import json
import math

import numpy as np
import torch

from .model import PHONEME_INVENTORY, collapsed_phoneme_path


class DisplayPayloadBuilder:
    SOURCE_MAX_BINS = 256
    COMPARISON_MAX_BINS = 128
    HEATMAP_MAX_TIME_BINS = 64
    MIN_SOURCE_SAMPLES_PER_BIN = 16

    @staticmethod
    def _signed_quantize(values: np.ndarray, axis: int = 0) -> np.ndarray:
        finite = np.asarray(values, dtype=np.float64)
        center = np.median(finite, axis=axis, keepdims=True)
        centered = finite - center
        scale = np.percentile(np.abs(centered), 99, axis=axis, keepdims=True)
        scale = np.where(scale > 1e-12, scale, 1.0)
        return np.rint(np.clip(centered / scale, -1, 1) * 127).astype(np.int8)

    @staticmethod
    def _fingerprint(value: object) -> str:
        encoded = json.dumps(value, separators=(",", ":"), sort_keys=True).encode()
        return sha256(encoded).hexdigest()[:12]

    @classmethod
    def _envelope(cls, values: np.ndarray, max_bins: int, minimum_bin: int) -> tuple[list[list[list[int]]], int]:
        array = np.asarray(values)
        if array.ndim != 2 or array.shape[1] != 8 or not np.isfinite(array).all():
            raise ValueError("display envelope source must be finite [time,8]")
        bin_size = max(minimum_bin, math.ceil(len(array) / max_bins))
        quantized = cls._signed_quantize(array, axis=0)
        result: list[list[list[int]]] = [[] for _ in range(8)]
        for start in range(0, len(array), bin_size):
            chunk = quantized[start : start + bin_size]
            for channel in range(8):
                result[channel].append([int(chunk[:, channel].min()), int(chunk[:, channel].max())])
        if not result[0] or len(result[0]) > max_bins:
            raise RuntimeError("display envelope cardinality exceeded")
        return result, bin_size

    @classmethod
    def source_envelope(cls, recorded: np.ndarray, source_rate: int = 1_000) -> dict:
        channels, bin_size = cls._envelope(recorded, cls.SOURCE_MAX_BINS, cls.MIN_SOURCE_SAMPLES_PER_BIN)
        payload = {
            "kind": "source_envelope",
            "channels": channels,
            "channel_count": 8,
            "source_rate": source_rate,
            "source_samples_per_bin": bin_size,
            "display_bins": len(channels[0]),
            "display_transform": "chronological min/max; per-channel median centering; robust clipping/scaling; signed 8-bit quantization",
            "not_untouched_raw": True,
            "label": "Transformed display envelope derived from the recorded source; 16:1 or greater decimation; per-channel centered/scaled; not untouched raw data.",
        }
        payload["display_fingerprint"] = cls._fingerprint(channels)
        return payload

    @classmethod
    def source_filtered_comparison(cls, recorded: np.ndarray, filtered: np.ndarray, source_rate: int = 1_000) -> dict:
        source, source_bin = cls._envelope(recorded, cls.COMPARISON_MAX_BINS, 1)
        filtered_display, filtered_bin = cls._envelope(filtered, cls.COMPARISON_MAX_BINS, 1)
        if source_bin != filtered_bin or len(source[0]) != len(filtered_display[0]):
            raise RuntimeError("comparison display bins are not aligned")
        payload = {
            "kind": "source_filtered_comparison",
            "source": source,
            "filtered": filtered_display,
            "channel_count": 8,
            "source_rate": source_rate,
            "source_samples_per_bin": source_bin,
            "display_bins": len(source[0]),
            "display_transform": "aligned chronological min/max; branches independently median-centered, robust-scaled and signed-8-bit quantized",
            "filter_operations": ["60 Hz notch plus harmonics 2–7", "2 Hz third-order high-pass", "immediate-recording context then exact trim"],
            "not_untouched_raw": True,
            "source_label": "Source-derived display; transformed and independently scaled.",
            "filtered_label": "Filtered display; transformed and independently scaled.",
        }
        payload["display_fingerprint"] = cls._fingerprint([source, filtered_display])
        return payload

    @classmethod
    def _heatmap(cls, values: np.ndarray, width: int, kind: str, label: str) -> dict:
        array = np.asarray(values)
        if array.ndim != 2 or array.shape[1] != width or not len(array) or not np.isfinite(array).all():
            raise ValueError(f"{kind} source must be finite [time,{width}]")
        bin_size = max(1, math.ceil(len(array) / cls.HEATMAP_MAX_TIME_BINS))
        binned = np.stack([array[start : start + bin_size].mean(axis=0) for start in range(0, len(array), bin_size)])
        quantized = cls._signed_quantize(binned, axis=0)
        rows = [[int(item) for item in row] for row in quantized]
        payload = {
            "kind": kind,
            "values": rows,
            "source_rate": "model_aligned_frames",
            "source_frames": len(array),
            "source_frames_per_bin": bin_size,
            "display_bins": len(rows),
            "value_bins": width,
            "display_transform": "chronological mean time bins; per-feature robust centering/scaling; signed 8-bit quantization",
            "not_untouched_raw": True,
            "label": label,
        }
        payload["display_fingerprint"] = cls._fingerprint(rows)
        return payload

    @classmethod
    def features(cls, values: np.ndarray, names: tuple[str, ...]) -> dict:
        payload = cls._heatmap(
            values,
            112,
            "feature_heatmap",
            "Real preprocessing output, time-binned and per-feature normalized for display; not model input.",
        )
        payload["names"] = list(names)
        payload["groups"] = [{"channel": index + 1, "start": index * 14, "count": 14} for index in range(8)]
        return payload

    @classmethod
    def mel(cls, values: np.ndarray) -> dict:
        return cls._heatmap(
            values,
            80,
            "mel_heatmap",
            "Real normalized mel-head prediction, transformed/time-binned for display; not audio or ground truth.",
        )

    @classmethod
    def phonemes(cls, logits: np.ndarray | torch.Tensor) -> dict:
        tensor = logits.detach().cpu().float() if isinstance(logits, torch.Tensor) else torch.from_numpy(np.asarray(logits)).float()
        if tensor.ndim != 2 or tensor.shape[1] != 48 or not torch.isfinite(tensor).all():
            raise ValueError("phoneme display source must be finite [frames,48]")
        probabilities = torch.softmax(tensor, dim=-1)
        values, indexes = probabilities.max(dim=-1)
        frames = [
            {"frame": frame, "class_index": int(index), "token": PHONEME_INVENTORY[int(index)], "top_class_diagnostic": round(float(value), 3)}
            for frame, (index, value) in enumerate(zip(indexes.tolist(), values.tolist(), strict=True))
        ]
        payload = {
            "kind": "phoneme_top_class",
            "frames": frames,
            "source_rate": "model_output_frames",
            "display_bins": len(frames),
            "class_count": 48,
            "collapsed_path": list(collapsed_phoneme_path(tensor)),
            "display_transform": "exact framewise top class; top softmax rounded to three decimals; full logits withheld",
            "not_untouched_raw": True,
            "label": "Real released auxiliary-head output; top-class diagnostic, not text confidence.",
        }
        payload["display_fingerprint"] = cls._fingerprint(frames)
        return payload
