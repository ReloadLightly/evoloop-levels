"""Compact grid engine. No external mutations are part of the CA physics."""
from pathlib import Path
import ctypes
import hashlib
import itertools
import json
import subprocess
import numpy as np
from .vendor.evoloop import Evoloop

ROOT = Path(__file__).resolve().parents[1]

def digest(a):
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()

def make_lut():
    # Independently implement fallback semantics; verify against reference call.
    ref = Evoloop()
    lut = np.empty(9**5, dtype=np.uint8)
    for i, key in enumerate(itertools.product(range(9), repeat=5)):
        c, *ns = key
        if key in ref.rule_table:
            value = ref.rule_table[key]
        elif c == 8:
            value = 0
        elif 8 in ns:
            if c in (0, 1):
                value = 8 if any(2 <= x <= 7 for x in ns) else c
            elif c in (2, 3, 5):
                value = 0
            else:
                value = 1
        else:
            value = 0 if c == 0 else 8
        lut[i] = value
    return lut

LUT = make_lut()
RULE_HASH = digest(LUT)

def load_kernel():
    src = Path(__file__).with_name('kernel.c')
    lib = src.with_suffix('.so')
    if not lib.exists() or lib.stat().st_mtime < src.stat().st_mtime:
        subprocess.run(['gcc', '-O3', '-std=c99', '-shared', '-fPIC', str(src), '-o', str(lib)], check=True)
    kernel = ctypes.CDLL(str(lib)).advance
    ptr = ctypes.POINTER(ctypes.c_uint8)
    kernel.argtypes = [ptr, ptr, ptr, ctypes.c_int, ctypes.c_int, ctypes.c_int]
    kernel.restype = None
    return kernel

KERNEL = load_kernel()
PTR = ctypes.POINTER(ctypes.c_uint8)

def advance(grid, steps=1, labels=None):
    assert grid.dtype == np.uint8 and grid.flags.c_contiguous
    assert grid.ndim == 2 and steps >= 0 and grid.max() <= 8
    if labels is not None:
        assert labels.shape == grid.shape and labels.dtype == np.uint8 and labels.flags.c_contiguous
    KERNEL(grid.ctypes.data_as(PTR), labels.ctypes.data_as(PTR) if labels is not None else None,
           LUT.ctypes.data_as(PTR), *grid.shape, steps)
    return grid

def seed13():
    a = Evoloop.init_species13_loop((60,60), 10, 10)[0].astype(np.uint8)
    return crop(a)

def crop(a):
    y,x = np.nonzero(a)
    if not len(y):
        return np.zeros((1,1), dtype=np.uint8)
    return a[y.min():y.max()+1,x.min():x.max()+1].copy()

def place(grid, organism, y, x, rotation=0):
    a = np.ascontiguousarray(np.rot90(organism, rotation))
    h,w = a.shape
    assert y >= 0 and x >= 0 and y+h <= grid.shape[0] and x+w <= grid.shape[1]
    target = grid[y:y+h,x:x+w]
    assert not np.any((target != 0) & (a != 0)), 'overlapping initial cells'
    target[a != 0] = a[a != 0]
    return (y,x,h,w)

def checkpoint(path, grid, time, labels=None, metadata=None):
    np.savez_compressed(path, grid=grid, labels=labels if labels is not None else np.zeros_like(grid),
                        time=time, rule_hash=RULE_HASH, metadata=json.dumps(metadata or {}))

def resume(path):
    a = np.load(path, allow_pickle=False)
    assert str(a['rule_hash']) == RULE_HASH, 'checkpoint rule mismatch'
    return a['grid'].copy(), int(a['time']), a['labels'].copy(), json.loads(str(a['metadata']))
