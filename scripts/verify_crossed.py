"""Independent response replay and exact interval audit for frozen protocol 012.

No crossed acquisition or analysis implementation is imported. Native worlds and
every executed serial search are replayed with the existing independent dense
verifiers. The pre-response design audit is accepted only through its frozen,
committed hash-bound receipt, since it deliberately rejects response evidence.
Run sequentially after acquisition under scripts.memory_guard.
"""
import argparse
import hashlib
import json
import resource
import subprocess
import sys
import time
from collections import Counter
from fractions import Fraction
from pathlib import Path

import numpy as np

from evoloop.engine import ROOT, RULE_HASH, advance, digest
from scripts.atlas import write_json
from scripts.memory_guard import available_mib
from scripts.verify_coverage import MemoryHeadroomError as SearchHeadroomError, search
from scripts.verify_developmental import independent_extraction, search_censoring
from scripts.verify_ecological import measured, read, require, same, sha
from scripts.verify_crossed_design import cap_contract, cartesian_specs

OUT = ROOT / 'data/crossed-v1'
FRESH = False
REUSED = ('scripts/verify_developmental.py', 'scripts/verify_coverage.py',
          'scripts/verify_ecological.py', 'scripts/verify_fresh.py',
          'scripts/verify_impact.py', 'scripts/verify_crossed_design.py',
          'scripts/memory_guard.py')
IMPLEMENTATION = ('evoloop/crossed.py', 'scripts/crossed_assay.py', 'scripts/verify_crossed.py',
                  'tests/test_crossed_assay.py', 'tests/test_crossed_audit.py',
                  'scripts/verify_developmental.py', 'scripts/memory_guard.py')
RESPONSE_NAMES = ('worlds', 'searches', 'roots', 'results.json', 'analysis.json',
                  'benchmark.json', 'acquisition.json', 'integrity.json', 'integrity-proofs')
ORIGIN_RECORDS = ('data/atlas-v2/manifest.json', 'data/atlas-v2/analysis.json',
                  'data/atlas-v2/confirmed/catalogue.json')


class MemoryHeadroomError(RuntimeError):
    """An execution interruption, never a scientific evidence mismatch."""


def headroom():
    if available_mib() < 200:
        raise MemoryHeadroomError('available memory below 200 MiB; resume guarded crossed audit')


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    write_json(temporary, value)
    temporary.replace(path)


def fraction_record(numerator, denominator=1):
    require(type(numerator) is int and type(denominator) is int and denominator > 0,
            'exact signed fraction requires integer terms and positive denominator')
    value = Fraction(numerator, denominator)
    return {'numerator': value.numerator, 'denominator': value.denominator}


def fraction_value(record):
    require(type(record['numerator']) is int and type(record['denominator']) is int and
            record['denominator'] > 0, 'invalid interval fraction')
    return Fraction(record['numerator'], record['denominator'])


def record_value(value):
    return fraction_record(value.numerator, value.denominator)


def partition(sources):
    qualified = 0
    for source in sources:
        confirmed = source['transmission_confirmed']
        require(type(confirmed) is bool, 'source confirmation must be a measured boolean')
        require(not confirmed or (source['extraction_status'] == 'eligible' and
                source['search_dir'] is not None and source['confirmed_identity'] is not None),
                'confirmation requires eligible complete-component isolation')
        qualified += int(confirmed)
    return {'Q': qualified, 'R': len(sources) - qualified, 'C': len(sources)}


def check_partition(row):
    require(all(type(row[k]) is int and row[k] >= 0 for k in ('Q', 'R', 'C')) and
            row['C'] == row['Q'] + row['R'], 'invalid exact Q/R/C partition')


def retention(disturbed, undisturbed):
    check_partition(disturbed)
    check_partition(undisturbed)
    if not undisturbed['C']:
        return {'status': 'undefined_zero_detected_control', 'lower': None, 'upper': None}
    return {'status': 'bounded' if undisturbed['Q'] else 'unbounded_upper',
            'lower': fraction_record(disturbed['Q'], undisturbed['C']),
            'upper': fraction_record(disturbed['C'], undisturbed['Q']) if undisturbed['Q'] else None}


def disturbed_mean(disturbed, snapshots):
    check_partition(disturbed)
    require(type(snapshots) is int and snapshots > 0, 'positive census snapshot count')
    return {'status': 'bounded', 'lower': fraction_record(disturbed['Q'], snapshots),
            'upper': fraction_record(disturbed['C'], snapshots)}


def interval_status(lower, upper):
    return ('unbounded_both' if lower is None and upper is None else
            'unbounded_lower' if lower is None else 'unbounded_upper' if upper is None else 'bounded')


def average_intervals(intervals):
    require(bool(intervals), 'empty interval panel')
    if any(interval['status'].startswith('undefined') for interval in intervals):
        return {'status': 'undefined_zero_detected_control', 'lower': None, 'upper': None}
    endpoints = {}
    for endpoint in ('lower', 'upper'):
        values = [interval[endpoint] for interval in intervals]
        endpoints[endpoint] = (record_value(sum(map(fraction_value, values), Fraction()) / len(values))
                               if all(v is not None for v in values) else None)
    return {'status': interval_status(endpoints['lower'], endpoints['upper']), **endpoints}


