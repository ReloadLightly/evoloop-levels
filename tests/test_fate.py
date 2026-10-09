"""Search-budget and transmission bookkeeping, using mock trees, not CA evidence."""
import unittest
import numpy as np
from evoloop.fate import expanded_search

class FateSearchTests(unittest.TestCase):
    def search(self, edges, identities, cap=24, depth=6):
        cfg={'max_generation_simulations_per_root':cap,'max_depth':depth,'stable_transmissions':2}
        def generation(snap,cfg):
            key=int(snap[0,0]);children=[];arrays={}
            for i,child in enumerate(edges.get(key,[])):
                children.append({'identity':identities[child],'detached_t':10+i,'core':[i,0,1,1],
                                 'snapshot_hash':str(child),'size_eligible':True})
                arrays[f'child{i}']=np.array([[child]],dtype=np.uint8)
            return {'children':children},arrays
        return expanded_search(np.array([[0]],dtype=np.uint8),identities[0],cfg,
                               lambda gt:gt=='B',lambda node,arrays:None,generation)

    def test_failed_first_sibling_does_not_hide_stable_second_path(self):
        r=self.search({0:[1,2],2:[3],3:[4]}, {0:'R',1:'A',2:'B',3:'B',4:'B'})
        self.assertEqual(r['status'],'confirmed')
        self.assertEqual(r['confirmation']['path'],[1,0,0])
        self.assertEqual(r['generation_simulations'],4)

    def test_budget_exhaustion_remains_unresolved(self):
        r=self.search({0:[1,2],2:[3],3:[4]}, {0:'R',1:'A',2:'B',3:'B',4:'B'},cap=2)
        self.assertEqual(r['status'],'unresolved')
        self.assertEqual(r['generation_simulations'],2)
        self.assertTrue(any(z['reason']=='simulation_budget' for z in r['truncations']))

    def test_changed_identity_resets_stable_transmission_streak(self):
        edges={0:[1],1:[2],2:[3],3:[4],4:[5]};ids={0:'R',1:'A',2:'A',3:'B',4:'B',5:'B'}
        self.assertEqual(self.search(edges,ids,depth=4)['status'],'unresolved')
        r=self.search(edges,ids,depth=5)
        self.assertEqual(r['status'],'confirmed')
        self.assertEqual(r['confirmation']['transmission_streak'],2)

if __name__=='__main__':unittest.main()
