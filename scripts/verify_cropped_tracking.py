"""Exact measurement equivalence and speed; writes only a new proof directory.

python -m scripts.verify_cropped_tracking
No scientific batch, frozen file, or existing result is changed. Complete output
order, dictionary keys/scalars, array dtype/shape/bytes, and input preservation
are compared. The proof includes its source hashes and the existing tiled proof.
"""
import hashlib
import json
import resource
import time
import numpy as np
from evoloop.engine import ROOT,RULE_HASH,advance,digest,place,seed13
from evoloop.periodic_tracking import detect as reference
from evoloop.cropped_tracking import detect as cropped
from scripts import fresh_atlas as atlas
from scripts import accelerated_fresh_atlas as tiled_driver
from scripts.atlas import write_json

OUT=ROOT/'data/measurement-crop-verification'
FILES=['evoloop/tracking.py','evoloop/periodic_tracking.py','evoloop/engine.py',
       'evoloop/kernel.c','evoloop/periodic_assays.py','evoloop/fate.py',
       'evoloop/cropped_tracking.py','scripts/verify_cropped_tracking.py',
       'scripts/cropped_fresh_atlas.py']


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def equal(a,b,path='result'):
    assert type(a)==type(b),(path,type(a),type(b))
    if isinstance(a,np.ndarray):
        assert a.dtype==b.dtype and a.shape==b.shape and np.array_equal(a,b),path
    elif isinstance(a,dict):
        assert list(a)==list(b),(path,'dictionary keys/order')
        for key in a:equal(a[key],b[key],path+'.'+key)
    elif isinstance(a,(list,tuple)):
        assert len(a)==len(b),(path,'length')
        for i,(x,y) in enumerate(zip(a,b)):equal(x,y,f'{path}[{i}]')
    else:assert a==b,(path,a,b)


def check(grid):
    original=grid.copy()
    a=reference(grid);b=cropped(grid)
    equal(a,b)
    assert np.array_equal(grid,original),'detector mutated input'


def timings(grid,repetitions=4):
    out={}
    for name,fn in [('reference',reference),('cropped',cropped)]:
        started=time.perf_counter()
        for _ in range(repetitions):fn(grid)
        out[name+'_seconds_per_call']=(time.perf_counter()-started)/repetitions
    out['speedup']=out['reference_seconds_per_call']/out['cropped_seconds_per_call']
    return out


def main():
    started=time.perf_counter();manifest=atlas.load_manifest()
    tiled_proof=atlas.OUT/'tiled_verification.json'
    proof=json.loads(tiled_proof.read_text())
    assert proof['mismatches']==0 and proof['rule_hash']==RULE_HASH
    assert proof['optimization_hashes']==tiled_driver.hashes()
    hashes={name:sha(ROOT/name) for name in FILES}
    rng=np.random.default_rng(20261012);random_cases=0
    for shape in ((7,9),(17,19),(64,80),(192,192),(640,640)):
        for density in (0,.0005,.01,.3,1):
            for edge_mode in ('random','empty_global_edges','compact'):
                g=rng.integers(1,9,shape,dtype=np.uint8)
                g[rng.random(shape)>density]=0
                if edge_mode=='empty_global_edges':g[[0,-1],:]=0;g[:,[0,-1]]=0
                elif edge_mode=='compact':
                    yy,xx=np.indices(shape)
                    g[(yy<shape[0]//3)|(yy>=2*shape[0]//3)|
                      (xx<shape[1]//3)|(xx>=2*shape[1]//3)]=0
                check(g);random_cases+=1
    organism_cases=0
    samples=[seed13(),np.load(ROOT/'data/exploration/N01.npz')['snapshot']]
    samples += [np.load(ROOT/f'data/panel-v2/{pid}.npz')['snapshot']
                for pid in manifest['config']['organisms']]
    # Real body near true edges and across seams; includes translations whose
    # crop clips to a global edge, and full-reference occupied-edge fallbacks.
    for snap in samples:
        base=np.zeros((192,192),np.uint8);place(base,snap,60,60)
        for dy,dx in ((0,0),(-59,0),(0,-59),(-58,-58),(125,0),
                      (0,125),(125,125)):
            check(np.roll(base,(dy,dx),(0,1)).copy());organism_cases+=1
    runs=manifest['runs']
    chosen=[]
    for treatment,split,which in [('near','main',0),('near','main',-1),
                                  ('near','heldout',0),('separated','main',0)]:
        pool=sorted((r for r in runs if r['treatment']==treatment and r['split']==split),
                    key=lambda r:r['run_id'])
        chosen.append(pool[which])
    trajectories=[];benchmarks=[]
    for spec in chosen:
        initial=np.load(atlas.OUT/'initial'/f'{spec["run_id"]}.npz')['grid']
        assert digest(initial)==spec['initial_hash'];g=initial.copy();checks=0
        for t in range(0,manifest['config']['horizon']+1,10):
            if t:advance(g,10)
            check(g);checks+=1
            if t in (0,800,1600):
                benchmarks.append({'run_id':spec['run_id'],'t':t,'grid_hash':digest(g),
                                   'occupied_cells':int(np.count_nonzero(g)),**timings(g)})
        trajectories.append({'run_id':spec['run_id'],'every_tenth_update_checks':checks,
                             'initial_hash':digest(initial),'final_hash':digest(g)})
        print('exact trajectory',spec['run_id'],checks,flush=True)
    completed_finals=[]
    for path in sorted((atlas.OUT/'runs').glob('*/result.json')):
        result=json.loads(path.read_text())
        grid=np.load(path.parent/'final.npz')['grid']
        assert digest(grid)==result['final_hash'];check(grid)
        completed_finals.append({'run_id':result['run_id'],'final_hash':digest(grid)})
    isolation_checks=0
    for path in sorted((ROOT/'data/fate-calibration/runs').glob('*/node-*.npz')):
        arrays=np.load(path)
        for key in ('initial','final'):
            check(arrays[key]);isolation_checks+=1
    assert hashes=={name:sha(ROOT/name) for name in FILES},'sources changed during proof'
    OUT.mkdir(exist_ok=True)
    report={'experiment_id':'EXP-measurement-crop-verification-001','rule_hash':RULE_HASH,
            'source_hashes':hashes,'experiment_manifest_sha256':sha(atlas.OUT/'manifest.json'),
            'tiled_proof_sha256':sha(tiled_proof),'tiled_optimization_hashes':proof['optimization_hashes'],
            'random_cases':random_cases,'translated_organism_cases':organism_cases,
            'trajectories':trajectories,'completed_final_checks':completed_finals,
            'isolation_initial_final_checks':isolation_checks,'benchmarks':benchmarks,
            'mismatches':0,'seconds':time.perf_counter()-started,
            'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'scope':'exact list/dictionary/array equivalence and input preservation; no scientific state or endpoint changes'}
    write_json(OUT/'verification.json',report)
    print(json.dumps({k:v for k,v in report.items() if k not in ('benchmarks','completed_final_checks','source_hashes')},indent=2),flush=True)


if __name__=='__main__':main()
