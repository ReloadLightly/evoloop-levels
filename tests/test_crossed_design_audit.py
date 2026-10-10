"""Small synthetic checks for crossed design audit, without CA responses."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from scripts import verify_crossed_design as auditor


class CrossedDesignAuditTests(unittest.TestCase):
    def test_complete_rotation_translation_recovers_an_exact_state(self):
        source = np.zeros((12, 12), np.uint8)
        source[2, 3:6] = [1, 2, 3]
        source[3:5, 3] = [4, 5]
        target = np.roll(np.rot90(source, 3), (7, 9), (0, 1))
        transform = auditor.transform_equivalence(source, target)
        self.assertIsNotNone(transform)
        recreated = np.roll(np.rot90(source, transform['rotation']), transform['translation'], (0, 1))
        self.assertTrue(np.array_equal(recreated, target))

    def test_same_histogram_and_reflection_do_not_imply_effective_equivalence(self):
        source = np.zeros((12, 12), np.uint8)
        source[2, 3:6] = [1, 2, 3]
        source[3:5, 3] = [4, 5]
        self.assertIsNone(auditor.transform_equivalence(source, np.fliplr(source)))
        target = source.copy()
        target[4, 3], target[2, 5] = target[2, 5], target[4, 3]
        self.assertIsNone(auditor.transform_equivalence(source, target))

    def test_zero_state_is_equivalent_but_different_shape_is_not(self):
        source = np.zeros((8, 8), np.uint8)
        self.assertEqual(auditor.transform_equivalence(source, source.copy()),
                         {'rotation': 0, 'translation': [0, 0]})
        self.assertIsNone(auditor.transform_equivalence(source, np.zeros((9, 9), np.uint8)))

    def test_direct_placement_keeps_arms_and_exact_one_third_cells(self):
        component = np.array([[0, 1, 0], [4, 7, 1], [0, 1, 0]], np.uint8)
        geometry = {'sites': [[3, 3], [3, 12], [12, 3]], 'remove_index': 1}
        before, after, mask = auditor.direct_placement(component, [1, 1], geometry, [20, 20])
        self.assertEqual(np.count_nonzero(before), 3 * np.count_nonzero(component))
        self.assertEqual(np.count_nonzero(after), 2 * np.count_nonzero(component))
        self.assertEqual(int(mask.sum()), np.count_nonzero(component))
        np.testing.assert_array_equal(before[2:5, 2:5], component)
        np.testing.assert_array_equal(after[2:5, 2:5], component)
        np.testing.assert_array_equal(after[2:5, 11:14], np.zeros((3, 3), np.uint8))
        occupied_before = np.bincount(before[before != 0], minlength=9)
        removed = np.bincount(before[mask != 0], minlength=9)
        np.testing.assert_array_equal(occupied_before, 3 * removed)

    def test_overlap_disconnected_residual_and_clipped_arm_are_rejected(self):
        component = np.array([[1, 1], [0, 4]], np.uint8)
        with self.assertRaises(AssertionError):
            auditor.direct_placement(component, [0, 0], {'sites': [[2, 2], [2, 2], [9, 9]], 'remove_index': 0}, [12, 12])
        with self.assertRaises(AssertionError):
            auditor.direct_placement(component, [0, 0], {'sites': [[2, 2], [2, 8], [11, 11]], 'remove_index': 0}, [12, 12])
        residual = np.array([[1, 0, 4]], np.uint8)
        with self.assertRaises(AssertionError):
            auditor.direct_placement(residual, [0, 0], {'sites': [[2, 2], [2, 8], [8, 2]], 'remove_index': 0}, [12, 12])

    def test_complete_crossing_and_caps_derived_from_measure(self):
        cfg = json.loads((auditor.ROOT / 'configs/crossed-v1.json').read_text())
        measure = json.loads((auditor.ROOT / 'configs/developmental-v1.json').read_text())
        specs = auditor.cartesian_specs(cfg)
        self.assertEqual(len(specs), 160)
        self.assertEqual(len({s['run_id'] for s in specs}), 160)
        self.assertEqual(len({s['pair_id'] for s in specs}), 80)
        self.assertEqual(auditor.cap_contract(cfg, measure), cfg['limits'])
        self.assertEqual(cfg['limits']['maximum_generation_simulations_including_controls'], 492312)

    def test_memory_stop_is_recorded_as_interruption(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            with patch.object(auditor, 'OUT', out), patch.object(auditor, 'audit',
                    side_effect=auditor.MemoryHeadroomError('synthetic stop')):
                with self.assertRaises(SystemExit) as caught:
                    auditor.main()
            report = json.loads((out / 'design-integrity.json').read_text())
            self.assertEqual(caught.exception.code, 75)
            self.assertEqual(report['status'], 'interrupted')
            self.assertEqual(report['mismatches'], 0)


if __name__ == '__main__':
    unittest.main()
