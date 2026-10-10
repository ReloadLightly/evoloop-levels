"""Prospective complete-state freeze, independent score calibration, paired responses."""
import argparse
import json
import platform
import resource
import time
import numpy as np
from evoloop.engine import ROOT, RULE_HASH, advance, digest
from evoloop.ecology import observation, chosen_cores
from evoloop.microcolony import phase_patch, assemble, equivalent
from scripts.atlas import write_json
from scripts.ecological_assay import sha, search_one

OUT = ROOT/'data/impact-v1'
CFG = ROOT/'configs/impact-v1.json'
PROTOCOL = ROOT/'protocols/009-impact-matched-paired-assay.md'
FILES = ['evoloop/kernel.c','evoloop/engine.py','evoloop/tracking.py',
'evoloop/periodic_tracking.py','evoloop/periodic_assays.py','evoloop/fate.py',
'evoloop/ecology.py','evoloop/impact.py','evoloop/microcolony.py',
'scripts/ecological_assay.py','scripts/impact_assay.py','scripts/analyze_impact.py']

def code_hashes():
    return {name:sha(ROOT/name) for name in FILES}

def freeze():
    assert not (OUT/'manifest.json').exists(), 'preserve frozen experiments'
    cfg=json.loads(CFG.read_text()); source=json.loads((ROOT/'data/ecological-v1/manifest.json').read_text())
    registry=source['registry']; states=source['states']; runs=[]; phases=[]; preparations=[]; equivalents=[]
    (OUT/'initial').mkdir(parents=True,exist_ok=True); (OUT/'phase').mkdir(exist_ok=True); (OUT/'prepared').mkdir(exist_ok=True)
    with np.load(ROOT/'data/ecological-v1/snapshots.npz') as snapshots:
        np.savez_compressed(OUT/'snapshots.npz',**{pid:snapshots[pid] for pid in cfg['states']})
        for pid in cfg['states']:
            for c in cfg['conditions']:
                sourcegrid,patch,offset=phase_patch(snapshots[pid],c['age'],cfg['shape'],states[pid]['identity'])
                name=f'{pid}-age{c["age"]}'
                np.savez_compressed(OUT/'phase'/f'{name}.npz',grid=sourcegrid,snapshot=patch)
                phases.append({'state':pid,'age':c['age'],'name':name,'grid_hash':digest(sourcegrid),'snapshot_hash':digest(patch),'offset':offset})
                pre,post,mask,impact=assemble(patch,offset,c['sites'],c['remove_index'],cfg['shape'],registry)
                pairid=f'{pid}-{c["id"]}'
                np.savez_compressed(OUT/'prepared'/f'{pairid}.npz',before=pre,after=post,mask=mask)
                preparations.append({'pair_id':pairid,'state':pid,'condition':c,'phase':name,'impact':impact})
                for treatment,grid in [('D',post)]+([] if c['split']=='calibration' else [('U',pre)]):
                    rid=f'{pairid}-{treatment}'
                    np.savez_compressed(OUT/'initial'/f'{rid}.npz',grid=grid)
                    runs.append({'run_id':rid,'split':c['split'],'state':pid,'condition':c,'treatment':treatment,
                        'initial_hash':digest(grid),'pair_id':pairid,'phase':name,'impact':impact})
    for pid in cfg['states']:
        for d in [p for p in preparations if p['state']==pid and p['condition']['split']=='development']:
            for c in [p for p in preparations if p['state']==pid and p['condition']['split']=='confirmation']:
                with np.load(OUT/'prepared'/f'{d["pair_id"]}.npz') as a, np.load(OUT/'prepared'/f'{c["pair_id"]}.npz') as b:
                    proof={key:equivalent(a[key],b[key]) for key in ('before','after','mask')}
                equivalents.append({'state':pid,'development':d['pair_id'],'confirmation':c['pair_id'],**proof})
    distinct=all(r['before'] is None and r['after'] is None for r in equivalents)
    aliases=[]
    # Same condition across states: do not mistake converged complete states for replications.
    for c in cfg['conditions']:
        for i,pid in enumerate(cfg['states']):
            for q in cfg['states'][i+1:]:
                with np.load(OUT/'prepared'/f'{pid}-{c["id"]}.npz') as a,np.load(OUT/'prepared'/f'{q}-{c["id"]}.npz') as b:
                    for key in ('before','after'):
                        eq=equivalent(a[key],b[key])
                        if eq is not None: aliases.append({'condition':c['id'],'states':[pid,q],'grid':key,'transform':eq})
    assert distinct, 'effective development/confirmation repeats; freeze blocked before responses'
    write_json(OUT/'manifest.json',{'config':cfg,'benefit':cfg,'states':states,'registry':registry,'runs':runs,
       'phases':phases,'preparations':preparations,'equivalence_checks':equivalents,'cross_state_aliases':aliases,
       'exposure_verified':True,'distinct_confirmation_verified':distinct,
       'calibration_experiment_id':cfg['calibration_experiment_id'],'benefit_experiment_id':cfg['benefit_experiment_id'],
       'rule_hash':RULE_HASH,'code_hashes':code_hashes(),'config_sha256':sha(CFG),'protocol_sha256':sha(PROTOCOL),
       'source_sha256':{f:sha(ROOT/f) for f in ['data/ecological-v1/manifest.json','data/ecological-v1/snapshots.npz','data/impact-exposure-v1/attempt-02/report.json']},
       'environment':{'python':platform.python_version(),'numpy':np.__version__,'platform':platform.platform()}})
    print('Frozen',len(runs),'native worlds;',len(phases),'phase controls; distinct confirmation',distinct,flush=True)

