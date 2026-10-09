"""Standardized isolation tests; destructive isolation is explicitly an assay intervention."""
import numpy as np
from .engine import advance, place, digest
from .tracking import detect

def generation(snapshot, genotype=None, horizon=1600, size=192, interval=10):
    if max(snapshot.shape)+20 > size:
        return {'status':'ineligible_component_size','shape':list(snapshot.shape),'horizon':horizon},None,None
    grid=np.zeros((size,size),dtype=np.uint8)
    y,x=size//2-snapshot.shape[0]//2,size//2-snapshot.shape[1]//2
    place(grid,snapshot,y,x)
    originals={tuple(o['core']) for o in detect(grid)}
    samples=[];other_genotypes=set();first_seen={}
    for t in range(0,horizon+1,interval):
        if t:advance(grid,interval)
        loops=detect(grid)
        if t%100==0:samples.append({'t':t,'closed_cores':len(loops)})
        for o in loops:
            if o['genotype']:other_genotypes.add(o['genotype'])
            if tuple(o['core']) not in originals:first_seen.setdefault(tuple(o['core']),t)
            if o['genotype'] and (genotype is None or o['genotype']==genotype) and tuple(o['core']) not in originals and o['isolation_snapshot'] is not None:
                return {'status':'reproduced','closure_first_seen_t':first_seen[tuple(o['core'])],
                        'detached_first_seen_t':t,'sampling_interval':interval,'core':o['core'],
                        'offspring_genotype':o['genotype'], 'extraction_bbox':o['extraction_bbox'],
                        'final_hash':digest(grid),'samples':samples},o['isolation_snapshot'],grid.copy()
    return {'status':'unresolved_at_horizon' if np.any(grid) else 'extinct',
            'horizon':horizon,'final_hash':digest(grid),'observed_genotypes':sorted(other_genotypes),
            'samples':samples},None,grid.copy()

def inheritance(snapshot, genotype, horizon=1600):
    first,child,grid1=generation(snapshot,None,horizon)
    stable=first.get('offspring_genotype')
    second,grandchild,grid2=generation(child,stable,horizon) if child is not None else ({'status':'not_run'},None,None)
    third,great,grid3=({'status':'not_needed'},None,None)
    if stable and stable!=genotype and grandchild is not None:
        third,great,grid3=generation(grandchild,stable,horizon)
    confirmed=second['status']=='reproduced' and third['status'] in ('not_needed','reproduced')
    status='confirmed' if confirmed else 'unresolved' if first['status']!='extinct' else 'assay_extinct'
    return {'status':status,'input_genotype':genotype,'stable_genotype':stable if confirmed else None,
            'transient_path':bool(stable and stable!=genotype),'generation1':first,'generation2':second,
            'generation3':third},(child,grandchild,grid1,grid2,grid3)
