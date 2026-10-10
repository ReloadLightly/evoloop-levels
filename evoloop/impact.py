"""Explicit whole-component population-removal policy; no CA rule changes."""
import numpy as np

from .engine import digest
from .periodic_tracking import detect


def complete_mask(grid, organism):
    snapshot = organism['isolation_snapshot']
    if snapshot is None:
        return None
    y, x, h, w = organism['extraction_bbox']
    rows, cols = (np.arange(h)+y)%grid.shape[0], (np.arange(w)+x)%grid.shape[1]
    mask = np.zeros(grid.shape, bool)
    mask[np.ix_(rows, cols)] = snapshot != 0
    assert np.array_equal(grid[np.ix_(rows, cols)][snapshot != 0], snapshot[snapshot != 0])
    return mask


def eligible_population(loops, registry):
    return len(loops) == 3 and all(o['genotype'] in registry and
        o['isolation_snapshot'] is not None for o in loops)


def select_component(loops, registry, initial_core, vector, shape):
    eligible = [o for o in loops if o['genotype'] in registry and o['isolation_snapshot'] is not None]
    if not eligible:
        return None
    def rank(o):
        delta = [((o['core'][i]-initial_core[i]+shape[i]//2)%shape[i])-shape[i]//2 for i in (0,1)]
        return sum(a*b for a,b in zip(delta,vector)), tuple(o['core'])
    return max(eligible, key=rank)


def removal(grid, organism, registry):
    before = detect(grid); mask = complete_mask(grid, organism)
    assert mask is not None and np.any(mask)
    result = grid.copy(); result[mask] = 0
    after = detect(result)
    remaining = sorted((tuple(o['core']), o['genotype'], digest(o['isolation_snapshot'])
                        if o['isolation_snapshot'] is not None else None)
                       for o in before if o['core'] != organism['core'])
    actual = sorted((tuple(o['core']), o['genotype'], digest(o['isolation_snapshot'])
                     if o['isolation_snapshot'] is not None else None) for o in after)
    report = {'removed_core': organism['core'], 'removed_identity': organism['genotype'],
        'removed_snapshot_hash': digest(organism['isolation_snapshot']),
        'removed_occupied_cells': int(mask.sum()), 'occupied_before': int(np.count_nonzero(grid)),
        'registered_before': sum(o['genotype'] in registry for o in before),
        'registered_after': sum(o['genotype'] in registry for o in after),
        'remaining_components_unchanged': remaining == actual,
        'before_hash': digest(grid), 'after_hash': digest(result), 'mask_hash': digest(mask.astype(np.uint8))}
    report['matched_impact'] = report['registered_before'] == 3 and report['registered_after'] == 2 and remaining == actual
    return result, mask.astype(np.uint8), report
