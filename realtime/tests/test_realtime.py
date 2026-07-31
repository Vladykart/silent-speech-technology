from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import json
import unittest

import numpy as np
import torch
from fastapi.testclient import TestClient

from realtime.app.config import MANIFEST_PATH, MODEL_PATH, SCENARIOS
from realtime.app.pipeline import InferencePipeline
from realtime.app.preprocessing import FEATURE_NAMES, preprocess
from realtime.app.service import app
from realtime.app.signal_source import (
    NoiseProfile,
    SimulatedSignalSource,
    inject_noise,
    profile_for_quality,
    synthesize_clean_signal,
)

ROOT = Path(__file__).resolve().parents[2]


def capture(scenario_id: str, repair: bool = False) -> np.ndarray:
    scenario = SCENARIOS[scenario_id]
    source = SimulatedSignalSource(
        scenario.repair_utterance if repair else scenario.utterance,
        profile=profile_for_quality("repair" if repair else scenario.quality),
        seed=71 if repair else {"clear": 31, "ambiguous": 47, "safety": 59}[scenario_id],
        alternate=None if repair else scenario.alternate,
    )
    source.start()
    frames = list(source.frames())
    source.stop()
    return np.concatenate([frame.samples for frame in frames])


class SignalAndFeatureTests(unittest.TestCase):
    def test_simulated_source_shape_chunks_and_noise(self):
        source = SimulatedSignalSource("check stock", seed=4, chunk_samples=37)
        source.start()
        frames = list(source.frames())
        source.stop()
        signal = np.concatenate([frame.samples for frame in frames])
        clean = synthesize_clean_signal("check stock", rng=np.random.default_rng(4))
        self.assertEqual(signal.shape, clean.shape)
        self.assertEqual(signal.shape[1], 8)
        self.assertTrue(all(frame.simulated and frame.sample_rate == 1_000 for frame in frames))
        self.assertGreater(float(np.std(signal - clean)), 0.02)
        self.assertEqual([frame.first_sample for frame in frames], list(range(0, len(signal), 37)))

    def test_each_required_noise_component_changes_signal(self):
        clean = np.zeros((600, 8), dtype=np.float32)
        noisy = inject_noise(
            clean,
            NoiseProfile(.05, .1, .04, 1.0, .5),
            np.random.default_rng(9),
        )
        self.assertEqual(noisy.shape, (600, 8))
        self.assertGreater(float(np.max(np.abs(noisy))), 0.3)
        self.assertGreater(float(np.std(noisy)), 0.05)

    def test_production_feature_shape_and_finite_values(self):
        result = preprocess(capture("clear"))
        self.assertEqual(result.raw.shape[1], 8)
        self.assertEqual(result.features.shape, (58, 32))
        self.assertEqual(len(FEATURE_NAMES), 32)
        self.assertTrue(np.isfinite(result.features).all())
        self.assertGreater(float(result.features[:, :24].max()), 0.05)


class ModelPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pipeline = InferencePipeline()

    def test_checkpoint_is_real_nonconstant_trained_state(self):
        manifest = json.loads(MANIFEST_PATH.read_text())
        self.assertEqual(sha256(MODEL_PATH.read_bytes()).hexdigest(), manifest["sha256"])
        self.assertEqual(manifest["parameter_count"], 185_820)
        self.assertFalse(manifest["training"]["human_or_biometric_data"])
        state = torch.load(MODEL_PATH, weights_only=True)
        self.assertGreater(len(state), 20)
        self.assertGreater(sum(float(tensor.std()) > 0 for tensor in state.values() if tensor.numel() > 1), 15)

    def test_model_forward_pass_has_ctc_sequence_shape(self):
        processed = preprocess(capture("clear"))
        raw = torch.from_numpy(processed.raw).unsqueeze(0)
        features = torch.from_numpy(processed.features).unsqueeze(0)
        with torch.inference_mode():
            logits, lengths = self.pipeline.model(raw, features, torch.tensor([len(processed.raw)]))
        self.assertEqual(tuple(logits.shape), (1, 58, 28))
        self.assertEqual(lengths.tolist(), [58])
        self.assertGreater(float(logits.std()), 1.0)

    def test_clear_ambiguous_repair_and_safety_are_model_driven(self):
        clear = self.pipeline.infer(capture("clear")).decoded
        ambiguous = self.pipeline.infer(capture("ambiguous")).decoded
        repair = self.pipeline.infer(capture("ambiguous", repair=True)).decoded
        safety = self.pipeline.infer(capture("safety")).decoded
        self.assertEqual(clear.candidates[0].text, "check stock")
        self.assertEqual(clear.status, "confirm_required")
        self.assertLess(ambiguous.confidence, 0.68)
        self.assertEqual(ambiguous.status, "abstain")
        self.assertEqual(repair.candidates[0].text, "open work order")
        self.assertEqual(repair.status, "confirm_required")
        self.assertEqual(safety.candidates[0].text, "cancel request")
        self.assertTrue(safety.safety_sensitive)
        self.assertNotEqual(ambiguous.raw_ctc, ambiguous.candidates[0].text)


