"""Fail-closed private asset registries with deliberately bounded public views."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from importlib import metadata as package_metadata
from pathlib import Path
from typing import Any
import json

import numpy as np

from .config import (
    ASSET_DIR,
    ASSET_MANIFEST_PATH,
    MODEL_REGISTRY_PATH,
    PUBLIC_SAMPLE_IDS,
    REPLAY_ROOT,
    SAMPLE_MANIFEST_PATH,
)


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("registry root must be an object")
    return value


def _digest(path: Path) -> str:
    value = sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            value.update(chunk)
    return value.hexdigest()


def _basename(member: str) -> str:
    # Never use member paths to construct directories outside the private ID root.
    name = Path(member).name
    if not name or name in {".", ".."}:
        raise RuntimeError("invalid private member name")
    return name


def _prompt_from_metadata(value: Any) -> str:
    # Source metadata inconsistently carries opening/closing typographic quotes.
    return str(value).strip().strip('"“”')


@dataclass(frozen=True)
class SampleRecord:
    public_id: str
    spec: dict[str, Any]
    root: Path

    def path_for(self, role: str) -> Path:
        return self.root / _basename(str(self.spec[role]["member"]))

    @property
    def prompt(self) -> str:
        return str(self.spec["prompt"])

    @property
    def decoder_text(self) -> str:
        return str(self.spec["decoder_text"])

    @property
    def safety_sensitive(self) -> bool:
        return bool(self.spec.get("safety_sensitive", False))

    @property
    def second_take_id(self) -> str | None:
        value = self.spec.get("second_take_id")
        return str(value) if value else None

    def safe_card(self) -> dict[str, Any]:
        return {
            "id": self.public_id,
            "classification": "official_recorded_example",
            "source_split": self.spec["source_split"],
            "sample_count": self.spec["sample_count"],
            "duration_seconds": self.spec["duration_seconds"],
            "sample_rate_hz": 1_000,
            "channels": 8,
            "native_dtype": "float64",
            "story": self.spec["story"],
            "prompt_state": "sealed_until_after_model_and_decoder",
            "second_official_take_available": bool(self.second_take_id),
        }


class AssetRegistry:
    """Loads unserved manifests and validates every frozen local member."""

    def __init__(self, asset_dir: Path = ASSET_DIR) -> None:
        self.asset_dir = asset_dir
        self.replay_root = asset_dir / "replays" if asset_dir != ASSET_DIR else REPLAY_ROOT
        self.assets = _json(ASSET_MANIFEST_PATH)
        self.catalogue = _json(SAMPLE_MANIFEST_PATH)
        self.models = _json(MODEL_REGISTRY_PATH)
        if self.assets.get("schema_version") != 2:
            raise RuntimeError("unsupported assets manifest")
        if self.catalogue.get("schema_version") != 1:
            raise RuntimeError("unsupported sample manifest")
        if self.models.get("schema_version") != 1:
            raise RuntimeError("unsupported model registry")
        raw_samples = self.catalogue.get("samples")
        if not isinstance(raw_samples, dict):
            raise RuntimeError("sample registry is missing samples")
        expected_ids = set(PUBLIC_SAMPLE_IDS) | {"QC-R02-T2"}
        if set(raw_samples) != expected_ids:
            raise RuntimeError("frozen sample IDs differ from the product contract")
        self.samples = {
            public_id: SampleRecord(public_id, spec, self.replay_root / public_id)
            for public_id, spec in raw_samples.items()
        }
        if self.samples["QC-R02"].second_take_id != "QC-R02-T2":
            raise RuntimeError("second-take policy differs from the frozen contract")
        if self.samples["QC-R02-T2"].spec.get("second_take_of") != "QC-R02":
            raise RuntimeError("repair sample is not bound to QC-R02")
        executed = [item for item in self.models.get("entries", []) if item.get("status") == "executed"]
        if len(executed) != 1 or executed[0].get("id") != "gaddy-transduction-6747411":
            raise RuntimeError("model registry must contain exactly one executed checkpoint")

    def get(self, public_id: str, *, allow_second_take: bool = False) -> SampleRecord:
        if public_id not in PUBLIC_SAMPLE_IDS and not (allow_second_take and public_id == "QC-R02-T2"):
            raise KeyError("unknown public sample ID")
        return self.samples[public_id]

    def grammar(self) -> tuple[tuple[str, str], ...]:
        result: list[tuple[str, str]] = []
        seen: set[str] = set()
        for public_id in PUBLIC_SAMPLE_IDS:
            sample = self.samples[public_id]
            if sample.prompt not in seen:
                result.append((sample.prompt, sample.decoder_text))
                seen.add(sample.prompt)
        return tuple(result)

    def verify_sample(self, sample: SampleRecord) -> None:
        for role in ("selected", "metadata", "context_before", "context_after"):
            path = sample.path_for(role)
            if not path.is_file() or _digest(path) != sample.spec[role]["sha256"]:
                raise RuntimeError(f"frozen member failed integrity verification for {sample.public_id}:{role}")
        selected = np.load(sample.path_for("selected"), mmap_mode="r", allow_pickle=False)
        if selected.dtype != np.dtype("float64") or selected.shape != (int(sample.spec["sample_count"]), 8):
            raise RuntimeError(f"selected recording shape/dtype mismatch for {sample.public_id}")
        if not np.isfinite(selected).all():
            raise RuntimeError(f"selected recording contains non-finite values for {sample.public_id}")
        for role in ("context_before", "context_after"):
            context = np.load(sample.path_for(role), mmap_mode="r", allow_pickle=False)
            if context.dtype != np.dtype("float64") or context.ndim != 2 or context.shape[1] != 8:
                raise RuntimeError(f"filter context shape/dtype mismatch for {sample.public_id}")
            if not np.isfinite(context).all():
                raise RuntimeError(f"filter context contains non-finite values for {sample.public_id}")
        metadata = json.loads(sample.path_for("metadata").read_text(encoding="utf-8"))
        if _prompt_from_metadata(metadata.get("text", "")) != sample.prompt:
            raise RuntimeError(f"metadata prompt mismatch for {sample.public_id}")
        chunks = metadata.get("chunks")
        if not isinstance(chunks, list) or sum(int(chunk[0]) for chunk in chunks) != int(sample.spec["sample_count"]):
            raise RuntimeError(f"metadata chunk count mismatch for {sample.public_id}")

    def verify_all(self) -> None:
        dependency = self.assets["dependencies"]["cmudict_python_package"]
        try:
            installed_version = package_metadata.version("cmudict")
            installed_license = package_metadata.metadata("cmudict").get("License")
        except package_metadata.PackageNotFoundError as error:
            raise RuntimeError("required pronunciation dependency is missing") from error
        if installed_version != dependency["version"] or installed_license != dependency["license"]:
            raise RuntimeError("pronunciation dependency version/license differs from the private manifest")
        for sample in self.samples.values():
            self.verify_sample(sample)

    def public_manifest(self, *, revision: str, parameter_count: int) -> dict[str, Any]:
        checkpoint = self.assets["model"]["checkpoint"]
        archive = self.assets["dataset"]["archive"]
        evidence = []
        for item in self.models["entries"]:
            if item.get("status") != "evidence_only":
                continue
            evidence.append({
                "id": item["id"],
                "name": item["name"],
                "type": item["type"],
                "status": "NOT EXECUTED HERE",
                "reason": item["not_executed_reason"],
            })
        return {
            "schema_version": 1,
            "revision": revision if len(revision) == 12 else "unbound",
            "truth": "Replay of official single-speaker recorded sEMG through David Gaddy’s official released pretrained model; not live capture.",
            "deployment": "Private Tailnet-only research demo delivery; not public or a product/customer deployment.",
            "browser_transfer": "Bounded transformed evidence is sent to this authorized browser; no third-party telemetry, persistence, raw archive, or actuation.",
            "selection_disclosure": self.catalogue["selection_disclosure"],
            "reference_visibility": "Official metadata prompt is omitted until model and decoder completion.",
            "samples": [self.samples[public_id].safe_card() for public_id in PUBLIC_SAMPLE_IDS],
            "executed_model": {
                "label": "Executed model 1 of 1",
                "name": "Gaddy released transduction checkpoint",
                "creator": "David Gaddy",
                "doi": "10.5281/zenodo.6747411",
                "license": "CC BY 4.0",
                "parameters": parameter_count,
                "strict_load": True,
                "fingerprint_prefix": checkpoint["sha256"][:10],
                "architecture": {"residual_blocks": 3, "transformer_layers": 6, "width": 768, "heads": 8},
                "outputs": {"mel_bins": 80, "phoneme_classes": 48},
            },
            "source": {
                "name": "Silent Speech EMG v1.0",
                "creator": "David Gaddy, UC Berkeley",
                "doi": "10.5281/zenodo.4064409",
                "license": "CC BY 4.0",
                "scope": "single-speaker English research data",
                "fingerprint_prefix": archive["sha256"][:10],
            },
            "evidence_only_registry": evidence,
            "telemetry": False,
            "persistence": False,
        }
