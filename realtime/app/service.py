"""Hardened same-origin service for one official-recording / one-model replay."""
from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from pathlib import Path
from threading import Lock
from typing import Literal
import json
import logging
import os
import secrets
import time

import numpy as np
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, ConfigDict

from .asset_registry import AssetRegistry, SampleRecord
from .config import (
    APP_REVISION,
    DIAGNOSTIC_THRESHOLD,
    MAX_ACTIVE_RUNS,
    PUBLIC_SAMPLE_IDS,
    RUN_TTL_SECONDS,
    TRUTH,
)
from .display_payload import DisplayPayloadBuilder
from .pipeline import InferencePipeline
from .signal_source import RecordedEMGReplaySource, SignalSource

logger = logging.getLogger("quiet_channel.realtime")
CLIENT = Path(__file__).resolve().parents[1] / "client"
EVENT_ORDER = (
    "asset_checks_passed",
    "source_opened",
    "replay_started",
    "source_complete",
    "preprocessing_complete",
    "branches_aligned",
    "model_forward_complete",
    "decoder_complete",
    "metadata_revealed",
    "decision_required",
)


class CreateRun(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sample_id: str


class DecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    action: Literal["confirm", "reject"]
    safety_acknowledged: bool = False


@dataclass
class Run:
    id: str
    sample_id: str
    original_sample_id: str
    created_at: float = field(default_factory=time.monotonic)
    state: str = "ready"
    streamed: bool = False
    event_index: int = 0
    prediction: str | None = None
    safety_sensitive: bool = False
    active_source: SignalSource | None = None
    lock: Lock = field(default_factory=Lock)
    event_started: float = 0.0

    def expired(self) -> bool:
        return time.monotonic() - self.created_at > RUN_TTL_SECONDS


@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.getenv("QUIET_CHANNEL_REQUIRE_RELEASE_BINDING") == "1":
        from realtime.generate_release_manifest import verify as verify_release
        release = json.loads((Path(__file__).resolve().parents[1] / "release-manifest.json").read_text(encoding="utf-8"))
        verify_release(release)
        expected_revision = os.getenv("QUIET_CHANNEL_REVISION", "")
        if release.get("application_revision") != expected_revision:
            raise RuntimeError("deployed revision differs from release manifest")
    registry = AssetRegistry()
    registry.verify_all()
    pipeline = InferencePipeline()
    app.state.registry = registry
    app.state.pipeline = pipeline
    app.state.runs = {}
    app.state.runs_lock = Lock()
    logger.info("official replay service ready; one strict-loaded checkpoint; %s parameters", pipeline.parameter_count)
    yield
    for run in list(app.state.runs.values()):
        if run.active_source:
            run.active_source.stop()
    app.state.runs.clear()


app = FastAPI(
    title="Quiet Channel official-recording replay",
    version="3.0.0",
    description=TRUTH,
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


@app.middleware("http")
async def hardened_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self'; "
        "img-src 'self' data:; connect-src 'self'; object-src 'none'; "
        "base-uri 'none'; form-action 'none'; frame-ancestors 'none'; "
        "media-src 'none'; worker-src 'none'; manifest-src 'none'"
    )
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=(), payment=(), usb=(), serial=(), bluetooth=()"
    )
    return response


def _cleanup(request: Request, *, prune_terminal: bool = False) -> None:
    with request.app.state.runs_lock:
        for run_id, run in list(request.app.state.runs.items()):
            repair_hold = run.original_sample_id == "QC-R02" and run.sample_id == "QC-R02" and run.state in {"abstain", "rejected"}
            terminal = run.state in {"confirmed", "rejected", "stopped", "error"}
            if run.expired() or (prune_terminal and terminal and not repair_hold):
                if run.active_source:
                    run.active_source.stop()
                del request.app.state.runs[run_id]


def _run(request: Request, run_id: str) -> Run:
    _cleanup(request)
    run = request.app.state.runs.get(run_id)
    if run is None:
        raise HTTPException(404, "run not found or expired")
    return run


