"""Standardized clone placement and complete-state equivalence, not CA physics."""
import numpy as np
from fractions import Fraction
from .engine import digest, place
from .ecology import prepared_grid
from .periodic_tracking import detect
from .impact import complete_mask, removal


def phase_patch(snapshot, age, shape, identity):
    from .engine import advance
    grid = prepared_grid(snapshot, shape, 0)
    advance(grid, age)
    loops = detect(grid)
    assert len(loops) == 1 and loops[0]['genotype'] == identity, 'ineligible phase core'
    o = loops[0]; mask = complete_mask(grid, o)
    assert mask is not None and int(mask.sum()) == int(np.count_nonzero(grid)), 'incomplete phase component'
    patch = o['isolation_snapshot'].copy()
    y,x,_,_ = o['extraction_bbox']
    offset = [(o['core'][0]-y)%shape[0], (o['core'][1]-x)%shape[1]]
    return grid, patch, offset


def assemble(patch, offset, sites, remove_index, shape, registry):
    grid = np.zeros(shape, np.uint8)
    for site in sites:
        place(grid, patch, site[0]-offset[0], site[1]-offset[1])
    loops = detect(grid)
    assert len(loops) == 3 and all(o['genotype'] in registry for o in loops)
    assert sorted(o['core'][:2] for o in loops) == sorted(sites)
    assert all(o['isolation_snapshot'] is not None and np.array_equal(o['isolation_snapshot'],patch) for o in loops)
    assert np.count_nonzero(grid) == 3*np.count_nonzero(patch)
    target = next(o for o in loops if o['core'][:2] == sites[remove_index])
    after, mask, impact = removal(grid, target, registry)
    assert impact['matched_impact'] and impact['occupied_before'] == 3*impact['removed_occupied_cells']
    return grid, after, mask, impact


def equivalent(a, b):
    """Exact equality under all four rotations and every torus translation."""
    if a.shape != b.shape or not np.array_equal(np.bincount(a.ravel(),minlength=9),np.bincount(b.ravel(),minlength=9)):
        return None
    counts = np.bincount(a.ravel(), minlength=9)
    present = [i for i in range(1,len(counts)) if counts[i]]
    if not present:
        return {'rotation':0,'translation':[0,0]}
    state = min(present,key=lambda i: counts[i]); targets = np.argwhere(b == state)
    for k in range(4):
        rotated = np.rot90(a,k); anchor = np.argwhere(rotated == state)[0]
        for target in targets:
            shift = target-anchor
            if np.array_equal(np.roll(rotated,tuple(shift),axis=(0,1)),b):
                return {'rotation':k,'translation':[int(x)%a.shape[i] for i,x in enumerate(shift)]}
    return None


def retention_panel(rows):
    """Mean of exact per-condition ratios; never pool unequal denominators."""
    assert len(rows) == 2
    if any(u == 0 for d,u in rows):
        return None
    return sum((Fraction(d,u) for d,u in rows),Fraction(0))/2


def rational(value):
    return None if value is None else {'numerator':value.numerator,'denominator':value.denominator,'value':float(value)}
