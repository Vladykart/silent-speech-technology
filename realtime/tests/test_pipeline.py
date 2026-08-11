from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json
import unittest

import numpy as np
import torch

from realtime.app.asset_registry import AssetRegistry
from realtime.app.config import ASSET_DIR, MODEL_PATH
from realtime.app.display_payload import DisplayPayloadBuilder
from realtime.app.pipeline import InferencePipeline
from realtime.app.preprocessing import FEATURE_NAMES, preprocess
from realtime.app.signal_source import RecordedEMGReplaySource

ROOT = Path(__file__).resolve().parents[1]
PREPARED = MODEL_PATH.is_file() and (ASSET_DIR / "replays/QC-R10/89_emg.npy").is_file()


def capture(sample):
    source = RecordedEMGReplaySource(sample)
    source.start()
    frames = list(source.frames())
    recording = np.concatenate([frame.samples for frame in frames])
    before, after = source.filter_context()
    alignment = source.alignment_frames
    metadata = dict(source.metadata)
    source.stop()
    return recording, before, after, alignment, frames, metadata


@unittest.skipUnless(PREPARED, "prepare approved ignored assets with realtime/fetch_assets.py")
class StrictRealPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = AssetRegistry()
        cls.registry.verify_all()
        cls.pipeline = InferencePipeline()

    def test_native_float64_source_and_explicit_runtime_conversion_boundary(self):
        sample = self.registry.get("QC-R01")
        recording, before, after, alignment, frames, _ = capture(sample)
        official = np.load(sample.path_for("selected"), allow_pickle=False)
        self.assertEqual(recording.dtype, np.float64)
        self.assertFalse(frames[0].samples.flags.writeable)
        np.testing.assert_array_equal(recording, official)
        processed = preprocess(recording, before, after, alignment)
        self.assertEqual(processed.recorded.dtype, np.float64)
        self.assertEqual(processed.filtered.dtype, np.float64)
        self.assertEqual(processed.model_raw.dtype, np.float32)
        self.assertEqual(processed.model_raw.shape, (1176, 8))
        self.assertEqual(processed.features.shape, (147, 112))
        self.assertEqual(processed.feature_names, FEATURE_NAMES)
        model_rows = [row for row in processed.provenance if row["model_input"]]
        self.assertEqual(len(model_rows), 1)
        self.assertIn("runtime float32 conversion", model_rows[0]["operation"])
        feature_row = next(row for row in processed.provenance if row["output_shape"][-1] == 112)
        self.assertFalse(feature_row["model_input"])
        self.assertIn("not consumed", feature_row["note"])

    def test_checkpoint_integrity_strict_state_architecture_and_parameter_count(self):
        assets = json.loads((ROOT / "assets-manifest.json").read_text())
        value = sha256()
        with MODEL_PATH.open("rb") as handle:
            while chunk := handle.read(4 * 1024 * 1024): value.update(chunk)
        self.assertEqual(value.hexdigest(), assets["model"]["checkpoint"]["sha256"])
        self.assertEqual(self.pipeline.parameter_count, 54_187_136)
        state = self.pipeline.model.state_dict()
        self.assertIn("transformer.layers.5.self_attn.relative_positional.embeddings", state)
        self.assertEqual(tuple(state["transformer.layers.5.self_attn.relative_positional.embeddings"].shape), (8, 199, 96, 1))
        self.assertEqual(tuple(state["w_out.weight"].shape), (80, 768))
        self.assertEqual(tuple(state["w_aux.weight"].shape), (48, 768))
        self.assertEqual(len(self.pipeline.model.transformer.layers), 6)
        self.assertEqual(len(self.pipeline.model.conv_blocks), 3)

    def test_model_forward_finishes_before_project_decoder_and_receives_only_raw_branch(self):
        recording, before, after, alignment, _, _ = capture(self.registry.get("QC-R01"))
        order = []
        original_forward = self.pipeline.model.forward
        from realtime.app import pipeline as pipeline_module
        original_decoder = pipeline_module.decode_phonemes

        def model_forward(raw):
            order.append(("model_start", tuple(raw.shape), raw.dtype))
            value = original_forward(raw)
            order.append(("model_end",))
            return value

        def decoder(logits):
            order.append(("decoder_start", tuple(logits.shape)))
            value = original_decoder(logits)
            order.append(("decoder_end",))
            return value

        self.pipeline.model.forward = model_forward
        try:
            with patch("realtime.app.pipeline.decode_phonemes", side_effect=decoder):
                result = self.pipeline.infer(recording, before, after, alignment)
        finally:
            self.pipeline.model.forward = original_forward
        self.assertEqual([item[0] for item in order], ["model_start", "model_end", "decoder_start", "decoder_end"])
        self.assertEqual(order[0][1], (1, 1176, 8))
        self.assertEqual(order[0][2], torch.float32)
        self.assertGreater(result.model_forward_ms, 0)
        self.assertGreater(result.project_decoder_ms, 0)
        self.assertFalse(hasattr(result, "latency_ms"))

    def test_all_frozen_catalogue_outputs_and_retained_selected_outcomes(self):
        expected = {
            "QC-R01": ((147, 80), "What news?", "confirm_required"),
            "QC-R02": ((213, 80), "09:48 AM", "abstain"),
            "QC-R02-T2": ((232, 80), "09:48 AM", "confirm_required"),
            "QC-R03": ((155, 80), "Keep back!", "confirm_required"),
            "QC-R04": ((273, 80), "I myself heard nothing of that.", "confirm_required"),
            "QC-R05": ((207, 80), "I know I did.", "confirm_required"),
            "QC-R06": ((249, 80), "I could not credit it.", "confirm_required"),
            "QC-R07": ((264, 80), "I felt a tug at the reins.", "confirm_required"),
            "QC-R08": ((158, 80), "That was it!", "abstain"),
            "QC-R09": ((237, 80), "09:48 AM", "abstain"),
            "QC-R10": ((230, 80), "Had they prepared pitfalls?", "abstain"),
        }
        retained = {}
        for public_id, sample in self.registry.samples.items():
            recording, before, after, alignment, _, _ = capture(sample)
            result = self.pipeline.infer(recording, before, after, alignment)
            wanted_shape, candidate, status = expected[public_id]
            self.assertEqual(result.mel_features.shape, wanted_shape)
            self.assertEqual(result.phoneme_logits.shape, (wanted_shape[0], 48))
            self.assertEqual(result.preprocessed.features.shape, (wanted_shape[0], 112))
            self.assertTrue(np.isfinite(result.mel_features).all() and np.isfinite(result.phoneme_logits).all())
            self.assertGreater(float(result.mel_features.std()), 0.1)
            self.assertGreater(float(result.phoneme_logits.std()), 0.1)
            self.assertEqual(result.decoded.candidates[0].text, candidate)
            self.assertEqual(result.decoded.status, status)
            retained[public_id] = status
        self.assertEqual(set(retained), set(expected))
        self.assertEqual(retained["QC-R02"], "abstain")
        self.assertEqual(retained["QC-R02-T2"], "confirm_required")

    def test_display_payloads_are_deterministic_bounded_transformed_and_causally_bound(self):
        recording, before, after, alignment, _, _ = capture(self.registry.get("QC-R04"))
        result = self.pipeline.infer(recording, before, after, alignment)
        source = DisplayPayloadBuilder.source_envelope(recording)
        comparison = DisplayPayloadBuilder.source_filtered_comparison(recording, result.preprocessed.filtered)
        features = DisplayPayloadBuilder.features(result.preprocessed.features, result.preprocessed.feature_names)
        mel = DisplayPayloadBuilder.mel(result.mel_features)
        phonemes = DisplayPayloadBuilder.phonemes(result.phoneme_logits)
        self.assertEqual(len(source["channels"]), 8)
        self.assertLessEqual(source["display_bins"], 256)
        self.assertGreaterEqual(source["source_samples_per_bin"], 16)
        self.assertTrue(source["not_untouched_raw"])
        self.assertEqual(len(comparison["source"]), 8)
        self.assertEqual(len(comparison["filtered"]), 8)
        self.assertLessEqual(comparison["display_bins"], 128)
        self.assertEqual(features["value_bins"], 112)
        self.assertLessEqual(features["display_bins"], 64)
        self.assertEqual(mel["value_bins"], 80)
        self.assertLessEqual(mel["display_bins"], 64)
        self.assertEqual(phonemes["class_count"], 48)
        self.assertEqual(len(phonemes["frames"]), alignment)
        self.assertTrue(all(len(row) == 112 and all(-127 <= value <= 127 for value in row) for row in features["values"]))
        self.assertTrue(all(len(row) == 80 and all(-127 <= value <= 127 for value in row) for row in mel["values"]))
        self.assertTrue(all(0 <= row["top_class_diagnostic"] <= 1 for row in phonemes["frames"]))
        self.assertEqual(source, DisplayPayloadBuilder.source_envelope(recording))
        tampered = recording.copy()
        tampered[:16, 0] *= -9
        self.assertNotEqual(source["display_fingerprint"], DisplayPayloadBuilder.source_envelope(tampered)["display_fingerprint"])

    def test_production_import_graph_has_no_simulator_or_authored_fallback(self):
        production = "\n".join(path.read_text() for path in (ROOT / "app").glob("*.py"))
        self.assertNotIn("SimulatedSignalSource", production)
        self.assertNotIn("synthetic_success", production)
        for fixture in ("0.84", "0.54", "0.91", "0.72"):
            self.assertNotIn(fixture, production)


if __name__ == "__main__":
    unittest.main(verbosity=2)