class ApiAndClaimTests(unittest.TestCase):
    def test_health_stream_abstention_repair_and_confirmation_contract(self):
        with TestClient(app) as client:
            health = client.get("/api/health")
            self.assertEqual(health.status_code, 200)
            self.assertEqual(health.json()["inference"], "real_trained_model")
            home = client.get("/")
            self.assertEqual(home.status_code, 200)
            self.assertIn("SIMULATED SIGNAL + NOISE", home.text)
            self.assertIn("default-src 'self'", home.headers["content-security-policy"])
            self.assertEqual(client.get("/styles.css").status_code, 200)
            self.assertEqual(client.get("/app.js").status_code, 200)
            created = client.post("/api/sessions", json={"scenario": "ambiguous"})
            self.assertEqual(created.status_code, 201)
            session = created.json()
            events = [json.loads(line) for line in client.get(session["stream"] + "?pace=false").iter_lines()]
            self.assertEqual(events[0]["event"], "acquisition_started")
            self.assertTrue(any(event["event"] == "features" for event in events))
            inference = next(event for event in events if event["event"] == "inference")
            decision = events[-1]
            self.assertGreater(inference["latency_ms"], 0)
            self.assertEqual(decision["state"], "abstain")
            denied = client.post(f"/api/sessions/{session['id']}/decision", json={"action": "confirm"})
            self.assertEqual(denied.status_code, 409)
            repaired = client.post(f"/api/sessions/{session['id']}/repair")
            self.assertEqual(repaired.status_code, 200)
            repaired_events = [json.loads(line) for line in client.get(repaired.json()["stream"] + "?pace=false").iter_lines()]
            self.assertEqual(repaired_events[-1]["state"], "confirm_required")
            confirmed = client.post(
                f"/api/sessions/{session['id']}/decision",
                json={"action": "confirm", "safety_acknowledged": False},
            )
            self.assertEqual(confirmed.status_code, 200)
            self.assertTrue(confirmed.json()["output_committed"])
            self.assertEqual(confirmed.json()["output"], "open work order")

    def test_safety_acknowledgement_and_stop_contract(self):
        with TestClient(app) as client:
            session = client.post("/api/sessions", json={"scenario": "safety"}).json()
            events = [json.loads(line) for line in client.get(session["stream"] + "?pace=false").iter_lines()]
            self.assertTrue(events[-1]["safety_sensitive"])
            denied = client.post(f"/api/sessions/{session['id']}/decision", json={"action": "confirm"})
            self.assertEqual(denied.status_code, 409)
            accepted = client.post(
                f"/api/sessions/{session['id']}/decision",
                json={"action": "confirm", "safety_acknowledged": True},
            )
            self.assertEqual(accepted.status_code, 200)
            stopped_session = client.post("/api/sessions", json={"scenario": "clear"}).json()
            stopped = client.post(f"/api/sessions/{stopped_session['id']}/stop")
            self.assertEqual(stopped.json()["state"], "stopped")
            self.assertFalse(stopped.json()["output_committed"])

    def test_truth_labels_and_prohibited_boundaries_are_visible(self):
        page = (ROOT / "realtime/client/index.html").read_text()
        documentation = (ROOT / "realtime/README.md").read_text() if (ROOT / "realtime/README.md").exists() else ""
        combined = (page + documentation).lower()
        for phrase in (
            "simulated signal + noise",
            "real model / real inference",
            "not measured accuracy",
            "no mind reading",
            "not medical",
            "no collection, accounts or telemetry",
            "dgaddy/silent_speech",
            "a89357c2086609b432919b9d14ffc0be5d8983d5",
        ):
            self.assertIn(phrase, combined)


if __name__ == "__main__":
    unittest.main(verbosity=2)
