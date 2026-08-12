from __future__ import annotations

from copy import deepcopy
import unittest

from realtime.app.evaluation_protocol import (
    complete_outcome_counts,
    deterministic_rank,
    load_protocol,
    plan_disjoint_cohorts,
    public_plan,
    validate_protocol,
)


class EvaluationProtocolTests(unittest.TestCase):
    def test_protocol_is_no_result_no_execution_and_unknown_overlap(self):
        protocol = load_protocol()
        self.assertEqual(protocol["status"], "protocol_only_no_results")
        self.assertFalse(protocol["execution_authorized"])
        self.assertIsNone(protocol["results"])
        self.assertIn("unknown", protocol["source_scope"]["training_overlap"].lower())
        summary = public_plan(protocol)
        self.assertEqual(summary["status"], "PROTOCOL ONLY · NO RESULTS")
        self.assertFalse(summary["execution_authorized"])
        serialized = str(summary).lower()
        for forbidden in ("accuracy result", "held-out performance", "project wer"):
            self.assertNotIn(forbidden, serialized)

    def test_synthetic_selection_is_deterministic_output_blind_and_disjoint(self):
        synthetic_ids = tuple(f"synthetic-{index:02d}" for index in range(12))
        first = deterministic_rank(synthetic_ids, "fixed-seed")
        second = deterministic_rank(reversed(synthetic_ids), "fixed-seed")
        self.assertEqual(first, second)
        cohorts = plan_disjoint_cohorts(
            synthetic_ids, seed="fixed-seed", development_count=4, evaluation_count=5
        )
        self.assertEqual(len(cohorts["development"]), 4)
        self.assertEqual(len(cohorts["evaluation"]), 5)
        self.assertFalse(set(cohorts["development"]) & set(cohorts["evaluation"]))
        with self.assertRaises(ValueError):
            deterministic_rank(("duplicate", "duplicate"), "fixed-seed")

    def test_denominator_retains_abstentions_errors_and_asset_failures(self):
        selected = ("synthetic-a", "synthetic-b", "synthetic-c", "synthetic-d")
        counts = complete_outcome_counts(selected, {
            "synthetic-a": "executed",
            "synthetic-b": "abstained",
            "synthetic-c": "error",
            "synthetic-d": "asset_failure",
        })
        self.assertEqual(counts, {
            "abstained": 1,
            "asset_failure": 1,
            "error": 1,
            "executed": 1,
            "total": 4,
        })
        with self.assertRaises(ValueError):
            complete_outcome_counts(selected, {"synthetic-a": "executed"})

    def test_protocol_rejects_results_overlap_claim_and_post_freeze_replacement(self):
        protocol = load_protocol()
        for mutation in ("results", "overlap", "replacement"):
            broken = deepcopy(protocol)
            if mutation == "results":
                broken["results"] = {"accuracy": 1.0}
            elif mutation == "overlap":
                broken["source_scope"]["training_overlap"] = "held out"
            else:
                broken["selection"]["replacement_after_freeze"] = "allowed"
            with self.assertRaises(ValueError):
                validate_protocol(broken)


if __name__ == "__main__":
    unittest.main(verbosity=2)
