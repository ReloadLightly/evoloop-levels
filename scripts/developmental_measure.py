"""Prospective recovery-certified developmental-source calibration, one worker."""
import argparse
import hashlib
import json
import platform
import resource
import subprocess
import time
from collections import Counter
from fractions import Fraction

import numpy as np
from evoloop.engine import ROOT, RULE_HASH, advance, digest
from evoloop.ecology import observation
from evoloop.microcolony import assemble, equivalent
from evoloop.fate import expanded_search
from evoloop.periodic_assays import offspring_generation
from evoloop.developmental import partition, conjunction
from scripts.coverage_protocol import sha, require
from scripts.coverage_assay import (atomic_json, atomic_npz, receipt, verify_receipt, search_fields)

OUT = ROOT/'data/developmental-v1'
CONFIG = ROOT/'configs/developmental-v1.json'
PROTOCOL = ROOT/'protocols/011-developmental-source-measure.md'
EXTRA = ['evoloop/developmental.py','scripts/developmental_measure.py','scripts/verify_developmental.py',
         'tests/test_developmental.py','tests/test_developmental_audit.py',
         'scripts/coverage_assay.py','scripts/verify_coverage.py','scripts/memory_guard.py',
         'scripts/verify_ecological.py','scripts/verify_fresh.py','scripts/verify_impact.py']

def read(path): return json.loads(path.read_text())
def classify(identity, registry):
    return 'unknown_identity' if identity is None else 'scored' if identity in registry else 'valid_unregistered'