def load_manifest():
    m=json.loads((OUT/'manifest.json').read_text())
    assert m['rule_hash']==RULE_HASH and m['code_hashes']==code_hashes()
    assert m['config_sha256']==sha(CFG) and m['protocol_sha256']==sha(PROTOCOL)
    assert all(sha(ROOT/f)==v for f,v in m['source_sha256'].items())
    return m

def run_ecology(spec, m):
    calibration = spec['split'] == 'calibration'
    folder = OUT/spec['split']/spec['run_id']
    folder.mkdir(parents=True, exist_ok=True)
    grid = np.load(OUT/'initial'/f'{spec["run_id"]}.npz')['grid'].copy()
    assert digest(grid) == spec['initial_hash']
    benefit = m['benefit']; cfg = m['config']; registry = m['registry']
    stop = max(cfg['calibration']['source_times'])+cfg['calibration']['native_continuation_horizon'] if calibration else benefit['horizon']
    samples = []; events = ([{'type':'disturbance','t':0,**spec['impact']}] if spec['treatment']=='D' else []); strata = []; targets = []; previous = {}
    frames = []; frame_times = []; then = time.perf_counter()
    capture = not calibration and {'state':spec['state'],'condition':spec['condition']['id']} in cfg['replays']
    for t in range(0, stop+1, benefit['sample_interval']):
        if t:
            advance(grid, benefit['sample_interval'])
        counts, records, loops = observation(grid, registry)
        samples.append({'t': t, **counts, 'cores': records})
        now = {tuple(o['core']): o['identity'] for o in records}
        for core, identity in now.items():
            if core not in previous:
                events.append({'type': 'core_appearance', 't': t, 'core': list(core), 'identity': identity})
            elif previous[core] != identity:
                events.append({'type': 'identity_change_at_core', 't': t, 'core': list(core),
                               'before': previous[core], 'after': identity})
        for core in sorted(previous.keys()-now.keys()):
            events.append({'type': 'core_loss', 't': t, 'core': list(core)})
        previous = now
        if capture and t % cfg['replay_interval'] == 0:
            frames.append(grid.copy()); frame_times.append(t)
        if calibration and t in cfg['calibration']['source_times']:
            np.savez_compressed(folder/f'source-{t}.npz', grid=grid)
            for scored in (True, False):
                chosen = chosen_cores(loops, scored, registry)
                stratum = f'{spec["run_id"]}-t{t}-{ "scored" if scored else "unscored"}'
                strata.append({'stratum_id': stratum, 't': t, 'scored': scored,
                                'available_cores': sum((o['genotype'] in registry) == scored for o in loops),
                                'selected_cores': len(chosen)})
                for i, o in enumerate(chosen):
                    snap = o['isolation_snapshot']
                    status = o['extraction_status'] if snap is None else 'ineligible_component_size' if max(snap.shape)+20 > cfg['search']['isolation_shape'][0] else 'eligible'
                    name = f'target-{t}-{ "scored" if scored else "unscored"}-{i}'
                    if snap is not None:
                        np.savez_compressed(folder/f'{name}.npz', snapshot=snap)
                    targets.append({'target_id': name, 'stratum_id': stratum, 't': t,
                                    'core': o['core'], 'identity': o['genotype'], 'scored': scored,
                                    'extraction_status': status, 'snapshot_hash': digest(snap) if snap is not None else None,
                                    'extraction_bbox': o.get('extraction_bbox'),
                                    'snapshot_file': f'{name}.npz' if snap is not None else None})
    np.savez_compressed(folder/'final.npz', grid=grid)
    if capture:
        np.savez_compressed(folder/'replay.npz', frames=np.array(frames), times=np.array(frame_times))
    score_samples = [s['scored_cores'] for s in samples if s['t'] <= benefit['horizon']]
    assert len(score_samples) == 81
    result = {**spec, 'rule_hash': RULE_HASH, 'completed_updates': stop,
              'final_hash': digest(grid), 'samples': samples, 'events': events,
              'score': sum(score_samples)/len(score_samples), 'score_sum': sum(score_samples), 'score_sample_count': len(score_samples),
              'score_scope': 'fixed known-identity closed-core structural population',
              'strata': strata, 'targets': targets, 'seconds': time.perf_counter()-then}
    if calibration:
        for target in targets:
            window = [s for s in samples if target['t'] <= s['t'] <= target['t']+cfg['calibration']['native_continuation_horizon']]
            present = [any(o['core'] == target['core'] for o in s['cores']) for s in window]
            loss = next((s['t'] for s, p in zip(window, present) if not p), None)
            recurrence = next((s['t'] for s, p in zip(window, present) if loss is not None and s['t'] > loss and p), None)
            endpoint = next((o for o in window[-1]['cores'] if o['core'] == target['core']), None)
            word = target['identity'].split(':',1)[1] if target['identity'] else None
            matched = [s['t'] for s in window if word and any(o['core'] != target['core'] and o['identity'] and o['identity'].split(':',1)[1] == word for o in s['cores'])]
            target['native_continuation'] = {'horizon': cfg['calibration']['native_continuation_horizon'],
                'sample_interval': benefit['sample_interval'], 'fixed_core_first_loss_t': loss,
                'fixed_core_first_recurrence_t': recurrence, 'endpoint_identity': endpoint['identity'] if endpoint else None,
                'matching_word_elsewhere_first_t': matched[0] if matched else None,
                'interpretation': 'overlapping structural continuations; no native offspring or genetic ancestry assignment'}
    write_json(folder/'result.json', result)
    print('ECOLOGY', spec['run_id'], f'{result["seconds"]:.2f}s', flush=True)
    return result


