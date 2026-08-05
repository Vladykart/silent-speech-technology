from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import json
import re
import unittest

import numpy as np
import torch
from fastapi.testclient import TestClient

from realtime.app.config import ASSET_MANIFEST_PATH, MODEL_PATH, REPLAY_ROOT, SCENARIOS
from realtime.app.pipeline import InferencePipeline
from realtime.app.preprocessing import FEATURE_NAMES, preprocess
from realtime.app.service import app
from realtime.app.signal_source import RecordedEMGReplaySource

ROOT = Path(__file__).resolve().parents[2]
ASSETS_AVAILABLE = MODEL_PATH.is_file() and (REPLAY_ROOT / "clear" / "314_emg.npy").is_file()


def source_for(scenario_id: str, repair: bool = False) -> RecordedEMGReplaySource:
    scenario = SCENARIOS[scenario_id]
    group, index = scenario.sample_group, scenario.sample_index
    if repair:
        group, index = scenario.repair_group, scenario.repair_index
    return RecordedEMGReplaySource(REPLAY_ROOT / str(group), int(index))


def load_capture(scenario_id: str, repair: bool = False):
    source = source_for(scenario_id, repair)
    source.start()
    frames = list(source.frames())
    before, after = source.filter_context()
    recording = np.concatenate([frame.samples for frame in frames])
    metadata = source.metadata.copy()
    metadata["_alignment_frames"] = source.alignment_frames
    source.stop()
    return recording, before, after, frames, metadata


def infer_capture(pipeline: InferencePipeline, scenario_id: str, repair: bool = False):
    recording, before, after, _, metadata = load_capture(scenario_id, repair)
    return pipeline.infer(recording, before, after, metadata["_alignment_frames"])


class ScenarioContractTests(unittest.TestCase):
    def test_committed_replay_metadata_and_safe_example_bindings_are_exact(self):
        manifest = json.loads(ASSET_MANIFEST_PATH.read_text())
        expected = {
            "clear": ("QC-R01", "clear", 314, "What news?", 1),
            "ambiguous": ("QC-R02", "ambiguous", 379, "09:48 AM", 2),
            "safety": ("QC-R03", "safety", 91, "Keep back!", 1),
        }
        for scenario_id, (example_id, group, index, prompt, takes) in expected.items():
            scenario = SCENARIOS[scenario_id]
            self.assertEqual(
                (scenario.example_id, scenario.sample_group, scenario.sample_index, scenario.reference_prompt, scenario.recorded_takes),
                (example_id, group, index, prompt, takes),
            )
            self.assertEqual(manifest["replays"][scenario_id]["index"], index)
            self.assertEqual(manifest["replays"][scenario_id]["reference_prompt"], prompt)
        self.assertEqual(SCENARIOS["ambiguous"].repair_group, "repair")
        self.assertEqual(SCENARIOS["ambiguous"].repair_index, 310)
        self.assertEqual(manifest["replays"]["repair"]["reference_prompt"], "09:48 AM")

    def test_browser_assets_keep_three_stage_accessible_no_egress_contract(self):
        page = (ROOT / "realtime/client/index.html").read_text()
        script = (ROOT / "realtime/client/app.js").read_text()
        styles = (ROOT / "realtime/client/styles.css").read_text()
        self.assertEqual(
            re.findall(r'data-stage-panel="([^"]+)"', page),
            ["data-collection", "model", "process-result"],
        )
        self.assertEqual(page.count('data-progress-stage="'), 3)
        for phrase in ("What news?", "09:48 AM", "Keep back!"):
            self.assertNotIn(phrase, page)
        for semantic in ('<fieldset id="scenario-list">', "<legend>", 'role="alert"', 'aria-live="polite"', '<meter id="score-meter"'):
            self.assertIn(semantic, page)
        self.assertIn(":focus-visible", styles)
        self.assertIn("prefers-reduced-motion: reduce", styles)
        combined = page + script + styles
        self.assertNotRegex(combined, r"https?://")
        for forbidden in ("sendBeacon", "localStorage", "sessionStorage", "getUserMedia", "mediaDevices", "WebSocket", "indexedDB"):
            self.assertNotIn(forbidden, combined)