def _line(event: dict) -> bytes:
    return (json.dumps(event, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def _event(run: Run, kind: str, **payload) -> bytes:
    if run.event_index >= len(EVENT_ORDER) or EVENT_ORDER[run.event_index] != kind:
        raise RuntimeError("run event ordering violation")
    elapsed = max(0.0, (time.perf_counter() - run.event_started) * 1_000.0)
    value = {"event": kind, "sequence": run.event_index + 1, "relative_ms": round(elapsed, 1), **payload}
    run.event_index += 1
    return _line(value)


@app.get("/api/v1/health")
def health(request: Request):
    pipeline: InferencePipeline = request.app.state.pipeline
    registry: AssetRegistry = request.app.state.registry
    return {
        "status": "ready",
        "revision": APP_REVISION if len(APP_REVISION) == 12 else "unbound",
        "service": "private_research_replay",
        "acquisition": "official_recorded_semg_replay",
        "live_capture": False,
        "executed_models": 1,
        "parameters": pipeline.parameter_count,
        "model_fingerprint_prefix": registry.assets["model"]["checkpoint"]["sha256"][:10],
        "catalogue_version": registry.catalogue["catalogue_version"],
        "telemetry": False,
        "persistence": False,
    }


@app.get("/api/v1/manifest")
def public_manifest(request: Request):
    registry: AssetRegistry = request.app.state.registry
    pipeline: InferencePipeline = request.app.state.pipeline
    return registry.public_manifest(revision=APP_REVISION, parameter_count=pipeline.parameter_count)


@app.post("/api/v1/runs", status_code=201)
def create_run(payload: CreateRun, request: Request):
    if payload.sample_id not in PUBLIC_SAMPLE_IDS:
        raise HTTPException(422, "unknown official replay ID")
    _cleanup(request, prune_terminal=True)
    with request.app.state.runs_lock:
        if len(request.app.state.runs) >= MAX_ACTIVE_RUNS:
            raise HTTPException(429, "bounded run capacity reached; reload after prior runs expire")
        run_id = secrets.token_urlsafe(18)
        run = Run(run_id, payload.sample_id, payload.sample_id)
        request.app.state.runs[run_id] = run
    return {
        "id": run.id,
        "sample_id": run.sample_id,
        "state": run.state,
        "events": f"/api/v1/runs/{run.id}/events",
        "truth": TRUTH,
    }


def _source_for(run: Run, registry: AssetRegistry) -> tuple[SampleRecord, RecordedEMGReplaySource]:
    sample = registry.get(run.sample_id, allow_second_take=run.sample_id == "QC-R02-T2")
    return sample, RecordedEMGReplaySource(sample)


def _stream(run: Run, registry: AssetRegistry, pipeline: InferencePipeline):
    sample, source = _source_for(run, registry)
    run.active_source = source
    try:
        yield _event(
            run,
            "asset_checks_passed",
            sample_id=sample.public_id,
            checkpoint="verified and strict-loaded",
            frozen_member_set="verified",
        )
        source.start()
        yield _event(
            run,
            "source_opened",
            sample_id=sample.public_id,
            source="official Silent Speech EMG v1.0 recording",
            source_doi="10.5281/zenodo.4064409",
            license="CC BY 4.0",
            source_split=sample.spec["source_split"],
            sample_count=sample.spec["sample_count"],
            duration_seconds=sample.spec["duration_seconds"],
            sample_rate_hz=1_000,
            channels=8,
            native_dtype="float64",
            live_capture=False,
        )
        frames: list[np.ndarray] = []
        for frame in source.frames():
            if run.state == "stopped":
                return
            frames.append(frame.samples)
        if not frames:
            raise RuntimeError("official source produced no frames")
        recording = np.concatenate(frames, axis=0)
        recording.flags.writeable = False
        source_display = DisplayPayloadBuilder.source_envelope(recording)
        yield _event(
            run,
            "replay_started",
            sample_id=sample.public_id,
            visualization="recorded-duration display only; not live sensing",
            visualization_duration_seconds=sample.spec["duration_seconds"],
            source_display=source_display,
        )
        if run.state == "stopped":
            return
        yield _event(
            run,
            "source_complete",
            sample_id=sample.public_id,
            sample_count=len(recording),
            channel_text_summary="Eight official recorded source channels prepared as bounded transformed display envelopes.",
        )
        before, after = source.filter_context()
        result = pipeline.infer(recording, before, after, source.alignment_frames)
        if run.state == "stopped":
            return
        comparison = DisplayPayloadBuilder.source_filtered_comparison(recording, result.preprocessed.filtered)
        yield _event(
            run,
            "preprocessing_complete",
            comparison_display=comparison,
            provenance=list(result.preprocessed.provenance),
        )
        feature_display = DisplayPayloadBuilder.features(result.preprocessed.features, result.preprocessed.feature_names)
        yield _event(
            run,
            "branches_aligned",
            model_raw_shape=list(result.preprocessed.model_raw.shape),
            model_raw_dtype="float32",
            feature_shape=list(result.preprocessed.features.shape),
            feature_branch="inspectable / not consumed by released forward path",
            feature_display=feature_display,
        )
        mel_display = DisplayPayloadBuilder.mel(result.mel_features)
        phoneme_display = DisplayPayloadBuilder.phonemes(result.phoneme_logits)
        yield _event(
            run,
            "model_forward_complete",
            executed_model="Executed model 1 of 1",
            architecture="3 residual CNN blocks; 6-layer 768-wide 8-head relative-position Transformer",
            parameters=pipeline.parameter_count,
            strict_load=True,
            output_shapes={"mel": list(result.mel_features.shape), "phoneme_logits": list(result.phoneme_logits.shape)},
            model_forward_ms=result.model_forward_ms,
            timing_label="Measured local software model forward time for this run on this host; excludes recording duration, sensing, hardware, network, endpointing, confirmation, and output.",
            mel_display=mel_display,
            phoneme_display=phoneme_display,
        )
        candidates = [
            {
                "text": candidate.text,
                "diagnostic_score": candidate.diagnostic_score,
                "phoneme_distance": candidate.phoneme_distance,
            }
            for candidate in result.decoded.candidates[:3]
        ]
        run.prediction = candidates[0]["text"] if candidates else None
        run.safety_sensitive = bool(sample.safety_sensitive or result.decoded.safety_sensitive)
        yield _event(
            run,
            "decoder_complete",
            decoder="project bounded phoneme-edit algorithm; not the released model",
            candidates=candidates,
            phoneme_alignment_score=result.decoded.phoneme_alignment_score,
            frame_top_class_diagnostic=result.decoded.frame_top_class_diagnostic,
            decoder_agreement=result.decoded.decoder_agreement,
            threshold=DIAGNOSTIC_THRESHOLD,
            project_decoder_ms=result.project_decoder_ms,
            timing_label="Measured local software project decoder time for this run on this host; excludes recording duration, sensing, hardware, network, endpointing, confirmation, and output.",
        )
        yield _event(
            run,
            "metadata_revealed",
            prompt=sample.prompt,
            label="revealed after model and decoder completed; official dataset metadata for audit only",
            matches_top_candidate=bool(run.prediction == sample.prompt),
        )
        run.state = result.decoded.status
        reason = result.decoded.reason
        if run.safety_sensitive and run.state == "confirm_required":
            reason = "Safety hold: acknowledgement and confirmation are both required; no actuation is connected."
        yield _event(
            run,
            "decision_required",
            state=run.state,
            reason=reason,
            prediction=run.prediction,
            safety_sensitive=run.safety_sensitive,
            second_official_take_available=bool(sample.second_take_id),
            output_committed=False,
        )
    except Exception as error:
        run.state = "error"
        run.prediction = None
        logger.error("real replay run failed safely; category=%s", type(error).__name__)
        yield _line({"event": "error", "detail": "real replay pipeline failed; no result is available", "state": "error"})
    finally:
        source.stop()
        run.active_source = None


@app.get("/api/v1/runs/{run_id}/events")
def stream_run(run_id: str, request: Request):
    run = _run(request, run_id)
    with run.lock:
        if run.streamed or run.state not in {"ready", "second_take_ready"}:
            raise HTTPException(409, "run events are unavailable in the current state")
        run.streamed = True
        run.state = "running"
        run.event_started = time.perf_counter()
        run.event_index = 0
    return StreamingResponse(
        _stream(run, request.app.state.registry, request.app.state.pipeline),
        media_type="application/x-ndjson",
        headers={"X-Accel-Buffering": "no"},
    )


@app.post("/api/v1/runs/{run_id}/stop")
def stop_run(run_id: str, request: Request):
    run = _run(request, run_id)
    with run.lock:
        if run.state in {"confirmed", "rejected", "stopped", "error"}:
            raise HTTPException(409, "run is already terminal")
        run.state = "stopped"
        run.prediction = None
        if run.active_source:
            run.active_source.stop()
    return {"state": "stopped", "output_committed": False, "terminal": True}


@app.post("/api/v1/runs/{run_id}/decision")
def decide(run_id: str, payload: DecisionRequest, request: Request):
    run = _run(request, run_id)
    with run.lock:
        if run.state != "confirm_required":
            raise HTTPException(409, "human decision is unavailable in the current state")
        if payload.action == "reject":
            run.state = "rejected"
            run.prediction = None
            return {
                "state": "rejected",
                "output_committed": False,
                "terminal": True,
                "second_official_take_available": run.original_sample_id == "QC-R02" and run.sample_id == "QC-R02",
            }
        if run.safety_sensitive and not payload.safety_acknowledged:
            raise HTTPException(409, "safety acknowledgement is required in addition to confirmation")
        if not run.prediction:
            raise HTTPException(409, "no candidate is available")
        output = run.prediction
        run.state = "confirmed"
        run.prediction = None
        return {
            "state": "confirmed",
            "output_committed": True,
            "output": output,
            "actuation": False,
            "terminal": True,
        }


@app.post("/api/v1/runs/{run_id}/second-take")
def second_take(run_id: str, request: Request):
    run = _run(request, run_id)
    with run.lock:
        if run.original_sample_id != "QC-R02" or run.sample_id != "QC-R02" or run.state not in {"abstain", "rejected"}:
            raise HTTPException(409, "second official take is unavailable")
        run.sample_id = "QC-R02-T2"
        run.state = "second_take_ready"
        run.streamed = False
        run.event_index = 0
        run.prediction = None
        run.safety_sensitive = False
    return {
        "state": run.state,
        "sample_id": "QC-R02-T2",
        "events": f"/api/v1/runs/{run.id}/events",
        "repair": "second official recorded take; no synthetic signal and the downstream pipeline is unchanged",
    }


@app.get("/")
def index():
    return FileResponse(CLIENT / "index.html", media_type="text/html")


@app.get("/styles.css", include_in_schema=False)
def styles():
    return FileResponse(CLIENT / "styles.css", media_type="text/css")


@app.get("/replay-contract.js", include_in_schema=False)
def replay_contract_script():
    return FileResponse(CLIENT / "replay-contract.js", media_type="text/javascript")


@app.get("/app.js", include_in_schema=False)
def client_script():
    return FileResponse(CLIENT / "app.js", media_type="text/javascript")
