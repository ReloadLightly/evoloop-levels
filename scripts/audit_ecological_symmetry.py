"""Supplementary symmetry/effective-exposure audit of the frozen benefit panel.

    OPENBLAS_NUM_THREADS=1 python -m scripts.audit_ecological_symmetry

Reads recorded arrays; no experiment, endpoint, or analyzer flag is changed.
The original update law commutes with the checked rotations and translations.
Matching initial states and matching effective clearing operations therefore
give equivalent deterministic trajectories. Nominally different empty clears
do not constitute a distinct challenge.
"""
import hashlib
import json
import time

import numpy as np

from evoloop.engine import ROOT, RULE_HASH, digest
from scripts.atlas import write_json

OUT = ROOT/'data/ecological-v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def transformed(array, rotation, translation):
    return np.roll(np.rot90(array, rotation), translation, (0, 1))


def mask(shape, block, size):
    result = np.zeros(shape, bool)
    y, x = block
    result[y:y+size, x:x+size] = True
    return result


def compare_arrays(left, right, rotation, translation, context):
    rotated = transformed(left, rotation, translation)
    equal = left.dtype == right.dtype and left.shape == right.shape and np.array_equal(rotated, right)
    require(equal, context)
    return {'equal_after_transform': bool(equal), 'left_hash': digest(left),
            'transformed_left_hash': digest(rotated), 'right_hash': digest(right)}


