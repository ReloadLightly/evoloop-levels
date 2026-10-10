"""An execution optimization; selected LUT and label semantics are unchanged."""
import ctypes,subprocess
import numpy as np
from .engine import ROOT,LUT
SRC=ROOT/'evoloop/tiled_kernel.c';LIB=SRC.with_suffix('.so')
if not LIB.exists() or LIB.stat().st_mtime<SRC.stat().st_mtime:
    subprocess.run(['gcc','-O3','-std=c99','-shared','-fPIC',str(SRC),'-o',str(LIB)],check=True)
PTR=ctypes.POINTER(ctypes.c_uint8);fn=ctypes.CDLL(str(LIB)).tiled_advance
fn.argtypes=[PTR,PTR,PTR,ctypes.c_int,ctypes.c_int,ctypes.c_int];fn.restype=None

def advance(grid,steps,labels=None):
    assert grid.dtype==np.uint8 and grid.flags.c_contiguous and grid.ndim==2
    assert grid.size and grid.max()<9
    assert steps>=0 and int(steps)==steps and LUT[0]==0
    if labels is not None:assert labels.dtype==np.uint8 and labels.flags.c_contiguous and labels.shape==grid.shape
    fn(grid.ctypes.data_as(PTR),labels.ctypes.data_as(PTR) if labels is not None else None,LUT.ctypes.data_as(PTR),*grid.shape,steps)
    return grid
