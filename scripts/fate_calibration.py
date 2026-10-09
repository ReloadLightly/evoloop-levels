"""Freeze/run/verify the paired native-continuation and isolation calibration."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import resource
import time
import numpy as np
from evoloop.engine import ROOT,RULE_HASH,advance,digest,place
from evoloop.tracking import detect
from evoloop.assays import inheritance
from evoloop.fate import isolated_initial,expanded_search
from scripts.atlas import load_manifest,write_json,code_hashes

OUT=ROOT/'data/fate-calibration';CFG=ROOT/'configs/fate-v1.json';PROTOCOL=ROOT/'protocols/004-candidate-fate-calibration.md'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def hashes():
    return {**code_hashes(),**{f:sha(ROOT/f) for f in ['evoloop/fate.py','scripts/fate_calibration.py','scripts/analyze_fate.py']}}

def freeze():
    assert not (OUT/'manifest.json').exists(),'already frozen: use a new experiment ID for changes'
    m=load_manifest();cfg=json.loads(CFG.read_text());OUT.mkdir(exist_ok=True);(OUT/'sources').mkdir(exist_ok=True)
    sources=[]
    for s in sorted(m['runs'],key=lambda z:z['run_id']):
        folder=ROOT/'data/atlas/runs'/s['run_id'];r=json.loads((folder/'result.json').read_text())
        for c in sorted(r['candidates'],key=lambda z:(z['first_observed_t'],z['genotype'])):
            a=np.load(ROOT/f'data/atlas/initial/{s["run_id"]}.npz');g=a['grid'].copy();lab=a['labels'].copy()
            advance(g,c['first_observed_t'],lab)
            candidates=sorted((o for o in detect(g) if o['genotype']==c['genotype']),key=lambda o:tuple(o['core']))
            assert candidates,'recorded first observation not reproducible'
            target=candidates[0];sid=f'C{len(sources)+1:02d}'
            np.savez_compressed(OUT/f'sources/{sid}.npz',grid=g,labels=lab)
            inputs=[m['panel'][pid]['genotype'] for pid in [s['focal'],s['partner']]]
            sources.append({'id':sid,'kind':'candidate','run_id':s['run_id'],'source_t':c['first_observed_t'],
                            'target_core':target['core'],'identity':target['genotype'],'source_hash':digest(g),
                            'source_labels_hash':digest(lab),'input_identities':inputs,'source_result_sha256':sha(folder/'result.json')})
    assert len(sources)==7 and len({s['run_id'] for s in sources})==6
    for pid in cfg['controls']:
        snap=np.load(ROOT/f'data/exploration/{pid}.npz')['snapshot'];g=np.zeros(cfg['control_world_shape'],dtype=np.uint8)
        place(g,snap,*cfg['control_snapshot_placement']);loops=detect(g)
        assert len(loops)==1 and loops[0]['genotype']==m['panel'][pid]['genotype']
        lab=(g!=0).astype(np.uint8);sid=f'P-{pid}';np.savez_compressed(OUT/f'sources/{sid}.npz',grid=g,labels=lab)
        sources.append({'id':sid,'kind':'control','organism':pid,'run_id':None,'source_t':0,
                        'target_core':loops[0]['core'],'identity':loops[0]['genotype'],'source_hash':digest(g),
                        'source_labels_hash':digest(lab),'input_identities':[loops[0]['genotype']]})
    report={'experiment_id':cfg['experiment_id'],'rule_hash':RULE_HASH,'config':cfg,'config_sha256':sha(CFG),
            'protocol_sha256':sha(PROTOCOL),'code_hashes':hashes(),'source_manifest_sha256':sha(ROOT/'data/atlas/manifest.json'),
            'sources':sources,'expected_cases':len(sources)*len(cfg['delays'])}
    write_json(OUT/'manifest.json',report);print('Frozen',len(sources),'sources and',report['expected_cases'],'delay cases')


def manifest():
    m=json.loads((OUT/'manifest.json').read_text());assert m['rule_hash']==RULE_HASH
    assert m['config_sha256']==sha(CFG) and m['protocol_sha256']==sha(PROTOCOL)
    assert m['code_hashes']==hashes(),'scientific code changed after freeze'
    assert m['source_manifest_sha256']==sha(ROOT/'data/atlas/manifest.json')
    return m


def native_run(initial,source,cfg):
    g=initial.copy();target=tuple(source['target_core']);word=source['identity'].split(':',1)[1]
    original_cores={tuple(o['core']) for o in detect(g)};samples=[];events=[];prev=set();new_word_cores=set();boundary=None
    for t in range(0,cfg['native_horizon_after_delay']+1,cfg['detection_interval']):
        if t:advance(g,cfg['detection_interval'])
        if boundary is None and (np.any(g[[0,-1]]) or np.any(g[:,[0,-1]])):boundary=t
        loops=detect(g);now={tuple(o['core']) for o in loops};o=next((o for o in loops if tuple(o['core'])==target),None)
        matching=[z for z in loops if z['genotype'] and z['genotype'].split(':',1)[1]==word]
        for z in matching:
            if tuple(z['core']) not in original_cores:new_word_cores.add(tuple(z['core']))
        samples.append({'t':t,'target_present':o is not None,'target_identity':o['genotype'] if o else None,
                        'original_word_cores':len(matching),'original_word_elsewhere':sum(tuple(z['core'])!=target for z in matching),
                        'other_word_cores':sum(bool(z['genotype']) and z['genotype'].split(':',1)[1]!=word for z in loops),
                        'unknown_word_cores':sum(z['genotype'] is None for z in loops),
                        'closed_cores':len(loops),'occupied_cells':int(np.count_nonzero(g)),
                        **({'original_word_locations':[z['core'] for z in matching],
                            'identity_counts':dict(Counter(z['genotype'] for z in loops if z['genotype']))} if t%100==0 else {})})
        for z in loops:
            if tuple(z['core']) not in prev:events.append({'type':'appearance','t':t,'core':z['core'],'identity':z['genotype']})
        for core in sorted(prev-now):events.append({'type':'loss','t':t,'core':list(core)})
        prev=now
    return {'initial_hash':digest(initial),'final_hash':digest(g),'completed_updates':cfg['native_horizon_after_delay'],
            'boundary_first_t':boundary,'samples':samples,'events':events,
            'new_original_word_core_locations':[list(c) for c in sorted(new_word_cores)],
            'interpretation':'structural word presence only; native ancestry and inheritance unresolved'},g


def run_case(source,delay,m):
    cfg=m['config'];rid=f'{source["id"]}-d{delay:03d}';folder=OUT/'runs'/rid;folder.mkdir(parents=True,exist_ok=True)
    started=time.perf_counter();a=np.load(OUT/f'sources/{source["id"]}.npz');g=a['grid'].copy();assert digest(g)==source['source_hash']
    delay_tracking=[];first_loss=None;first_recurrence=None
    for t in range(0,delay+1,cfg['detection_interval']):
        if t:advance(g,cfg['detection_interval'])
        current=next((o for o in detect(g) if o['core']==source['target_core']),None)
        if current is None and first_loss is None:first_loss=t
        if current is not None and first_loss is not None and first_recurrence is None:first_recurrence=t
        delay_tracking.append({'t':t,'target_present':current is not None,'identity':current['genotype'] if current else None})
    initial=g.copy();loops=detect(g)
    target=next((o for o in loops if o['core']==source['target_core']),None)
    status='target_lost' if target is None else 'unknown_identity' if not target['genotype'] else target['extraction_status']
    snap=None
    if target is not None and target['genotype'] and target['isolation_snapshot'] is not None:
        snap=target['isolation_snapshot'];status='eligible' if isolated_initial(snap) is not None else 'oversized_component'
    if target is not None and first_loss is not None:status='target_recurrence_after_loss'
    arrays={'native_initial':initial}
    if target is not None:arrays['target_body']=target['snapshot']
    if snap is not None:arrays['component']=snap
    native,final=native_run(initial,source,cfg);arrays['native_final']=final
    np.savez_compressed(folder/'native.npz',**arrays)
    legacy=None;expanded=None
    if status=='eligible':
        legacy,e=inheritance(snap,target['genotype'],cfg['generation_horizon'])
        legacy_arrays={'initial':isolated_initial(snap),**{f'evidence{i}':z for i,z in enumerate(e) if z is not None}}
        for i,child in enumerate(e[:2],2):
            if child is not None and isolated_initial(child) is not None:
                legacy_arrays[f'generation{i}_initial']=isolated_initial(child)
        np.savez_compressed(folder/'legacy.npz',**legacy_arrays)
        words={z.split(':',1)[1] for z in source['input_identities']}
        accept=(lambda gt:gt==source['identity']) if source['kind']=='control' else (lambda gt:gt.split(':',1)[1] not in words)
        legacy['endpoint_confirmed']=bool(legacy['status']=='confirmed' and accept(legacy['stable_genotype']))
        def persist(node,arr):
            name='confirmation' if 'confirmation' in node else f'node-{node["node"]:02d}'
            np.savez_compressed(folder/f'{name}.npz',**arr);write_json(folder/f'{name}.json',node)
        expanded=expanded_search(snap,target['genotype'],cfg,accept,persist)
    report={'case_id':rid,'source_id':source['id'],'source_kind':source['kind'],'run_id':source['run_id'],
            'delay':delay,'absolute_source_t':source['source_t']+delay,'target_core':source['target_core'],
            'delay_tracking':delay_tracking,'first_target_loss_before_delay':first_loss,
            'first_target_recurrence_before_delay':first_recurrence,
            'source_identity':source['identity'],'delayed_identity':target['genotype'] if target else None,
            'target_status':status,'component_hash':digest(snap) if snap is not None else None,
            'extraction_bbox':target.get('extraction_bbox') if target else None,'native':native,
            'legacy':legacy,'expanded':expanded,'rule_hash':RULE_HASH,'config_sha256':m['config_sha256'],
            'benefit_status':'not_assayed','seconds':time.perf_counter()-started}
    write_json(folder/'result.json',report)
    return report


def run():
    m=manifest();started=time.perf_counter();results=[]
    for source in m['sources']:
        for delay in m['config']['delays']:
            path=OUT/f'runs/{source["id"]}-d{delay:03d}/result.json'
            r=json.loads(path.read_text()) if path.exists() else run_case(source,delay,m)
            results.append(r)
            print(r['case_id'],r['target_status'],'legacy',r['legacy']['endpoint_confirmed'] if r['legacy'] else '-',
                  'expanded',r['expanded']['status'] if r['expanded'] else '-',f'{r["seconds"]:.1f}s',flush=True)
    write_json(OUT/'batch.json',{'experiment_id':m['experiment_id'],'completed_cases':len(results),
                              'generation_simulations':sum(r['expanded']['generation_simulations'] for r in results if r['expanded']),
                              'sum_case_seconds':sum(r['seconds'] for r in results),'seconds_this_invocation':time.perf_counter()-started,
                              'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})


def verify():
    m=manifest();native_checks=0;nodes=0;legacy_checks=0
    for s in m['sources']:
        a=np.load(OUT/f'sources/{s["id"]}.npz');assert digest(a['grid'])==s['source_hash'] and digest(a['labels'])==s['source_labels_hash']
        for delay in m['config']['delays']:
            p=OUT/f'runs/{s["id"]}-d{delay:03d}';r=json.loads((p/'result.json').read_text());a=np.load(p/'native.npz')
            g=np.load(OUT/f'sources/{s["id"]}.npz')['grid'].copy();advance(g,delay);assert np.array_equal(g,a['native_initial'])
            advance(g,m['config']['native_horizon_after_delay']);assert digest(g)==r['native']['final_hash']==digest(a['native_final']);native_checks+=1
            if r['target_status']!='eligible':assert r['expanded'] is None and r['legacy'] is None;continue
            assert digest(a['component'])==r['component_hash']
            e=np.load(p/'legacy.npz');stages=[a['component'],e['evidence0'] if 'evidence0' in e else None,e['evidence1'] if 'evidence1' in e else None]
            for i,snap in enumerate(stages,1):
                outcome=r['legacy'][f'generation{i}']
                if snap is None or 'final_hash' not in outcome:continue
                g=isolated_initial(snap);advance(g,outcome.get('detached_first_seen_t',outcome.get('horizon',1600)))
                assert digest(g)==outcome['final_hash'];legacy_checks+=1
            for node in r['expanded']['nodes']:
                a=np.load(p/f'node-{node["node"]:02d}.npz');o=node['outcome'];g=a['initial'].copy()
                if node['parent_node'] is not None:
                    parent=r['expanded']['nodes'][node['parent_node']]
                    child=parent['outcome']['children'][node['incoming_child']]
                    assert node['input_identity']==child['identity'] and node['input_snapshot_hash']==child['snapshot_hash']
                    assert node['depth']==parent['depth']+1
                    expected=parent['incoming_streak']+1 if child['identity']==parent['input_identity'] else 0
                    assert node['incoming_streak']==expected
                assert digest(g)==o['initial_hash'];advance(g,o['completed_updates']);assert digest(g)==o['final_hash']==digest(a['final']);nodes+=1
                for i,c in enumerate(o['children']):
                    assert digest(a[f'child{i}'])==c['snapshot_hash']
                    selected=next(z for z in detect(a[f'selection_grid{i}']) if z['core']==c['core'])
                    assert np.array_equal(selected['isolation_snapshot'],a[f'child{i}'])
            assert r['expanded']['generation_simulations']<=m['config']['max_generation_simulations_per_root']
            confirmation=r['expanded']['confirmation']
            if confirmation:
                node=r['expanded']['nodes'][confirmation['node']];child=node['outcome']['children'][confirmation['child']]
                assert confirmation['identity']==child['identity']==node['input_identity']
                assert node['incoming_streak']+1>=m['config']['stable_transmissions']
                assert digest(np.load(p/'confirmation.npz')['stable_snapshot'])==confirmation['snapshot_hash']==child['snapshot_hash']
                assert confirmation['identity']==s['identity'] if s['kind']=='control' else confirmation['identity'].split(':',1)[1] not in {gt.split(':',1)[1] for gt in s['input_identities']}
    report={'experiment_id':m['experiment_id'],'native_replays':native_checks,'expanded_generation_replays':nodes,
            'legacy_generation_replays':legacy_checks,'all_hashes_and_extractions':'pass','frozen_code_protocol':'pass'}
    write_json(OUT/'integrity.json',report);print(json.dumps(report))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['freeze','run','verify']);a=p.parse_args()
    {'freeze':freeze,'run':run,'verify':verify}[a.command]()
