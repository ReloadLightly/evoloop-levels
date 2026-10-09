import unittest
import numpy as np
from evoloop.engine import seed13, place, advance
from evoloop.tracking import detect
from evoloop.assays import inheritance

class TrackingTests(unittest.TestCase):
    def test_rotation_spacing_and_complete_extraction(self):
        genotypes=[]
        for r in range(4):
            g=np.zeros((160,160),dtype=np.uint8)
            place(g,seed13(),60,60,r)
            o=detect(g)[0];genotypes.append(o['genotype'])
            self.assertEqual(np.count_nonzero(o['isolation_snapshot']),np.count_nonzero(seed13()))
        self.assertEqual(len(set(genotypes)),1)

    def test_seed_inheritance_after_complete_isolation(self):
        g=np.zeros((192,192),dtype=np.uint8);place(g,seed13(),70,60)
        gt=detect(g)[0]['genotype']
        r,e=inheritance(seed13(),gt)
        self.assertEqual(r['status'],'confirmed')
        self.assertEqual(r['stable_genotype'],gt)
        self.assertGreater(r['generation1']['detached_first_seen_t'],0)
        self.assertGreater(r['generation2']['detached_first_seen_t'],0)

    def test_rectangular_rotation_equivalence(self):
        # This natural rectangular descendant is evidence, not an invented genome.
        from pathlib import Path
        p=Path('data/exploration/N01.npz')
        if not p.exists():self.skipTest('natural variant not yet discovered')
        s=np.load(p)['snapshot']; genotypes=[]
        for r in range(4):
            g=np.zeros((160,160),dtype=np.uint8);place(g,s,60,60,r)
            genotypes.append(detect(g)[0]['genotype'])
        self.assertEqual(len(set(genotypes)),1)

if __name__=='__main__':unittest.main()
