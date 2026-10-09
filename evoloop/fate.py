"""Bounded multi-offspring isolation calibration; the CA dynamics are unchanged."""
import numpy as np
from .engine import advance, digest, place
from .tracking import detect


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


def expanded_search(snapshot, identity, cfg, accept, persist, generation=offspring_generation):
    """DFS with a hard simulation cap; accept is the prospectively fixed endpoint."""
    nodes=[];confirmation=None;truncations=[];stable_observations=[]
    def visit(snap,gt,streak,depth,parent=None,edge=None,path=()):
        nonlocal confirmation
        if len(nodes)>=cfg['max_generation_simulations_per_root']:
            truncations.append({'reason':'simulation_budget','path':list(path),'depth':depth});return
        node_id=len(nodes);report,arrays=generation(snap,cfg)
        node={'node':node_id,'parent_node':parent,'incoming_child':edge,'path':list(path),'depth':depth,
              'input_identity':gt,'input_snapshot_hash':digest(snap),'incoming_streak':streak,'outcome':report}
        nodes.append(node);persist(node,arrays)
        order=sorted(range(len(report['children'])),key=lambda i:(report['children'][i]['detached_t'],
                    tuple(report['children'][i]['core']),report['children'][i]['snapshot_hash']))
        for i in order:
            child=report['children'][i];new_gt=child['identity'];new_streak=streak+1 if new_gt==gt else 0
            if new_streak>=cfg['stable_transmissions']:
                stable_observations.append({'identity':new_gt,'node':node_id,'child':i,
                                            'accepted_endpoint':bool(accept(new_gt)),
                                            'path':list(path+(i,))})
            if new_streak>=cfg['stable_transmissions'] and accept(new_gt):
                confirmation={'identity':new_gt,'node':node_id,'child':i,'transmission_streak':new_streak,
                              'path':list(path+(i,)),'snapshot_hash':child['snapshot_hash']}
                persist({'confirmation':confirmation}, {'stable_snapshot':arrays[f'child{i}']});return
            if not child['size_eligible']:
                truncations.append({'reason':'component_size','path':list(path+(i,)),'depth':depth+1});continue
            if depth>=cfg['max_depth']:
                truncations.append({'reason':'depth_limit','path':list(path+(i,)),'depth':depth+1});continue
            visit(arrays[f'child{i}'],new_gt,new_streak,depth+1,node_id,i,path+(i,))
            if confirmation:return
    visit(snapshot,identity,0,1)
    return {'status':'confirmed' if confirmation else 'unresolved', 'confirmation':confirmation,
            'generation_simulations':len(nodes),'nodes':nodes,'truncations':truncations,
            'stable_observations':stable_observations,
            'stable_paths':'serial imposed isolation; not native ancestry'}
