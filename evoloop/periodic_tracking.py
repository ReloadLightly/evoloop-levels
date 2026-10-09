"""Periodic rectangular-core measurement, independently versioned from legacy.

Four cuts cover bodies smaller than half each domain dimension. Components
are joined across both torus seams, then unwrapped only if an empty row and
column exist. Global winding components cannot be isolated conservatively.
"""
import numpy as np
from scipy import ndimage
from .tracking import detect as legacy_detect


def periodic_view(grid, box):
    y,x,h,w=box
    return grid[np.ix_((np.arange(h)+y)%grid.shape[0],(np.arange(w)+x)%grid.shape[1])]


def circular_span(values, size):
    values=np.unique(values)
    if len(values)==size:return None
    if len(values)==1:return int(values[0]),1
    gaps=(np.roll(values,-1)-values)%size
    i=int(np.argmax(gaps))
    return int(values[(i+1)%len(values)]),int(size-gaps[i]+1)


def detect(grid):
    H,W=grid.shape
    if not (np.any(grid[[0,-1]]) or np.any(grid[:,[0,-1]])):
        return legacy_detect(grid)
    found={}
    for dy,dx in ((0,0),(H//2,0),(0,W//2),(H//2,W//2)):
        shifted=np.roll(grid,(-dy,-dx),(0,1))
        for o in legacy_detect(shifted):
            y,x,h,w=o['core']
            if h+6>=H//2 or w+6>=W//2:continue
            core=((y+dy)%H,(x+dx)%W,h,w)
            if core in found:
                assert found[core]['genotype']==o['genotype']
                assert np.array_equal(found[core]['snapshot'],o['snapshot'])
                continue
            o['core']=list(core);o['bbox']=[(core[0]-3)%H,(core[1]-3)%W,h+6,w+6]
            found[core]=o
    loops=[found[k] for k in sorted(found)]
    cc,n=ndimage.label(grid!=0);parent=np.arange(n+1)
    def root(a):
        while parent[a]!=a:
            parent[a]=parent[parent[a]];a=int(parent[a])
        return a
    def join(a,b):
        if a and b:parent[root(a)]=root(b)
    for a,b in zip(cc[0],cc[-1]):join(int(a),int(b))
    for a,b in zip(cc[:,0],cc[:,-1]):join(int(a),int(b))
    mapping=np.array([root(i) for i in range(n+1)])
    cc=mapping[cc]
    ids=[int(cc[(o['core'][0]-1)%H,o['core'][1]]) for o in loops]
    for o,cid in zip(loops,ids):
        o['isolation_snapshot']=None;o.pop('extraction_bbox',None)
        o['extraction_status']='shared_component'
        if not cid or ids.count(cid)!=1:continue
        rows,cols=np.where(cc==cid);rs=circular_span(rows,H);cs=circular_span(cols,W)
        if rs is None or cs is None:
            o['extraction_status']='noncontractible_component';continue
        y,h=rs;x,w=cs;box=[y,x,h,w]
        cells=periodic_view(grid,box);mask=periodic_view(cc,box)==cid
        o['isolation_snapshot']=np.where(mask,cells,0).astype(np.uint8)
        o['extraction_bbox']=box;o['extraction_wraps']=y+h>H or x+w>W
        o['extraction_status']='complete_single_core_component'
    return loops