def search_key(snapshot_hash, identity, cfg, original=False):
    binding={'snapshot_hash':snapshot_hash,'input_identity':identity,'rule_hash':RULE_HASH,
             'search_config':cfg,'original_endpoint':original}
    return hashlib.sha256(json.dumps(binding,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def freeze():
    require(not (OUT/'manifest.json').exists(),'immutable freeze already exists')
    cfg=read(CONFIG); old=read(ROOT/'data/impact-v1/manifest.json')
    require(cfg['search']==old['config']['search'],'search version changed')
    require(all(sha(ROOT/p)==h for p,h in old['code_hashes'].items()),'prior frozen implementation changed')
    validation=(OUT/'validation.txt').read_text()
    require('\nOK\n' in validation and 'FAILED' not in validation,'tests must pass before freeze')
    sources={'configs/developmental-v1.json','protocols/011-developmental-source-measure.md',
             'protocols/000-scientific-contract.md','requirements.txt','requirements-lock.txt','data/impact-v1/manifest.json',
             'data/impact-v1/analysis.json','data/impact-v1/benefit.json',
             'data/coverage-v1/manifest.json','data/coverage-v1/readiness.json',
             'data/coverage-v1/analysis.json','data/coverage-v1/integrity.json',
             'data/coverage-v1/recovery.json','data/coverage-v1/component-equivalence.json'}
    files=set(old['code_hashes'])|set(EXTRA)|sources
    controls=[]
    for p in old['phases']:
        path=f'data/impact-v1/phase/{p["name"]}.npz';files.add(path)
        controls.append({**p,'kind':'phase','identity':old['states'][p['state']]['identity'],'file':path})
    coverage=read(ROOT/'data/coverage-v1/recovery.json'); seen=set()
    for o in coverage['observations']:
        d=o['delays'][0]
        if o['source_class']=='unknown_identity' and d['transmission_confirmed'] and d['snapshot_hash'] not in seen:
            seen.add(d['snapshot_hash']); path='data/coverage-v1/'+d['snapshot_file'];files.add(path)
            controls.append({'name':f'omitted-{len(seen)}','kind':'omitted','state':o['state'],
                             'identity':None,'file':path,'snapshot_hash':d['snapshot_hash'],
                             'source_observation':o['observation_id']})
    require(len(controls)==33,'30 phases plus three distinct omitted controls required')
    runs=[]; preparations=[]; equivalences=[]
    for state in cfg['states']:
        for c in cfg['conditions']:
            phase=next(p for p in old['phases'] if p['state']==state and p['age']==c['age'])
            path=ROOT/f'data/impact-v1/phase/{phase["name"]}.npz'
            with np.load(path,allow_pickle=False) as a:
                patch=a['snapshot'].copy(); grid=a['grid']
                require(np.count_nonzero(patch)==np.count_nonzero(grid),'disconnected phase residual')
                require(digest(grid)==phase['grid_hash'] and digest(patch)==phase['snapshot_hash'],'phase physical hash')
            pre,post,mask,impact=assemble(patch,phase['offset'],c['sites'],c['remove_index'],cfg['shape'],old['registry'])
            hpre=np.bincount(pre.ravel(),minlength=9).tolist();hpost=np.bincount(post.ravel(),minlength=9).tolist()
            require(all(hpre[i]==3*(hpre[i]-hpost[i]) for i in range(1,9)),'one-third occupied-state histogram')
            pair=f'{state}-{c["id"]}'; pp=f'data/developmental-v1/prepared/{pair}.npz'
            atomic_npz(ROOT/pp,before=pre,after=post,mask=mask); files.add(pp)
            preparations.append({'pair_id':pair,'state':state,'condition':c,'phase':phase['name'],
                                 'file':pp,'impact':impact,'histogram_before':hpre,'histogram_after':hpost})
            for treatment,g in [('D',post),('U',pre)]:
                rid=f'{pair}-{treatment}';ip=f'data/developmental-v1/initial/{rid}.npz'
                atomic_npz(ROOT/ip,grid=g);files.add(ip)
                runs.append({'run_id':rid,'state':state,'condition':c,'treatment':treatment,
                             'initial_file':ip,'initial_hash':digest(g),'pair_id':pair})
                for prior in old['runs']:
                    op=f'data/impact-v1/initial/{prior["run_id"]}.npz';files.add(op)
                    with np.load(ROOT/op,allow_pickle=False) as a: eq=equivalent(g,a['grid'])
                    require(eq is None,'new calibration repeats a prior effective start')
                    equivalences.append({'run_id':rid,'prior_run_id':prior['run_id'],'transform':eq})
    require(len(runs)==20,'complete D/U calibration panel')
    atomic_json(OUT/'manifest.json',{'experiment_id':cfg['experiment_id'],'config':cfg,'rule_hash':RULE_HASH,
        'registry':old['registry'],'states':old['states'],'runs':runs,'controls':controls,
        'preparations':preparations,'prior_equivalence_checks':equivalences,
        'source_file_sha256':{p:sha(ROOT/p) for p in sorted(files)},
        'validation_sha256':sha(OUT/'validation.txt'),
        'environment':{'python':platform.python_version(),'numpy':np.__version__},
        'acquisition_status':'not started','prior_coverage_gate':'failed',
        'scope':'prospective new-context recovery and detected-source resolution; existing controls are deterministic checks'})
    print('Frozen20 worlds,100 census snapshots,33 controls; no new responses',flush=True)

def verify():
    m=read(OUT/'manifest.json')
    require(m['config']==read(CONFIG) and m['rule_hash']==RULE_HASH,'configuration/rule changed')
    require(all(sha(ROOT/p)==h for p,h in m['source_file_sha256'].items()),'frozen source/input/code changed')
    require(sha(OUT/'validation.txt')==m['validation_sha256'],'validation changed')
    return m

def search(snapshot,identity,m,original=False):
    cfg=m['config']['search']; key=search_key(digest(snapshot),identity,cfg,original)
    folder=OUT/'searches'/key
    binding={'manifest_sha256':sha(OUT/'manifest.json'),'snapshot_hash':digest(snapshot),
             'input_identity':identity,'original_endpoint':original,'search_config':cfg,'rule_hash':RULE_HASH}
    if not verify_receipt(folder,binding):
        def persist(node,arrays):
            name='confirmation' if 'confirmation' in node else f'node-{node["node"]:02d}'
            atomic_json(folder/f'{name}.json',node);atomic_npz(folder/f'{name}.npz',**arrays)
        outcome=expanded_search(snapshot,identity,cfg,(lambda gt:gt==identity) if original else (lambda gt:True),persist,generation=offspring_generation)
        atomic_json(folder/'result.json',outcome);receipt(folder,binding)
    return key,read(folder/'result.json')

def control(spec,m):
    with np.load(ROOT/spec['file'],allow_pickle=False) as a: patch=a['snapshot'].copy()
    require(digest(patch)==spec['snapshot_hash'],'control snapshot changed')
    key,outcome=search(patch,spec['identity'],m,spec['kind']=='phase')
    return {**spec,'snapshot_file':spec['file'],'search_key':key,
            'search_dir':f'searches/{key}','transmission_confirmed':outcome['confirmation'] is not None,
            'confirmed_identity':outcome['confirmation']['identity'] if outcome['confirmation'] else None}

def benchmark():
    m=verify();require(not (OUT/'benchmark.json').exists(),'preserve benchmark')
    start=time.perf_counter(); result=control(m['controls'][0],m)
    require(result['transmission_confirmed'],'first positive control failed')
    atomic_json(OUT/'benchmark.json',{'status':'passed','control':result['name'],
        'seconds':time.perf_counter()-start,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'workers':1,'manifest_sha256':sha(OUT/'manifest.json'),'scope':'timing and repeated control, not replication'})
    print(read(OUT/'benchmark.json'),flush=True)

def world(spec,m):
    folder=OUT/'worlds'/spec['run_id'];binding={'manifest_sha256':sha(OUT/'manifest.json'),
                  'initial_hash':spec['initial_hash'],'run_id':spec['run_id']}
    if verify_receipt(folder,binding):return read(folder/'result.json')
    with np.load(ROOT/spec['initial_file'],allow_pickle=False) as a:g=a['grid'].copy()
    require(digest(g)==spec['initial_hash'],'initial physical hash changed')
    cfg=m['config']; samples=[]; sources=[]; totals=[];admitted=set();start=time.perf_counter()
    for t in range(0,cfg['horizon']+1,cfg['structural_sample_interval']):
        if t:advance(g,cfg['structural_sample_interval'])
        counts,records,loops=observation(g,m['registry']);samples.append({'t':t,**counts,'cores':records})
        if t not in cfg['source_times']:continue
        atomic_npz(folder/f'grid-{t}.npz',grid=g); rows=[]
        for o in sorted(loops,key=lambda o:tuple(o['core'])):
            patch=o['isolation_snapshot'];eligible=patch is not None and max(patch.shape)+20<=cfg['shape'][0]
            status='eligible' if eligible else 'component_too_large' if patch is not None else o['extraction_status']
            key=search_key(digest(patch),o['genotype'],cfg['search']) if eligible else None
            rootfile=f'roots/{key}.npz' if eligible else None
            outcome=None; directory=None
            if eligible:
                atomic_npz(OUT/rootfile,snapshot=patch)
                if key not in admitted and len(admitted)>=cfg['limits']['unique_admitted_keys_per_world']:
                    status='unsearched_budget'
                else:
                    admitted.add(key); key,outcome=search(patch,o['genotype'],m)
                    directory=f'searches/{key}';status='confirmed' if outcome['confirmation'] else 'unresolved_search'
            fields=search_fields(outcome,o['genotype'],m['registry'])
            row={'run_id':spec['run_id'],'state':spec['state'],'treatment':spec['treatment'],'t':t,
                 'core':o['core'],'source_identity':o['genotype'],'source_class':classify(o['genotype'],m['registry']),
                 'extraction_status':'eligible' if eligible else status,'snapshot_hash':digest(patch) if eligible else None,
                 'snapshot_file':rootfile,'search_key':key,'search_dir':directory,'status':status,**fields}
            rows.append(row);sources.append(row)
        totals.append({'t':t,**partition(rows)})
    atomic_npz(folder/'final.npz',grid=g)
    result={**spec,'rule_hash':RULE_HASH,'completed_updates':cfg['horizon'],'final_hash':digest(g),
            'samples':samples,'sources':sources,'snapshot_counts':totals,
            'admitted_distinct_keys':len(admitted),'seconds':time.perf_counter()-start}
    atomic_json(folder/'result.json',result);receipt(folder,binding)
    print('WORLD',spec['run_id'],'Q/C',sum(x['Q'] for x in totals),sum(x['C'] for x in totals),flush=True)
    return result

def summary(m,worlds,controls):
    rows=[r for w in worlds for r in w['sources']];cfg=m['config'];states=cfg['states']
    def threshold(q,c,value):return None if not c else Fraction(q,c)>=Fraction(value)
    scored=[r for r in rows if r['source_class']=='scored'];scored_states=[];resolved=[]
    for state in states:
        ss=[r for r in scored if r['state']==state];v=partition(ss)
        scored_states.append({'state':state,**v,'passed':threshold(v['Q'],v['C'],cfg['gates']['scored_per_state'])})
        for treatment in cfg['treatments']:
            v=partition([r for r in rows if r['state']==state and r['treatment']==treatment])
            resolved.append({'state':state,'treatment':treatment,**v,
                             'passed':threshold(v['Q'],v['C'],cfg['gates']['resolved_share_per_state_treatment'])})
    score=partition(scored);phase=[c for c in controls if c['kind']=='phase'];omitted=[c for c in controls if c['kind']=='omitted']
    checks={'phase_controls':sum(c['transmission_confirmed'] for c in phase)==30,
            'omitted_controls':sum(c['transmission_confirmed'] for c in omitted)==3,
            'scored_overall':threshold(score['Q'],score['C'],cfg['gates']['scored_overall']),
            'scored_per_state':conjunction(x['passed'] for x in scored_states),
            'resolved_share':conjunction(x['passed'] for x in resolved)}
    gate='failed' if False in checks.values() else 'unresolved' if None in checks.values() else 'passed'
    keys={r['search_key'] for r in rows if r['search_dir']}|{c['search_key'] for c in controls}
    return {'experiment_id':cfg['experiment_id'],'complete_worlds':len(worlds),'snapshot_strata':sum(len(w['snapshot_counts']) for w in worlds),
        'controls':{'phase_confirmed':sum(c['transmission_confirmed'] for c in phase),'phase_selected':len(phase),
                    'omitted_confirmed':sum(c['transmission_confirmed'] for c in omitted),'omitted_selected':len(omitted)},
        'gate_status':gate,'gate_checks':checks,'scored':score,'scored_per_state':scored_states,'resolution':resolved,
        'total':partition(rows),'by_class':[{'source_class':label,**partition([r for r in rows if r['source_class']==label])}
                                          for label in ('scored','valid_unregistered','unknown_identity')],
        'source_statuses':dict(Counter(r['status'] for r in rows)),
        'unique_searches':len(keys),'generation_simulations':sum(read(OUT/'searches'/key/'result.json')['generation_simulations'] for key in keys),
        'source_reproduction_observations':sum(r['root_reproduction_observed'] is True for r in rows),
        'prior_coverage_gate':'failed; unchanged','benefit':'not_assayed',
        'scope':'finite detected-source recovery; Q,R,C are not total viable population or independent histories'}

def run(commit):
    m=verify(); b=read(OUT/'benchmark.json')
    require(b['status']=='passed' and b['manifest_sha256']==sha(OUT/'manifest.json'),'manifest-bound benchmark first')
    require(commit and subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==commit,'frozen acquisition commit must be current HEAD')
    committed=subprocess.check_output(['git','show',f'{commit}:data/developmental-v1/manifest.json'],cwd=ROOT)
    require(hashlib.sha256(committed).hexdigest()==sha(OUT/'manifest.json'),'manifest must be committed before acquisition')
    atomic_json(OUT/'acquisition.json',{'freeze_commit':commit,'manifest_sha256':sha(OUT/'manifest.json')})
    start=time.perf_counter();controls=[control(c,m) for c in m['controls']]
    worlds=[world(r,m) for r in m['runs']]
    atomic_json(OUT/'results.json',{'experiment_id':m['experiment_id'],'manifest_sha256':sha(OUT/'manifest.json'),
        'worlds':[{'run_id':w['run_id'],'result_sha256':sha(OUT/'worlds'/w['run_id']/'result.json')} for w in worlds],
        'controls':controls,'seconds':time.perf_counter()-start,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
    atomic_json(OUT/'analysis.json',summary(m,worlds,controls))
    print('COMPLETE',read(OUT/'analysis.json')['gate_status'],flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['freeze','verify','benchmark','run']);p.add_argument('--freeze-commit');args=p.parse_args()
    if args.command=='freeze':freeze()
    elif args.command=='verify':print('Verified',len(verify()['source_file_sha256']),'frozen source/input/code hashes')
    elif args.command=='benchmark':benchmark()
    else:run(args.freeze_commit)
if __name__=='__main__':main()