class AssetAndReplayTests(unittest.TestCase):
    def test_manifest_records_official_identity_rights_sizes_and_hashes(self):
        manifest = json.loads(ASSET_MANIFEST_PATH.read_text())
        self.assertEqual(manifest["model"]["doi"], "10.5281/zenodo.6747411")
        self.assertEqual(manifest["model"]["license"], "CC BY 4.0")
        self.assertEqual(manifest["model"]["checkpoint"]["bytes"], 216_859_418)
        self.assertEqual(
            manifest["model"]["checkpoint"]["sha256"],
            "67d40b64f7831ae15c3c24264e2d13cdff98a212953901048d2923b3db60171a",
        )
        self.assertEqual(manifest["dataset"]["version_doi"], "10.5281/zenodo.4064409")
        self.assertEqual(manifest["dataset"]["license"], "CC BY 4.0")
        self.assertTrue(manifest["dataset"]["single_speaker"])
        self.assertEqual(manifest["dataset"]["archive"]["md5"], "7f97d2182b896652999b1b2d0c69fd7b")

    @unittest.skipUnless(ASSETS_AVAILABLE, "run realtime/fetch_assets.py to install official local assets")
    def test_recorded_source_replays_untouched_real_array(self):
        recording, _, _, frames, metadata = load_capture("clear")
        official = np.load(REPLAY_ROOT / "clear" / "314_emg.npy", allow_pickle=False).astype(np.float32)
        np.testing.assert_array_equal(recording, official)
        self.assertEqual(recording.shape, (1752, 8))
        self.assertEqual(metadata["text"], "“What news?”")
        self.assertTrue(all(frame.provenance == "recorded_research_data_replay" for frame in frames))
        self.assertTrue(all(frame.sample_rate == 1_000 for frame in frames))
        self.assertGreater(abs(float(recording.mean())), 1_000)  # preserves recorded DC before preprocessing

    @unittest.skipUnless(ASSETS_AVAILABLE, "run realtime/fetch_assets.py to install official local assets")
    def test_upstream_preprocessing_shapes_and_values(self):
        recording, before, after, _, _ = load_capture("clear")
        result = preprocess(recording, before, after, 147)
        self.assertEqual(result.model_raw.shape, (1176, 8))
        self.assertEqual(result.features.shape, (147, 112))
        self.assertEqual(len(FEATURE_NAMES), 112)
        self.assertTrue(np.isfinite(result.model_raw).all())
        self.assertTrue(np.isfinite(result.features).all())
        self.assertGreater(float(result.filtered.std()), 1.0)
        self.assertLess(abs(float(result.filtered.mean())), 10.0)


@unittest.skipUnless(ASSETS_AVAILABLE, "run realtime/fetch_assets.py to install official local assets")
class ReleasedModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pipeline = InferencePipeline()

    def test_official_checkpoint_integrity_and_strict_state(self):
        manifest = json.loads(ASSET_MANIFEST_PATH.read_text())
        self.assertEqual(MODEL_PATH.stat().st_size, 216_859_418)
        self.assertEqual(sha256(MODEL_PATH.read_bytes()).hexdigest(), manifest["model"]["checkpoint"]["sha256"])
        self.assertEqual(self.pipeline.parameter_count, 54_187_136)
        state = torch.load(MODEL_PATH, map_location="cpu", weights_only=True)
        self.assertIn("transformer.layers.5.self_attn.relative_positional.embeddings", state)
        self.assertEqual(tuple(state["w_aux.weight"].shape), (48, 768))
        self.assertEqual(tuple(state["w_out.weight"].shape), (80, 768))

    def test_real_recording_real_forward_pass_and_outputs(self):
        result = infer_capture(self.pipeline, "clear")
        self.assertEqual(result.mel_features.shape, (147, 80))
        self.assertGreater(float(result.mel_features.std()), 0.1)
        self.assertEqual(result.decoded.candidates[0].text, "What news?")
        self.assertEqual(result.decoded.status, "confirm_required")
        self.assertEqual(result.decoded.raw_phonemes, ("hh", "w", "ah", "t", "ah", "t", "n", "uw", "z"))
        self.assertGreater(result.latency_ms, 0)

    def test_real_recorded_abstention_second_take_and_safety(self):
        first = infer_capture(self.pipeline, "ambiguous").decoded
        second = infer_capture(self.pipeline, "ambiguous", repair=True).decoded
        safety = infer_capture(self.pipeline, "safety").decoded
        self.assertEqual(first.candidates[0].text, "09:48 AM")
        self.assertLess(first.confidence, 0.60)
        self.assertEqual(first.status, "abstain")
        self.assertEqual(second.candidates[0].text, "09:48 AM")
        self.assertGreaterEqual(second.confidence, 0.60)
        self.assertEqual(second.status, "confirm_required")
        self.assertEqual(safety.candidates[0].text, "Keep back!")
        self.assertTrue(safety.safety_sensitive)
        self.assertEqual(safety.status, "confirm_required")


