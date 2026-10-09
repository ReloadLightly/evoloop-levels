"""Prospective natural panel selection; freeze before run."""
import argparse,hashlib,json,resource,time
import numpy as np
from evoloop.engine import ROOT,RULE_HASH,advance,place,digest,seed13,crop
from evoloop.periodic_tracking import detect
from evoloop.periodic_assays import offspring_generation
from scripts.atlas import write_json

OUT=ROOT/'data/panel-v2';CFG=ROOT/'configs/panel-v2.json';PROTOCOL=ROOT/'protocols/005-natural-panel-discovery.md'
FILES=['evoloop/kernel.c','evoloop/engine.py','evoloop/tracking.py','evoloop/periodic_tracking.py','evoloop/periodic_assays.py','scripts/panel_discovery.py']
def hashes():return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in FILES}
def word(gt):return gt.split(':',1)[1] if gt else None

def freeze():
    assert not (OUT/'manifest.json').exists()
    OUT.mkdir(parents=True,exist_ok=True);cfg=json.loads(CFG.read_text());sources={'S13':seed13(),'N01':np.load(ROOT/'data/exploration/N01.npz')['snapshot']}
    specs=[]
    for h in cfg['histories']:
        g=np.zeros(h['shape'],np.uint8);a=sources[h['focal']];place(g,a,h['y'],h['x'])
        if h['partner']:place(g,sources[h['partner']],h['y']+h['dy'],h['x']+a.shape[1]+h['gap'],h['rotation'])
        np.savez_compressed(OUT/f'{h["id"]}-initial.npz',grid=g)
        specs.append({**h,'initial_hash':digest(g)})
    old=np.load(ROOT/'data/exploration/N01.npz')
    original=json.loads((ROOT/'data/exploration/discovery.json').read_text())['discoveries'][-1]
    native=next(o for o in detect(old['source_grid']) if o['core']==original['core'] and o['genotype']==original['genotype'])
    assert native['isolation_snapshot'] is not None
    np.savez_compressed(OUT/'imported-N01.npz',snapshot=native['isolation_snapshot'],source_grid=old['source_grid'])
    write_json(OUT/'manifest.json',{'experiment_id':cfg['experiment_id'],'rule_hash':RULE_HASH,'config':cfg,'histories':specs,'code_hashes':hashes(),
        'config_hash':hashlib.sha256(CFG.read_bytes()).hexdigest(),'protocol_hash':hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        'imported_source_hash':digest(old['source_grid']),'imported_snapshot_hash':digest(native['isolation_snapshot']),'imported_native_identity':native['genotype'],'imported_native_core':native['core']})
    print('Frozen discovery',cfg['experiment_id'],flush=True)

def load():
    m=json.loads((OUT/'manifest.json').read_text());assert m['code_hashes']==hashes();assert m['rule_hash']==RULE_HASH
    assert m['config_hash']==hashlib.sha256(CFG.read_bytes()).hexdigest()
    assert m['protocol_hash']==hashlib.sha256(PROTOCOL.read_bytes()).hexdigest();return m

