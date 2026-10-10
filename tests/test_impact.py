import unittest
import numpy as np
from evoloop.engine import ROOT
from evoloop.ecology import prepared_grid
from evoloop.periodic_tracking import detect
from evoloop.impact import complete_mask, removal


class ImpactTests(unittest.TestCase):
    def test_complete_component_removal_across_both_periodic_seams(self):
        with np.load(ROOT/'data/panel-v2/V01.npz') as source:
            initial = prepared_grid(source['snapshot'], [192,192], 0)
        for shift in ((0,0),(92,87),(-88,-93)):
            grid = np.roll(initial,shift,(0,1)); organisms=detect(grid)
            self.assertEqual(len(organisms),1)
            organism=organisms[0]
            np.testing.assert_array_equal(complete_mask(grid,organism),grid!=0)
            after,mask,report=removal(grid,organism,[organism['genotype']])
            self.assertEqual(np.count_nonzero(after),0)
            self.assertEqual(report['registered_before'],1)
            self.assertEqual(report['registered_after'],0)
            np.testing.assert_array_equal(mask,grid!=0)


if __name__ == '__main__': unittest.main()
