"""Predeclared exploratory diagnostic of a multi-transient isolated lineage."""
import hashlib
import json
import numpy as np
from evoloop.engine import ROOT,RULE_HASH,digest
from evoloop.assays import generation
from scripts.atlas import load_manifest,write_json

def main():
    m=load_manifest();folder=ROOT/'data/lineage-followup';folder.mkdir(exist_ok=True)
    origin='near-main-N01-N01-p0-offset';file='candidate-9f6cc7c1ea89-0.npz'
    source=ROOT/f'data/atlas/runs/{origin}/{file}';snap=np.load(source)['snapshot']
    meta=json.loads((source.parent/(source.stem+'-inheritance.json')).read_text())
    gt=meta['input_genotype'];initial_gt=gt;streak=0;stages=[];confirmed=False
    for stage in range(1,7):
        input_hash=digest(snap);r,child,g=generation(snap,None,1600)
        arrays={'input':snap}
        if g is not None:arrays['final_grid']=g
        if child is not None:arrays['offspring']=child
        np.savez_compressed(folder/f'stage-{stage}.npz',**arrays)
        next_gt=r.get('offspring_genotype');streak=streak+1 if next_gt==gt else 0
        stages.append({'stage':stage,'input_identity':gt,'input_hash':input_hash,'outcome':r,
                       'stable_transmission_streak':streak})
        print('stage',stage,gt,'->',next_gt,r['status'],'streak',streak,flush=True)
        if child is None:break
        snap=child;gt=next_gt
        if streak>=2:confirmed=True;break
    input_words={m['panel'][pid]['genotype'].split(':',1)[1] for pid in ('N01',)}
    report={'experiment_id':'EXP-lineage-followup-001','status':'exploratory_after_atlas_observation',
            'originating_encounter':origin,'source_snapshot':file,'source_snapshot_hash':digest(np.load(source)['snapshot']),
            'source_identity':initial_gt,'source_time':meta['source']['t'],'rule_hash':RULE_HASH,
            'protocol_sha256':hashlib.sha256((ROOT/'protocols/003-exploratory-lineage-followup.md').read_bytes()).hexdigest(),
            'stages':stages,'stable_path_confirmed':confirmed,'stable_identity':gt if confirmed else None,
            'stable_signal_novel_vs_inputs':bool(confirmed and gt.split(':',1)[1] not in input_words),
            'main_atlas_endpoint':'unchanged','benefit_status':'pending','ancestry':'ambiguous originating pair; serial isolation intervention'}
    write_json(folder/'result.json',report)
    if confirmed:np.savez_compressed(folder/'stable-organism.npz',snapshot=snap)
    print('Exploratory stable path:',report['stable_path_confirmed'],'signal novel:',report['stable_signal_novel_vs_inputs'])

if __name__=='__main__':main()