def main():
    started = time.perf_counter()
    manifest = json.loads((OUT/'manifest.json').read_text())
    integrity = json.loads((OUT/'integrity.json').read_text())
    require(integrity['status'] == 'passed', 'run the complete independent verification first')
    require(integrity['manifest_sha256'] == sha(OUT/'manifest.json'), 'integrity manifest differs')
    require(manifest['rule_hash'] == RULE_HASH, 'reference rule differs')
    records = []; all_results = {}
    for state in manifest['config']['states']:
        for left_split, left_number, right_split, right_number, rotation in (
                ('development', 1, 'confirmation', 0, 1),
                ('development', 0, 'confirmation', 1, 3)):
            left_id = f'{left_split}-{state}-{left_split}-{left_number}'
            right_id = f'{right_split}-{state}-{right_split}-{right_number}'
            left_folder = OUT/left_split/left_id; right_folder = OUT/right_split/right_id
            left = json.loads((left_folder/'result.json').read_text())
            right = json.loads((right_folder/'result.json').read_text())
            all_results[left_id] = left; all_results[right_id] = right
            with np.load(OUT/'initial'/f'{left_id}.npz', allow_pickle=False) as saved:
                left_initial = saved['grid'].copy()
            with np.load(OUT/'initial'/f'{right_id}.npz', allow_pickle=False) as saved:
                right_initial = saved['grid'].copy()
            rotation_only = np.rot90(left_initial, rotation)
            translation = next(((dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                if np.array_equal(np.roll(rotation_only, (dy, dx), (0, 1)), right_initial)), None)
            require(translation is not None, f'{state}: proposed symmetry does not match initial state')
            record = {'state': state, 'left_run_id': left_id, 'right_run_id': right_id,
                'rotation_quarter_turns_counterclockwise': rotation,
                'translation_rows_columns': list(translation),
                'raw_array_files': {'left_initial': f'initial/{left_id}.npz',
                    'right_initial': f'initial/{right_id}.npz',
                    'left_final': str((left_folder/'final.npz').relative_to(OUT)),
                    'right_final': str((right_folder/'final.npz').relative_to(OUT))},
                'sample_record_files': {'left': str((left_folder/'result.json').relative_to(OUT)),
                    'right': str((right_folder/'result.json').relative_to(OUT))},
                'initial': compare_arrays(left_initial, right_initial, rotation, translation, f'{state}: initial symmetry'),
                'sample_count': 81, 'sample_series_equality': {}, 'disturbances': []}
            require([s['t'] for s in left['samples']] == [s['t'] for s in right['samples']] == list(range(0, 1601, 20)),
                    f'{state}: sample-time inventory')
            for field in ('scored_cores', 'unscored_valid_cores', 'unknown_identity_cores', 'closed_cores', 'occupied_cells'):
                bad = [l['t'] for l, r in zip(left['samples'], right['samples']) if l[field] != r[field]]
                require(not bad, f'{state}: sampled {field} is not symmetric')
                record['sample_series_equality'][field] = {'all_equal': True, 'mismatch_times': bad}
            require(left['score_sum'] == right['score_sum'], f'{state}: exact score sum')
            record['score_sum'] = left['score_sum']
            size = manifest['benefit']['block_size']
            left_mask = mask(left_initial.shape, left['condition']['block'], size)
            right_mask = mask(right_initial.shape, right['condition']['block'], size)
            planned_equal = np.array_equal(transformed(left_mask, rotation, translation), right_mask)
            for t in manifest['benefit']['disturbance_times']:
                with np.load(left_folder/f'disturbance-{t}.npz', allow_pickle=False) as saved:
                    left_pre = saved['before'].copy(); left_post = saved['after'].copy()
                with np.load(right_folder/f'disturbance-{t}.npz', allow_pickle=False) as saved:
                    right_pre = saved['before'].copy(); right_post = saved['after'].copy()
                pre = compare_arrays(left_pre, right_pre, rotation, translation, f'{state}@{t}: pre-clearing symmetry')
                post = compare_arrays(left_post, right_post, rotation, translation, f'{state}@{t}: post-clearing symmetry')
                left_deleted = left_pre != left_post; right_deleted = right_pre != right_post
                left_event = next(e for e in left['events'] if e['type'] == 'disturbance' and e['t'] == t)
                right_event = next(e for e in right['events'] if e['type'] == 'disturbance' and e['t'] == t)
                deletion_equal = np.array_equal(transformed(left_deleted, rotation, translation), right_deleted)
                require(deletion_equal, f'{state}@{t}: effective deletions differ')
                record['disturbances'].append({'t': t, 'left_block': left['condition']['block'],
                    'right_block': right['condition']['block'], 'block_size': size,
                    'left_raw_file': str((left_folder/f'disturbance-{t}.npz').relative_to(OUT)),
                    'right_raw_file': str((right_folder/f'disturbance-{t}.npz').relative_to(OUT)),
                    'planned_block_masks_equal_after_transform': bool(planned_equal),
                    'effective_deleted_cell_masks_equal_after_transform': bool(deletion_equal),
                    'left_removed_occupied_cells': int(np.count_nonzero(left_deleted)),
                    'right_removed_occupied_cells': int(np.count_nonzero(right_deleted)),
                    'left_pre_scored_cores': left_event['pre_counts']['scored_cores'],
                    'left_post_scored_cores': left_event['post_counts']['scored_cores'],
                    'right_pre_scored_cores': right_event['pre_counts']['scored_cores'],
                    'right_post_scored_cores': right_event['post_counts']['scored_cores'],
                    'pre': pre, 'post': post})
            with np.load(left_folder/'final.npz', allow_pickle=False) as saved:
                left_final = saved['grid'].copy()
            with np.load(right_folder/'final.npz', allow_pickle=False) as saved:
                right_final = saved['grid'].copy()
            record['final'] = compare_arrays(left_final, right_final, rotation, translation, f'{state}: final symmetry')
            record['effective_challenge_equivalent'] = True
            record['independent_challenge_confirmation'] = False
            records.append(record)
    clears = [e for result in all_results.values() for e in result['events'] if e['type'] == 'disturbance']
    require(len(records) == 10 and len(all_results) == 20 and len(clears) == 40, 'full paired audit inventory')
    report = {'experiment_id': manifest['benefit_experiment_id'], 'status': 'passed', 'mismatches': 0,
        'manifest_sha256': sha(OUT/'manifest.json'), 'integrity_sha256': sha(OUT/'integrity.json'),
        'rule_hash': RULE_HASH, 'script_sha256': sha(ROOT/'scripts/audit_ecological_symmetry.py'),
        'regeneration_command': 'OPENBLAS_NUM_THREADS=1 python -m scripts.audit_ecological_symmetry',
        'paired_symmetries': records, 'paired_runs_checked': len(all_results),
        'zero_impact_clears': sum(e['removed_occupied_cells'] == 0 for e in clears),
        'nonzero_impact_clears': sum(e['removed_occupied_cells'] > 0 for e in clears),
        'immediate_scored_core_loss_clears': sum(e['post_counts']['scored_cores'] < e['pre_counts']['scored_cores'] for e in clears),
        'immediate_scored_core_count_change_clears': sum(e['post_counts']['scored_cores'] != e['pre_counts']['scored_cores'] for e in clears),
        'interpretation': 'Frozen numerical criterion is unchanged. Nominal confirmation conditions repeat development effective challenges under rotation/translation or no-op clearing; independent challenge confirmation remains unresolved. This is not evidence of disturbance robustness, native genetic ancestry, total viable population, evolvability, or RSI.',
        'seconds': time.perf_counter()-started}
    write_json(OUT/'symmetry-audit.json', report)
    print(json.dumps({key: value for key, value in report.items() if key != 'paired_symmetries'}, indent=2), flush=True)


if __name__ == '__main__':
    main()
