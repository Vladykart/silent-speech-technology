from __future__ import annotations

from hashlib import md5, sha256
from pathlib import Path
import json
import unittest

from realtime.app.asset_registry import AssetRegistry
from realtime.app.config import ASSET_DIR, MODEL_PATH
from realtime.fetch_assets import extraction_targets
from realtime.generate_release_manifest import verify as verify_release_manifest

ROOT = Path(__file__).resolve().parents[1]
DATASET_ARCHIVE = Path("/root/.local/share/silent-speech-lab/datasets/zenodo-4064408/emg_data.tar.gz")
MODEL_ARCHIVE = ASSET_DIR / "downloads" / "pretrained_models.zip"
PREPARED = MODEL_PATH.is_file() and (ASSET_DIR / "replays" / "QC-R10" / "89_emg.npy").is_file()


def digests(path: Path) -> tuple[str, str]:
    left, right = md5(), sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(4 * 1024 * 1024):
            left.update(chunk); right.update(chunk)
    return left.hexdigest(), right.hexdigest()


class ManifestAuthorityTests(unittest.TestCase):
    def test_asset_model_sample_and_dependency_authorities_are_exact(self):
        assets = json.loads((ROOT / "assets-manifest.json").read_text())
        samples = json.loads((ROOT / "sample-manifest.json").read_text())
        models = json.loads((ROOT / "model-registry.json").read_text())
        evaluation = json.loads((ROOT / "evaluation-protocol.json").read_text())
        self.assertEqual(assets["schema_version"], 2)
        self.assertEqual(assets["model"]["archive"]["sha256"], "be370313ffc53e4d9c118032d7eededd9c807f8b8449fadcb2eb2008379a3f54")
        self.assertEqual(assets["model"]["checkpoint"]["sha256"], "67d40b64f7831ae15c3c24264e2d13cdff98a212953901048d2923b3db60171a")
        self.assertEqual(assets["model"]["checkpoint"]["trainable_parameters"], 54_187_136)
        self.assertEqual(assets["dataset"]["archive"]["sha256"], "1a4b205195185d2972923ed4fdaa71bb51cc01462c6b1ab279ed4d00acbd0089")
        self.assertEqual(assets["dependencies"]["cmudict_python_package"]["license"], "GPL-3.0-or-later")
        self.assertIn("separate", assets["dependencies"]["cmu_pronouncing_dictionary_data"]["license"].lower())
        self.assertTrue(samples["frozen_before_new_execution"])
        self.assertEqual(set(samples["samples"]), {*(f"QC-R{i:02d}" for i in range(1, 11)), "QC-R02-T2"})
        self.assertEqual(samples["samples"]["QC-R02"]["second_take_id"], "QC-R02-T2")
        self.assertEqual(samples["samples"]["QC-R02-T2"]["second_take_of"], "QC-R02")
        self.assertEqual(sum(item["catalogue_card"] for item in samples["samples"].values()), 10)
        self.assertEqual(models["schema_version"], 2)
        readiness_fields = set(models["required_readiness_fields"])
        executed = [item for item in models["entries"] if item["status"] == "executed"]
        evidence = [item for item in models["entries"] if item["status"] == "evidence_only"]
        self.assertEqual([item["id"] for item in executed], ["gaddy-transduction-6747411"])
        self.assertEqual(executed[0]["type"], "checkpoint")
        self.assertTrue(all(executed[0][field] is True for field in ("weights_available", "rights_verified", "checksum_verified", "runtime_approved")))
        self.assertTrue(all(readiness_fields.issubset(item) for item in models["entries"]))
        self.assertTrue(evidence and all(item["badge"] == "NOT EXECUTED HERE" and item["not_executed_reason"] for item in evidence))
        self.assertTrue(all(item["runtime_approved"] is False and item["comparability_notes"] for item in evidence))
        self.assertEqual(evaluation["status"], "protocol_only_no_results")
        self.assertFalse(evaluation["execution_authorized"])
        self.assertIsNone(evaluation["results"])
        decoder = next(item for item in models["entries"] if item["id"] == "project-phoneme-edit-decoder")
        self.assertEqual(decoder["type"], "algorithm")
        self.assertTrue(decoder["not_a_model"])

    def test_extractor_allowlist_is_exact_and_excludes_audio_buttons_and_extra_members(self):
        targets = extraction_targets()
        self.assertEqual(len(targets), 44)
        self.assertEqual(sum(len(values) for values in targets.values()), 44)
        self.assertTrue(all(member.endswith(("_emg.npy", "_info.json")) for member in targets))
        combined = "\n".join(targets).lower()
        for forbidden in ("audio", "button", "cleaned", ".flac", ".wav"):
            self.assertNotIn(forbidden, combined)
        for values in targets.values():
            for public_id, role, digest in values:
                self.assertRegex(public_id, r"^QC-R(?:0[1-9]|10|02-T2)$")
                self.assertIn(role, {"selected", "metadata", "context_before", "context_after"})
                self.assertRegex(digest, r"^[0-9a-f]{64}$")

    def test_release_manifest_binds_runtime_manifests_and_dependency_lock(self):
        release = json.loads((ROOT / "release-manifest.json").read_text())
        self.assertEqual(release["schema_version"], 1)
        self.assertRegex(release["application_revision"], r"^[0-9a-f]{40}$")
        self.assertIn("realtime/app/service.py", release["files"])
        self.assertIn("realtime/client/app.js", release["files"])
        self.assertIn("realtime/evaluation-protocol.json", release["files"])
        self.assertIn("realtime/app/evaluation_protocol.py", release["files"])
        self.assertNotIn("realtime/release-manifest.json", release["files"])
        verify_release_manifest(release)

    def test_notices_separate_cmudict_package_and_data_rights(self):
        notice = (ROOT / "THIRD_PARTY_NOTICES.md").read_text()
        self.assertIn("GPL-3.0-or-later", notice)
        self.assertIn("CMU Pronouncing Dictionary data", notice)
        self.assertNotIn("package supplies pronunciations to the modern bounded phoneme decoder. CMUdict is distributed under a permissive", notice)


@unittest.skipUnless(PREPARED, "prepare approved ignored assets with realtime/fetch_assets.py")
class PreparedAssetTests(unittest.TestCase):
    def test_every_selected_context_and_metadata_member_is_hash_shape_dtype_and_prompt_bound(self):
        registry = AssetRegistry()
        registry.verify_all()
        for sample in registry.samples.values():
            selected = sample.path_for("selected")
            self.assertTrue(selected.is_file())
            self.assertEqual(selected.name, Path(sample.spec["selected"]["member"]).name)

    @unittest.skipUnless(DATASET_ARCHIVE.is_file(), "official dataset archive unavailable")
    def test_dataset_archive_bytes_md5_and_sha256(self):
        assets = json.loads((ROOT / "assets-manifest.json").read_text())
        spec = assets["dataset"]["archive"]
        self.assertEqual(DATASET_ARCHIVE.stat().st_size, spec["bytes"])
        self.assertEqual(digests(DATASET_ARCHIVE), (spec["md5"], spec["sha256"]))

    @unittest.skipUnless(MODEL_ARCHIVE.is_file(), "official model ZIP unavailable")
    def test_model_zip_bytes_md5_and_sha256(self):
        assets = json.loads((ROOT / "assets-manifest.json").read_text())
        spec = assets["model"]["archive"]
        self.assertEqual(MODEL_ARCHIVE.stat().st_size, spec["bytes"])
        self.assertEqual(digests(MODEL_ARCHIVE), (spec["md5"], spec["sha256"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