def subtract_intervals(later, earlier):
    """[l1-u0,u1-l0], preserving signed infinity and undefined controls."""
    if any(interval['status'].startswith('undefined') for interval in (later, earlier)):
        return {'status': 'undefined', 'lower': None, 'upper': None}
    lower = (record_value(fraction_value(later['lower']) - fraction_value(earlier['upper']))
             if later['lower'] is not None and earlier['upper'] is not None else None)
    upper = (record_value(fraction_value(later['upper']) - fraction_value(earlier['lower']))
             if later['upper'] is not None and earlier['lower'] is not None else None)
    return {'status': interval_status(lower, upper), 'lower': lower, 'upper': upper}


def strict_superiority(candidate, inputs):
    """A missing endpoint cannot establish a robust advantage; exact ties fail."""
    if candidate['lower'] is None or any(row['upper'] is None for row in inputs):
        return None
    return all(fraction_value(candidate['lower']) > fraction_value(row['upper']) for row in inputs)


def exact_threshold(numerator, denominator, threshold):
    return Fraction(numerator, denominator) >= Fraction(threshold) if denominator else None


def joint(checks):
    values = list(checks)
    return False if False in values else None if None in values else True


def cache_key(patch, identity, original, cfg):
    binding = {'snapshot_hash': digest(patch), 'snapshot_shape': list(patch.shape),
               'snapshot_dtype': str(patch.dtype), 'input_identity': identity,
               'rule_hash': RULE_HASH, 'search_config': cfg, 'original_endpoint': original}
    return hashlib.sha256(json.dumps(binding, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def local_admission(key, admitted, cap):
    """Global cache existence deliberately cannot bypass a world's distinct cap."""
    accepted = key in admitted or len(admitted) < cap
    if accepted:
        admitted.add(key)
    return accepted


def extraction_status(organism, cfg):
    patch = organism['isolation_snapshot']
    if patch is None:
        status = organism['extraction_status']
        return status if status in ('shared_component', 'noncontractible_component') else 'missing_complete_component'
    if max(patch.shape) + cfg['extraction']['minimum_empty_margin_total'] > cfg['shape'][0]:
        return 'component_too_large'
    return 'eligible'


def identity_class(identity, registry):
    return 'unknown_identity' if identity is None else 'scored' if identity in registry else 'valid_unregistered'


def source_labels(source, cfg, registry):
    outcome = read(OUT / source['search_dir'] / 'result.json') if source['search_dir'] else None
    confirmation = outcome['confirmation'] if outcome is not None else None
    confirmed = confirmation is not None
    identity = confirmation['identity'] if confirmed else None
    expected = {'transmission_confirmed': confirmed, 'confirmed_identity': identity,
        'root_reproduction_observed': bool(outcome['nodes'][0]['outcome']['children']) if outcome else None,
        'isolated_grid_extinction_nodes': [node['node'] for node in outcome['nodes']
             if node['outcome']['status'] == 'assay_extinct'] if outcome else [],
        'confirmed_identity_in_registry': identity in registry if confirmed else None,
        'same_as_source_identity': identity == source['source_identity']
             if confirmed and source['source_identity'] is not None else None,
        'search_censoring': search_censoring(outcome, cfg), 'inheritance_unresolved': not confirmed,
        'ancestry_ambiguous': True, 'benefit_pending': True if confirmed else None,
        'status': 'confirmed' if confirmed else 'unresolved_search' if outcome is not None else
                  'unsearched_budget' if source['extraction_status'] == 'eligible' else source['extraction_status']}
    require(all(source[k] == value for k, value in expected.items()), 'source fate/censoring labels')


def execution_config(manifest):
    return {**manifest['config'], 'search': manifest['measure_config']['search'],
            'extraction': manifest['measure_config']['extraction']}


def receipt(folder, binding):
    recorded = read(folder / 'receipt.json')
    require(recorded['binding'] == binding, f'{folder}: complete acquisition binding')
    actual = {str(path.relative_to(folder)): sha(path) for path in sorted(folder.rglob('*'))
              if path.is_file() and path.name != 'receipt.json' and not path.name.endswith('.tmp')}
    require(recorded['artifact_sha256'] == actual, f'{folder}: complete receipt artifact inventory')


def evidence_hashes(paths):
    files = set()
    for path in paths:
        require(path.exists(), f'missing proof source: {path}')
        files.update(p for p in path.rglob('*') if p.is_file()) if path.is_dir() else files.add(path)
    return {str(path.relative_to(ROOT)): sha(path) for path in sorted(files)}


def proven(kind, name, paths, initial_hash, counts, operation):
    headroom()
    evidence = evidence_hashes(paths)
    provenance = {'auditor_sha256': sha(Path(__file__)), 'manifest_sha256': sha(OUT / 'manifest.json'),
        'readiness_sha256': sha(OUT / 'readiness.json'),
        'design_integrity_sha256': sha(OUT / 'design-integrity.json'), 'rule_hash': RULE_HASH,
        'initial_grid_or_component_hash': initial_hash,
        'reused_verifier_sha256': {path: sha(ROOT / path) for path in REUSED},
        'physical_source_sha256': evidence}
    destination = OUT / 'integrity-proofs' / kind / f'{name}.json'
    if destination.exists() and not FRESH:
        previous = read(destination)
        if previous.get('status') == 'passed' and previous.get('mismatches') == 0 and previous.get('provenance') == provenance:
            delta = previous['verified_counts_delta']
            require(all(type(value) is int and value >= 0 for value in delta.values()), 'invalid proof counts')
            counts.update(delta)
            counts[f'{kind}_proofs_reused'] += 1
            print('reused checked crossed proof', kind, name, flush=True)
            return
    before = counts.copy()
    started = time.perf_counter()
    operation()
    require(evidence_hashes(paths) == evidence, f'{kind}/{name}: evidence changed during audit')
    delta = {key: counts[key] - before[key] for key in counts if counts[key] != before[key]}
    require(all(value >= 0 for value in delta.values()), 'proof count regression')
    atomic_json(destination, {'status': 'passed', 'mismatches': 0, 'kind': kind, 'unit': name,
        'provenance': provenance, 'verified_counts_delta': delta,
        'verification_seconds': time.perf_counter() - started})
    counts[f'{kind}_proofs_created'] += 1


def world(spec, manifest, counts):
    rid = spec['run_id']
    cfg = execution_config(manifest)
    folder = OUT / 'worlds' / rid
    result = read(folder / 'result.json')
    require(all(result[key] == value for key, value in spec.items()), f'{rid}: immutable world spec')
    require(result['rule_hash'] == RULE_HASH and result['completed_updates'] == cfg['horizon'],
            f'{rid}: pinned rule and full native horizon')
    with np.load(ROOT / spec['initial_file'], allow_pickle=False) as saved:
        require(saved.files == ['grid'], 'complete native initial array inventory')
        grid = saved['grid'].copy()
    require(grid.dtype == np.uint8 and grid.shape == tuple(cfg['shape']) and digest(grid) == spec['initial_hash'],
            f'{rid}: complete native start')
    expected_times = list(range(0, cfg['horizon'] + 1, cfg['structural_sample_interval']))
    require(len(result['samples']) == len(expected_times) == 81, f'{rid}: all81 structural samples')
    source_cursor = 0
    expected_counts = []
    expected_files = {'result.json', 'receipt.json', 'final.npz'}
    admitted = set()
    for index, t in enumerate(expected_times):
        headroom()
        if t:
            advance(grid, cfg['structural_sample_interval'])
        values, records, loops = measured(grid, manifest['registry'])
        require(result['samples'][index] == {'t': t, **values, 'cores': records}, f'{rid}@{t}: exact native sample')
        counts['world_samples_verified'] += 1
        if t not in cfg['source_times']:
            continue
        path = folder / f'grid-{t}.npz'
        expected_files.add(path.name)
        with np.load(path, allow_pickle=False) as saved:
            require(saved.files == ['grid'], 'complete census array inventory')
            same(saved['grid'], grid, f'{rid}@{t}: complete census grid')
        independent_extraction(grid, loops, counts)
        census = []
        for organism in sorted(loops, key=lambda row: tuple(row['core'])):
            require(source_cursor < len(result['sources']), f'{rid}@{t}: omitted detected source')
            source = result['sources'][source_cursor]
            source_cursor += 1
            status = extraction_status(organism, cfg)
            patch = organism['isolation_snapshot']
            expected = {'run_id': rid, 'state': spec['state'], 'treatment': spec['treatment'],
                't': t, 'core': organism['core'], 'source_identity': organism['genotype'],
                'source_class': identity_class(organism['genotype'], manifest['registry']),
                'extraction_status': status, 'snapshot_hash': digest(patch) if status == 'eligible' else None,
                'snapshot_shape': list(patch.shape) if status == 'eligible' else None,
                'snapshot_dtype': str(patch.dtype) if status == 'eligible' else None}
            require(all(source[key] == value for key, value in expected.items()), f'{rid}@{t}: exact source metadata')
            if status == 'eligible':
                key = cache_key(patch, organism['genotype'], False, cfg['search'])
                require(source['search_key'] == key and source['snapshot_file'] == f'roots/{key}.npz',
                        'complete input key/root, including unsearched eligible sources')
                with np.load(OUT / source['snapshot_file'], allow_pickle=False) as saved:
                    require(saved.files == ['snapshot'], 'root snapshot array inventory')
                    same(saved['snapshot'], patch, 'source complete root including arms')
                accepted = local_admission(key, admitted, cfg['limits']['unique_admitted_keys_per_world'])
                require(source['search_dir'] == (f'searches/{key}' if accepted else None),
                        f'{rid}@{t}: local chronological/lexicographic distinct-key admission including cached keys')
                counts['eligible_sources_verified'] += 1
            else:
                require(source['search_key'] is None and source['snapshot_file'] is None and source['search_dir'] is None,
                        'ineligible source must retain absent search')
                counts['ineligible_sources_verified'] += 1
            source_labels(source, cfg['search'], manifest['registry'])
            census.append(source)
            counts['detected_sources_verified'] += 1
        expected_counts.append({'t': t, **partition(census)})
        counts['census_grids_verified'] += 1
    require(source_cursor == len(result['sources']), f'{rid}: trailing sources')
    require(result['admitted_distinct_keys'] == len(admitted), f'{rid}: local distinct admission count')
    require(result['snapshot_counts'] == expected_counts, f'{rid}: every exact Q/R/C census partition')
    with np.load(folder / 'final.npz', allow_pickle=False) as saved:
        require(saved.files == ['grid'], 'complete terminal array inventory')
        same(saved['grid'], grid, f'{rid}: terminal state')
    require(result['final_hash'] == digest(grid), f'{rid}: terminal hash')
    require({p.name for p in folder.iterdir() if p.is_file() and not p.name.endswith('.tmp')} == expected_files,
            f'{rid}: exact compact native evidence inventory')
    counts['full_world_trajectories_verified'] += 1
    counts['dense_world_updates_replayed'] += cfg['horizon']
    print('verified crossed world', rid, 'sources', source_cursor, flush=True)


def search_unit(key, path, identity, original, manifest, counts):
    cfg = manifest['measure_config']['search']
    with np.load(path, allow_pickle=False) as saved:
        patch = saved['snapshot'].copy()
    require(patch.dtype == np.uint8 and key == cache_key(patch, identity, original, cfg), 'complete-input cache key')
    folder = OUT / 'searches' / key
    binding = {'manifest_sha256': sha(OUT / 'manifest.json'), 'readiness_sha256': sha(OUT / 'readiness.json'),
               'snapshot_hash': digest(patch), 'snapshot_shape': list(patch.shape),
               'snapshot_dtype': str(patch.dtype), 'input_identity': identity, 'original_endpoint': original,
               'search_config': cfg, 'rule_hash': RULE_HASH}
    receipt(folder, binding)
    outcome = read(folder / 'result.json')
    proven('search', key, [folder, path], digest(patch), counts,
           lambda: search(outcome, folder, patch, identity, original, cfg, counts))
    return outcome


def comparison_summary(cfg, worlds):
    """Recompute every cell, exact panel average, and signed crossed contrast."""
    by_id = {world_result['run_id']: world_result for world_result in worlds}
    require(len(by_id) == len(worlds), 'duplicate world result identifiers')
    cells = []
    for state in cfg['states']:
        for age in cfg['ages']:
            for geometry in cfg['geometries']:
                pair_id = f'{state}-age{age}-{geometry["id"]}'
                twins = {treatment: by_id[f'{pair_id}-{treatment}'] for treatment in cfg['treatments']}
                totals, registry = {}, {}
                for treatment, result in twins.items():
                    require([row['t'] for row in result['snapshot_counts']] == cfg['source_times'],
                            'all five chronological census strata for each cell')
                    for row in result['snapshot_counts']:
                        check_partition(row)
                    totals[treatment] = {key: sum(row[key] for row in result['snapshot_counts'])
                                         for key in ('Q', 'R', 'C')}
                    samples = result['samples']
                    require(len(samples) > 0, 'missing structural samples')
                    registry_total = sum(sample['scored_cores'] for sample in samples)
                    registry[treatment] = {'total': registry_total, 'samples': len(samples),
                                           'mean': fraction_record(registry_total, len(samples))}
                cells.append({'pair_id': pair_id, 'state': state, 'age': age, 'geometry': geometry['id'],
                    'split': geometry['split'], **totals,
                    'retention': retention(totals['D'], totals['U']),
                    'disturbed_mean': disturbed_mean(totals['D'], len(cfg['source_times'])),
                    'registry_diagnostic': registry})
    panels = []
    for state in cfg['states']:
        for split in ('development', 'confirmation'):
            selected = [cell for cell in cells if cell['state'] == state and cell['split'] == split]
            require(len(selected) == 8, 'each frozen state panel has four ages by two layouts')
            panels.append({'state': state, 'split': split, 'conditions': len(selected),
                'retention': average_intervals([cell['retention'] for cell in selected]),
                'disturbed_mean': average_intervals([cell['disturbed_mean'] for cell in selected])})
    lookup = {(cell['state'], cell['age'], cell['geometry']): cell for cell in cells}
    contrasts = []
    measures = ('retention', 'disturbed_mean')
    for state in cfg['states']:
        for geometry in cfg['geometries']:
            for ages in cfg['contrasts']['age_pairs']:
                first, second = [lookup[state, age, geometry['id']] for age in ages]
                contrasts.append({'state': state, 'kind': 'age', 'geometry': geometry['id'],
                    'split': geometry['split'], 'age_pair': ages,
                    **{measure: subtract_intervals(second[measure], first[measure]) for measure in measures}})
        for split, geometries in cfg['contrasts']['geometry_pairs'].items():
            for age in cfg['ages']:
                first, second = [lookup[state, age, geometry] for geometry in geometries]
                contrasts.append({'state': state, 'kind': 'geometry', 'split': split,
                    'geometry_pair': geometries, 'age': age,
                    **{measure: subtract_intervals(second[measure], first[measure]) for measure in measures}})
            for ages in cfg['contrasts']['age_pairs']:
                first_layout = [lookup[state, age, geometries[0]] for age in ages]
                second_layout = [lookup[state, age, geometries[1]] for age in ages]
                contrasts.append({'state': state, 'kind': 'interaction', 'split': split,
                    'geometry_pair': geometries, 'age_pair': ages,
                    **{measure: subtract_intervals(
                        subtract_intervals(second_layout[1][measure], second_layout[0][measure]),
                        subtract_intervals(first_layout[1][measure], first_layout[0][measure]))
                       for measure in measures}})
    return cells, panels, contrasts


def analysis_summary(manifest, worlds, controls):
    cfg = manifest['config']
    rows = [source for world_result in worlds for source in world_result['sources']]
    cells, panels, contrasts = comparison_summary(cfg, worlds)
    lookup = {(panel['state'], panel['split']): panel for panel in panels}
    phase = [control for control in controls if control['kind'] == 'phase']
    omitted = [control for control in controls if control['kind'] == 'omitted']
    gates = {'frozen_calibration': manifest['calibration_gate_status'] == 'passed',
        'repeated_phase_controls': sum(control['transmission_confirmed'] for control in phase) == 30,
        'repeated_omitted_controls': sum(control['transmission_confirmed'] for control in omitted) == 3,
        'matched_exposure': manifest['exposure_verified'],
        'distinct_confirmation': manifest['distinct_confirmation_verified']}
    benefits = []
    for pair in cfg['pairs']:
        details = []
        for split in ('development', 'confirmation'):
            candidate = lookup[pair['candidate'], split]
            inputs = [lookup[state, split] for state in pair['inputs']]
            details.append({'split': split,
                'relative_robust_superiority': strict_superiority(candidate['retention'], [row['retention'] for row in inputs]),
                'absolute_robust_superiority': strict_superiority(candidate['disturbed_mean'], [row['disturbed_mean'] for row in inputs])})
        relative = joint(detail['relative_robust_superiority'] for detail in details)
        absolute = joint(detail['absolute_robust_superiority'] for detail in details)
        confirmed = joint([relative, absolute, *gates.values()])
        benefits.append({**pair, 'originating_encounter': manifest['states'][pair['candidate']]['source']['run_id'],
            'panels': details, 'relative_robust_superiority': relative, 'absolute_robust_superiority': absolute,
            'joint_confirmed': confirmed is True,
            'classification': 'joint_confirmed' if confirmed is True else
                'robust_criterion_unresolved' if confirmed is None else 'robust_criterion_not_met',
            'biological_advantage': 'conditional_assay_advantage' if confirmed is True else 'unresolved'})
    confirmed_origins = {benefit['originating_encounter'] for benefit in benefits if benefit['joint_confirmed']}
    denominators = cfg['benefit']['originating_encounter_denominators']
    yield_rows = []
    for split in ('main', 'held_out', 'overall'):
        number = len(confirmed_origins) if split == 'overall' else sum(
            f'-{"heldout" if split == "held_out" else "main"}-' in origin for origin in confirmed_origins)
        yield_rows.append({'split': split, 'confirmed': number, 'denominator': denominators[split],
                           'fraction': fraction_record(number, denominators[split])})
    keys = {source['search_key'] for source in rows if source['search_dir']} | {control['search_key'] for control in controls}
    return {'experiment_id': manifest['experiment_id'], 'complete_worlds': len(worlds),
        'snapshot_strata': sum(len(world_result['snapshot_counts']) for world_result in worlds),
        'total': partition(rows),
        'by_class': [{'source_class': label, **partition([row for row in rows if row['source_class'] == label])}
                     for label in ('scored', 'valid_unregistered', 'unknown_identity')],
        'source_statuses': dict(Counter(row['status'] for row in rows)), 'unique_searches': len(keys),
        'generation_simulations': sum(read(OUT / 'searches' / key / 'result.json')['generation_simulations'] for key in keys),
        'controls': {'phase_confirmed': sum(control['transmission_confirmed'] for control in phase),
                     'phase_selected': len(phase),
                     'omitted_confirmed': sum(control['transmission_confirmed'] for control in omitted),
                     'omitted_selected': len(omitted)},
        'gate_checks': gates, 'cells': cells, 'panels': panels, 'contrasts': contrasts, 'benefits': benefits,
        'originating_encounter_denominators': denominators, 'joint_confirmed_encounters': len(confirmed_origins),
        'yield': yield_rows, 'unresolved_other_candidate_encounters': 16,
        'earlier_outcomes': 'protocols007/009/010 unchanged',
        'scope': 'detected-source recovery/population envelopes; nested deterministic configurations, not total viable population, independent histories, H1/H3 or RSI'}


def committed_hash(commit, path):
    require(isinstance(commit, str) and len(commit) == 40 and all(c in '0123456789abcdef' for c in commit),
            'full acquisition freeze commit required')
    value = subprocess.check_output(['git', 'show', f'{commit}:{path}'], cwd=ROOT)
    return hashlib.sha256(value).hexdigest()


def provenance(manifest, acquisition):
    """Verify immutable prospective design/readiness without re-running design."""
    cfg = manifest['config']
    require(cfg == read(ROOT / 'configs/crossed-v1.json') and manifest['rule_hash'] == RULE_HASH,
            'frozen crossed configuration and native physics')
    measure = read(ROOT / cfg['measure_config'])
    require(manifest['measure_config'] == measure and cfg['limits'] == cap_contract(cfg, measure),
            'unchanged frozen measurement and exact ceilings')
    require(all(sha(ROOT / path) == value for path, value in manifest['source_file_sha256'].items()),
            'frozen contract/source/calibration/prepared input changed')
    design = read(OUT / 'design-integrity.json')
    require(design['status'] == 'passed' and design['mismatches'] == 0 and
            design['manifest_sha256'] == sha(OUT / 'manifest.json') and
            design['auditor_sha256'] == sha(ROOT / 'scripts/verify_crossed_design.py') and
            design['rule_hash'] == RULE_HASH and design['responses'] == 'not acquired' and
            design['counts']['complete_initial_states_verified'] == 160 and
            design['counts']['complete_preparations_verified'] == 80 and
            design['all_equivalence_pairs_verified'] == 23920 and design['reserved_equivalence_checks'] == 12000,
            'complete prospective design integrity receipt')
    assessment = read(ROOT / cfg['calibration_assessment'])
    calibration = read(ROOT / cfg['calibration_integrity'])
    require(manifest['calibration_gate_status'] == assessment['gate_status'] == design['calibration_gate_status'] and
            manifest['calibration_gate_checks'] == assessment['gate_checks'] and
            manifest['calibration_analysis_sha256'] == design['calibration_analysis_sha256'] == sha(ROOT / cfg['calibration_assessment']) and
            manifest['calibration_integrity_sha256'] == design['calibration_integrity_sha256'] == sha(ROOT / cfg['calibration_integrity']) and
            calibration['status'] == 'passed' and calibration['mismatches'] == 0 and
            calibration['evidence_sha256']['analysis.json'] == sha(ROOT / cfg['calibration_assessment']),
            'all frozen calibration gates/assessment retained')
    require(assessment['prior_coverage_gate'] == 'failed; unchanged' and
            read(ROOT / 'data/coverage-v1/analysis.json')['gate_status'] == 'failed', 'prior protocol010 failure preserved')
    ready = read(OUT / 'readiness.json')
    expected_code = {path: sha(ROOT / path) for path in IMPLEMENTATION}
    require(ready['status'] == 'ready_before_main_acquisition' and ready['experiment_id'] == manifest['experiment_id'] and
            ready['manifest_sha256'] == sha(OUT / 'manifest.json') and
            ready['design_integrity_sha256'] == sha(OUT / 'design-integrity.json') and
            ready['code_hashes'] == expected_code and ready['execution'] == cfg['execution'] and
            ready['main_outcomes'] == 'not acquired' and
            ready['pre_acquisition_inventory'] == {name: False for name in RESPONSE_NAMES},
            'prospective hash-bound tested implementation readiness')
    validation = OUT / 'implementation-validation.txt'
    review = ROOT / 'docs/crossed-implementation-review.md'
    require(ready['validation_sha256'] == sha(validation) and validation.read_text().rstrip().endswith('OK') and
            'FAILED' not in validation.read_text() and ready['review_sha256'] == sha(review) and
            'Status: accepted' in review.read_text(), 'frozen passing tests and independent review')
    require(acquisition['manifest_sha256'] == sha(OUT / 'manifest.json') and
            acquisition['readiness_sha256'] == sha(OUT / 'readiness.json'), 'acquisition provenance binding')
    commit = acquisition['freeze_commit']
    committed = {**expected_code,
        'data/crossed-v1/manifest.json': sha(OUT / 'manifest.json'),
        'data/crossed-v1/readiness.json': sha(OUT / 'readiness.json'),
        'data/crossed-v1/design-integrity.json': sha(OUT / 'design-integrity.json'),
        'data/crossed-v1/implementation-validation.txt': sha(validation),
        'docs/crossed-implementation-review.md': sha(review)}
    source_records = ready['source_records_sha256']
    require(source_records == {path: sha(ROOT / path) for path in ORIGIN_RECORDS},
            'all frozen original catalogue and encounter denominator records')
    committed.update(source_records)
    require(all(committed_hash(commit, path) == value for path, value in committed.items()),
            'design receipt, readiness, runner/auditor/tests/review must be committed before acquisition')
    benchmark = read(OUT / 'benchmark.json')
    require(benchmark['status'] == 'passed' and benchmark['workers'] == 1 and
            benchmark['control'] == manifest['controls'][0]['name'] and
            benchmark['manifest_sha256'] == sha(OUT / 'manifest.json') and
            benchmark['readiness_sha256'] == sha(OUT / 'readiness.json'), 'first control and bound one-worker benchmark')
    return ready


def originating_encounters(manifest):
    """Link advantage only to the two actual source encounters and old totals."""
    atlas = read(ROOT / 'data/atlas-v2/manifest.json')
    catalogue = read(ROOT / 'data/atlas-v2/confirmed/catalogue.json')
    old_analysis = read(ROOT / 'data/atlas-v2/analysis.json')
    entries = {entry['id']: entry for entry in catalogue['entries']}
    near = {run['run_id']: run for run in atlas['runs'] if run['treatment'] == 'near'}
    counts = Counter(run['split'] for run in near.values())
    expected_denominators = {'main': counts['main'], 'held_out': counts['heldout'], 'overall': len(near)}
    require(expected_denominators == {'main': 36, 'held_out': 18, 'overall': 54} ==
            manifest['config']['benefit']['originating_encounter_denominators'],
            'all original near encounters remain in declared denominators')
    origins = set()
    for pair in manifest['config']['pairs']:
        state = manifest['states'][pair['candidate']]
        entry = entries[pair['candidate']]
        require(state['source'] == entry['representative'] and state['identity'] == entry['identity'],
                'candidate is exact saved original catalogue representative')
        rid = state['source']['run_id']
        require(rid in near and pair['inputs'] == [near[rid]['focal'], near[rid]['partner']],
                'both originating inputs preserved without genetic parent assignment')
        origins.add(rid)
    require(len(origins) == len(manifest['config']['pairs']) == 2, 'two actual distinct originating encounters')
    candidates = 0
    inherited = 0
    for split, size in (('main', 36), ('heldout', 18)):
        panel = old_analysis['splits'][split]
        require(panel['total'] == size and sum(cell['denominator'] for cell in panel['cells']) == size,
                'original encounter census denominators unchanged')
        candidates += panel['candidate_runs']
        inherited += panel['confirmed_inherited_runs']
    require(inherited == 2 and candidates - len(origins) == 16,
            'other16 candidate encounters remain unresolved; assay cannot classify their futures')


def audit(report):
    require(not sys.flags.optimize, 'dense isolated verification requires ordinary Python, not -O')
    headroom()
    manifest = read(OUT / 'manifest.json')
    acquisition = read(OUT / 'acquisition.json')
    provenance(manifest, acquisition)
    originating_encounters(manifest)
    cfg = manifest['config']
    counts = report['counts']
    expected_specs = cartesian_specs(cfg)
    require(len(expected_specs) == len(manifest['runs']) == 160 and len(manifest['preparations']) == 80,
            'all160 worlds and80 complete twin preparations')
    require(all(all(spec[key] == value for key, value in expected.items())
                for spec, expected in zip(manifest['runs'], expected_specs)), 'exact declared Cartesian world order')
    require({p.name for p in (OUT / 'initial').iterdir() if p.is_file()} ==
            {Path(spec['initial_file']).name for spec in manifest['runs']}, 'exact160 complete initial inventory')
    require({p.name for p in (OUT / 'prepared').iterdir() if p.is_file()} ==
            {Path(preparation['file']).name for preparation in manifest['preparations']}, 'exact80 complete preparation inventory')
    metric = read(ROOT / 'data/developmental-v1/manifest.json')
    require(manifest['controls'] == metric['controls'] and len(manifest['controls']) == 33 and
            Counter(spec['kind'] for spec in manifest['controls']) == {'phase': 30, 'omitted': 3},
            'all30 original phase and3 known omitted-source control inputs')
    results = read(OUT / 'results.json')
    require(results['experiment_id'] == manifest['experiment_id'] and
            results['manifest_sha256'] == sha(OUT / 'manifest.json') and
            results['readiness_sha256'] == sha(OUT / 'readiness.json'), 'complete results experiment/readiness link')
    require(len(results['controls']) == 33, 'all controls retained including failures')
    search_inputs = {}
    for spec, control in zip(manifest['controls'], results['controls']):
        require(all(control[key] == value for key, value in spec.items()) and control['snapshot_file'] == spec['file'],
                'immutable control complete source link')
        path = ROOT / spec['file']
        with np.load(path, allow_pickle=False) as saved:
            patch = saved['snapshot'].copy()
        require(digest(patch) == spec['snapshot_hash'], 'complete control physical hash')
        original = spec['kind'] == 'phase'
        key = cache_key(patch, spec['identity'], original, manifest['measure_config']['search'])
        require(control['search_key'] == key and control['search_dir'] == f'searches/{key}', 'control canonical input binding')
        outcome = read(OUT / control['search_dir'] / 'result.json')
        confirmation = outcome['confirmation']
        require(control['transmission_confirmed'] == (confirmation is not None) and
                control['confirmed_identity'] == (confirmation['identity'] if confirmation else None), 'control exact endpoint labels')
        require(not original or confirmation is None or confirmation['identity'] == spec['identity'],
                'original phase control cannot pass using a different stable identity')
        candidate = (path, spec['identity'], original)
        require(key not in search_inputs or search_inputs[key][1:] == candidate[1:], 'control cache identity/endpoint collision')
        search_inputs[key] = candidate
        counts['phase_controls_verified' if original else 'omitted_controls_verified'] += 1
    worlds, links = [], []
    ecological_keys = set()
    for spec in manifest['runs']:
        headroom()
        rid = spec['run_id']
        folder = OUT / 'worlds' / rid
        binding = {'manifest_sha256': sha(OUT / 'manifest.json'), 'readiness_sha256': sha(OUT / 'readiness.json'),
                   'initial_hash': spec['initial_hash'], 'run_id': rid}
        receipt(folder, binding)
        result = read(folder / 'result.json')
        paths = [folder, ROOT / spec['initial_file']]
        for source in result['sources']:
            if source['snapshot_file'] is not None:
                paths.append(OUT / source['snapshot_file'])
            if source['search_dir'] is not None:
                paths.append(OUT / source['search_dir'] / 'result.json')
                key = source['search_key']
                candidate = (OUT / source['snapshot_file'], source['source_identity'], False)
                require(key not in search_inputs or search_inputs[key][1:] == candidate[1:],
                        'reused complete input identity/endpoint must agree')
                search_inputs[key] = candidate
                ecological_keys.add(key)
        proven('world', rid, paths, spec['initial_hash'], counts, lambda spec=spec: world(spec, manifest, counts))
        links.append({'run_id': rid, 'result_sha256': sha(folder / 'result.json')})
        worlds.append(result)
    require(results['worlds'] == links, 'all160 complete native result links and ordering')
    require({p.name for p in (OUT / 'worlds').iterdir() if p.is_dir()} == {spec['run_id'] for spec in manifest['runs']},
            'extra or omitted native world folders')
    simulations = {}
    for key, (path, identity, original) in sorted(search_inputs.items()):
        outcome = search_unit(key, path, identity, original, manifest, counts)
        simulations[key] = outcome['generation_simulations']
    require({p.name for p in (OUT / 'searches').iterdir() if p.is_dir()} == set(search_inputs),
            'extra or omitted executed serial searches')
    expected_roots = {source['search_key'] + '.npz' for result in worlds for source in result['sources'] if source['snapshot_file']}
    require({p.name for p in (OUT / 'roots').iterdir() if p.is_file() and not p.name.endswith('.tmp')} == expected_roots,
            'all eligible complete roots retained including capped/unsearched')
    require(counts['full_world_trajectories_verified'] == 160 and counts['census_grids_verified'] == 800 and
            counts['world_samples_verified'] == 12960 and counts['dense_world_updates_replayed'] == 256000,
            'complete160 trajectories,800 census grids,81 samples per world and every native update')
    require(len(ecological_keys) <= cfg['limits']['max_ecological_root_executions'] and
            sum(simulations[key] for key in ecological_keys) <= cfg['limits']['maximum_ecological_generation_simulations'] and
            sum(simulations.values()) <= cfg['limits']['maximum_generation_simulations_including_controls'],
            'ecological and combined immutable execution ceilings')
    expected = analysis_summary(manifest, worlds, results['controls'])
    require(len(expected['cells']) == 80 and len(expected['panels']) == 10 and len(expected['contrasts']) == 100,
            'all crossed cells, eight-cell panel means and100 declared contrasts')
    require(read(OUT / 'analysis.json') == expected, 'independent exact census, interval contrasts, gates and benefits differ')
    counts['exact_analysis_verified'] += 1
    report.update({'status': 'passed', 'mismatches': 0, 'experiment_id': manifest['experiment_id'],
        'manifest_sha256': sha(OUT / 'manifest.json'), 'readiness_sha256': sha(OUT / 'readiness.json'),
        'design_integrity_sha256': sha(OUT / 'design-integrity.json'), 'auditor_sha256': sha(Path(__file__)),
        'rule_hash': RULE_HASH, 'freeze_commit': acquisition['freeze_commit'],
        'calibration_gate_status': manifest['calibration_gate_status'],
        'calibration_gate_checks': manifest['calibration_gate_checks'],
        'evidence_sha256': {name: sha(OUT / name) for name in ('results.json', 'analysis.json', 'acquisition.json', 'benchmark.json')},
        'total': expected['total'], 'unique_searches': len(search_inputs), 'ecological_search_keys': len(ecological_keys),
        'generation_simulations': sum(simulations.values()), 'gate_checks': expected['gate_checks'],
        'benefits': expected['benefits'], 'prior_coverage_gate': 'failed; unchanged'})


def main():
    global FRESH
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fresh', action='store_true', help='replay instead of reusing passed hash-bound proofs')
    FRESH = parser.parse_args().fresh
    started = time.perf_counter()
    report = {'status': 'running', 'counts': Counter(),
        'scope': 'all160 complete native trajectories,800 complete censuses and12960 structural samples; every detected source, complete extraction, cached-key local128 admission,33 controls, all executed serial searches/children, exact per-cell/panel/contrast intervals and joint gates; frozen design proof linkage; no total viable population or genetic ancestry'}
    try:
        audit(report)
    except BaseException as error:
        interrupted = isinstance(error, (KeyboardInterrupt, MemoryHeadroomError, SearchHeadroomError))
        report.update({'status': 'interrupted' if interrupted else 'failed', 'mismatches': 0 if interrupted else 1,
            'error_type': type(error).__name__, 'error': str(error), 'seconds': time.perf_counter() - started,
            'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
        atomic_json(OUT / 'integrity.json', report)
        if isinstance(error, (MemoryHeadroomError, SearchHeadroomError)):
            raise SystemExit(75) from error
        raise
    report.update({'seconds': time.perf_counter() - started,
                   'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
    atomic_json(OUT / 'integrity.json', report)
    print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    main()
