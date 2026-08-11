from __future__ import annotations

from pathlib import Path
import json
import re
import unittest

from fastapi.testclient import TestClient

from realtime.app.config import MODEL_PATH
from realtime.app.service import EVENT_ORDER, app

ROOT = Path(__file__).resolve().parents[1]
PREPARED = MODEL_PATH.is_file() and (ROOT / "local_assets/replays/QC-R10/89_emg.npy").is_file()
PROMPTS = (
    "What news?", "09:48 AM", "Keep back!", "I myself heard nothing of that.", "I know I did.",
    "I could not credit it.", "I felt a tug at the reins.", "That was it!", "Are we far from Sunbury?",
    "Had they prepared pitfalls?",
)


def read_events(client: TestClient, path: str) -> list[dict]:
    response = client.get(path)
    assert response.status_code == 200
    return [json.loads(line) for line in response.iter_lines() if line]


def walk(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key; yield from walk(item)
    elif isinstance(value, list):
        for item in value: yield from walk(item)
    elif isinstance(value, str):
        yield value


@unittest.skipUnless(PREPARED, "prepare approved ignored assets with realtime/fetch_assets.py")
class SafeApiContractTests(unittest.TestCase):
    def test_order_prompt_sealing_bounded_payload_human_policy_and_fail_closed_routes(self):
        with TestClient(app) as client:
            health = client.get("/api/v1/health")
            self.assertEqual(health.status_code, 200)
            self.assertEqual(health.json()["executed_models"], 1)
            self.assertEqual(health.json()["parameters"], 54_187_136)
            self.assertFalse(health.json()["live_capture"])
            self.assertNotIn("sha256", json.dumps(health.json()).lower())
            manifest_response = client.get("/api/v1/manifest")
            self.assertEqual(manifest_response.status_code, 200)
            manifest = manifest_response.json()
            self.assertEqual([item["id"] for item in manifest["samples"]], [f"QC-R{i:02d}" for i in range(1, 11)])
            self.assertEqual(len(manifest["samples"]), 10)
            self.assertEqual(manifest["executed_model"]["label"], "Executed model 1 of 1")
            self.assertTrue(all(item["status"] == "NOT EXECUTED HERE" for item in manifest["evidence_only_registry"]))
            serialized_manifest = json.dumps(manifest)
            for prompt in PROMPTS:
                self.assertNotIn(prompt, serialized_manifest)

            home = client.get("/")
            self.assertEqual(home.status_code, 200)
            self.assertIn("ONE REAL RELEASED PRETRAINED MODEL", home.text)
            self.assertIn("frame-ancestors 'none'", home.headers["content-security-policy"])
            self.assertIn("camera=()", home.headers["permissions-policy"])
            self.assertEqual(home.headers["cache-control"], "no-store, max-age=0")
            for route in ("/api/docs", "/docs", "/openapi.json", "/api/health", "/api/scenarios", "/api/sessions", "/data", "/download"):
                self.assertEqual(client.get(route).status_code, 404, route)

            clear = client.post("/api/v1/runs", json={"sample_id": "QC-R01"})
            self.assertEqual(clear.status_code, 201)
            self.assertNotRegex(clear.json()["id"], r"^[0-9a-f]{32,64}$")
            clear_events = read_events(client, clear.json()["events"])
            self.assertEqual([item["event"] for item in clear_events], list(EVENT_ORDER))
            self.assertEqual([item["sequence"] for item in clear_events], list(range(1, 11)))
            self.assertEqual(client.get(clear.json()["events"]).status_code, 409)
            self.assertTrue(all(clear_events[index]["relative_ms"] <= clear_events[index + 1]["relative_ms"] for index in range(9)))
            metadata_index = [item["event"] for item in clear_events].index("metadata_revealed")
            decoder_index = [item["event"] for item in clear_events].index("decoder_complete")
            pre_inference_decoder = json.dumps(clear_events[:decoder_index])
            for prompt in PROMPTS:
                self.assertNotIn(prompt, pre_inference_decoder)
            self.assertEqual(clear_events[metadata_index]["prompt"], "What news?")
            self.assertLess([item["event"] for item in clear_events].index("model_forward_complete"), [item["event"] for item in clear_events].index("decoder_complete"))
            model_event = next(item for item in clear_events if item["event"] == "model_forward_complete")
            decoder_event = next(item for item in clear_events if item["event"] == "decoder_complete")
            self.assertIn("model forward", model_event["timing_label"])
            self.assertIn("project decoder", decoder_event["timing_label"])
            self.assertNotIn("latency_ms", json.dumps(clear_events))
            source_display = next(item for item in clear_events if item["event"] == "replay_started")["source_display"]
            self.assertEqual(len(source_display["channels"]), 8)
            self.assertLessEqual(source_display["display_bins"], 256)
            preprocess_event = next(item for item in clear_events if item["event"] == "preprocessing_complete")
            self.assertLessEqual(preprocess_event["comparison_display"]["display_bins"], 128)
            branches = next(item for item in clear_events if item["event"] == "branches_aligned")
            self.assertLessEqual(branches["feature_display"]["display_bins"], 64)
            self.assertTrue(all(len(row) == 112 for row in branches["feature_display"]["values"]))
            self.assertLessEqual(model_event["mel_display"]["display_bins"], 64)
            self.assertTrue(all(len(row) == 80 for row in model_event["mel_display"]["values"]))
            self.assertNotIn("logits", model_event["phoneme_display"])
            self.assertLessEqual(len(decoder_event["candidates"]), 3)
            rejected = client.post(f"/api/v1/runs/{clear.json()['id']}/decision", json={"action": "reject"})
            self.assertEqual(rejected.status_code, 200)
            self.assertFalse(rejected.json()["output_committed"])
            self.assertNotIn("output", rejected.json())

            ambiguous = client.post("/api/v1/runs", json={"sample_id": "QC-R02"}).json()
            first = read_events(client, ambiguous["events"])
            self.assertEqual(first[-1]["state"], "abstain")
            self.assertFalse(first[-1]["output_committed"])
            self.assertEqual(client.post(f"/api/v1/runs/{ambiguous['id']}/decision", json={"action": "confirm"}).status_code, 409)
            second = client.post(f"/api/v1/runs/{ambiguous['id']}/second-take")
            self.assertEqual(second.status_code, 200)
            self.assertEqual(second.json()["sample_id"], "QC-R02-T2")
            second_events = read_events(client, second.json()["events"])
            self.assertEqual([item["event"] for item in second_events], list(EVENT_ORDER))
            self.assertEqual(next(item for item in second_events if item["event"] == "source_opened")["sample_id"], "QC-R02-T2")
            self.assertEqual(second_events[-1]["state"], "confirm_required")
            confirmed = client.post(f"/api/v1/runs/{ambiguous['id']}/decision", json={"action": "confirm"})
            self.assertEqual(confirmed.status_code, 200)
            self.assertTrue(confirmed.json()["output_committed"])
            self.assertFalse(confirmed.json()["actuation"])

            safety = client.post("/api/v1/runs", json={"sample_id": "QC-R03"}).json()
            safety_events = read_events(client, safety["events"])
            self.assertTrue(safety_events[-1]["safety_sensitive"])
            denied = client.post(f"/api/v1/runs/{safety['id']}/decision", json={"action": "confirm"})
            self.assertEqual(denied.status_code, 409)
            accepted = client.post(f"/api/v1/runs/{safety['id']}/decision", json={"action": "confirm", "safety_acknowledged": True})
            self.assertEqual(accepted.status_code, 200)
            self.assertTrue(accepted.json()["output_committed"])
            self.assertFalse(accepted.json()["actuation"])

            stopped = client.post("/api/v1/runs", json={"sample_id": "QC-R04"}).json()
            stopped_result = client.post(f"/api/v1/runs/{stopped['id']}/stop")
            self.assertEqual(stopped_result.status_code, 200)
            self.assertFalse(stopped_result.json()["output_committed"])
            self.assertEqual(client.post(f"/api/v1/runs/{stopped['id']}/decision", json={"action": "confirm"}).status_code, 409)
            self.assertEqual(client.post("/api/v1/runs", json={"sample_id": "QC-R05"}).status_code, 201)
            self.assertEqual(client.post("/api/v1/runs", json={"sample_id": "QC-R02-T2"}).status_code, 422)
            self.assertEqual(client.post("/api/v1/runs", json={"sample_id": "QC-R99"}).status_code, 422)
            self.assertEqual(client.post("/api/v1/runs", json={"sample_id": "QC-R01", "prompt": "forbidden"}).status_code, 422)

            browser_values = list(walk([manifest, clear.json(), clear_events, first, second_events, safety_events]))
            browser_text = "\n".join(str(value) for value in browser_values)
            self.assertNotRegex(browser_text, r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])")
            for forbidden in ("/root/", "emg_data/", "_emg.npy", "_info.json", "sentence_index", '"book"', "transduction_model.pt", "pretrained_models.zip"):
                self.assertNotIn(forbidden, browser_text)

    def test_bounded_active_run_capacity_fails_closed(self):
        with TestClient(app) as client:
            for sample_id in ("QC-R01", "QC-R03", "QC-R04", "QC-R05"):
                self.assertEqual(client.post("/api/v1/runs", json={"sample_id": sample_id}).status_code, 201)
            blocked = client.post("/api/v1/runs", json={"sample_id": "QC-R06"})
            self.assertEqual(blocked.status_code, 429)
            self.assertIn("bounded run capacity", blocked.json()["detail"])

    def test_static_client_has_no_prompt_leak_synthetic_fallback_external_request_or_persistence(self):
        html = (ROOT / "client/index.html").read_text()
        script = (ROOT / "client/app.js").read_text()
        reducer = (ROOT / "client/replay-contract.js").read_text()
        combined = html + script + reducer
        for prompt in PROMPTS:
            self.assertNotIn(prompt, combined)
        self.assertNotRegex(combined, r"https?://")
        for forbidden in ("SimulatedSignalSource", "authored_future", "sendBeacon", "localStorage", "sessionStorage", "indexedDB", "serviceWorker", "WebSocket", "EventSource", "RTCPeerConnection", "getUserMedia", "mediaDevices"):
            self.assertNotIn(forbidden, combined)
        self.assertNotRegex(combined, r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])")
        self.assertEqual(html.count('data-sample-id="QC-R'), 10)
        self.assertEqual(re.findall(r'data-stage-panel="([^"]+)"', html), ["recorded-source", "released-model", "human-decision"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
