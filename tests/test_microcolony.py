import unittest
from fractions import Fraction
import numpy as np
from evoloop.engine import ROOT
from evoloop.microcolony import phase_patch,assemble,equivalent,retention_panel
from evoloop.periodic_tracking import detect

class MicrocolonyTests(unittest.TestCase):
    def test_exact_ratios_are_not_pooled_and_ties_are_exact(self):
        self.assertEqual(retention_panel([(1,2),(9,10)]),Fraction(7,10))
        self.assertNotEqual(retention_panel([(1,2),(9,10)]),Fraction(10,12))
        self.assertIsNone(retention_panel([(1,0),(9,10)]))
        self.assertFalse(retention_panel([(1,3),(2,3)])>Fraction(1,2))

    def test_all_cells_anchored_and_fraction_removed(self):
        with np.load(ROOT/'data/ecological-v1/snapshots.npz') as s: snap=s['V01']
        from evoloop.ecology import prepared_grid
        identity=detect(prepared_grid(snap,[192,192],0))[0]['genotype']
        grid,patch,offset=phase_patch(snap,100,[192,192],identity)
        before,after,mask,impact=assemble(patch,offset,[[55,45],[83,115],[140,72]],1,[192,192],[identity])
        self.assertEqual(np.count_nonzero(before),3*np.count_nonzero(patch))
        self.assertEqual(np.count_nonzero(after),2*np.count_nonzero(patch))
        np.testing.assert_array_equal(before[mask==0],after[mask==0])
        self.assertTrue(impact['matched_impact'])

    def test_equivalence_detects_seam_rotation_and_rejects_changed_geometry(self):
        a=np.zeros((16,16),np.uint8);a[1,1]=1;a[2,4]=2;a[9,8]=3
        b=np.roll(np.rot90(a,3),(7,11),(0,1))
        self.assertIsNotNone(equivalent(a,b))
        b[tuple(np.argwhere(b==3)[0])]=0;b[0,0]=3
        self.assertIsNone(equivalent(a,b))

if __name__=='__main__':unittest.main()
