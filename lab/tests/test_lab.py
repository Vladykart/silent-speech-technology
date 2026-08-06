"""Standard-library tests for the default-safe pre-hardware foundation."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True
from lab import acquisition, bootstrap_plan, model_contract, signal_pipeline, split_rules

ROOT = Path(__file__).resolve().parents[1]


class AcquisitionTests(unittest.TestCase):
    def test_mock_metadata_drops_timestamps_and_shutdown(self):
        board = acquisition.MockBoard(sample_count=10, dropped_sequences=(2, 8))
        with board:
            samples = list(board.samples())
        self.assertEqual(len(samples), 8)
        self.assertEqual(board.dropped_sample_count, 2)
        self.assertTrue(board.shutdown_clean)
        self.assertEqual(len(samples[0].values), 8)
        self.assertTrue(all(sample.session_id.startswith("synthetic-") for sample in samples))
        self.assertTrue(all(right.timestamp_ns > left.timestamp_ns for left, right in zip(samples, samples[1:])))
        self.assertNotIn(2, [sample.sequence for sample in samples])

    def test_shutdown_on_exception(self):
        board = acquisition.MockBoard()
        with self.assertRaises(RuntimeError):
            with board:
                raise RuntimeError("authored test")
        self.assertTrue(board.shutdown_clean)


class SignalAndModelTests(unittest.TestCase):
    def test_synthetic_envelope_and_filter_validation(self):
        config = signal_pipeline.FilterConfig()
        config.validate()
        values = signal_pipeline.synthetic_semg(32)
        envelope = signal_pipeline.rectified_moving_envelope(values, 4)
        self.assertEqual(len(values), len(envelope))
        self.assertTrue(all(value >= 0 for value in envelope))
        with self.assertRaises(ValueError):
            signal_pipeline.FilterConfig(sample_rate_hz=500, bandpass_high_hz=450).validate()

    def test_model_contract_shapes_masks_and_abstention_schema(self):
        report = model_contract.dry_run()
        self.assertEqual(report["inputShape"], [2, 96, 8])
        self.assertEqual(report["logitShape"], [2, 48, 32])
        self.assertEqual(report["paddingMaskShape"], [2, 48])
        self.assertEqual(report["outputSchema"]["requiresConfirmation"], True)
        self.assertFalse(report["checkpointLoaded"])


class RegistryAndSplitTests(unittest.TestCase):
    def test_safe_profiles_and_dataset_license_separation(self):
        profile = json.loads((ROOT / "software-profiles.json").read_text())
        self.assertFalse(profile["policy"]["installByDefault"])
        self.assertEqual(set(profile["groups"]), {"core", "acquisition", "signal", "model", "edge"})
        plan = bootstrap_plan.plan(["core", "signal"])
        self.assertEqual(plan["mode"], "dry_run_only")
        self.assertEqual(plan["commandsExecuted"], [])

        registry = json.loads((ROOT / "datasets.json").read_text())
        self.assertFalse(registry["policy"]["downloadByDefault"])
        gaddy = registry["datasets"][0]
        self.assertEqual(gaddy["conceptDoi"], "10.5281/zenodo.4064408")
        self.assertEqual(gaddy["versionDoi"], "10.5281/zenodo.4064409")
        self.assertEqual(gaddy["recordLicense"]["identifier"], "cc-by-4.0")
        self.assertEqual(gaddy["codeLicense"]["identifier"], "MIT")
        self.assertIn("modelLicense", gaddy)

    def test_split_rules_accept_separated_sessions_and_reject_leakage(self):
        valid = json.loads((ROOT / "examples/split-manifest.json").read_text())
        self.assertEqual(split_rules.validate_manifest(valid), [])
        leaked = json.loads(json.dumps(valid))
        leaked["records"].append({"recordId": "synthetic-r005", "subjectId": "synthetic-p01", "sessionId": "synthetic-s01", "split": "test"})
        self.assertTrue(any("session leakage" in error for error in split_rules.validate_manifest(leaked)))


if __name__ == "__main__":
    unittest.main()
