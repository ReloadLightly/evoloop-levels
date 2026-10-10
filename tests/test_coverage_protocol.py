"""Check scientific panel completeness and frozen-input mutation detection."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.coverage_protocol import ROOT, CONFIG, validate_config, verify, freeze


class CoverageFreezeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads((ROOT / CONFIG).read_text())
        cls.source = json.loads((ROOT / cls.config["source_manifest"]).read_text())

    def test_missing_treatment_or_unknown_class_rejected(self):
        for section, key, value in ((None, "treatments", ["D"]),
                                    ("sampling", "classes", ["scored", "valid_unregistered"])):
            cfg = copy.deepcopy(self.config)
            (cfg if section is None else cfg[section])[key] = value
            with self.assertRaises(ValueError):
                validate_config(cfg, self.source)

    def test_incomplete_continuation_or_understated_budget_rejected(self):
        for section, key, value in (("native", "maximum_world_update", 1600),
                                    ("limits", "maximum_generation_simulations", 25920)):
            cfg = copy.deepcopy(self.config)
            cfg[section][key] = value
            with self.assertRaises(ValueError):
                validate_config(cfg, self.source)

    def test_frozen_manifest_and_every_bound_file_verify(self):
        receipt = verify()
        self.assertEqual(len(receipt["runs"]), 40)
        self.assertEqual(len(receipt["phase_controls"]), 30)

    def test_input_hash_mutation_rejected(self):
        from scripts import coverage_protocol
        actual_sha = coverage_protocol.sha
        altered = ROOT / "data/impact-v1/initial/V01-development-0-D.npz"
        with patch.object(coverage_protocol, "sha",
                          side_effect=lambda p: "0" * 64 if p == altered else actual_sha(p)):
            with self.assertRaisesRegex(ValueError, "bound source files changed"):
                verify()

    def test_existing_freeze_never_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            minimal = {"config": {"output": "data/coverage-v1"}}
            target = root / "data/coverage-v1/manifest.json"
            target.parent.mkdir(parents=True)
            target.write_text("preserve exact original bytes\n")
            with patch("scripts.coverage_protocol.build_manifest", return_value=minimal):
                with self.assertRaisesRegex(ValueError, "preserve frozen design"):
                    freeze(root)
            self.assertEqual(target.read_text(), "preserve exact original bytes\n")


if __name__ == "__main__":
    unittest.main()
