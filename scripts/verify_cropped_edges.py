"""Exact true-edge and seam fallback supplement to cropped measurement proof."""
import hashlib
import json
import numpy as np
from evoloop.engine import ROOT,place,seed13,digest
from evoloop.periodic_tracking import detect as reference
from evoloop.cropped_tracking import detect as cropped
from scripts.verify_cropped_tracking import equal,OUT
from scripts.atlas import write_json


def main():
    samples=[seed13(),np.load(ROOT/'data/exploration/N01.npz')['snapshot']]
    samples += [np.load(ROOT/f'data/panel-v2/V{k:02d}.npz')['snapshot'] for k in range(1,4)]
    cases=[]
    for number,snap in enumerate(samples):
        for rotation in range(4):
            a=np.rot90(snap,rotation)
            for margin in (0,1,2,4):
                top=margin;bottom=192-a.shape[0]-margin
                left=margin;right=192-a.shape[1]-margin
                for y,x in ((top,60),(bottom,60),(60,left),(60,right),
                            (top,left),(bottom,right)):
                    grid=np.zeros((192,192),np.uint8);place(grid,a,y,x)
                    original=grid.copy();expected=reference(grid);actual=cropped(grid)
                    equal(expected,actual);assert np.array_equal(grid,original)
                    cases.append({'sample':number,'rotation':rotation,'placement':[y,x],
                        'margin':margin,'grid_hash':digest(grid),
                        'occupied_global_edge':bool(np.any(grid[[0,-1]]) or np.any(grid[:,[0,-1]]))})
    completed=[]
    for path in sorted((ROOT/'data/atlas-v2/runs').glob('*/result.json')):
        result=json.loads(path.read_text());grid=np.load(path.parent/'final.npz')['grid']
        assert digest(grid)==result['final_hash'];equal(reference(grid),cropped(grid))
        completed.append({'run_id':result['run_id'],'final_hash':digest(grid),
            'occupied_global_edge':bool(np.any(grid[[0,-1]]) or np.any(grid[:,[0,-1]]))})
    names=['scripts/verify_cropped_edges.py','scripts/verify_cropped_tracking.py',
           'evoloop/cropped_tracking.py','evoloop/periodic_tracking.py','evoloop/tracking.py']
    OUT.mkdir(exist_ok=True)
    report={'experiment_id':'EXP-measurement-crop-verification-001',
            'source_hashes':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in names},
            'true_edge_cases':cases,'completed_final_checks':completed,'mismatches':0,
            'completed_edge_final_count':sum(c['occupied_global_edge'] for c in completed),
            'completed_nonedge_final_count':sum(not c['occupied_global_edge'] for c in completed)}
    write_json(OUT/'edge-verification.json',report)
    print(json.dumps({k:v for k,v in report.items() if k not in ('source_hashes','true_edge_cases','completed_final_checks')}),flush=True)


if __name__=='__main__':main()
