"""FastAPI service for real recorded-sEMG replay through released weights."""
from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import asdict, dataclass, field
from pathlib import Path
from threading import Lock
from typing import Literal
from uuid import uuid4
import json
import logging
import os
import time

import numpy as np
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from .config import CONFIDENCE_THRESHOLD, MODEL_PATH, REPLAY_ROOT, SCENARIOS
from .pipeline import InferencePipeline
from .signal_source import RecordedEMGReplaySource, SignalSource

logger = logging.getLogger("quiet_channel.realtime")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s %(name)s %(message)s")
CLIENT = Path(__file__).resolve().parents[1] / "client"
TRUTH = "Replay of real recorded sEMG through the real released pretrained model; not live capture."


class CreateSession(BaseModel):
    scenario: Literal["clear", "ambiguous", "safety"]


class DecisionRequest(BaseModel):
    action: Literal["confirm", "reject"]
    safety_acknowledged: bool = False


@dataclass
class Session:
    id: str
    scenario_id: str
    state: str = "ready"
    attempt: str = "initial"
    prediction: str | None = None
    safety_sensitive: bool = False
    active_source: SignalSource | None = None
    lock: Lock = field(default_factory=Lock)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pipeline = InferencePipeline(MODEL_PATH)
    app.state.sessions = {}
    logger.info(
        "released_model_loaded path=%s sha256=%s parameters=%s acquisition=recorded_replay",
        MODEL_PATH,
        app.state.pipeline.asset_manifest["model"]["checkpoint"]["sha256"],
        app.state.pipeline.parameter_count,
    )
    yield
    for session in app.state.sessions.values():
        if session.active_source:
            session.active_source.stop()


app = FastAPI(
    title="Quiet Channel real recorded-sEMG replay service",
    version="2.0.0",
    description=TRUTH,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url=None,
)


@app.middleware("http")
async def local_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self'; "
        "img-src 'self' data:; connect-src 'self'; object-src 'none'; frame-ancestors 'none'"
    )
    return response


@app.get("/api/health")
def health(request: Request):
    pipeline: InferencePipeline = request.app.state.pipeline
    checkpoint = pipeline.asset_manifest["model"]["checkpoint"]
    return {
        "status": "ok",
        "service": "local-only_non-commercial_research_demo",
        "acquisition": "official_recorded_semg_replay",
        "live_capture": False,
        "inference": "official_released_pretrained_model",
        "model": {
            "kind": "released residual CNN + relative-position Transformer transduction model",
            "parameters": pipeline.parameter_count,
            "sha256": checkpoint["sha256"],
            "license": "CC BY 4.0",
            "creator": "David Gaddy",
        },
        "dataset": {
            "name": "Silent Speech EMG v1.0",
            "doi": "10.5281/zenodo.4064409",
            "license": "CC BY 4.0",
            "single_speaker": True,
        },
        "truth": TRUTH,
        "telemetry": False,
    }


@app.get("/api/scenarios")
def scenarios():
    return {
        "truth": TRUTH,
        "confidence": "Uncalibrated phoneme-alignment score; not accuracy or probability of correctness.",
        "items": [
            {
                "id": scenario.id,
                "title": scenario.title,
                "description": scenario.description,
                "source_split": scenario.evaluation_split,
                "safety_sensitive": scenario.safety_sensitive,
            }
            for scenario in SCENARIOS.values()
        ],
    }


@app.post("/api/sessions", status_code=201)
def create_session(payload: CreateSession, request: Request):
    session = Session(uuid4().hex, payload.scenario)
    request.app.state.sessions[session.id] = session
    return {
        "id": session.id,
        "scenario": payload.scenario,
        "state": session.state,
        "stream": f"/api/sessions/{session.id}/stream",
        "truth": TRUTH,
    }


def _session(request: Request, session_id: str) -> Session:
    session = request.app.state.sessions.get(session_id)
    if session is None:
        raise HTTPException(404, "session not found")
    return session


def _event(kind: str, **payload) -> bytes:
    return (json.dumps({"event": kind, **payload}, separators=(",", ":")) + "\n").encode()


def _source_for(session: Session) -> RecordedEMGReplaySource:
    scenario = SCENARIOS[session.scenario_id]
    group = scenario.sample_group
    index = scenario.sample_index
    if session.attempt == "repair":
        if scenario.repair_group is None or scenario.repair_index is None:
            raise RuntimeError("scenario has no recorded repair take")
        group, index = scenario.repair_group, scenario.repair_index
    return RecordedEMGReplaySource(REPLAY_ROOT / group, index)


