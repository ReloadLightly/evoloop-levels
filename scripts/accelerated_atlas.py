"""Resume frozen atlas with a verified read-only contact diagnostic accelerator.

The original frozen runner, physics, labels, configurations, and endpoint
definitions remain unchanged. This replaces only the NumPy diagnostic's scan.
The implementation-equivalence check and source hashes are recorded before use.
"""
import ctypes
import hashlib
import itertools
import json
import subprocess
import time
import numpy as np
from evoloop.engine import ROOT,advance
from evoloop.tracking import contact as numpy_contact
from scripts import atlas

SRC=ROOT/'evoloop/contact_scan.c';LIB=SRC.with_suffix('.so')
if not LIB.exists() or LIB.stat().st_mtime < SRC.stat().st_mtime:
    subprocess.run(['gcc','-O3','-std=c99','-shared','-fPIC',str(SRC),'-o',str(LIB)],check=True)
scan=ctypes.CDLL(str(LIB)).contact_scan
PTR=ctypes.POINTER(ctypes.c_uint8)
scan.argtypes=[PTR,PTR,ctypes.c_int,ctypes.c_int];scan.restype=ctypes.c_int

def compiled_contact(grid,labels):
    return bool(scan(grid.ctypes.data_as(PTR),labels.ctypes.data_as(PTR),*grid.shape))

def verify():
    cases=0
    # All occupancy/provenance choices for an adjacent pair, including torus seams.
    for occ1,occ2,label1,label2 in itertools.product(range(2),range(2),range(4),range(4)):
        for positions in [((1,1),(1,2)),((1,0),(1,4)),((0,1),(4,1)),((1,1),(3,3))]:
            g=np.zeros((5,5),dtype=np.uint8);lab=np.zeros_like(g)
            g[positions[0]]=occ1;g[positions[1]]=occ2;lab[positions[0]]=label1;lab[positions[1]]=label2
            assert numpy_contact(g,lab)==compiled_contact(g,lab);cases+=1
    rng=np.random.default_rng(73001)
    for _ in range(100):
        g=rng.integers(0,9,(17,19),dtype=np.uint8);lab=rng.integers(0,4,g.shape,dtype=np.uint8)
        assert numpy_contact(g,lab)==compiled_contact(g,lab);cases+=1
    m=atlas.load_manifest();selected=[r for r in m['runs'] if r['treatment']=='near'][:3]
    selected += [r for r in m['runs'] if r['treatment']=='separated'][:1]
    trajectories=[]
    for r in selected:
        a=np.load(atlas.OUT/'initial'/f'{r["run_id"]}.npz');g=a['grid'].copy();lab=a['labels'].copy();first=None
        for t in range(m['config']['horizon']+1):
            if t:advance(g,1,lab)
            assert numpy_contact(g,lab)==compiled_contact(g,lab);cases+=1
            if first is None and compiled_contact(g,lab):first=t
        result=json.loads((atlas.OUT/'runs'/r['run_id']/'result.json').read_text())
        assert first==result['contact_t']
        trajectories.append({'run_id':r['run_id'],'matched_contact_t':first,'updates_compared':1601})
    a=np.load(atlas.OUT/'initial'/f'{selected[-1]["run_id"]}.npz');g=a['grid'];lab=a['labels']
    timing={}
    for name,fn in [('numpy',numpy_contact),('compiled',compiled_contact)]:
        start=time.perf_counter()
        for _ in range(100):fn(g,lab)
        timing[name+'_seconds_100_calls']=time.perf_counter()-start
    report={'equivalent_cases':cases,'mismatches':0,'raw_trajectories':trajectories,'benchmark':timing,
            'scope':'read-only contact diagnostic; original scientific definitions and CA unchanged',
            'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),
            'runner_sha256':hashlib.sha256((ROOT/'scripts/accelerated_atlas.py').read_bytes()).hexdigest()}
    atlas.write_json(atlas.OUT/'contact_accelerator_verification.json',report)
    print(json.dumps(report,indent=2),flush=True)

def main():
    verify()
    completed=[p.parent.name for p in (atlas.OUT/'runs').glob('*/result.json')]
    atlas.write_json(atlas.OUT/'execution.json',{'unchanged_frozen_runner':'scripts/atlas.py',
                                              'diagnostic_accelerator':'scripts/accelerated_atlas.py',
                                              'original_completed_runs':sorted(completed),
                                              'equivalence_evidence':'contact_accelerator_verification.json'})
    atlas.contact=compiled_contact
    atlas.run()

if __name__=='__main__':main()
