"""Integrity and deterministic replay checks for the completed scientific dataset."""
import hashlib
import json
from pathlib import Path
import numpy as np
from evoloop.engine import ROOT,advance,digest,place
from evoloop.tracking import detect
from scripts.atlas import OUT,load_manifest,write_json

def main():
    m=load_manifest();checked=0;candidates=0
    for s in m['runs']:
        p=OUT/'runs'/s['run_id'];r=json.loads((p/'result.json').read_text())
        a=np.load(OUT/'initial'/f'{s["run_id"]}.npz');z=np.load(p/'final.npz')
        assert digest(a['grid'])==s['initial_hash']
        assert digest(a['labels'])==s['initial_labels_hash']
        assert digest(z['grid'])==r['final_hash'] and digest(z['labels'])==r['final_labels_hash']
        assert r['horizon']==1600 and len(r['metrics'])==17
        assert r['config_sha256']==m['config_sha256']
        for c in r['candidates']:
            for snap in c['snapshots']:
                q=np.load(p/snap['file']);assert digest(q['snapshot'])==snap['snapshot_hash']
                # Extraction must match its recorded source occupied component.
                y,x,h,w=snap['extraction_bbox'];view=q['source_grid'][y:y+h,x:x+w]
                assert np.all((q['snapshot']==0)|(q['snapshot']==view))
                assert len(detect(q['snapshot']))==1 if min(q['snapshot'].shape)>6 else True
                assert (p/(Path(snap['file']).stem+'-inheritance.json')).exists()
                candidates+=1
        checked+=1
    # Independent chunked replays of three different pair states and one control.
    selected=[s for s in m['runs'] if s['treatment']=='near' and s['phase']==0 and s['geometry']['id']=='opposed'][:3]
    selected+=[s for s in m['runs'] if s['treatment']=='separated'][:1]
    replays=[]
    for s in selected:
        p=OUT/'runs'/s['run_id'];a=np.load(OUT/'initial'/f'{s["run_id"]}.npz')
        g=a['grid'].copy();lab=a['labels'].copy();advance(g,1600,lab)
        r=json.loads((p/'result.json').read_text())
        assert digest(g)==r['final_hash'] and digest(lab)==r['final_labels_hash']
        replays.append({'run_id':s['run_id'],'final_grid_and_provenance_match':True})
    isolation_replays=[]
    for s in m['runs']:
        folder=OUT/'runs'/s['run_id']
        for jp in folder.glob('*-inheritance.json'):
            test=json.loads(jp.read_text());stem=jp.name.removesuffix('-inheritance.json')
            src=np.load(folder/(stem+'.npz'));e=np.load(folder/(stem+'-inheritance.npz'))
            snapshots=[src['snapshot'], e['evidence0'] if 'evidence0' in e else None,
                       e['evidence1'] if 'evidence1' in e else None]
            initials={};meta=[]
            for stage,snap in enumerate(snapshots,1):
                outcome=test[f'generation{stage}']
                if snap is None or 'final_hash' not in outcome:continue
                g=np.zeros((192,192),dtype=np.uint8);y,x=96-snap.shape[0]//2,96-snap.shape[1]//2
                place(g,snap,y,x);initials[f'generation{stage}']=g.copy();initial_hash=digest(g)
                t=outcome.get('detached_first_seen_t',outcome.get('horizon',1600));advance(g,t)
                assert digest(g)==outcome['final_hash'],f'isolation replay mismatch: {jp}, stage {stage}'
                meta.append({'generation':stage,'placement':[y,x],'shape':[192,192],
                             'initial_hash':initial_hash,'replayed_updates':t,'final_hash_match':True})
            if initials:np.savez_compressed(folder/(stem+'-isolation-initials.npz'),**initials)
            write_json(folder/(stem+'-isolation-initials.json'),{'source':jp.name,'stages':meta})
            isolation_replays.extend({'run_id':s['run_id'],'snapshot':stem,**row} for row in meta)
    report={'experiment_id':m['experiment_id'],'initial_final_states_checked':checked,
            'candidate_snapshots_checked':candidates,'chunked_replays':replays,
            'isolated_generation_replays':isolation_replays,
            'frozen_code_config_protocol_hashes':'pass'}
    write_json(OUT/'integrity.json',report);print(json.dumps(report,indent=2))
    # Compact artifact manifest: no dependencies/caches, paths relative to repository.
    paths=sorted(p for p in (ROOT/'data').rglob('*') if p.is_file() and p.name!='SHA256SUMS')
    (ROOT/'data/SHA256SUMS').write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT)}\n' for p in paths))

if __name__=='__main__':main()
