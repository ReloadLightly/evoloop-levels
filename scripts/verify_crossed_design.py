"""Independently verify protocol 012's prepared design without response futures.

Run after metric acquisition/audit and crossed design freezing, sequentially
under memory_guard. No production clone assembly or equivalence helper is used.
"""
import hashlib
import json
import resource
import sys
import time
from collections import Counter
from itertools import combinations
from pathlib import Path

import numpy as np

from evoloop.engine import ROOT, RULE_HASH, digest
from scripts.atlas import write_json
from scripts.memory_guard import available_mib
from scripts.verify_ecological import measured, read, require, same, sha
from scripts.verify_impact import components, mask_for

OUT = ROOT / 'data/crossed-v1'


class MemoryHeadroomError(RuntimeError):
    """A design-check interruption, never an evidence mismatch."""


def headroom():
    if available_mib() < 200:
        raise MemoryHeadroomError('available memory below 200 MiB; resume guarded design audit')


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    write_json(temporary, value)
    temporary.replace(path)


def transform_equivalence(a, b):
    """Exhaust rotations and anchored translations of complete state arrays."""
    if a.shape != b.shape or a.dtype != b.dtype:
        return None
    histogram = np.bincount(a.ravel(), minlength=9)
    if not np.array_equal(histogram, np.bincount(b.ravel(), minlength=9)):
        return None
    occupied_states = [state for state in range(1, 9) if histogram[state]]
    if not occupied_states:
        return {'rotation': 0, 'translation': [0, 0]}
    anchor_state = min(occupied_states, key=lambda state: histogram[state])
    destinations = np.argwhere(b == anchor_state)
    for turns in range(4):
        rotated = np.rot90(a, turns)
        source = np.argwhere(rotated == anchor_state)[0]
        for target in destinations:
            shift = target - source
            if np.array_equal(np.roll(rotated, tuple(shift), (0, 1)), b):
                return {'rotation': turns,
                        'translation': [int(shift[i]) % a.shape[i] for i in (0, 1)]}
    return None


def cartesian_specs(cfg):
    return [{'run_id': f'{state}-age{age}-{geometry["id"]}-{treatment}',
             'state': state, 'age': age, 'geometry': geometry['id'], 'split': geometry['split'],
             'treatment': treatment, 'pair_id': f'{state}-age{age}-{geometry["id"]}'}
            for state in cfg['states'] for age in cfg['ages']
            for geometry in cfg['geometries'] for treatment in ('D', 'U')]


def cap_contract(cfg, measure):
    worlds = len(cfg['states']) * len(cfg['ages']) * len(cfg['geometries']) * len(cfg['treatments'])
    controls = (measure['gates']['phase_original_identity_required'] +
                measure['gates']['omitted_any_identity_required'])
    ecological_roots = worlds * measure['limits']['unique_admitted_keys_per_world']
    ecological_simulations = ecological_roots * measure['search']['max_generation_simulations_per_root']
    return {'worlds': worlds, 'pairs': worlds // len(cfg['treatments']),
        'census_snapshots': worlds * len(cfg['source_times']),
        'unique_admitted_keys_per_world': measure['limits']['unique_admitted_keys_per_world'],
        'max_ecological_root_executions': ecological_roots,
        'maximum_ecological_generation_simulations': ecological_simulations, 'controls': controls,
        'maximum_generation_simulations_including_controls': ecological_simulations +
            controls * measure['search']['max_generation_simulations_per_root']}


def direct_placement(patch, offset, geometry, shape):
    """Retain every occupied phase cell and delete exactly the chosen clone."""
    before = np.zeros(shape, np.uint8)
    masks = []
    for site in geometry['sites']:
        y, x = site[0] - offset[0], site[1] - offset[1]
        require(0 <= y and 0 <= x and y + patch.shape[0] <= shape[0] and x + patch.shape[1] <= shape[1],
                'full phase placement inside arena')
        region = before[y:y + patch.shape[0], x:x + patch.shape[1]]
        require(not np.any(region[patch != 0]), 'occupied phase placement overlap')
        region[patch != 0] = patch[patch != 0]
        mask = np.zeros(shape, bool)
        mask[y:y + patch.shape[0], x:x + patch.shape[1]] = patch != 0
        masks.append(mask)
    require(np.count_nonzero(before) == len(geometry['sites']) * np.count_nonzero(patch),
            'all occupied phase cells retained')
    occupied_components = components(before)
    require(len(occupied_components) == 3 and
            all(any(np.array_equal(mask, component) for component in occupied_components) for mask in masks),
            'three disconnected complete phase components including arms')
    mask = masks[geometry['remove_index']]
    after = before.copy()
    after[mask] = 0
    return before, after, mask.astype(np.uint8)


