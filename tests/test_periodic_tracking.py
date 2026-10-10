"""Translation, complete-component extraction, and raw deterministic seam checks."""
import unittest
import numpy as np
from evoloop.engine import ROOT,advance,place,seed13,digest
from evoloop.tracking import detect as legacy
from evoloop.periodic_tracking import detect,periodic_view

class PeriodicTests(unittest.TestCase):
    def test_translations_and_replay(self):
        samples=[seed13(),np.load(ROOT/'data/exploration/N01.npz')['snapshot']]
        # A recorded rectangular transient, not an invented organism.
        samples += [np.load(p)['snapshot'] for p in [p for p in sorted((ROOT/'data/atlas/runs').glob('*/candidate-*.npz')) if 'inheritance' not in p.name and 'isolation' not in p.name][:1]]
        for snap in samples:
            base=np.zeros((192,192),np.uint8);place(base,snap,70,70)
            expected=legacy(base);self.assertTrue(expected)
            for dy,dx in ((0,0),(115,0),(0,115),(115,115)):
                g=np.roll(base,(dy,dx),(0,1)).copy();loops=detect(g)
                self.assertEqual(len(loops),len(expected))
                self.assertEqual(sorted(o['genotype'] or '' for o in loops),sorted(o['genotype'] or '' for o in expected))
                for o in loops:
                    if o['isolation_snapshot'] is not None:
                        self.assertEqual(digest(o['isolation_snapshot']),digest(snap))
                        self.assertTrue(np.array_equal(periodic_view(g,o['bbox']),o['snapshot']))
                raw=base.copy();advance(raw,100);advance(g,100)
                self.assertTrue(np.array_equal(g,np.roll(raw,(dy,dx),(0,1))))
                self.assertEqual(sorted(o['genotype'] or '' for o in detect(g)),sorted(o['genotype'] or '' for o in detect(raw)))
    def test_away_exact(self):
        g=np.zeros((192,192),np.uint8);place(g,seed13(),70,70)
        a=legacy(g);b=detect(g)
        self.assertEqual(a[0]['core'],b[0]['core'])
        self.assertEqual(a[0]['extraction_bbox'],b[0]['extraction_bbox'])
        self.assertTrue(np.array_equal(a[0]['isolation_snapshot'],b[0]['isolation_snapshot']))
    def test_shared_across_seam(self):
        g=np.zeros((192,192),np.uint8);s=seed13();place(g,s,70,70)
        place(g,s,70,120)
        g[70,70:121]=2
        translated=np.roll(g,(115,115),(0,1)).copy()
        for grid in (g,translated):
            loops=detect(grid);self.assertEqual(len(loops),2)
            self.assertTrue(all(o['isolation_snapshot'] is None for o in loops))

    def test_winding_component_ineligible(self):
        g=np.zeros((192,192),np.uint8);place(g,seed13(),70,70)
        g[70,:]=2
        loops=detect(g);self.assertEqual(len(loops),1)
        self.assertEqual(loops[0]['extraction_status'],'noncontractible_component')
        self.assertIsNone(loops[0]['isolation_snapshot'])

if __name__=='__main__':unittest.main()
