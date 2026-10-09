"""Conservative closed-core detector and operational signal-word genotype.

This recognizes intact rectangular inner sheaths, including transient candidates.
It is not a universal organism or ancestry detector; reproduction establishes viability.
"""
import hashlib
import numpy as np
from scipy import ndimage

def cycle_min(word):
    if not word:
        return ''
    return min(word[i:]+word[:i] for i in range(len(word)))

def detect(grid):
    labels,n = ndimage.label(grid == 0)
    objects = ndimage.find_objects(labels)
    found = []
    for k,s in enumerate(objects,1):
        if s is None:
            continue
        y,x = s[0].start,s[1].start
        h,w = s[0].stop-y,s[1].stop-x
        if h < 1 or w < 1 or y < 3 or x < 3 or y+h+3 > grid.shape[0] or x+w+3 > grid.shape[1]:
            continue
        if not np.all(labels[s] == k):
            continue
        # A complete inner sheath (2/3) and a surrounding signal channel.
        a = grid[y-3:y+h+3, x-3:x+w+3].copy()
        core = a[2:-2,2:-2]
        edge = np.r_[core[0,:],core[-1,:],core[1:-1,0],core[1:-1,-1]]
        if not np.all(np.isin(edge,[2,3])):
            continue
        ring = a[1:-1,1:-1]
        signal = np.r_[ring[0,:], ring[1:,-1], ring[-1,-2::-1], ring[-2:0:-1,0]]
        # Retain all carrier states: gene spacing matters (Salzberg et al., 2004).
        # Circular shift removes circulation phase; reflection is NOT equivalent.
        # Channel contamination remains a structural candidate, with unknown genotype.
        valid = np.all(np.isin(signal,[0,1,4,7]))
        word = cycle_min(''.join(str(v) for v in signal)) if valid else None
        genotype = f'{min(h,w)}x{max(h,w)}:{word}' if word else None
        found.append(dict(core=[y,x,h,w], bbox=[y-3,x-3,h+6,w+6], genotype=genotype,
                          snapshot=a, snapshot_hash=hashlib.sha256(a.tobytes()).hexdigest()))
    # Isolation preserves the entire occupied component, including arms. It is
    # allowed only when that component has exactly one recognized closed core.
    cc,_ = ndimage.label(grid != 0)
    pieces=ndimage.find_objects(cc)
    ids=[int(cc[o['core'][0]-1,o['core'][1]]) for o in found]
    for o,cid in zip(found,ids):
        o['isolation_snapshot']=None
        o['extraction_status']='shared_component'
        if not cid or ids.count(cid)!=1:continue
        s=pieces[cid-1]
        if s[0].start==0 or s[1].start==0 or s[0].stop==grid.shape[0] or s[1].stop==grid.shape[1]:
            o['extraction_status']='boundary_component'
            continue
        snap=np.where(cc[s]==cid,grid[s],0).astype(np.uint8)
        o['isolation_snapshot']=snap
        o['extraction_bbox']=[s[0].start,s[1].start,s[0].stop-s[0].start,s[1].stop-s[1].start]
        o['extraction_status']='complete_single_core_component'
    return found

def contact(grid, labels):
    # First occupied von Neumann adjacency between exclusive input provenance,
    # or occupied local causal provenance mixing. Labels overapproximate causality.
    if np.any((grid != 0) & (labels == 3)):
        return True
    for axis in (0,1):
        other = np.roll(labels,1,axis)
        occupied = (grid != 0) & (np.roll(grid,1,axis) != 0)
        if np.any(occupied & (((labels == 1) & (other == 2)) | ((labels == 2) & (other == 1)))):
            return True
    return False
