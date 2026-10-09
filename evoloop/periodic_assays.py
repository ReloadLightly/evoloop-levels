"""Versioned seam-aware isolation measurement for the fresh atlas."""
import numpy as np
from .engine import advance, digest, place
from .periodic_tracking import detect


def isolated_initial(snapshot, size=192):
    if max(snapshot.shape)+20 > size:
        return None
    grid=np.zeros((size,size),dtype=np.uint8)
    place(grid,snapshot,size//2-snapshot.shape[0]//2,size//2-snapshot.shape[1]//2)
    return grid


def offspring_generation(snapshot, cfg):
    initial=isolated_initial(snapshot,cfg['isolation_shape'][0])
    if initial is None:
        return {'status':'ineligible_component_size','children':[]}, {}
    grid=initial.copy();originals={tuple(o['core']) for o in detect(grid)}
    admitted=set();first_seen={};children=[];arrays={'initial':initial};samples=[];events=[];prev=set()
    boundary=None;horizon=cfg['generation_horizon'];interval=cfg['detection_interval']
    for t in range(0,horizon+1,interval):
        if t:advance(grid,interval)
        if boundary is None and (np.any(grid[[0,-1]]) or np.any(grid[:,[0,-1]])):boundary=t
        loops=detect(grid);now={tuple(o['core']) for o in loops}
        for o in loops:
            core=tuple(o['core'])
            if core not in prev:
                first_seen.setdefault(core,t)
                events.append({'type':'core_appearance','t':t,'core':o['core'],'identity':o['genotype']})
            if core in originals or core in admitted or not o['genotype'] or o['isolation_snapshot'] is None:continue
            snap=o['isolation_snapshot'];admitted.add(core)
            child={'detached_t':t,'closure_first_seen_t':first_seen[core],'core':o['core'],
                   'identity':o['genotype'],'snapshot_hash':digest(snap),'extraction_bbox':o['extraction_bbox'],
                   'size_eligible':max(snap.shape)+20<=cfg['isolation_shape'][0]}
            children.append(child);arrays[f'child{len(children)-1}']=snap
            # The complete selection state makes component extraction reviewable.
            arrays[f'selection_grid{len(children)-1}']=grid.copy()
            if len(children)>=cfg['offspring_per_generation']:break
        for core in sorted(prev-now):events.append({'type':'core_loss','t':t,'core':list(core)})
        prev=now
        if t%100==0:samples.append({'t':t,'closed_cores':len(loops),'occupied_cells':int(np.count_nonzero(grid))})
        if len(children)>=cfg['offspring_per_generation']:break
    arrays['final']=grid.copy()
    report={'status':'offspring_observed' if children else 'unresolved_at_horizon' if np.any(grid) else 'assay_extinct',
            'initial_hash':digest(initial),'final_hash':digest(grid),'completed_updates':t,'horizon':horizon,
            'sampling_interval':interval,'boundary_first_t':boundary,'children':children,'samples':samples,'events':events}
    return report,arrays

