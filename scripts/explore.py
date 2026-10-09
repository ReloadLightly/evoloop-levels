"""Exploratory natural panel discovery, separate from the frozen atlas."""
import json
from pathlib import Path
import time
import numpy as np
from evoloop.engine import ROOT, seed13, advance, place, digest, RULE_HASH
from evoloop.tracking import detect
from evoloop.assays import inheritance

def main():
    out=ROOT/'data/exploration';out.mkdir(exist_ok=True)
    g=np.zeros((160,160),dtype=np.uint8);place(g,seed13(),65,45)
    np.savez_compressed(out/'initial.npz',grid=g)
    baseline=detect(g)[0]['genotype'];panel=[dict(id='S13',genotype=baseline,source='CellPyLib documented species13 seed',t=0)]
    np.savez_compressed(out/'S13.npz',snapshot=seed13())
    checked={};attempts={};discoveries=[];frames=[]
    start=time.perf_counter()
    for t in range(0,12001,10):
        if t:advance(g,10)
        if t%100==0:frames.append(g.copy())
        for o in detect(g):
            gt=o['genotype']
            if not gt or gt==baseline or gt in checked or o['isolation_snapshot'] is None:continue
            # Up to four naturally occurring circulation phases per genotype.
            seen=attempts.setdefault(gt,set())
            sh=digest(o['isolation_snapshot'])
            if sh in seen or len(seen)>=4:continue
            seen.add(sh)
            test,evidence=inheritance(o['isolation_snapshot'],gt)
            item=dict(t=t,core=o['core'],genotype=gt,snapshot_hash=o['snapshot_hash'],isolation=test)
            discoveries.append(item)
            print('discovery attempt',t,gt,test['status'],flush=True)
            if test['status']=='confirmed' and test['stable_genotype'] not in [p['genotype'] for p in panel]:
                pid=f'N{len(panel):02d}';checked[gt]=pid
                snap=o['isolation_snapshot'] if test['stable_genotype']==gt else evidence[0]
                np.savez_compressed(out/f'{pid}.npz',snapshot=snap,child=evidence[0],grandchild=evidence[1],
                                    source_grid=g,first_generation=evidence[2],second_generation=evidence[3])
                panel.append(dict(id=pid,genotype=test['stable_genotype'],source='natural descendant in EXP-discovery-001',t=t,core=o['core'],isolation=test))
                print('verified natural variant',pid,gt,'at',t,flush=True)
        if len(panel)>=3:break
    np.savez_compressed(out/'world.npz',frames=np.array(frames),times=np.arange(len(frames))*100)
    report={'experiment_id':'EXP-discovery-001','rule_hash':RULE_HASH,'shape':[160,160],
            'horizon_actual':t,'sampling_interval':10,'initial_hash':digest(np.load(out/'initial.npz')['grid']),
            'seconds':time.perf_counter()-start,'panel':panel,'discoveries':discoveries}
    (out/'discovery.json').write_text(json.dumps(report,indent=2)+'\n')
    print('panel',len(panel),'attempts',len(discoveries),'seconds',report['seconds'])

if __name__=='__main__':main()
