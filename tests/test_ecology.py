import unittest

import numpy as np

from evoloop.ecology import prepared_grid, observation, remove_block, chosen_cores, strict_advantage, panel_summary
from evoloop.engine import ROOT, advance, place


class EcologicalContract(unittest.TestCase):
    def test_registered_alias_count_and_centered_rotation(self):
        snapshot = np.load(ROOT/'data/panel-v2/V01.npz')['snapshot']
        for rotation in range(4):
            g = prepared_grid(snapshot, [192,192], rotation)
            _, records, loops = observation(g, [])
            gt = records[0]['identity']
            counts, _, _ = observation(g, [gt, gt])
            self.assertEqual(counts['scored_cores'], 1)
            self.assertEqual(counts['closed_cores'], 1)
            self.assertEqual(len(chosen_cores(loops, True, [gt])), 1)
            a = np.rot90(snapshot, rotation); expected = np.zeros_like(g)
            place(expected, a, 96-a.shape[0]//2, 96-a.shape[1]//2)
            self.assertTrue(np.array_equal(g, expected))

    def test_intervention_after_update_and_replay(self):
        snapshot = np.load(ROOT/'data/panel-v2/V02.npz')['snapshot']
        initial = prepared_grid(snapshot, [192,192], 0)
        actual = initial.copy(); advance(actual, 600)
        before, impact = remove_block(actual, [80,80], 24)
        oracle = initial.copy(); advance(oracle, 600)
        self.assertTrue(np.array_equal(before, oracle))
        self.assertEqual(impact['removed_occupied_cells'], int(np.count_nonzero(oracle[80:104,80:104])))
        oracle[80:104,80:104] = 0
        self.assertTrue(np.array_equal(actual, oracle))
        advance(actual, 20); advance(oracle, 20)
        self.assertTrue(np.array_equal(actual, oracle))

    def test_ties_and_both_parent_comparison(self):
        self.assertFalse(strict_advantage(2, [2,1]))
        self.assertFalse(strict_advantage(2, [1,3]))
        self.assertTrue(strict_advantage(2, [1,1.9]))

    def test_equal_exact_panel_totals_do_not_create_float_advantage(self):
        a = panel_summary([0,42]); b = panel_summary([1,41])
        self.assertEqual(a['mean'], b['mean'])
        self.assertEqual(a['sample_count'], 162)
        self.assertFalse(strict_advantage(a['score_sum'], [b['score_sum'], 40]))


if __name__ == '__main__':
    unittest.main()
