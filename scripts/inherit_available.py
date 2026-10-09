"""Complete isolation evidence for available runs while acquisition continues.

Does not write the global completed-batch inheritance ledger. The frozen full
runner later joins these exact per-snapshot results without repeating assays.
"""
import json
from pathlib import Path
import numpy as np
from evoloop.engine import digest
from evoloop.assays import inheritance
from scripts.atlas import OUT,load_manifest,write_json

def main():
    m=load_manifest();count=0
    for spec in m['runs']:
        folder=OUT/'runs'/spec['run_id'];rp=folder/'result.json'
        if not rp.exists():continue
        r=json.loads(rp.read_text());inputs={m['panel'][pid]['genotype'] for pid in (spec['focal'],spec['partner']) if pid}
        for c in r['candidates']:
            for snap in c['snapshots']:
                p=folder/snap['file'];target=folder/(p.stem+'-inheritance.json')
                if target.exists():continue
                a=np.load(p)['snapshot'];assert digest(a)==snap['snapshot_hash']
                test,e=inheritance(a,c['genotype'],m['config']['inheritance_horizon_per_generation'])
                test['stable_novel_vs_both_inputs']=bool(test['status']=='confirmed' and test['stable_genotype'] not in inputs)
                test['encounter_observed_genotype']=c['genotype']
                test['stable_genotype_observed_in_encounter']=test.get('stable_genotype') in [z['genotype'] for z in r['candidates']]
                test['source']=snap;write_json(target,test)
                arrays={f'evidence{k}':a for k,a in enumerate(e) if a is not None}
                if arrays:np.savez_compressed(folder/(p.stem+'-inheritance.npz'),**arrays)
                print(spec['run_id'],snap['file'],test['status'],'stable',test['stable_genotype'],'novel',test['stable_novel_vs_both_inputs'],flush=True)
                count+=1
    print('Completed',count,'additional isolation paths; global ledger awaits all runs.')

if __name__=='__main__':main()
