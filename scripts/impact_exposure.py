"""Exposure-only pilot: never continue a disturbed state or calculate response."""
import hashlib
import json
import resource
import time
import numpy as np

from evoloop.engine import ROOT, RULE_HASH, advance, digest
from evoloop.ecology import prepared_grid, observation
from evoloop.periodic_tracking import detect
from evoloop.impact import eligible_population, select_component, removal
from scripts.atlas import write_json

OUT = ROOT/'data/impact-exposure-v1'
OFFSETS = [0,40,80,120,160,200]
VECTORS = [[1,2],[-2,1],[2,-3],[-3,-1]]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not (OUT/'report.json').exists(), 'preserve the completed pilot'
    started = time.perf_counter(); OUT.mkdir(parents=True, exist_ok=True)
    source = json.loads((ROOT/'data/ecological-v1/manifest.json').read_text())
    registry = source['registry']; records = []
    with np.load(ROOT/'data/ecological-v1/snapshots.npz') as snapshots:
        for pid in source['config']['states']:
            folder = OUT/pid; folder.mkdir(exist_ok=True)
            grid = prepared_grid(snapshots[pid], [192,192], 0)
            initial_core = detect(grid)[0]['core']; initial_hash = digest(grid)
            np.savez_compressed(folder/'initial.npz', grid=grid)
            anchor = None; samples = []; phases = []
            for t in range(0,2201,10):
                if t: advance(grid,10)
                counts, cores, loops = observation(grid,registry)
                samples.append({'t':t,**counts,'cores':cores})
                if anchor is None and t <= 2000 and eligible_population(loops,registry):
                    anchor = t
                if anchor is not None and t-anchor in OFFSETS:
                    offset = t-anchor
                    np.savez_compressed(folder/f'phase-{offset}.npz',grid=grid)
                    choices = []
                    for i, vector in enumerate(VECTORS):
                        selected = select_component(loops,registry,initial_core,vector,grid.shape)
                        if selected is None:
                            choices.append({'vector':vector,'status':'no_eligible_component'}); continue
                        post,mask,impact = removal(grid,selected,registry)
                        np.savez_compressed(folder/f'exposure-{offset}-{i}.npz',before=grid,after=post,mask=mask)
                        choices.append({'vector':vector,**impact})
                    phases.append({'offset':offset,'t':t,'hash':digest(grid),
                                   'eligible_population':eligible_population(loops,registry),'choices':choices})
                if anchor is not None and t == anchor+OFFSETS[-1]: break
                if anchor is None and t == 2000:break
            record = {'state':pid,'initial_hash':initial_hash,'initial_core':initial_core,
                      'anchor_t':anchor,'completed_updates':t,'samples':samples,'phases':phases}
            write_json(folder/'result.json',record); records.append(record)
            print(pid,'anchor',anchor,'offsets',[(p['offset'],p['eligible_population']) for p in phases],flush=True)
    write_json(OUT/'report.json',{'experiment_id':'EXP-impact-exposure-001','rule_hash':RULE_HASH,
        'protocol_sha256':sha(ROOT/'protocols/008-impact-exposure-calibration.md'),
        'code_sha256':{name:sha(ROOT/name) for name in ['evoloop/impact.py','scripts/impact_exposure.py']},
        'source_sha256':{name:sha(ROOT/name) for name in ['data/ecological-v1/manifest.json','data/ecological-v1/snapshots.npz']},
        'offsets':OFFSETS,'vectors':VECTORS,'states':records,
        'seconds':time.perf_counter()-started,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'scope':'pre-response preparation and removal only; no disturbed continuation or score selection'})


if __name__ == '__main__': main()