def _stream_events(session: Session, pipeline: InferencePipeline, pace: bool):
    with session.lock:
        if session.state not in {"ready", "repair_ready"}:
            yield _event("error", detail=f"session cannot stream from state {session.state}")
            return
        session.state = "capturing"
    source = _source_for(session)
    session.active_source = source
    samples: list[np.ndarray] = []
    scenario = SCENARIOS[session.scenario_id]
    yield _event(
        "acquisition_started",
        stage="raw_signal",
        source="RecordedEMGReplaySource",
        provenance="official Zenodo 4064409 single-speaker research recording",
        simulated=False,
        live_capture=False,
        license="CC BY 4.0",
        sample_rate=source.sample_rate,
        channels=source.channels,
        attempt=session.attempt,
        truth=TRUTH,
    )
    try:
        source.start()
        for frame in source.frames():
            if session.state == "stopped":
                yield _event("stopped", stage="raw_signal", state="stopped")
                return
            samples.append(frame.samples)
            preview = frame.samples[::8, :4]
            yield _event(
                "raw_frame",
                stage="raw_signal",
                first_sample=frame.first_sample,
                sample_count=len(frame.samples),
                preview=np.round(preview, 2).tolist(),
                provenance=frame.provenance,
            )
            if pace:
                time.sleep(len(frame.samples) / source.sample_rate * 0.35)
        recording = np.concatenate(samples, axis=0)
        before, after = source.filter_context()
        yield _event(
            "preprocessing",
            stage="features",
            operations=[
                "60 Hz notch + harmonics (upstream)",
                "2 Hz high-pass (upstream)",
                "689.06 Hz raw-model resample",
                "516.79 Hz / 112-value upstream features",
            ],
            input_shape=list(recording.shape),
        )
        result = pipeline.infer(recording, before, after, source.alignment_frames)
        feature_preview = result.preprocessed.features
        yield _event(
            "features",
            stage="features",
            shape=list(feature_preview.shape),
            names=list(result.preprocessed.feature_names[:8]),
            preview=np.round(feature_preview[:: max(1, len(feature_preview) // 20), :8], 4).tolist(),
            model_note="Released architecture consumes the identically preprocessed raw branch; explicit features are inspectable but unused by architecture.py.",
        )
        decoded = result.decoded
        candidates = [asdict(candidate) for candidate in decoded.candidates]
        yield _event(
            "inference",
            stage="model",
            architecture="Official 54M-parameter residual CNN + relative Transformer (Gaddy release)",
            parameter_count=pipeline.parameter_count,
            model_license="CC BY 4.0",
            model_sha256=pipeline.asset_manifest["model"]["checkpoint"]["sha256"],
            output_steps=result.output_steps,
            mel_shape=list(result.mel_features.shape),
            latency_ms=result.latency_ms,
            raw_phonemes=list(decoded.raw_phonemes),
            candidates=candidates,
            confidence=decoded.confidence,
            frame_certainty=decoded.frame_certainty,
            decoder_agreement=decoded.decoder_agreement,
            confidence_label="uncalibrated phoneme-alignment score — not accuracy",
        )
        session.prediction = candidates[0]["text"]
        session.safety_sensitive = scenario.safety_sensitive or decoded.safety_sensitive
        session.state = decoded.status
        reason = decoded.reason
        if scenario.safety_sensitive and session.state != "abstain":
            reason = "Safety-sensitive research replay: explicit confirmation is mandatory; no actuation is connected."
        yield _event(
            "record_reference",
            stage="model",
            prompt=source.metadata["text"],
            label="dataset metadata shown after inference; never passed to the model or decoder",
            book=source.metadata["book"],
            sentence_index=source.metadata["sentence_index"],
            source_split=scenario.evaluation_split,
        )
        yield _event(
            "decision",
            stage="decision",
            state=decoded.status,
            reason=reason,
            prediction=session.prediction,
            safety_sensitive=session.safety_sensitive,
            threshold=CONFIDENCE_THRESHOLD,
            output_committed=False,
        )
    except Exception:
        logger.exception("stream_failed session=%s", session.id)
        session.state = "error"
        yield _event("error", detail="real replay pipeline failed; see local service log", state="error")
    finally:
        source.stop()
        session.active_source = None


@app.get("/api/sessions/{session_id}/stream")
def stream_session(session_id: str, request: Request, pace: bool = Query(default=True)):
    session = _session(request, session_id)
    return StreamingResponse(
        _stream_events(session, request.app.state.pipeline, pace),
        media_type="application/x-ndjson",
        headers={"X-Accel-Buffering": "no"},
    )


@app.post("/api/sessions/{session_id}/stop")
def stop_session(session_id: str, request: Request):
    session = _session(request, session_id)
    session.state = "stopped"
    if session.active_source:
        session.active_source.stop()
    return {"id": session.id, "state": "stopped", "output_committed": False}


@app.post("/api/sessions/{session_id}/decision")
def decide(session_id: str, payload: DecisionRequest, request: Request):
    session = _session(request, session_id)
    if session.state != "confirm_required":
        raise HTTPException(409, f"decision unavailable in state {session.state}")
    if payload.action == "reject":
        session.state = "rejected"
        return {
            "id": session.id,
            "state": "rejected",
            "output_committed": False,
            "repair_available": SCENARIOS[session.scenario_id].repair_group is not None,
        }
    if session.safety_sensitive and not payload.safety_acknowledged:
        raise HTTPException(409, "safety acknowledgement is required")
    session.state = "confirmed"
    return {
        "id": session.id,
        "state": "confirmed",
        "output_committed": True,
        "output": session.prediction,
        "local_only": True,
    }


@app.post("/api/sessions/{session_id}/repair")
def repair(session_id: str, request: Request):
    session = _session(request, session_id)
    if session.state not in {"abstain", "rejected"}:
        raise HTTPException(409, f"repair unavailable in state {session.state}")
    scenario = SCENARIOS[session.scenario_id]
    if scenario.repair_group is None:
        raise HTTPException(409, "this scenario has no second recorded take")
    session.attempt = "repair"
    session.state = "repair_ready"
    session.prediction = None
    return {
        "id": session.id,
        "state": session.state,
        "stream": f"/api/sessions/{session.id}/stream",
        "repair": "second real recorded take of the same source prompt; downstream pipeline is unchanged",
    }


@app.get("/")
def index():
    return FileResponse(CLIENT / "index.html")


@app.get("/styles.css", include_in_schema=False)
def styles():
    return FileResponse(CLIENT / "styles.css", media_type="text/css")


@app.get("/app.js", include_in_schema=False)
def client_script():
    return FileResponse(CLIENT / "app.js", media_type="text/javascript")
