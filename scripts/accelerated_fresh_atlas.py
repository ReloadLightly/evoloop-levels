"""Verified equivalent tiled execution of an unchanged frozen experiment."""
import argparse,hashlib,itertools,json,time
import numpy as np
from evoloop.engine import ROOT,LUT,advance as reference,digest,RULE_HASH
from evoloop.tiled_engine import advance as tiled
from scripts import fresh_atlas as atlas
from scripts.atlas import write_json
FILES=['evoloop/tiled_kernel.c','evoloop/tiled_engine.py','scripts/accelerated_fresh_atlas.py']
def hashes():return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in FILES}

def verify():
    start=time.perf_counter();cases=0
    # Every local transition, plus all other simultaneous sites on a small torus.
    for states in itertools.product(range(9),repeat=5):
        g=np.zeros((5,5),np.uint8)
        for pos,v in zip(((2,2),(1,2),(2,3),(3,2),(2,1)),states):g[pos]=v
        a=g.copy();b=g.copy();reference(a,1);tiled(b,1);assert np.array_equal(a,b)
        index=0
        for v in states:index=index*9+v
        assert b[2,2]==LUT[index];cases+=1
    rng=np.random.default_rng(20261010);random_checks=0
    for shape in [(5,5),(17,19),(32,48),(160,160),(192,192),(640,640)]:
        for density in [0,.0005,.01,1]:
            g=rng.integers(1,9,shape,dtype=np.uint8);g[rng.random(shape)>density]=0
            labels=rng.integers(0,4,shape,dtype=np.uint8);labels[g==0]=0
            a=g.copy();b=g.copy();la=labels.copy();lb=labels.copy()
            for _ in range(20):
                reference(a,1,la);tiled(b,1,lb)
                assert np.array_equal(a,b) and np.array_equal(la,lb);random_checks+=1
    m=atlas.load_manifest();done=[r for r in m['runs'] if (atlas.OUT/'runs'/r['run_id']/'result.json').exists() and r['treatment']=='near' and r['split']=='main']
    # Fixed run-ID choice from completed original execution; candidates not used for selection.
    chosen=sorted(done,key=lambda r:r['run_id'])[:2];assert len(chosen)==2
    trajectories=[]
    for r in chosen:
        a=np.load(atlas.OUT/'initial'/f'{r["run_id"]}.npz');g=a['grid'].copy();lab=a['labels'].copy();fast=g.copy();flab=lab.copy()
        for t in range(m['config']['horizon']+1):
            if t:reference(g,1,lab);tiled(fast,1,flab)
            assert np.array_equal(g,fast) and np.array_equal(lab,flab)
        result=json.loads((atlas.OUT/'runs'/r['run_id']/'result.json').read_text());assert digest(fast)==result['final_hash'];assert digest(flab)==result['final_labels_hash']
        trajectories.append({'run_id':r['run_id'],'updates_compared':1601,'final_hash':digest(fast),'final_labels_hash':digest(flab)})
    a=np.load(atlas.OUT/'initial'/f'{chosen[0]["run_id"]}.npz');timings={}
    for name,fn in [('reference',reference),('tiled',tiled)]:
        g=a['grid'].copy();lab=a['labels'].copy();s=time.perf_counter();fn(g,200,lab);timings[name+'_seconds_200_updates']=time.perf_counter()-s
    report={'experiment_id':m['experiment_id'],'rule_hash':RULE_HASH,'local_transition_cases':cases,'random_step_checks':random_checks,'full_trajectories':trajectories,'mismatches':0,
        'optimization_hashes':hashes(),'benchmark':timings,'seconds':time.perf_counter()-start,'scope':'synchronous implementation equivalence; no changed scientific states, endpoints, or search budgets'}
    write_json(atlas.OUT/'tiled_verification.json',report);print(json.dumps(report,indent=2),flush=True)

def run():
    report=json.loads((atlas.OUT/'tiled_verification.json').read_text());assert report['optimization_hashes']==hashes();assert report['mismatches']==0 and report['rule_hash']==RULE_HASH
    completed=sorted(p.parent.name for p in (atlas.OUT/'runs').glob('*/result.json'))
    write_json(atlas.OUT/'execution.json',{'experiment_id':'EXP-atlas-002','unchanged_frozen_runner':'scripts/fresh_atlas.py','optimization_hashes':hashes(),
        'equivalence_evidence':'tiled_verification.json','original_completed_runs':completed,'optimized_run_ids':[r['run_id'] for r in atlas.load_manifest()['runs'] if r['run_id'] not in completed],
        'remaining_execution':'equivalent tiled stepping; original contact and measurements'})
    atlas.advance=tiled;atlas.run()
def inherit():
    report=json.loads((atlas.OUT/'tiled_verification.json').read_text());assert report['optimization_hashes']==hashes();assert report['mismatches']==0
    atlas.load_manifest()
    from evoloop import periodic_assays
    periodic_assays.advance=tiled
    path=atlas.OUT/'execution.json';record=json.loads(path.read_text()) if path.exists() else {}
    record['inheritance_stepping']='same verified tiled implementation';record['inheritance_optimization_hashes']=hashes();write_json(path,record)
    atlas.inherit()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['verify','run','inherit']);a=p.parse_args();{'verify':verify,'run':run,'inherit':inherit}[a.command]()