@unittest.skipUnless(ASSETS_AVAILABLE, "run realtime/fetch_assets.py to install official local assets")
class ApiAndClaimTests(unittest.TestCase):
    def test_api_real_replay_repair_confirmation_safety_and_static_contract(self):
        with TestClient(app) as client:
            health = client.get("/api/health")
            self.assertEqual(health.status_code, 200)
            self.assertEqual(health.json()["inference"], "official_released_pretrained_model")
            self.assertEqual(health.json()["acquisition"], "official_recorded_semg_replay")
            self.assertFalse(health.json()["live_capture"])
            self.assertEqual(health.json()["model"]["parameters"], 54_187_136)
            home = client.get("/")
            self.assertIn("REAL RECORDED sEMG REPLAY", home.text)
            self.assertIn("default-src 'self'", home.headers["content-security-policy"])
            self.assertIn("camera=()", home.headers["permissions-policy"])
            self.assertEqual(client.get("/styles.css").status_code, 200)
            self.assertEqual(client.get("/replay-contract.js").status_code, 200)
            self.assertEqual(client.get("/app.js").status_code, 200)

            scenario_response = client.get("/api/scenarios")
            self.assertEqual(scenario_response.status_code, 200)
            scenario_payload = scenario_response.json()
            self.assertIn("only after inference", scenario_payload["reference_visibility"])
            self.assertEqual(
                [(item["id"], item["example_id"], item["classification"], item["executable"], item["recorded_takes"]) for item in scenario_payload["items"]],
                [
                    ("clear", "QC-R01", "official_recorded_example", True, 1),
                    ("ambiguous", "QC-R02", "official_recorded_example", True, 2),
                    ("safety", "QC-R03", "official_recorded_example", True, 1),
                ],
            )
            serialized_scenarios = json.dumps(scenario_payload)
            for reference in ("What news?", "09:48 AM", "Keep back!"):
                self.assertNotIn(reference, serialized_scenarios)

            created = client.post("/api/sessions", json={"scenario": "ambiguous"}).json()
            self.assertEqual(created["example_id"], "QC-R02")
            events = [json.loads(line) for line in client.get(created["stream"] + "?pace=false").iter_lines()]
            names = [event["event"] for event in events]
            self.assertEqual(names[0], "acquisition_started")
            self.assertFalse(events[0]["simulated"])
            self.assertLess(names.index("inference"), names.index("record_reference"))
            self.assertEqual(events[-1]["state"], "abstain")
            repaired = client.post(f"/api/sessions/{created['id']}/repair")
            self.assertEqual(repaired.status_code, 200)
            second_events = [json.loads(line) for line in client.get(repaired.json()["stream"] + "?pace=false").iter_lines()]
            self.assertEqual(second_events[-1]["state"], "confirm_required")
            rejected = client.post(
                f"/api/sessions/{created['id']}/decision",
                json={"action": "reject"},
            )
            self.assertEqual(rejected.status_code, 200)
            self.assertEqual(rejected.json()["state"], "rejected")
            self.assertFalse(rejected.json()["output_committed"])
            self.assertTrue(rejected.json()["repair_available"])

            safety = client.post("/api/sessions", json={"scenario": "safety"}).json()
            safety_events = [json.loads(line) for line in client.get(safety["stream"] + "?pace=false").iter_lines()]
            self.assertTrue(safety_events[-1]["safety_sensitive"])
            denied = client.post(f"/api/sessions/{safety['id']}/decision", json={"action": "confirm"})
            self.assertEqual(denied.status_code, 409)
            accepted = client.post(
                f"/api/sessions/{safety['id']}/decision",
                json={"action": "confirm", "safety_acknowledged": True},
            )
            self.assertEqual(accepted.status_code, 200)
            self.assertTrue(accepted.json()["output_committed"])
            self.assertTrue(accepted.json()["local_only"])

            stopped = client.post("/api/sessions", json={"scenario": "clear"}).json()
            stop_response = client.post(f"/api/sessions/{stopped['id']}/stop")
            self.assertEqual(stop_response.status_code, 200)
            self.assertFalse(stop_response.json()["output_committed"])
            unavailable = client.post(f"/api/sessions/{stopped['id']}/decision", json={"action": "confirm"})
            self.assertEqual(unavailable.status_code, 409)

    def test_truth_attribution_and_boundaries_are_visible(self):
        page = (ROOT / "realtime/client/index.html").read_text()
        docs = (ROOT / "realtime/README.md").read_text()
        combined = (page + docs).lower()
        for phrase in (
            "real recorded semg",
            "real released",
            "not live capture",
            "not measured project accuracy",
            "no mind reading",
            "not medical",
            "no new collection, accounts or telemetry",
            "non-commercial",
            "cc by 4.0",
            "10.5281/zenodo.4064409",
            "10.5281/zenodo.6747411",
            "dgaddy/silent_speech",
            "a89357c2086609b432919b9d14ffc0be5d8983d5",
        ):
            self.assertIn(phrase, combined)


if __name__ == "__main__":
    unittest.main(verbosity=2)