def calibrate():
    m=load_manifest(); then=time.perf_counter(); baselines=[]; observations=[]
    for phase in m['phases']:
        pid=phase['state']; folder=OUT/'calibration'/'baseline'/phase['name']
        with np.load(OUT/'phase'/f'{phase["name"]}.npz') as saved: snapshot=saved['snapshot'].copy()
        assert digest(snapshot)==phase['snapshot_hash']
        report=search_one(snapshot,m['states'][pid]['identity'],m,folder,True)
        baselines.append({**phase,'folder':str(folder.relative_to(OUT)),'outcome':report})
        print('PHASE CONTROL',phase['name'],report['status'],flush=True)
    for spec in m['runs']:
        if spec['split']!='calibration': continue
        folder=OUT/'calibration'/spec['run_id']
        result=json.loads((folder/'result.json').read_text()) if (folder/'result.json').exists() else run_ecology(spec,m)
        for target in result['targets']:
            report=None; path=folder/f'{target["target_id"]}-search'
            if target['extraction_status']=='eligible':
                with np.load(folder/target['snapshot_file']) as saved: snapshot=saved['snapshot'].copy()
                assert digest(snapshot)==target['snapshot_hash']
                report=search_one(snapshot,target['identity'],m,path,target['scored'])
            observations.append({'run_id':spec['run_id'],'state':spec['state'],**target,
                                 'folder':str(path.relative_to(OUT)) if report else None,'outcome':report})
        print('CALIBRATION',spec['run_id'],'targets',len(result['targets']),flush=True)
    write_json(OUT/'calibration.json',{'experiment_id':m['calibration_experiment_id'],'baselines':baselines,'observations':observations,
        'seconds_this_invocation':time.perf_counter()-then,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})

def benefit():
    m=load_manifest(); calibration=json.loads((OUT/'calibration-analysis.json').read_text())
    assert calibration['calibration_sha256']==sha(OUT/'calibration.json')
    then=time.perf_counter(); runs=[]
    for split in ('development','confirmation'):
        for spec in m['runs']:
            if spec['split']!=split: continue
            folder=OUT/split/spec['run_id']
            result=json.loads((folder/'result.json').read_text()) if (folder/'result.json').exists() else run_ecology(spec,m)
            runs.append({'run_id':spec['run_id'],'score_sum':result['score_sum'],'final_hash':result['final_hash']})
    write_json(OUT/'benefit.json',{'experiment_id':m['benefit_experiment_id'],'calibration_passed':calibration['gate_passed'],'runs':runs,
        'seconds_this_invocation':time.perf_counter()-then,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('command',choices=['freeze','calibrate','benefit']); args=parser.parse_args()
    {'freeze':freeze,'calibrate':calibrate,'benefit':benefit}[args.command]()
