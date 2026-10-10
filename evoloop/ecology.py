"""Prospectively declared ecological intervention and known-identity score.

The original CA transition kernel is unchanged. Clearing a block is an explicit
experimental intervention; recognized cores are structural observations.
"""
import numpy as np

from .engine import digest, place
from .periodic_tracking import detect


def prepared_grid(snapshot, shape, rotation):
    rotated = np.ascontiguousarray(np.rot90(snapshot, rotation))
    grid = np.zeros(shape, dtype=np.uint8)
    place(grid, rotated, shape[0]//2-rotated.shape[0]//2,
          shape[1]//2-rotated.shape[1]//2)
    return grid


def observation(grid, registry):
    loops = detect(grid)
    records = []
    for o in loops:
        snap = o['isolation_snapshot']
        records.append({
            'core': o['core'], 'identity': o['genotype'],
            'scored': o['genotype'] in registry,
            'extraction_status': o['extraction_status'],
            'extraction_bbox': o.get('extraction_bbox'),
            'snapshot_hash': digest(snap) if snap is not None else None,
            'component_shape': list(snap.shape) if snap is not None else None,
        })
    counts = {
        'scored_cores': sum(o['scored'] for o in records),
        'unscored_valid_cores': sum(o['identity'] is not None and not o['scored'] for o in records),
        'unknown_identity_cores': sum(o['identity'] is None for o in records),
        'closed_cores': len(records), 'occupied_cells': int(np.count_nonzero(grid)),
    }
    return counts, records, loops


def remove_block(grid, block, size):
    y, x = block
    assert 0 <= y <= grid.shape[0]-size and 0 <= x <= grid.shape[1]-size
    before = grid.copy()
    cells = int(np.count_nonzero(grid[y:y+size, x:x+size]))
    grid[y:y+size, x:x+size] = 0
    return before, {'block': list(block), 'block_size': size,
                    'removed_occupied_cells': cells,
                    'before_hash': digest(before), 'after_hash': digest(grid)}


def chosen_cores(loops, scored, registry, budget=2):
    assert budget == 2
    rows = sorted([o for o in loops if (o['genotype'] in registry) == scored],
                  key=lambda o: tuple(o['core']))
    return rows[:1] if len(rows) < 2 else [rows[0], rows[-1]]


def panel_summary(condition_sums, samples_per_condition=81):
    assert len(condition_sums) == 2
    assert all(isinstance(s, (int, np.integer)) for s in condition_sums)
    total = int(sum(condition_sums))
    samples = samples_per_condition*2
    return {'score_sum': total, 'sample_count': samples, 'mean': total/samples}


def strict_advantage(candidate, inputs):
    return all(candidate > parent for parent in inputs)