def audit(report):
    require(not sys.flags.optimize, 'ordinary Python is required for design checks')
    manifest = read(OUT / 'manifest.json')
    cfg = read(ROOT / 'configs/crossed-v1.json')
    metric = read(ROOT / 'data/developmental-v1/manifest.json')
    assessment = read(ROOT / cfg['calibration_assessment'])
    integrity = read(ROOT / cfg['calibration_integrity'])
    old = read(ROOT / 'data/impact-v1/manifest.json')
    require(manifest['config'] == cfg and manifest['measure_config'] == metric['config'] ==
            read(ROOT / cfg['measure_config']), 'crossed and developmental configuration links')
    require(manifest['rule_hash'] == metric['rule_hash'] == RULE_HASH, 'unchanged pinned native physics')
    require(manifest['registry'] == old['registry'] and manifest['states'] == old['states'],
            'original fixed registry and source states preserved')
    require(manifest['controls'] == metric['controls'] and len(manifest['controls']) == 33,
            'same33 frozen complete recovery control inputs')
    require(integrity['status'] == 'passed' and integrity['mismatches'] == 0 and
            integrity['manifest_sha256'] == sha(ROOT / 'data/developmental-v1/manifest.json') and
            integrity['evidence_sha256']['analysis.json'] == sha(ROOT / cfg['calibration_assessment']) and
            integrity['evidence_sha256']['results.json'] == sha(ROOT / 'data/developmental-v1/results.json'),
            'complete independent metric assessment must precede crossed freeze')
    require(manifest['calibration_gate_status'] == assessment['gate_status'] and
            manifest['calibration_gate_checks'] == assessment['gate_checks'] and
            manifest['calibration_analysis_sha256'] == sha(ROOT / cfg['calibration_assessment']) and
            manifest['calibration_integrity_sha256'] == sha(ROOT / cfg['calibration_integrity']),
            'actual metric qualification and failures remain bound unchanged')
    require(assessment['prior_coverage_gate'] == 'failed; unchanged' and
            read(ROOT / 'data/coverage-v1/analysis.json')['gate_status'] == 'failed',
            'prior RV02 recovery gate failure unchanged')
    require(all(sha(ROOT / path) == value for path, value in manifest['source_file_sha256'].items()),
            'frozen source, configuration, assessment, implementation or prepared bytes changed')
    require(all(path in manifest['source_file_sha256'] for path in (
        'configs/crossed-v1.json', cfg['protocol'], 'scripts/freeze_crossed.py',
        'scripts/verify_crossed_design.py', 'tests/test_crossed_design_audit.py',
        'data/developmental-v1/manifest.json', cfg['calibration_assessment'], cfg['calibration_integrity'])),
            'prospectively bound design and independent verifier source inventory')
    require(cfg['limits'] == cap_contract(cfg, metric['config']), 'exact Cartesian execution cap arithmetic')
    require(cfg['source_times'] == metric['config']['source_times'] and
            cfg['structural_sample_interval'] == metric['config']['structural_sample_interval'] and
            cfg['horizon'] == metric['config']['horizon'] and cfg['shape'] == metric['config']['shape'] and
            cfg['treatments'] == metric['config']['treatments'] and cfg['boundary'] == metric['config']['boundary'],
            'unchanged native schedule, horizon, shape and intervention twins')
    require(manifest['acquisition_status'] == 'not started; implementation readiness and benchmark required' and
            not any((OUT / name).exists() for name in ('worlds', 'searches', 'results.json', 'analysis.json', 'benchmark.json', 'acquisition.json')),
            'freeze contains no crossed response or benefit evidence')
    counts = report['counts']
    expected_specs = cartesian_specs(cfg)
    require(len(expected_specs) == len(manifest['runs']) == 160 and len(manifest['preparations']) == 80,
            'full160 world and80 paired preparation Cartesian inventory')
    for spec, expected in zip(manifest['runs'], expected_specs):
        require(all(spec[k] == v for k, v in expected.items()), 'exact declared Cartesian input and ordering')
    grids = {}
    expected_preparations = [(state, age, geometry) for state in cfg['states'] for age in cfg['ages']
                             for geometry in cfg['geometries']]
    for preparation, (state, age, geometry) in zip(manifest['preparations'], expected_preparations):
        headroom()
        phase = next(p for p in old['phases'] if p['state'] == state and p['age'] == age)
        pair_id = f'{state}-age{age}-{geometry["id"]}'
        require(preparation['pair_id'] == pair_id and preparation['state'] == state and
                preparation['age'] == age and preparation['geometry'] == geometry and
                preparation['phase'] == phase['name'], 'exact saved phase × fixed geometry link')
        with np.load(ROOT / f'data/impact-v1/phase/{phase["name"]}.npz', allow_pickle=False) as saved:
            patch = saved['snapshot'].copy()
            phase_grid = saved['grid'].copy()
        phase_values, _, phase_loops = measured(phase_grid, old['registry'])
        require(digest(patch) == phase['snapshot_hash'] and digest(phase_grid) == phase['grid_hash'] and
                phase_values['closed_cores'] == 1 and len(components(phase_grid)) == 1 and
                phase_loops[0]['genotype'] == old['states'][state]['identity'] and
                np.count_nonzero(patch) == np.count_nonzero(phase_grid), 'saved complete single-core phase with arms and no residual')
        same(phase_loops[0]['isolation_snapshot'], patch, 'saved full phase extraction')
        before, after, mask = direct_placement(patch, phase['offset'], geometry, cfg['shape'])
        values, _, loops = measured(before, old['registry'])
        after_values, _, after_loops = measured(after, old['registry'])
        require(values['closed_cores'] == values['scored_cores'] == 3 and
                after_values['closed_cores'] == after_values['scored_cores'] == 2 and
                sorted(o['core'][:2] for o in loops) == sorted(geometry['sites']),
                'exact initial core sites and three-to-two registry loss')
        target = next(o for o in loops if o['core'][:2] == geometry['sites'][geometry['remove_index']])
        require(np.array_equal(mask_for(before, target), mask != 0), 'deletion removes entire selected component')
        expected_residual = sorted((tuple(o['core']), o['genotype'], digest(o['isolation_snapshot']))
                                  for o in loops if o is not target)
        actual_residual = sorted((tuple(o['core']), o['genotype'], digest(o['isolation_snapshot'])) for o in after_loops)
        require(actual_residual == expected_residual, 'other full phase components unchanged')
        before_histogram = np.bincount(before.ravel(), minlength=9).tolist()
        after_histogram = np.bincount(after.ravel(), minlength=9).tolist()
        require(preparation['histogram_before'] == before_histogram and preparation['histogram_after'] == after_histogram and
                all(before_histogram[i] == 3 * (before_histogram[i] - after_histogram[i]) for i in range(1, 9)),
                'exact one-third occupied-state histogram removal')
        impact = {'removed_core': target['core'], 'removed_identity': target['genotype'],
            'removed_snapshot_hash': digest(patch), 'removed_occupied_cells': int(mask.sum()),
            'occupied_before': int(np.count_nonzero(before)), 'registered_before': 3, 'registered_after': 2,
            'remaining_components_unchanged': True, 'before_hash': digest(before), 'after_hash': digest(after),
            'mask_hash': digest(mask), 'matched_impact': True}
        require(preparation['impact'] == impact, 'independent exact deletion/exposure metadata')
        with np.load(ROOT / preparation['file'], allow_pickle=False) as saved:
            same(saved['before'], before, 'independent complete undisturbed preparation')
            same(saved['after'], after, 'independent complete disturbed preparation')
            same(saved['mask'], mask, 'independent exact deletion mask')
        for treatment, grid in (('D', after), ('U', before)):
            rid = f'{pair_id}-{treatment}'
            spec = next(r for r in manifest['runs'] if r['run_id'] == rid)
            require(spec['initial_hash'] == digest(grid), 'Cartesian complete start hash')
            with np.load(ROOT / spec['initial_file'], allow_pickle=False) as saved:
                same(saved['grid'], grid, 'Cartesian complete start from preparation')
            grids[rid] = grid
            counts['complete_initial_states_verified'] += 1
        counts['complete_preparations_verified'] += 1
    references = [('protocol009', r) for r in old['runs']] + [('calibration011', r) for r in metric['runs']]
    reference_grids = {}
    for group, spec in references:
        path = spec.get('initial_file', f'data/impact-v1/initial/{spec["run_id"]}.npz')
        require(path in manifest['source_file_sha256'], 'full all-state prior effective context input binding')
        with np.load(ROOT / path, allow_pickle=False) as saved:
            reference_grids[group, spec['run_id']] = saved['grid'].copy()
    checks = []
    aliases = []
    for spec in manifest['runs']:
        headroom()
        for group, prior in references:
            transform = transform_equivalence(grids[spec['run_id']], reference_grids[group, prior['run_id']])
            entry = {'run_id': spec['run_id'], 'reference_group': group,
                     'reference_run_id': prior['run_id'], 'transform': transform}
            if spec['split'] == 'confirmation':
                require(transform is None, 'reserved full state repeats any old or calibration state')
                checks.append(entry)
            elif transform is not None:
                aliases.append(entry)
            counts['prior_effective_state_pairs_verified'] += 1
    for first, second in combinations(manifest['runs'], 2):
        headroom()
        transform = transform_equivalence(grids[first['run_id']], grids[second['run_id']])
        entry = {'run_id': first['run_id'], 'reference_group': 'crossed012',
                 'reference_run_id': second['run_id'], 'transform': transform}
        if first['split'] != second['split']:
            require(transform is None, 'reserved complete state repeats development')
            checks.append(entry)
        elif transform is not None:
            aliases.append(entry)
        counts['crossed_effective_state_pairs_verified'] += 1
    require(manifest['reserved_equivalence_checks'] == checks and
            manifest['development_and_within_panel_aliases'] == aliases and
            manifest['exposure_verified'] is True and manifest['distinct_confirmation_verified'] is True,
            'independent complete effective-state and alias inventory')
    require({p.name for p in (OUT / 'initial').iterdir() if p.is_file()} ==
            {Path(r['initial_file']).name for r in manifest['runs']}, 'exact Cartesian initial file inventory')
    require({p.name for p in (OUT / 'prepared').iterdir() if p.is_file()} ==
            {Path(p['file']).name for p in manifest['preparations']}, 'exact Cartesian preparation file inventory')
    report.update({'status': 'passed', 'mismatches': 0, 'experiment_id': cfg['experiment_id'],
        'manifest_sha256': sha(OUT / 'manifest.json'), 'auditor_sha256': sha(Path(__file__)),
        'calibration_gate_status': assessment['gate_status'], 'rule_hash': RULE_HASH,
        'calibration_analysis_sha256': sha(ROOT / cfg['calibration_assessment']),
        'calibration_integrity_sha256': sha(ROOT / cfg['calibration_integrity']),
        'all_equivalence_pairs_verified': counts['prior_effective_state_pairs_verified'] + counts['crossed_effective_state_pairs_verified'],
        'reserved_equivalence_checks': len(checks), 'effective_aliases_retained': len(aliases),
        'source_files_verified': len(manifest['source_file_sha256']), 'responses': 'not acquired'})


def main():
    started = time.perf_counter()
    report = {'status': 'running', 'counts': Counter(),
        'scope': 'prepared crossed design only; complete phase placement, all Cartesian starts, exact exposure, effective-state equivalence/aliases, calibration qualification and provenance; no response futures'}
    try:
        audit(report)
    except BaseException as error:
        interrupted = isinstance(error, (KeyboardInterrupt, MemoryHeadroomError))
        report.update({'status': 'interrupted' if interrupted else 'failed', 'mismatches': 0 if interrupted else 1,
            'error_type': type(error).__name__, 'error': str(error), 'seconds': time.perf_counter() - started,
            'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
        atomic_json(OUT / 'design-integrity.json', report)
        if isinstance(error, MemoryHeadroomError):
            raise SystemExit(75) from error
        raise
    report.update({'seconds': time.perf_counter() - started,
                   'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
    atomic_json(OUT / 'design-integrity.json', report)
    print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    main()
