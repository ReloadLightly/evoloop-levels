"""Freeze, run, and check inheritance in the prospective deterministic atlas.

Run from repository root: python -m scripts.atlas freeze|run|inherit
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time
import numpy as np
from evoloop.engine import ROOT, RULE_HASH, advance, crop, place, digest
from evoloop.tracking import detect, contact
from evoloop.assays import inheritance

OUT=ROOT/'data/atlas'
CFG=ROOT/'configs/atlas-v1.json'

def write_json(p,data):
    p=Path(p);tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(data,indent=2)+'\n');tmp.replace(p)

def code_hashes():
    files=['evoloop/kernel.c','evoloop/engine.py','evoloop/tracking.py','evoloop/assays.py','scripts/atlas.py']
    return {f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files}

def freeze():
    assert not (OUT/'manifest.json').exists(), 'freeze already exists; use a new experiment ID for changes'
    OUT.mkdir(exist_ok=True);(OUT/'initial').mkdir(exist_ok=True)
    cfg=json.loads(CFG.read_text());discovery=json.loads((ROOT/'data/exploration/discovery.json').read_text())
    panel={p['id']:p for p in discovery['panel']}
    phases={};phase_meta=[]
    for pid in cfg['organisms']:
        snap=np.load(ROOT/f'data/exploration/{pid}.npz')['snapshot']
        for phase in sorted(set(cfg['main_phases']+[cfg['heldout_phase']])):
            g=np.zeros((192,192),dtype=np.uint8);place(g,snap,60,60);advance(g,phase)
            loops=detect(g);assert len(loops)==1 and loops[0]['genotype']==panel[pid]['genotype']
            assert not np.any(g[[0,-1],:]) and not np.any(g[:,[0,-1]])
            phases[pid,phase]=crop(g)
            phase_meta.append({'organism':pid,'phase':phase,'hash':digest(crop(g)),'shape':list(crop(g).shape)})
    np.savez_compressed(OUT/'phase_states.npz',**{f'{pid}_p{phase}':s for (pid,phase),s in phases.items()})
    runs=[]
    def add(pid,qid,phase,geo,split,treatment):
        solo=treatment=='alone';far=treatment=='separated'
        shape=cfg['far_shape'] if far else cfg['near_shape']
        g=np.zeros(shape,dtype=np.uint8);lab=np.zeros_like(g)
        sy,sx=(320,140) if far else (192,144)
        a=phases[pid,phase];pbox=place(g,a,sy,sx,0 if not solo else geo['partner_rotation'])
        lab[g!=0]=1
        qbox=None
        if not solo:
            b=phases[qid,phase];qy=sy+geo['dy'];qx=sx+cfg['far_dx'] if far else sx+a.shape[1]+geo['gap']
            rotated=np.rot90(b,geo['partner_rotation'])
            assert qx >= sx+a.shape[1], 'bounding rectangles overlap'
            qbox=place(g,b,qy,qx,geo['partner_rotation'])
            view=lab[qy:qy+rotated.shape[0],qx:qx+rotated.shape[1]];view[rotated!=0]=2
        rid=f'{treatment}-{split}-{pid}-{qid or "none"}-p{phase}-{geo["id"]}'
        np.savez_compressed(OUT/'initial'/f'{rid}.npz',grid=g,labels=lab)
        cores=[]
        for o in detect(g):
            y,x,h,w=o['core'];mask=int(np.bitwise_or.reduce(lab[y-3:y+h+3,x-3:x+w+3].ravel()))
            cores.append({'core':o['core'],'genotype':o['genotype'],'provenance':mask})
        assert len(cores)==(1 if solo else 2)
        assert not contact(g,lab)
        runs.append({'run_id':rid,'focal':pid,'partner':qid,'phase':phase,'geometry':geo,
                     'split':split,'treatment':treatment,'shape':shape,'initial_hash':digest(g),
                     'initial_labels_hash':digest(lab),'initial_cores':cores,'input_boxes':[pbox,qbox]})
    for split,plist,geometries in [('main',cfg['main_phases'],cfg['main_geometries']),
                                 ('heldout',[cfg['heldout_phase']],cfg['heldout_geometries'])]:
        for pid in cfg['organisms']:
            for qid in cfg['organisms']:
                for phase in plist:
                    for geo in geometries:
                        for treatment in ('near','separated'):add(pid,qid,phase,geo,split,treatment)
    for pid in cfg['organisms']:
        for phase in sorted(set(cfg['main_phases']+[cfg['heldout_phase']])):
            for rotation in range(4):
                add(pid,None,phase,{'id':f'r{rotation}','partner_rotation':rotation,'dy':0,'gap':0},'control','alone')
    manifest={'experiment_id':cfg['experiment_id'],'config_sha256':hashlib.sha256(CFG.read_bytes()).hexdigest(),
              'protocol_sha256':hashlib.sha256((ROOT/'protocols/001-encounter-atlas.md').read_bytes()).hexdigest(),
              'rule_hash':RULE_HASH,'code_hashes':code_hashes(),'config':cfg,'panel':panel,
              'phase_states':phase_meta,'runs':runs,'expected_runs':len(runs)}
    write_json(OUT/'manifest.json',manifest)
    print('Frozen',len(runs),'complete starting states; manifest SHA256',hashlib.sha256((OUT/'manifest.json').read_bytes()).hexdigest())

def load_manifest(check_code=True):
    m=json.loads((OUT/'manifest.json').read_text())
    assert m['rule_hash']==RULE_HASH
    assert m['config_sha256']==hashlib.sha256(CFG.read_bytes()).hexdigest(), 'configuration changed after freeze'
    assert m['protocol_sha256']==hashlib.sha256((ROOT/'protocols/001-encounter-atlas.md').read_bytes()).hexdigest(), 'protocol changed after freeze'
    if check_code:assert m['code_hashes']==code_hashes(),'scientific code changed after freeze'
    return m

def run_one(spec,m):
    cfg=m['config'];rid=spec['run_id'];folder=OUT/'runs'/rid;folder.mkdir(parents=True,exist_ok=True)
    initial=np.load(OUT/'initial'/f'{rid}.npz');g=initial['grid'].copy();lab=initial['labels'].copy()
    assert digest(g)==spec['initial_hash'] and digest(lab)==spec['initial_labels_hash']
    contact_t=None;boundary_t=None;metrics=[];events=[];prev=set();first_cores={};candidate={}
    inputs={m['panel'][pid]['genotype'] for pid in (spec['focal'],spec['partner']) if pid}
    then=time.perf_counter()
    for t in range(cfg['horizon']+1):
        if t:advance(g,1,lab)
        if contact_t is None and contact(g,lab):contact_t=t
        if boundary_t is None and (np.any(g[[0,-1],:]) or np.any(g[:,[0,-1]])):boundary_t=t
        if t%cfg['detection_interval']:continue
        loops=detect(g);now=set()
        for o in loops:
            core=tuple(o['core']);now.add(core);first_cores.setdefault(core,t)
            if core not in prev:
                events.append({'type':'closed_core_first_observed','t':t,'core':o['core'],
                               'genotype':o['genotype'],'interval':cfg['detection_interval'],
                               'ancestry_status':'input' if t==0 else 'unassigned_structure'})
            gt=o['genotype']
            if gt and gt not in inputs:
                item=candidate.setdefault(gt,{'genotype':gt,'first_observed_t':t,'observations':0,
                                             'snapshots':[],'seen_hashes':[],'unextractable_observations':0})
                item['observations']+=1
                if o['isolation_snapshot'] is None:
                    item['unextractable_observations']+=1;continue
                snap=o['isolation_snapshot'];sh=digest(snap)
                if sh in item['seen_hashes'] or len(item['snapshots'])>=cfg['candidate_phase_budget_per_run_genotype']:continue
                item['seen_hashes'].append(sh)
                name=f'candidate-{hashlib.sha256(gt.encode()).hexdigest()[:12]}-{len(item["snapshots"])}.npz'
                np.savez_compressed(folder/name,snapshot=snap,source_grid=g,source_labels=lab)
                y,x,h,w=o['bbox'];mask=int(np.bitwise_or.reduce(lab[y:y+h,x:x+w].ravel()))
                item['snapshots'].append({'file':name,'t':t,'core':o['core'],'extraction_bbox':o['extraction_bbox'],
                                          'snapshot_hash':sh,'provenance_mask':mask,
                                          'ancestry_status':'ambiguous_pair' if contact_t is not None else 'precontact_provenance',
                                          'conservative_parent_set':[spec['focal'],spec['partner']] if spec['partner'] else [spec['focal']]})
        for core in prev-now:events.append({'type':'closed_core_lost','t':t,'core':list(core),'interval':cfg['detection_interval']})
        prev=now
        if t%cfg['metrics_interval']==0:
            metrics.append({'t':t,'occupied_cells':int(np.count_nonzero(g)),'closed_cores':len(loops),
                            'unknown_genotype_cores':sum(o['genotype'] is None for o in loops),
                            'genotypes':sorted({o['genotype'] for o in loops if o['genotype']})})
    final_loops=detect(g);final_cores={tuple(o['core']):o for o in final_loops}
    survival=[]
    for initial_core in spec['initial_cores']:
        o=final_cores.get(tuple(initial_core['core']))
        survival.append({**initial_core,'closed_core_present_at_horizon':o is not None,
                         'same_genotype_at_horizon':bool(o and o['genotype']==initial_core['genotype']),
                         'interpretation':'structural survival only; lineage survival/viability unresolved'})
    np.savez_compressed(folder/'final.npz',grid=g,labels=lab)
    result={**spec,'rule_hash':RULE_HASH,'config_sha256':m['config_sha256'],'contact_t':contact_t,
            'no_contact_control_valid':contact_t is None if spec['treatment']=='separated' else None,
            'boundary_first_t':boundary_t,'horizon':cfg['horizon'],'final_hash':digest(g),'final_labels_hash':digest(lab),
            'input_structural_survival':survival,'new_core_count':sum(t>0 for t in first_cores.values()),
            'events':events,'metrics':metrics,'candidates':list(candidate.values()),
            'inheritance_status':'pending' if candidate else 'no_observed_candidate',
            'benefit_status':'pending_viability_calibration' if candidate else 'not_applicable_to_observed_candidates',
            'ancestry':'conservative pair-level novelty; no genetic parent assignment',
            'observation_status':'completed; nonrectangular/boundary structures may remain unresolved',
            'seconds':time.perf_counter()-then}
    write_json(folder/'result.json',result)
    return result

def run():
    m=load_manifest();specs=sorted(m['runs'],key=lambda r:(r['treatment']!='near',r['split']!='main',r['run_id']))
    total=time.perf_counter()
    for i,spec in enumerate(specs,1):
        p=OUT/'runs'/spec['run_id']/'result.json'
        if p.exists():continue
        r=run_one(spec,m)
        print(f'{i}/{len(specs)} {r["run_id"]} contact={r["contact_t"]} candidates={len(r["candidates"])} newcores={r["new_core_count"]} {r["seconds"]:.2f}s',flush=True)
    results=[json.loads((OUT/'runs'/s['run_id']/'result.json').read_text()) for s in m['runs']]
    assert len(results)==m['expected_runs']
    write_json(OUT/'batch.json',{'experiment_id':m['experiment_id'],'completed_runs':len(results),
                              'seconds_this_invocation':time.perf_counter()-total,
                              'sum_run_seconds':sum(r['seconds'] for r in results),
                              'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                              'separated_contact_violations':[r['run_id'] for r in results if r['no_contact_control_valid'] is False]})

def inherit():
    m=load_manifest();items=[];then=time.perf_counter()
    for i,spec in enumerate(m['runs'],1):
        folder=OUT/'runs'/spec['run_id'];r=json.loads((folder/'result.json').read_text())
        inputs={m['panel'][pid]['genotype'] for pid in (spec['focal'],spec['partner']) if pid}
        for c in r['candidates']:
            outcomes=[]
            for snap in c['snapshots']:
                p=folder/snap['file'];a=np.load(p)['snapshot'];assert digest(a)==snap['snapshot_hash']
                target=folder/(p.stem+'-inheritance.json')
                if target.exists():test=json.loads(target.read_text())
                else:
                    test,e=inheritance(a,c['genotype'],m['config']['inheritance_horizon_per_generation'])
                    test['stable_novel_vs_both_inputs']=bool(test['status']=='confirmed' and test['stable_genotype'] not in inputs)
                    test['encounter_observed_genotype']=c['genotype']
                    test['stable_genotype_observed_in_encounter']=test.get('stable_genotype') in [z['genotype'] for z in r['candidates']]
                    test['source']=snap;write_json(target,test)
                    arrays={f'evidence{k}':a for k,a in enumerate(e) if a is not None}
                    if arrays:np.savez_compressed(folder/(p.stem+'-inheritance.npz'),**arrays)
                outcomes.append({'file':target.name,**test})
            items.append({'run_id':spec['run_id'],'encounter_genotype':c['genotype'],
                          'first_observed_t':c['first_observed_t'],'outcomes':outcomes,
                          'confirmed_novel':any(o['stable_novel_vs_both_inputs'] for o in outcomes),
                          'status':'confirmed' if any(o['stable_novel_vs_both_inputs'] for o in outcomes) else 'unresolved',
                          'unextractable_observations':c['unextractable_observations']})
        if r['candidates']:print('inheritance',i,spec['run_id'],'candidates',len(r['candidates']),flush=True)
    write_json(OUT/'inheritance.json',{'experiment_id':m['experiment_id'],'items':items,
                                     'seconds_this_invocation':time.perf_counter()-then,
                                     'benefit_status':'pending_viability_calibration_and_paired_assay'})
    print('Inheritance checks complete:',len(items),'run/genotype candidates')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['freeze','run','inherit']);a=p.parse_args()
    {'freeze':freeze,'run':run,'inherit':inherit}[a.command]()
