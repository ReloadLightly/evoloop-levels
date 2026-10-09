"""Exhaustive local comparison, grid oracle, replay, resume and benchmarks."""
import itertools
import json
import platform
import resource
import tempfile
import time
from pathlib import Path
import numpy as np
from evoloop.engine import advance, LUT, RULE_HASH, digest, seed13, place, checkpoint, resume, ROOT
from evoloop.vendor.evoloop import Evoloop
from evoloop.tracking import detect

def main():
    ref=Evoloop()
    mismatches=[]
    for i,(c,t,r,b,l) in enumerate(itertools.product(range(9),repeat=5)):
        n=np.array([[0,t,0],[l,c,r],[0,b,0]])
        if LUT[i] != ref(n,None,0): mismatches.append(i)
    assert not mismatches
    rng=np.random.default_rng(1027)
    a=rng.integers(0,9,(17,19),dtype=np.uint8)
    expected=np.zeros_like(a)
    for y,x in np.ndindex(a.shape):
        expected[y,x]=ref(np.array([[0,a[(y-1)%17,x],0],
                                    [a[y,(x-1)%19],a[y,x],a[y,(x+1)%19]],
                                    [0,a[(y+1)%17,x],0]]),None,0)
    advance(a)
    assert np.array_equal(a,expected)
    a=np.zeros((128,128),dtype=np.uint8);place(a,seed13(),50,30)
    start=a.copy();advance(a,777)
    b=start.copy();advance(b,777);assert np.array_equal(a,b)
    b=start.copy();advance(b,321)
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/'checkpoint.npz';checkpoint(p,b,321,metadata={'check':'resume'})
        b,t,_,meta=resume(p);assert t==321 and meta['check']=='resume'
        advance(b,456);assert np.array_equal(a,b)
    # Sample complete raw snapshots for birth verification, not just cell counts.
    g=start.copy();frames=[];observations=[]
    for t in range(0,1201,10):
        if t: advance(g,10)
        loops=detect(g)
        observations.append({'t':t,'loops':[dict(core=o['core'],genotype=o['genotype']) for o in loops]})
        if t in (0,200,400,600,800,1000,1200):frames.append(g.copy())
    assert max(len(o['loops']) for o in observations)>=3, 'documented seed failed to reproduce'
    np.savez_compressed(ROOT/'data/verification_reproduction.npz',frames=np.array(frames),times=np.arange(0,1201,200))
    g=np.zeros((192,192),dtype=np.uint8);place(g,seed13(),75,60)
    then=time.perf_counter();advance(g,2000);seconds=time.perf_counter()-then
    report={'local_transitions':59049,'reference_mismatches':0,'grid_oracle':'pass',
            'deterministic_replay':'pass','checkpoint_resume':'pass','rule_hash':RULE_HASH,
            'seed_hash':digest(seed13()),'replay_hash_t777':digest(a),
            'reproduction_observations':observations,'benchmark':{'shape':[192,192],'steps':2000,
            'seconds':seconds,'million_cell_updates_per_second':192*192*2000/seconds/1e6,
            'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'platform':platform.platform(),'python':platform.python_version(),'workers':1}}
    (ROOT/'data/verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='reproduction_observations'},indent=2))

if __name__=='__main__': main()
