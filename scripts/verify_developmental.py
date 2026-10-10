"""Independent dense replay and exact census audit for protocol 011.

Production developmental acquisition, selection and analysis helpers are not
imported. The pinned kernel/detector and existing independent search verifier
remain the measurement references. Run only after guarded acquisition finishes.
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
from evoloop.periodic_tracking import detect
from scripts.atlas import write_json
from scripts.memory_guard import available_mib
from scripts.verify_ecological import isolated, measured, read, require, same, sha
from scripts.verify_coverage import MemoryHeadroomError as SearchHeadroomError, complete_component, search
from scripts.verify_impact import components, equivalence, mask_for

OUT = ROOT / 'data/developmental-v1'
FRESH = False


class MemoryHeadroomError(RuntimeError):
    """An execution interruption rather than a scientific mismatch."""


def headroom():
    if available_mib() < 200:
        raise MemoryHeadroomError('available memory below 200 MiB; resume guarded audit')


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    write_json(temporary, value)
    temporary.replace(path)


def fraction_record(numerator, denominator):
    """Keep missing denominators distinct from a measured zero."""
    require(isinstance(numerator, int) and isinstance(denominator, int), 'integer fraction terms')
    require(numerator >= 0 and denominator >= 0, 'negative census fraction')
    if denominator == 0:
        return None
    value = Fraction(numerator, denominator)
    return {'numerator': value.numerator, 'denominator': value.denominator}


def exact_threshold(numerator, denominator, threshold):
    return Fraction(numerator, denominator) >= Fraction(threshold) if denominator else None


def source_partition(sources):
    """Count confirmations once per detected source; every exclusion remains R."""
    qualified = 0
    for source in sources:
        confirmed = source['transmission_confirmed']
        require(isinstance(confirmed, bool), 'source confirmation must be measured boolean')
        require(not confirmed or (source['extraction_status'] == 'eligible' and
                source['search_dir'] is not None and source['confirmed_identity'] is not None),
                'confirmation cannot bypass complete-component isolation')
        qualified += int(confirmed)
    return {'Q': qualified, 'R': len(sources) - qualified, 'C': len(sources)}


def bounded_retention(disturbed, undisturbed):
    """Operational detected-core envelope, not native viability bounds."""
    require(all(0 <= row['Q'] <= row['C'] and row['R'] == row['C'] - row['Q']
                for row in (disturbed, undisturbed)), 'invalid Q/R/C partition')
    if undisturbed['C'] == 0:
        return {'lower': None, 'upper': None, 'status': 'undefined_no_undisturbed_detected_cores'}
    return {'lower': fraction_record(disturbed['Q'], undisturbed['C']),
            'upper': fraction_record(disturbed['C'], undisturbed['Q']),
            'status': 'finite' if undisturbed['Q'] else 'unbounded_upper'}


def average_retention(conditions):
    require(bool(conditions), 'empty condition panel')
    bounds = [bounded_retention(d, u) for d, u in conditions]
    if any(b['lower'] is None for b in bounds):
        return {'lower': None, 'upper': None, 'status': 'undefined_no_undisturbed_detected_cores'}
    def value(record):
        return Fraction(record['numerator'], record['denominator'])
    lower = sum((value(b['lower']) for b in bounds), Fraction()) / len(bounds)
    upper = (sum((value(b['upper']) for b in bounds), Fraction()) / len(bounds)
             if all(b['upper'] is not None for b in bounds) else None)
    return {'lower': fraction_record(lower.numerator, lower.denominator),
            'upper': fraction_record(upper.numerator, upper.denominator) if upper is not None else None,
            'status': 'finite' if upper is not None else 'unbounded_upper'}


def strict_superiority(candidate, inputs):
    if candidate['lower'] is None or any(i['upper'] is None for i in inputs):
        return None
    lower = Fraction(candidate['lower']['numerator'], candidate['lower']['denominator'])
    return all(lower > Fraction(i['upper']['numerator'], i['upper']['denominator']) for i in inputs)


def independent_extraction(grid, loops, counts):
    """Check retained cells and rejected component topology by flood fill."""
    filled = components(grid)
    identifiers = []
    for organism in loops:
        y, x, _, _ = organism['core']
        anchor = ((y - 1) % grid.shape[0], x % grid.shape[1])
        matches = [i for i, cc in enumerate(filled) if cc[anchor]]
        require(len(matches) == 1, 'detected core occupied-component anchor')
        identifiers.append(matches[0])
    for organism, component_id in zip(loops, identifiers):
        cells = filled[component_id]
        if identifiers.count(component_id) > 1:
            require(organism['isolation_snapshot'] is None and
                    organism['extraction_status'] == 'shared_component', 'multicore extraction rejection')
            counts['shared_components_verified'] += 1
        elif np.all(np.any(cells, axis=1)) or np.all(np.any(cells, axis=0)):
            require(organism['isolation_snapshot'] is None and
                    organism['extraction_status'] == 'noncontractible_component', 'winding component rejection')
            counts['noncontractible_components_verified'] += 1
        else:
            patch = organism['isolation_snapshot']
            require(patch is not None, 'single complete contractible component must be retained')
            complete_component(grid, organism, patch, counts)


def evidence_hashes(paths):
    files = set()
    for path in paths:
        require(path.exists(), f'missing proof source: {path}')
        if path.is_dir():
            files.update(p for p in path.rglob('*') if p.is_file())
        else:
            files.add(path)
    return {str(p.relative_to(ROOT)): sha(p) for p in sorted(files)}


def proven(kind, name, paths, initial_hash, counts, operation):
    headroom()
    evidence = evidence_hashes(paths)
    provenance = {'auditor_sha256': sha(Path(__file__)),
        'manifest_sha256': sha(OUT / 'manifest.json'),
        'rule_hash': RULE_HASH,
        'initial_grid_or_component_hash': initial_hash,
        'reused_verifier_sha256': {p: sha(ROOT / p) for p in (
            'scripts/verify_coverage.py', 'scripts/verify_ecological.py',
            'scripts/verify_fresh.py', 'scripts/verify_impact.py', 'scripts/memory_guard.py')},
        'physical_source_sha256': evidence}
    destination = OUT / 'integrity-proofs' / kind / f'{name}.json'
    if destination.exists() and not FRESH:
        previous = read(destination)
        if previous.get('status') == 'passed' and previous.get('provenance') == provenance:
            delta = previous['verified_counts_delta']
            require(all(isinstance(v, int) and v >= 0 for v in delta.values()), 'invalid proof counts')
            counts.update(delta)
            counts[f'{kind}_proofs_reused'] += 1
            print('reused checked developmental proof', kind, name, flush=True)
            return
    before = counts.copy()
    started = time.perf_counter()
    operation()
    require(evidence_hashes(paths) == evidence, f'{kind}/{name}: evidence changed during audit')
    delta = {k: counts[k] - before[k] for k in counts if counts[k] != before[k]}
    require(all(v >= 0 for v in delta.values()), 'proof count regression')
    atomic_json(destination, {'status': 'passed', 'mismatches': 0, 'kind': kind,
        'unit': name, 'provenance': provenance, 'verified_counts_delta': delta,
        'verification_seconds': time.perf_counter() - started})
    counts[f'{kind}_proofs_created'] += 1


def identity_class(identity, registry):
    return ('unknown_identity' if identity is None else
            'scored' if identity in registry else 'valid_unregistered')


def cache_key(patch, identity, original, cfg):
    binding = {'snapshot_hash': digest(patch), 'input_identity': identity,
               'rule_hash': RULE_HASH, 'search_config': cfg, 'original_endpoint': original}
    return hashlib.sha256(json.dumps(binding, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def extraction_status(organism, cfg):
    patch = organism['isolation_snapshot']
    if patch is None:
        raw = organism['extraction_status']
        return raw if raw in ('shared_component', 'noncontractible_component') else 'missing_complete_component'
    if max(patch.shape) + cfg['extraction']['minimum_empty_margin_total'] > cfg['shape'][0]:
        return 'component_too_large'
    return 'eligible'


def search_censoring(outcome, cfg):
    if outcome is None:
        return []
    censored = list(outcome['truncations'])
    for node in outcome['nodes']:
        report = node['outcome']
        if len(report['children']) == cfg['offspring_per_generation']:
            censored.append({'reason': 'offspring_cap', 'node': node['node']})
        elif report['status'] == 'unresolved_at_horizon':
            censored.append({'reason': 'generation_horizon', 'node': node['node']})
    return censored


def verify_source_labels(source, cfg, registry):
    outcome = read(OUT / source['search_dir'] / 'result.json') if source['search_dir'] else None
    confirmation = outcome['confirmation'] if outcome is not None else None
    identity = confirmation['identity'] if confirmation is not None else None
    confirmed = confirmation is not None
    expected = {'transmission_confirmed': confirmed, 'confirmed_identity': identity,
        'root_reproduction_observed': bool(outcome['nodes'][0]['outcome']['children']) if outcome else None,
        'isolated_grid_extinction_nodes': [n['node'] for n in outcome['nodes']
             if n['outcome']['status'] == 'assay_extinct'] if outcome else [],
        'confirmed_identity_in_registry': identity in registry if confirmed else None,
        'same_as_source_identity': identity == source['source_identity']
             if confirmed and source['source_identity'] is not None else None,
        'search_censoring': search_censoring(outcome, cfg), 'inheritance_unresolved': not confirmed,
        'ancestry_ambiguous': True, 'benefit_pending': True if confirmed else None,
        'status': 'confirmed' if confirmed else 'unresolved_search' if outcome is not None else
                  'unsearched_budget' if source['extraction_status'] == 'eligible' else source['extraction_status']}
    require(all(source[k] == v for k, v in expected.items()), 'source isolation and fate labels')


def world(spec, manifest, counts):
    """Replay every native update and every census before search eligibility."""
    rid = spec['run_id']
    cfg = manifest['config']
    folder = OUT / 'worlds' / rid
    result = read(folder / 'result.json')
    require(all(result[k] == v for k, v in spec.items()), f'{rid}: manifest fields')
    require(result['rule_hash'] == RULE_HASH and result['completed_updates'] == cfg['horizon'],
            f'{rid}: pinned rule and full native horizon')
    with np.load(ROOT / spec['initial_file'], allow_pickle=False) as saved:
        grid = saved['grid'].copy()
    require(grid.dtype == np.uint8 and grid.shape == tuple(cfg['shape']) and
            digest(grid) == spec['initial_hash'], f'{rid}: complete native initial state')
    require(len(result['samples']) == cfg['horizon'] // cfg['structural_sample_interval'] + 1,
            f'{rid}: all structural samples retained')
    source_cursor = 0
    expected_counts = []
    expected_files = {'result.json', 'receipt.json', 'final.npz'}
    admitted = set()
    for index, t in enumerate(range(0, cfg['horizon'] + 1, cfg['structural_sample_interval'])):
        headroom()
        if t:
            advance(grid, cfg['structural_sample_interval'])
        values, records, loops = measured(grid, manifest['registry'])
        require(result['samples'][index] == {'t': t, **values, 'cores': records},
                f'{rid}@{t}: complete native sample')
        counts['world_samples_verified'] += 1
        if t not in cfg['source_times']:
            continue
        path = folder / f'grid-{t}.npz'
        expected_files.add(path.name)
        with np.load(path, allow_pickle=False) as saved:
            require(saved.files == ['grid'], f'{rid}@{t}: full snapshot array inventory')
            same(saved['grid'], grid, f'{rid}@{t}: full census grid')
        independent_extraction(grid, loops, counts)
        census = []
        for organism in sorted(loops, key=lambda o: tuple(o['core'])):
            require(source_cursor < len(result['sources']), f'{rid}@{t}: missing detected source')
            source = result['sources'][source_cursor]
            source_cursor += 1
            status = extraction_status(organism, cfg)
            patch = organism['isolation_snapshot']
            expected = {'run_id': rid, 'state': spec['state'], 'treatment': spec['treatment'],
                't': t, 'core': organism['core'], 'source_identity': organism['genotype'],
                'source_class': identity_class(organism['genotype'], manifest['registry']),
                'extraction_status': status,
                'snapshot_hash': digest(patch) if status == 'eligible' else None}
            require(all(source[k] == v for k, v in expected.items()), f'{rid}@{t}: exact complete source metadata')
            if status == 'eligible':
                key = cache_key(patch, organism['genotype'], False, cfg['search'])
                require(source['search_key'] == key and source['snapshot_file'] == f'roots/{key}.npz',
                        f'{rid}@{t}: canonical complete input cache key/root')
                with np.load(OUT / source['snapshot_file'], allow_pickle=False) as saved:
                    require(saved.files == ['snapshot'], 'root snapshot array inventory')
                    same(saved['snapshot'], patch, 'complete source root with arms')
                accepted = key in admitted or len(admitted) < cfg['limits']['unique_admitted_keys_per_world']
                if accepted:
                    admitted.add(key)
                require(source['search_dir'] == (f'searches/{key}' if accepted else None),
                        f'{rid}@{t}: chronological local unique-key admission')
                counts['eligible_sources_verified'] += 1
            else:
                require(source['search_key'] is None and source['snapshot_file'] is None and
                        source['search_dir'] is None, 'ineligible source search must remain absent')
                counts['ineligible_sources_verified'] += 1
            verify_source_labels(source, cfg['search'], manifest['registry'])
            census.append(source)
            counts['detected_sources_verified'] += 1
        expected_counts.append({'t': t, **source_partition(census)})
        counts['census_grids_verified'] += 1
    require(source_cursor == len(result['sources']), f'{rid}: trailing or omitted detected sources')
    require(result['admitted_distinct_keys'] == len(admitted), f'{rid}: local admission count')
    require(expected_counts == result['snapshot_counts'], f'{rid}: exact Q/R/C census partitions')
    with np.load(folder / 'final.npz', allow_pickle=False) as saved:
        require(saved.files == ['grid'], 'terminal array inventory')
        same(saved['grid'], grid, f'{rid}: full terminal state')
    require(result['final_hash'] == digest(grid), f'{rid}: terminal hash')
    require({p.name for p in folder.iterdir() if p.is_file() and not p.name.endswith('.tmp')} == expected_files,
            f'{rid}: full native evidence inventory')
    counts['full_world_trajectories_verified'] += 1
    counts['dense_world_updates_replayed'] += cfg['horizon']
    print('verified developmental world', rid, 'sources', source_cursor, flush=True)


def analysis_summary(manifest, worlds, controls):
    """Independently derive the frozen scored and resolved-share gates."""
    cfg = manifest['config']
    rows = [r for world_result in worlds for r in world_result['sources']]
    scored = [r for r in rows if r['source_class'] == 'scored']
    scored_by_state = []
    resolution = []
    for state in cfg['states']:
        state_counts = source_partition([r for r in scored if r['state'] == state])
        scored_by_state.append({'state': state, **state_counts,
            'passed': exact_threshold(state_counts['Q'], state_counts['C'], cfg['gates']['scored_per_state'])})
        for treatment in cfg['treatments']:
            counts = source_partition([r for r in rows if r['state'] == state and r['treatment'] == treatment])
            resolution.append({'state': state, 'treatment': treatment, **counts,
                'passed': exact_threshold(counts['Q'], counts['C'], cfg['gates']['resolved_share_per_state_treatment'])})
    phase = [c for c in controls if c['kind'] == 'phase']
    omitted = [c for c in controls if c['kind'] == 'omitted']
    phase_count = sum(c['transmission_confirmed'] for c in phase)
    omitted_count = sum(c['transmission_confirmed'] for c in omitted)
    score = source_partition(scored)
    def joint(items):
        if any(item['passed'] is False for item in items):
            return False
        return None if any(item['passed'] is None for item in items) else True
    checks = {'phase_controls': phase_count == cfg['gates']['phase_original_identity_required'],
        'omitted_controls': omitted_count == cfg['gates']['omitted_any_identity_required'],
        'scored_overall': exact_threshold(score['Q'], score['C'], cfg['gates']['scored_overall']),
        'scored_per_state': joint(scored_by_state), 'resolved_share': joint(resolution)}
    if any(check is False for check in checks.values()):
        gate = 'failed'
    elif any(check is None for check in checks.values()):
        gate = 'unresolved'
    else:
        gate = 'passed'
    keys = {r['search_key'] for r in rows if r['search_dir'] is not None}
    keys.update(c['search_key'] for c in controls)
    return {'experiment_id': cfg['experiment_id'], 'complete_worlds': len(worlds),
        'snapshot_strata': sum(len(w['snapshot_counts']) for w in worlds),
        'controls': {'phase_confirmed': phase_count, 'phase_selected': len(phase),
                     'omitted_confirmed': omitted_count, 'omitted_selected': len(omitted)},
        'gate_status': gate, 'gate_checks': checks, 'scored': score,
        'scored_per_state': scored_by_state, 'resolution': resolution,
        'total': source_partition(rows),
        'by_class': [{'source_class': label, **source_partition([r for r in rows if r['source_class'] == label])}
                     for label in ('scored', 'valid_unregistered', 'unknown_identity')],
        'source_statuses': dict(Counter(r['status'] for r in rows)), 'unique_searches': len(keys),
        'generation_simulations': sum(read(OUT / 'searches' / key / 'result.json')['generation_simulations'] for key in keys),
        'source_reproduction_observations': sum(r['root_reproduction_observed'] is True for r in rows),
        'prior_coverage_gate': 'failed; unchanged', 'benefit': 'not_assayed',
        'scope': 'finite detected-source recovery; Q,R,C are not total viable population or independent histories'}


def receipt(folder, binding):
    recorded = read(folder / 'receipt.json')
    require(recorded['binding'] == binding, f'{folder}: complete acquisition binding')
    actual = {str(p.relative_to(folder)): sha(p) for p in sorted(folder.rglob('*'))
              if p.is_file() and p.name != 'receipt.json' and not p.name.endswith('.tmp')}
    require(recorded['artifact_sha256'] == actual, f'{folder}: complete receipt artifact inventory')


def search_unit(key, path, identity, original, manifest, counts):
    cfg = manifest['config']['search']
    with np.load(path, allow_pickle=False) as saved:
        patch = saved['snapshot'].copy()
    require(key == cache_key(patch, identity, original, cfg), 'full complete-input cache key')
    folder = OUT / 'searches' / key
    binding = {'manifest_sha256': sha(OUT / 'manifest.json'), 'snapshot_hash': digest(patch),
               'input_identity': identity, 'original_endpoint': original, 'search_config': cfg,
               'rule_hash': RULE_HASH}
    receipt(folder, binding)
    outcome = read(folder / 'result.json')
    proven('search', key, [folder, path], digest(patch), counts,
           lambda: search(outcome, folder, patch, identity, original, cfg, counts))
    return outcome


def preparation_checks(manifest, counts):
    """Reconstruct complete clones and the deletion without production assembly."""
    old = read(ROOT / 'data/impact-v1/manifest.json')
    cfg = manifest['config']
    lookup = {spec['run_id']: spec for spec in manifest['runs']}
    expected_equivalence = []
    for prep in manifest['preparations']:
        phase = next(p for p in old['phases'] if p['name'] == prep['phase'])
        require(phase['state'] == prep['state'] and phase['age'] == prep['condition']['age'],
                'preparation phase link')
        with np.load(ROOT / f'data/impact-v1/phase/{phase["name"]}.npz', allow_pickle=False) as saved:
            patch = saved['snapshot'].copy()
            phase_grid = saved['grid'].copy()
        require(digest(patch) == phase['snapshot_hash'] and digest(phase_grid) == phase['grid_hash'] and
                np.count_nonzero(patch) == np.count_nonzero(phase_grid), 'complete phase component without residual')
        before = np.zeros(cfg['shape'], np.uint8)
        clone_masks = []
        for site in prep['condition']['sites']:
            y, x = (site[i] - phase['offset'][i] for i in (0, 1))
            require(0 <= y and 0 <= x and y + patch.shape[0] <= before.shape[0] and
                    x + patch.shape[1] <= before.shape[1], 'preparation placement bounds')
            region = before[y:y + patch.shape[0], x:x + patch.shape[1]]
            require(not np.any(region[patch != 0]), 'preparation occupied overlap')
            region[patch != 0] = patch[patch != 0]
            mask = np.zeros(cfg['shape'], bool)
            mask[y:y + patch.shape[0], x:x + patch.shape[1]] = patch != 0
            clone_masks.append(mask)
        values, _, loops = measured(before, manifest['registry'])
        require(values['scored_cores'] == values['closed_cores'] == 3 and
                np.count_nonzero(before) == 3 * np.count_nonzero(patch), 'three complete phase clones')
        independent_extraction(before, loops, counts)
        require(sorted(o['core'][:2] for o in loops) == sorted(prep['condition']['sites']),
                'declared core sites')
        target_mask = clone_masks[prep['condition']['remove_index']]
        target = next(o for o in loops if o['core'][:2] == prep['condition']['sites'][prep['condition']['remove_index']])
        require(np.array_equal(mask_for(before, target), target_mask), 'exact whole-component deletion mask')
        after = before.copy()
        after[target_mask] = 0
        after_values, _, after_loops = measured(after, manifest['registry'])
        require(after_values['scored_cores'] == after_values['closed_cores'] == 2,
                'exact three-to-two initial core loss')
        independent_extraction(after, after_loops, counts)
        unchanged_before = sorted((tuple(o['core']), o['genotype'], digest(o['isolation_snapshot']))
                                  for o in loops if o is not target)
        unchanged_after = sorted((tuple(o['core']), o['genotype'], digest(o['isolation_snapshot']))
                                 for o in after_loops)
        require(unchanged_before == unchanged_after and len(components(before)) == 3 and
                len(components(after)) == 2, 'unchanged complete residual clone components')
        impact = {'removed_core': target['core'], 'removed_identity': target['genotype'],
            'removed_snapshot_hash': digest(patch), 'removed_occupied_cells': int(target_mask.sum()),
            'occupied_before': int(np.count_nonzero(before)), 'registered_before': 3, 'registered_after': 2,
            'remaining_components_unchanged': True, 'before_hash': digest(before), 'after_hash': digest(after),
            'mask_hash': digest(target_mask.astype(np.uint8)), 'matched_impact': True}
        require(prep['impact'] == impact, 'independent exact occupied-cell exposure report')
        hist_before = np.bincount(before.ravel(), minlength=9).tolist()
        hist_after = np.bincount(after.ravel(), minlength=9).tolist()
        require(prep['histogram_before'] == hist_before and prep['histogram_after'] == hist_after and
                all(hist_before[i] == 3 * (hist_before[i] - hist_after[i]) for i in range(1, 9)),
                'exact one-third occupied-state histogram removal')
        with np.load(ROOT / prep['file'], allow_pickle=False) as saved:
            same(saved['before'], before, 'complete constructed undisturbed preparation')
            same(saved['after'], after, 'complete disturbed preparation')
            same(saved['mask'], target_mask.astype(np.uint8), 'complete source deletion mask')
        for treatment, initial in (('D', after), ('U', before)):
            rid = f'{prep["pair_id"]}-{treatment}'
            spec = lookup[rid]
            require(spec['initial_hash'] == digest(initial), 'response start preparation hash')
            with np.load(ROOT / spec['initial_file'], allow_pickle=False) as saved:
                same(saved['grid'], initial, 'response start exact constructed preparation')
            for prior in old['runs']:
                with np.load(ROOT / f'data/impact-v1/initial/{prior["run_id"]}.npz', allow_pickle=False) as saved:
                    transform = equivalence(initial, saved['grid'])
                require(transform is None, 'new-context start is prior effective challenge')
                expected_equivalence.append({'run_id': rid, 'prior_run_id': prior['run_id'], 'transform': transform})
                counts['prior_effective_context_checks_verified'] += 1
        counts['complete_preparations_verified'] += 1
    require(manifest['prior_equivalence_checks'] == expected_equivalence, 'full prior effective-context inventory')


def audit(report):
    require(not sys.flags.optimize, 'dense generation checks require ordinary Python, not -O')
    manifest = read(OUT / 'manifest.json')
    cfg = manifest['config']
    require(cfg == read(ROOT / 'configs/developmental-v1.json') and manifest['rule_hash'] == RULE_HASH,
            'frozen configuration and native rule')
    require(all(sha(ROOT / name) == value for name, value in manifest['source_file_sha256'].items()),
            'frozen scientific contract, source, implementation or input changed')
    require(manifest['validation_sha256'] == sha(OUT / 'validation.txt'), 'frozen validation bytes')
    require(manifest['prior_coverage_gate'] == 'failed' and
            read(ROOT / 'data/coverage-v1/analysis.json')['gate_status'] == 'failed',
            'prior RV02 recovery gate failure must be preserved')
    benchmark = read(OUT / 'benchmark.json')
    require(benchmark['status'] == 'passed' and benchmark['workers'] == 1 and
            benchmark['manifest_sha256'] == sha(OUT / 'manifest.json'), 'frozen benchmark and single worker')
    acquisition = read(OUT / 'acquisition.json')
    require(acquisition['manifest_sha256'] == sha(OUT / 'manifest.json') and
            isinstance(acquisition['freeze_commit'], str) and len(acquisition['freeze_commit']) == 40,
            'prospective acquisition freeze commit')
    committed = subprocess.check_output(['git', 'show',
        f'{acquisition["freeze_commit"]}:data/developmental-v1/manifest.json'], cwd=ROOT)
    require(hashlib.sha256(committed).hexdigest() == sha(OUT / 'manifest.json'),
            'manifest was committed before acquisition')
    results = read(OUT / 'results.json')
    require(results['experiment_id'] == manifest['experiment_id'] and
            results['manifest_sha256'] == sha(OUT / 'manifest.json'), 'acquisition experiment/design')
    counts = report['counts']
    preparation_checks(manifest, counts)
    old = read(ROOT / 'data/impact-v1/manifest.json')
    expected_phase = [{**p, 'kind': 'phase', 'identity': old['states'][p['state']]['identity'],
                       'file': f'data/impact-v1/phase/{p["name"]}.npz'} for p in old['phases']]
    coverage = read(ROOT / 'data/coverage-v1/recovery.json')
    seen = set()
    expected_omitted = []
    for observation in coverage['observations']:
        delay = observation['delays'][0]
        if observation['source_class'] == 'unknown_identity' and delay['transmission_confirmed'] and delay['snapshot_hash'] not in seen:
            seen.add(delay['snapshot_hash'])
            expected_omitted.append({'name': f'omitted-{len(seen)}', 'kind': 'omitted', 'state': observation['state'],
                'identity': None, 'file': 'data/coverage-v1/' + delay['snapshot_file'],
                'snapshot_hash': delay['snapshot_hash'], 'source_observation': observation['observation_id']})
    require(manifest['controls'] == expected_phase + expected_omitted and len(seen) == 3,
            'all30 phase and three distinct complete omitted controls')
    require(len(results['controls']) == len(manifest['controls']) == 33, 'all controls retained')
    search_inputs = {}
    for spec, control in zip(manifest['controls'], results['controls']):
        require(all(control[k] == v for k, v in spec.items()) and control['snapshot_file'] == spec['file'],
                'immutable control source link')
        path = ROOT / spec['file']
        with np.load(path, allow_pickle=False) as saved:
            patch = saved['snapshot'].copy()
        require(digest(patch) == spec['snapshot_hash'], 'control complete-component hash')
        original = spec['kind'] == 'phase'
        key = cache_key(patch, spec['identity'], original, cfg['search'])
        require(control['search_key'] == key and control['search_dir'] == f'searches/{key}', 'control canonical input binding')
        outcome = read(OUT / control['search_dir'] / 'result.json')
        confirmation = outcome['confirmation']
        require(control['transmission_confirmed'] == (confirmation is not None) and
                control['confirmed_identity'] == (confirmation['identity'] if confirmation else None),
                'control endpoint labels')
        search_inputs[key] = (path, spec['identity'], original)
        counts['phase_controls_verified' if original else 'omitted_controls_verified'] += 1
    expected_world_links = []
    worlds = []
    require(len(manifest['runs']) == cfg['limits']['worlds'] == 20, 'all20 native worlds')
    for spec in manifest['runs']:
        rid = spec['run_id']
        folder = OUT / 'worlds' / rid
        binding = {'manifest_sha256': sha(OUT / 'manifest.json'), 'initial_hash': spec['initial_hash'], 'run_id': rid}
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
                        'cached complete input must retain same identity and endpoint')
                search_inputs[key] = candidate
        proven('world', rid, paths, spec['initial_hash'], counts,
               lambda spec=spec: world(spec, manifest, counts))
        expected_world_links.append({'run_id': rid, 'result_sha256': sha(folder / 'result.json')})
        worlds.append(result)
    require(results['worlds'] == expected_world_links, 'complete native result link inventory')
    require({p.name for p in (OUT / 'worlds').iterdir() if p.is_dir()} == {s['run_id'] for s in manifest['runs']},
            'extra or omitted native world folders')
    for key, (path, identity, original) in sorted(search_inputs.items()):
        search_unit(key, path, identity, original, manifest, counts)
    require({p.name for p in (OUT / 'searches').iterdir() if p.is_dir()} == set(search_inputs),
            'extra or omitted cached search folders')
    expected_roots = {s['search_key'] + '.npz' for w in worlds for s in w['sources'] if s['snapshot_file']}
    require({p.name for p in (OUT / 'roots').iterdir() if p.is_file() and not p.name.endswith('.tmp')} == expected_roots,
            'complete eligible root inventory including unsearched')
    expected = analysis_summary(manifest, worlds, results['controls'])
    require(read(OUT / 'analysis.json') == expected, 'independent exact source census, search totals or gate differs')
    counts['exact_census_and_gate_verified'] += 1
    report.update({'status': 'passed', 'mismatches': 0, 'experiment_id': manifest['experiment_id'],
        'rule_hash': RULE_HASH, 'manifest_sha256': sha(OUT / 'manifest.json'),
        'auditor_sha256': sha(Path(__file__)), 'gate_status': expected['gate_status'],
        'evidence_sha256': {name: sha(OUT / name) for name in ('results.json', 'analysis.json', 'acquisition.json')},
        'total': expected['total'], 'prior_coverage_gate': 'failed; unchanged'})


def main():
    global FRESH
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fresh', action='store_true', help='replay instead of reusing passed hash-bound proofs')
    FRESH = parser.parse_args().fresh
    started = time.perf_counter()
    report = {'status': 'running', 'counts': Counter(),
        'scope': 'all20 complete1600 native histories,100 full census grids, every detected source, complete topology/extraction, local key admission,33 controls, all executed unique serial searches and exact independent gates; no total viable population or native genetic ancestry'}
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