def verify_source(snap,gt,source,name,cfg):
    folder=OUT/'trials'/name;folder.mkdir(parents=True,exist_ok=True)
    stages=[];original=snap.copy();current=snap;stable=None
    for k in range(3):
        report,arrays=offspring_generation(current,cfg);np.savez_compressed(folder/f'g{k+1}.npz',**arrays)
        write_json(folder/f'g{k+1}.json',report);stages.append(report)
        if not report['children']:break
        child=report['children'][0];new=child['identity']
        if k==0:stable=new
        if new!=stable:break
        current=arrays['child0']
    valid=len(stages)==3 and all(r['children'] and r['children'][0]['identity']==stable for r in stages)
    reason='verified' if valid else 'unresolved_or_identity_changed'
    if valid and max(current.shape)+20>cfg['isolation_shape'][0]:valid=False;reason='final_component_oversize'
    if valid and word(stable)!=word(gt):valid=False;reason='stable_word_not_native_source_word'
    phases={}
    if valid:
        for phase in cfg['phases']:
            g=np.zeros(cfg['isolation_shape'],np.uint8);place(g,current,96-current.shape[0]//2,96-current.shape[1]//2);advance(g,phase)
            loops=detect(g)
            if len(loops)!=1 or loops[0]['genotype']!=stable or np.any(g[[0,-1]]) or np.any(g[:,[0,-1]]):
                valid=False;reason='phase_ineligible';break
            phases[f'p{phase}']=crop(g)
    np.savez_compressed(folder/'source.npz',snapshot=original,source_grid=source['grid'])
    if valid:np.savez_compressed(folder/'verified.npz',snapshot=current,**phases)
    result={'eligible':valid,'reason':reason,'native_identity':gt,'stable_identity':stable if valid else None,
            'native_word':word(gt),'morphological_stabilization':bool(valid and gt!=stable),
            'snapshot_hash':digest(current) if valid else None,'source':{k:v for k,v in source.items() if k!='grid'},'stages':stages,'trial':name}
    write_json(folder/'result.json',result);return result

def run():
    m=load();cfg=m['config'];start=time.perf_counter();panel=[];trials=[];histories=[]
    imported=np.load(OUT/'imported-N01.npz');gt=m['imported_native_identity']
    assert digest(imported['snapshot'])==m['imported_snapshot_hash']
    assert digest(imported['source_grid'])==m['imported_source_hash']
    first=verify_source(imported['snapshot'],gt,{'grid':imported['source_grid'],'history':'EXP-discovery-001','t':2910,'core':m['imported_native_core'],'source_hash':m['imported_source_hash'],'note':'same native complete component originally observed at update2910'},'imported-N01',cfg)
    trials.append(first)
    if first['eligible']:panel.append({'id':'V01',**first})
    baseline=word(detect(np.load(OUT/'D01-initial.npz')['grid'])[0]['genotype'])
    for spec in m['histories']:
        if len(panel)>=cfg['target_identities']:break
        g=np.load(OUT/f'{spec["id"]}-initial.npz')['grid'].copy();assert digest(g)==spec['initial_hash'];seen={};attempts=0;metrics=[];frames=[];times=[];unexamined=set()
        for t in range(0,spec['horizon']+1,cfg['sampling_interval']):
            if t:advance(g,cfg['sampling_interval'])
            loops=detect(g)
            if t%cfg['metrics_interval']==0:
                metrics.append({'t':t,'closed_cores':len(loops),'occupied_cells':int(np.count_nonzero(g))})
                frames.append(g.copy());times.append(t)
            for o in loops:
                gt=o['genotype'];snap=o['isolation_snapshot']
                if not gt or word(gt)==baseline or word(gt) in {word(p['stable_identity']) for p in panel}:continue
                if snap is None:unexamined.add(gt);continue
                sh=digest(snap);used=seen.setdefault(gt,set())
                if sh in used:continue
                if len(used)>=cfg['attempts_per_source_identity'] or attempts>=cfg['attempts_per_history']:unexamined.add(gt);continue
                used.add(sh);attempts+=1;name=f'{spec["id"]}-{attempts:02d}'
                result=verify_source(snap,gt,{'grid':g,'history':spec['id'],'t':t,'core':o['core'],'extraction_bbox':o['extraction_bbox'],'source_hash':digest(g)},name,cfg)
                trials.append(result);print(name,'t',t,gt,result['reason'],flush=True)
                if result['eligible'] and word(result['stable_identity']) not in {word(p['stable_identity']) for p in panel}:
                    panel.append({'id':f'V{len(panel)+1:02d}',**result});print('ADMITTED',panel[-1]['id'],result['stable_identity'],flush=True)
                if len(panel)>=cfg['target_identities']:break
            if len(panel)>=cfg['target_identities']:break
        np.savez_compressed(OUT/f'{spec["id"]}-world.npz',frames=np.array(frames),times=np.array(times),final=g)
        histories.append({'id':spec['id'],'completed_updates':t,'final_hash':digest(g),'attempts':attempts,'metrics':metrics,'unexamined_identities':sorted(unexamined)})
    for p in panel:
        a=np.load(OUT/'trials'/p['trial']/'verified.npz');np.savez_compressed(OUT/f'{p["id"]}.npz',**{k:a[k] for k in a.files})
    report={'experiment_id':m['experiment_id'],'status':'target_reached' if len(panel)==cfg['target_identities'] else 'shortfall',
        'panel':panel,'trials':trials,'histories':histories,'seconds':time.perf_counter()-start,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    write_json(OUT/'discovery.json',report);print('DONE',report['status'],len(panel),report['seconds'],flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['freeze','run']);a=p.parse_args();{'freeze':freeze,'run':run}[a.command]()
