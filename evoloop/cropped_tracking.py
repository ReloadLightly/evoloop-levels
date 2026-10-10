"""Equivalent finite-background crop for the unchanged periodic detector.

An occupied global edge always uses the complete reference grid. Otherwise all
occupied components fit inside their bounding rectangle. Four extra zero cells
retain the connected exterior and the reference detector's three-cell margin;
clipping to actual domain edges preserves its original exclusion conditions.
Neither snapshots nor organism definitions change.
"""
import numpy as np
from .periodic_tracking import detect as reference_detect


def detect(grid):
    if np.any(grid[[0,-1],:]) or np.any(grid[:,[0,-1]]):
        return reference_detect(grid)
    rows,cols=np.nonzero(grid)
    if not len(rows):
        return []
    y0=max(0,int(rows.min())-4);x0=max(0,int(cols.min())-4)
    y1=min(grid.shape[0],int(rows.max())+5)
    x1=min(grid.shape[1],int(cols.max())+5)
    if y0==0 and x0==0 and y1==grid.shape[0] and x1==grid.shape[1]:
        return reference_detect(grid)
    result=reference_detect(grid[y0:y1,x0:x1])
    for organism in result:
        for key in ('core','bbox','extraction_bbox'):
            if key in organism:
                organism[key]=[organism[key][0]+y0,organism[key][1]+x0,
                               *organism[key][2:]]
    return result
