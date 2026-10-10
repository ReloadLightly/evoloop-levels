"""Fresh three-identity crossed atlas; independent frozen module."""
import argparse,hashlib,json,resource,time
import numpy as np
from evoloop.engine import ROOT,RULE_HASH,advance,place,digest
from evoloop.periodic_tracking import detect,periodic_view
from evoloop.periodic_assays import offspring_generation
from evoloop.fate import expanded_search
from scripts.accelerated_atlas import compiled_contact
from scripts.atlas import write_json
from scripts.panel_discovery import word

OUT=ROOT/'data/atlas-v2';CFG=ROOT/'configs/atlas-v2.json';PROTOCOL=ROOT/'protocols/006-fresh-crossed-atlas.md'
FILES=['evoloop/kernel.c','evoloop/engine.py','evoloop/tracking.py','evoloop/periodic_tracking.py','evoloop/periodic_assays.py','evoloop/fate.py','evoloop/contact_scan.c','scripts/accelerated_atlas.py','scripts/panel_discovery.py','scripts/fresh_atlas.py','scripts/analyze_fresh_atlas.py']
def code_hashes():return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in FILES}

def freeze():
    assert not (OUT/'manifest.json').exists()
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'initial').mkdir(exist_ok=True)
    cfg=json.loads(CFG.read_text());d=json.loads((ROOT/'data/panel-v2/discovery.json').read_text())
    assert d['status']=='target_reached'
    panel={p['id']:{**p,'genotype':p['stable_identity']} for p in d['panel']};phases={};phase_meta=[]
    for pid in cfg['organisms']:
        a=np.load(ROOT/f'data/panel-v2/{pid}.npz')
        for phase in sorted(set(cfg['main_phases']+[cfg['heldout_phase']])):
            snap=a[f'p{phase}'];phases[pid,phase]=snap
            g=np.zeros((192,192),np.uint8);place(g,snap,96-snap.shape[0]//2,96-snap.shape[1]//2)
            loops=detect(g);assert len(loops)==1 and loops[0]['genotype']==panel[pid]['genotype']
            phase_meta.append({'organism':pid,'phase':phase,'hash':digest(snap),'shape':list(snap.shape)})
    np.savez_compressed(OUT/'phase_states.npz',**{f'{pid}_p{phase}':s for (pid,phase),s in phases.items()})
    runs=[];old_hashes={r['initial_hash'] for r in json.loads((ROOT/'data/atlas/manifest.json').read_text())['runs']}
    def add(pid,qid,phase,geo,split,treatment):
        g=np.zeros(cfg['shape'],np.uint8);lab=np.zeros_like(g);sy,sx=cfg['focal_origin'];a=phases[pid,phase]
        solo=treatment=='alone';rotation=geo['partner_rotation'] if solo else 0
        pbox=place(g,a,sy,sx,rotation);lab[g!=0]=1;qbox=None
        if not solo:
            qy=sy+geo['dy'];qx=sx+cfg['far_dx'] if treatment=='separated' else sx+a.shape[1]+geo['gap']
            b=phases[qid,phase];qbox=place(g,b,qy,qx,geo['partner_rotation']);rot=np.rot90(b,geo['partner_rotation'])
            assert qx>=sx+a.shape[1]
            view=lab[qy:qy+rot.shape[0],qx:qx+rot.shape[1]];view[rot!=0]=2
        rid=f'{treatment}-{split}-{pid}-{qid or "none"}-p{phase}-{geo["id"]}'
        cores=[]
        for o in detect(g):
            cores.append({'core':o['core'],'genotype':o['genotype'],'provenance':int(np.bitwise_or.reduce(periodic_view(lab,o['bbox']).ravel()))})
        assert len(cores)==(1 if solo else 2);assert not compiled_contact(g,lab)
        assert digest(g) not in old_hashes
        np.savez_compressed(OUT/'initial'/f'{rid}.npz',grid=g,labels=lab)
        runs.append({'run_id':rid,'focal':pid,'partner':qid,'phase':phase,'geometry':geo,'split':split,'treatment':treatment,
            'shape':cfg['shape'],'initial_hash':digest(g),'initial_labels_hash':digest(lab),'initial_cores':cores,'input_boxes':[pbox,qbox]})
    for split,plist,geometries in [('main',cfg['main_phases'],cfg['main_geometries']),('heldout',[cfg['heldout_phase']],cfg['heldout_geometries'])]:
        for pid in cfg['organisms']:
            for qid in cfg['organisms']:
                for phase in plist:
                    for geo in geometries:
                        for treatment in ('near','separated'):add(pid,qid,phase,geo,split,treatment)
    for pid in cfg['organisms']:
        for phase in sorted(set(cfg['main_phases']+[cfg['heldout_phase']])):
            for rotation in range(4):add(pid,None,phase,{'id':f'r{rotation}','partner_rotation':rotation,'gap':0,'dy':0},'control','alone')
    assert len(runs)==144 and len({r['initial_hash'] for r in runs})==144
    write_json(OUT/'manifest.json',{'experiment_id':cfg['experiment_id'],'config':cfg,'panel':panel,'phase_states':phase_meta,'runs':runs,'expected_runs':len(runs),
        'rule_hash':RULE_HASH,'code_hashes':code_hashes(),'config_sha256':hashlib.sha256(CFG.read_bytes()).hexdigest(),'protocol_sha256':hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        'discovery_sha256':hashlib.sha256((ROOT/'data/panel-v2/discovery.json').read_bytes()).hexdigest(),'initial_states_disjoint_from_old_atlas':True})
    print('Frozen',len(runs),'states',flush=True)

def load_manifest():
    m=json.loads((OUT/'manifest.json').read_text());assert m['rule_hash']==RULE_HASH;assert m['code_hashes']==code_hashes()
    assert m['config_sha256']==hashlib.sha256(CFG.read_bytes()).hexdigest()
    assert m['protocol_sha256']==hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    assert m['discovery_sha256']==hashlib.sha256((ROOT/'data/panel-v2/discovery.json').read_bytes()).hexdigest();return m

def run_one(spec,m):
    cfg=m['config'];rid=spec['run_id'];folder=OUT/'runs'/rid;folder.mkdir(parents=True,exist_ok=True)
    initial=np.load(OUT/'initial'/f'{rid}.npz');g=initial['grid'].copy();lab=initial['labels'].copy()
    assert digest(g)==spec['initial_hash'] and digest(lab)==spec['initial_labels_hash']
    contact_t=None;boundary_t=None;metrics=[];events=[];prev=set();first_cores={};candidate={};shape_only=set()
    inputs={word(m['panel'][pid]['genotype']) for pid in (spec['focal'],spec['partner']) if pid}
    then=time.perf_counter()
    for t in range(cfg['horizon']+1):
        if t:advance(g,1,lab)
        if contact_t is None and compiled_contact(g,lab):contact_t=t
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
            if gt and gt not in {m['panel'][p]['genotype'] for p in (spec['focal'],spec['partner']) if p} and word(gt) in inputs:shape_only.add(gt)
            if gt and word(gt) not in inputs:
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
                mask=int(np.bitwise_or.reduce(periodic_view(lab,o['bbox']).ravel()))
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
            'events':events,'metrics':metrics,'candidates':list(candidate.values()),'shape_only_changed_identities':sorted(shape_only),
            'inheritance_status':'pending' if candidate else 'no_observed_candidate',
            'benefit_status':'pending_viability_calibration' if candidate else 'not_applicable_to_observed_candidates',
            'ancestry':'conservative pair-level novelty; no genetic parent assignment',
            'observation_status':'completed; seam-aware small rectangular detection; large/nonrectangular structures unresolved',
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
    for spec in m['runs']:
        folder=OUT/'runs'/spec['run_id'];r=json.loads((folder/'result.json').read_text())
        inputs={word(m['panel'][p]['genotype']) for p in (spec['focal'],spec['partner']) if p}
        for c in r['candidates']:
            outcomes=[]
            for snap in c['snapshots']:
                a=np.load(folder/snap['file'])['snapshot'];assert digest(a)==snap['snapshot_hash']
                target=folder/(snap['file'].replace('.npz','-search'));target.mkdir(exist_ok=True)
                def persist(node,arrays):
                    name='confirmation' if 'confirmation' in node else f'node-{node["node"]:02d}'
                    write_json(target/f'{name}.json',node);np.savez_compressed(target/f'{name}.npz',**arrays)
                if (target/'result.json').exists():test=json.loads((target/'result.json').read_text())
                else:
                    test=expanded_search(a,c['genotype'],m['config'],lambda gt:word(gt) not in inputs,persist,generation=offspring_generation)
                    test['source']=snap;test['stable_novel_vs_both_inputs']=test['status']=='confirmed'
                    stable=test['confirmation']['identity'] if test['confirmation'] else None
                    test['stable_word_observed_natively']=bool(stable and word(stable) in {word(z['genotype']) for z in r['candidates']})
                    write_json(target/'result.json',test)
                outcomes.append({'folder':str(target.relative_to(OUT)),**test})
            items.append({'run_id':spec['run_id'],'encounter_genotype':c['genotype'],'outcomes':outcomes,
                'confirmed_novel':any(o['status']=='confirmed' for o in outcomes),
                'status':'confirmed' if any(o['status']=='confirmed' for o in outcomes) else 'unresolved',
                'unextractable_observations':c['unextractable_observations']})
        if r['candidates']:print('INHERIT',spec['run_id'],len(r['candidates']),flush=True)
    write_json(OUT/'inheritance.json',{'experiment_id':m['experiment_id'],'items':items,'seconds_this_invocation':time.perf_counter()-then,
        'benefit_status':'pending_viability_calibration_and_paired_assay'})
    print('INHERIT DONE',len(items),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['freeze','run','inherit']);a=p.parse_args();{'freeze':freeze,'run':run,'inherit':inherit}[a.command]()
