"""Exact replay and periodic extraction audit for fresh evidence."""
import argparse,json,time
import numpy as np
from evoloop.engine import ROOT,RULE_HASH,advance,digest
from evoloop.periodic_tracking import detect
from scripts.atlas import write_json

def generation_check(npz,report):
    a=np.load(npz)
    if 'initial_hash' not in report:
        assert report['status']=='ineligible_component_size' and not a.files;return
    g=a['initial'].copy();assert digest(g)==report['initial_hash']
    for child_idx,child in enumerate(report['children']):
        selected=a[f'selection_grid{child_idx}'];raw=a['initial'].copy();advance(raw,child['detached_t'])
        assert np.array_equal(raw,selected)
        found=next(o for o in detect(selected) if o['core']==child['core'] and o['genotype']==child['identity'])
        assert np.array_equal(found['isolation_snapshot'],a[f'child{child_idx}'])
        assert digest(a[f'child{child_idx}'])==child['snapshot_hash']
    advance(g,report['completed_updates']);assert np.array_equal(g,a['final']);assert digest(g)==report['final_hash']

def panel():
    out=ROOT/'data/panel-v2';m=json.loads((out/'manifest.json').read_text());d=json.loads((out/'discovery.json').read_text());start=time.perf_counter();stages=0;sources=0
    for h in d['histories']:
        g=np.load(out/f'{h["id"]}-initial.npz')['grid'].copy();spec=next(x for x in m['histories'] if x['id']==h['id']);assert digest(g)==spec['initial_hash']
        advance(g,h['completed_updates']);assert digest(g)==h['final_hash'];assert np.array_equal(g,np.load(out/f'{h["id"]}-world.npz')['final'])
    for trial in d['trials']:
        folder=out/'trials'/trial['trial'];a=np.load(folder/'source.npz');source=trial['source'];g=a['source_grid']
        if 'source_hash' in source:assert digest(g)==source['source_hash']
        if 'core' in source:
            o=next(o for o in detect(g) if o['core']==source['core'] and o['genotype']==trial['native_identity'])
            assert np.array_equal(o['isolation_snapshot'],a['snapshot']);sources+=1
        for k,r in enumerate(trial['stages'],1):generation_check(folder/f'g{k}.npz',r);stages+=1
    report={'experiment_id':m['experiment_id'],'rule_hash':RULE_HASH,'native_histories_replayed':len(d['histories']),'source_extractions_checked':sources,'generation_states_replayed':stages,'mismatches':0,'seconds':time.perf_counter()-start}
    write_json(out/'verification.json',report);print(json.dumps(report),flush=True)

def atlas():
    out=ROOT/'data/atlas-v2';m=json.loads((out/'manifest.json').read_text());i=json.loads((out/'inheritance.json').read_text());start=time.perf_counter();stages=0
    # Three deterministic trajectories, chosen by fixed split/treatment then run-ID.
    chosen=[next(r for r in sorted(m['runs'],key=lambda r:r['run_id']) if r['treatment']==t and (t=='alone' or r['split']==s)) for t,s in [('near','main'),('near','heldout'),('separated','main'),('alone','control')]]
    replay=[]
    from scripts.accelerated_atlas import compiled_contact
    from evoloop.tracking import contact
    for spec in chosen:
        folder=out/'runs'/spec['run_id'];r=json.loads((folder/'result.json').read_text());a=np.load(out/'initial'/f'{spec["run_id"]}.npz');g=a['grid'].copy();lab=a['labels'].copy();first=None
        for t in range(m['config']['horizon']+1):
            if t:advance(g,1,lab)
            found=compiled_contact(g,lab)
            if t%10==0:assert found==contact(g,lab)
            if first is None and found:first=t
        assert first==r['contact_t'];assert digest(g)==r['final_hash'];assert digest(lab)==r['final_labels_hash'];replay.append({'run_id':spec['run_id'],'contact_t':first,'final_hash':digest(g)})
    for item in i['items']:
        folder=out/'runs'/item['run_id']
        r=json.loads((folder/'result.json').read_text());c=next(c for c in r['candidates'] if c['genotype']==item['encounter_genotype'])
        for snap in c['snapshots']:
            a=np.load(folder/snap['file']);g=a['source_grid'];o=next(o for o in detect(g) if o['core']==snap['core'] and o['genotype']==c['genotype'])
            assert np.array_equal(o['isolation_snapshot'],a['snapshot']);assert digest(a['snapshot'])==snap['snapshot_hash']
        for outcome in item['outcomes']:
            p=out/outcome['folder']
            for node in outcome['nodes']:
                report=node['outcome']
                if 'initial_hash' in report:generation_check(p/f'node-{node["node"]:02d}.npz',report);stages+=1
    report={'experiment_id':m['experiment_id'],'rule_hash':RULE_HASH,'full_trajectories':replay,'generation_states_replayed':stages,'mismatches':0,'seconds':time.perf_counter()-start}
    write_json(out/'verification.json',report);print(json.dumps(report),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['panel','atlas']);a=p.parse_args();{'panel':panel,'atlas':atlas}[a.command]()
