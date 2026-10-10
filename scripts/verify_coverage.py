"""Independent protocol 010 native, extraction, search and exact-gate replay.

Run after acquisition and analysis, under scripts.memory_guard, with one worker.
Production coverage acquisition/analysis helpers are deliberately not imported.
Atomic per-world and per-search proof receipts permit hash-verified resumption.
"""
import argparse
import json
import resource
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
from scripts.verify_ecological import graph, isolated, measured, read, require, same, sha
from scripts.verify_impact import components, mask_for

OUT = ROOT / 'data/coverage-v1'
FRESH = False


class MemoryHeadroomError(RuntimeError):
    """Execution interruption, never a scientific evidence mismatch."""


def headroom():
    if available_mib() < 200:
        raise MemoryHeadroomError('memory headroom below 200 MiB; resume guarded audit')


def evidence_hashes(paths):
    files = set()
    for path in paths:
        require(path.exists(), f'proof evidence missing: {path}')
        if path.is_dir():
            files.update(p for p in path.rglob('*') if p.is_file())
        else:
            files.add(path)
    return {str(p.relative_to(ROOT)): sha(p) for p in sorted(files)}


def proven(kind, name, paths, initial_hash, counts, operation):
    """Reuse only a passed complete proof whose evidence and verifier bytes agree."""
    headroom()
    evidence = evidence_hashes(paths)
    provenance = {'auditor_sha256': sha(Path(__file__)),
        'manifest_sha256': sha(OUT / 'manifest.json'),
        'readiness_sha256': sha(OUT / 'readiness.json'),
        'rule_hash': RULE_HASH, 'initial_grid_or_component_hash': initial_hash,
        'reused_verifier_sha256': {p: sha(ROOT / p) for p in (
            'scripts/verify_ecological.py', 'scripts/verify_fresh.py',
            'scripts/verify_impact.py', 'scripts/memory_guard.py')},
        'physical_source_sha256': evidence}
    destination = OUT / 'integrity-proofs' / kind / f'{name}.json'
    if destination.exists() and not FRESH:
        receipt = read(destination)
        if receipt.get('status') == 'passed' and receipt.get('provenance') == provenance:
            delta = receipt['verified_counts_delta']
            require(all(isinstance(v, int) and v >= 0 for v in delta.values()), 'invalid proof counts')
            counts.update(delta)
            counts[f'{kind}_proofs_reused'] += 1
            print('reused checked coverage proof', kind, name, flush=True)
            return
    before = counts.copy()
    started = time.perf_counter()
    operation()
    require(evidence_hashes(paths) == evidence, f'{kind}/{name}: evidence changed during verification')
    delta = {k: counts[k] - before[k] for k in counts if counts[k] != before[k]}
    require(all(v >= 0 for v in delta.values()), 'proof count regression')
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix('.json.tmp')
    write_json(temporary, {'status': 'passed', 'mismatches': 0, 'kind': kind,
        'unit': name, 'provenance': provenance, 'verified_counts_delta': delta,
        'verification_seconds': time.perf_counter() - started,
        'scope': 'complete original-dense trajectory and source/delay evidence' if kind == 'world'
                 else 'complete DFS graph, dense isolated states and sampled child-admission schedule'})
    temporary.replace(destination)
    counts[f'{kind}_proofs_created'] += 1


def identity_class(identity, registry):
    return ('unknown_identity' if identity is None else
            'scored' if identity in registry else 'valid_unregistered')


def native_labels(target, samples, horizon=1600, interval=20):
    window = [s for s in samples if target['t'] <= s['t'] <= target['t'] + horizon]
    require([s['t'] for s in window] == list(range(target['t'], target['t'] + horizon + 1, interval)),
            'native observation window incomplete')
    present = [next((o for o in s['cores'] if o['core'] == target['core']), None) for s in window]
    loss = next((s['t'] for s, o in zip(window, present) if o is None), None)
    recurrence = next((s['t'] for s, o in zip(window, present)
                       if loss is not None and s['t'] > loss and o is not None), None)
    word = target['identity'].split(':', 1)[1] if target['identity'] else None
    matches = None if word is None else [s['t'] for s in window if any(
        o['core'] != target['core'] and o['identity'] is not None and
        o['identity'].split(':', 1)[1] == word for o in s['cores'])]
    return {'horizon': horizon, 'sample_interval': interval,
        'fixed_core_first_loss_t': loss, 'fixed_core_first_recurrence_t': recurrence,
        'endpoint_identity': present[-1]['identity'] if present[-1] is not None else None,
        'endpoint_core_present': present[-1] is not None,
        'matching_word_status': 'unknown_source_word' if word is None else 'observed',
        'matching_word_elsewhere_first_t': matches[0] if matches else None,
        'boundary_first_t': next((s['t'] for s in window if s['boundary_activity']), None),
        'interpretation': 'overlapping structural continuations; no native offspring or genetic ancestry assignment'}


def complete_component(grid, organism, patch, counts):
    same(patch, organism['isolation_snapshot'], 'complete periodic component snapshot')
    require(any(np.array_equal(mask_for(grid, organism), cc) for cc in components(grid)),
            'independent occupied flood fill differs from complete extracted component')
    counts['complete_components_verified'] += 1


def generation_schedule(folder, node, cfg, counts):
    """Reconstruct every admitted child and ignored interval with the dense kernel.

    This checks first-seen events, sampling, horizon, order and offspring cap,
    beyond the saved-child/final-state replay performed by graph().
    """
    headroom()
    report = node['outcome']
    path = folder / f'node-{node["node"]:02d}.npz'
    with np.load(path, allow_pickle=False) as saved:
        if 'initial_hash' not in report:
            require(report == {'status': 'ineligible_component_size', 'children': []}
                    and not saved.files, 'invalid oversized node')
            return
        grid = saved['initial'].copy()
        initial = grid.copy()
        originals = {tuple(o['core']) for o in detect(grid)}
        admitted = set()
        first_seen = {}
        previous = set()
        children = []
        samples = []
        events = []
        boundary = None
        interval = cfg['detection_interval']
        for t in range(0, cfg['generation_horizon'] + 1, interval):
            if t:
                advance(grid, interval)
            if boundary is None and (np.any(grid[[0, -1]]) or np.any(grid[:, [0, -1]])):
                boundary = t
            loops = detect(grid)
            now = {tuple(o['core']) for o in loops}
            for o in loops:
                core = tuple(o['core'])
                if core not in previous:
                    first_seen.setdefault(core, t)
                    events.append({'type': 'core_appearance', 't': t,
                                   'core': o['core'], 'identity': o['genotype']})
                patch = o['isolation_snapshot']
                if core in originals or core in admitted or o['genotype'] is None or patch is None:
                    continue
                admitted.add(core)
                child = {'detached_t': t, 'closure_first_seen_t': first_seen[core],
                    'core': o['core'], 'identity': o['genotype'], 'snapshot_hash': digest(patch),
                    'extraction_bbox': o['extraction_bbox'],
                    'size_eligible': max(patch.shape) + 20 <= cfg['isolation_shape'][0]}
                index = len(children)
                require(index < len(report['children']), f'{folder}: omitted eligible child')
                require(report['children'][index] == child, f'{folder}: first detached child ordering/metadata')
                same(saved[f'child{index}'], patch, 'independent admitted child extraction')
                same(saved[f'selection_grid{index}'], grid, 'independent complete child selection grid')
                complete_component(grid, o, patch, counts)
                children.append(child)
                if len(children) >= cfg['offspring_per_generation']:
                    break
            events.extend({'type': 'core_loss', 't': t, 'core': list(core)}
                          for core in sorted(previous - now))
            previous = now
            if t % 100 == 0:
                samples.append({'t': t, 'closed_cores': len(loops),
                                'occupied_cells': int(np.count_nonzero(grid))})
            counts['isolated_detection_samples_verified'] += 1
            if len(children) >= cfg['offspring_per_generation']:
                break
        expected = {'status': 'offspring_observed' if children else
                    'unresolved_at_horizon' if np.any(grid) else 'assay_extinct',
            'initial_hash': digest(initial), 'final_hash': digest(grid),
            'completed_updates': t, 'horizon': cfg['generation_horizon'],
            'sampling_interval': interval, 'boundary_first_t': boundary,
            'children': children, 'samples': samples, 'events': events}
        require(expected == report, f'{folder}: full isolated report differs')
        same(saved['final'], grid, 'independent isolated terminal state')
        counts['dense_admission_schedule_updates_replayed'] += t


def search(outcome, folder, snapshot, identity, original, cfg, counts):
    headroom()
    graph(outcome, folder, snapshot, identity, original, cfg, counts)
    expected = {'result.json', 'receipt.json'}
    for node in outcome['nodes']:
        expected.update((f'node-{node["node"]:02d}.json', f'node-{node["node"]:02d}.npz'))
    if outcome['confirmation'] is not None:
        expected.update(('confirmation.json', 'confirmation.npz'))
    require({p.name for p in folder.iterdir() if p.is_file() and not p.name.endswith('.tmp')} == expected,
            f'{folder}: complete isolated evidence inventory')
    for node in outcome['nodes']:
        generation_schedule(folder, node, cfg, counts)


def receipt(folder, binding):
    saved = read(folder / 'receipt.json')
    require(saved['binding'] == binding, f'{folder}: acquisition receipt binding')
    actual = {str(p.relative_to(folder)): sha(p) for p in sorted(folder.rglob('*'))
              if p.is_file() and p != folder / 'receipt.json' and not p.name.endswith('.tmp')}
    require(saved['artifact_sha256'] == actual, f'{folder}: complete acquisition receipt artifact hashes')


def world(spec, manifest, counts):
    """Reconstruct the source-time choice before any extraction eligibility test."""
    rid = spec['run_id']
    folder = OUT / 'worlds' / rid
    result = read(folder / 'result.json')
    cfg = manifest['config']
    require(all(result[k] == v for k, v in spec.items()), f'{rid}: manifest fields')
    require(result['rule_hash'] == RULE_HASH, f'{rid}: rule hash')
    require(result['readiness_sha256'] == sha(OUT / 'readiness.json'), f'{rid}: readiness link')
    stop = cfg['native']['maximum_world_update']
    interval = cfg['native']['sample_interval']
    source_times = cfg['sampling']['source_times']
    delays = cfg['native']['maturation_delays']
    require(result['completed_updates'] == stop and len(result['samples']) == stop // interval + 1,
            f'{rid}: complete native observation horizon')
    with np.load(ROOT / spec['initial_file'], allow_pickle=False) as saved:
        grid = saved['grid'].copy()
    require(digest(grid) == spec['initial_hash'] and grid.shape == tuple(cfg['shape'])
            and grid.dtype == np.uint8, f'{rid}: complete original start')
    original_path = ROOT / Path(cfg['source_manifest']).parent / spec['split'] / rid / 'result.json'
    original = read(original_path)
    require(original['completed_updates'] == 1600, f'{rid}: original response horizon')
    samples = []
    strata = []
    targets = []
    snapshot_times = {t + d for t in source_times for d in delays}
    expected_files = {'result.json', 'receipt.json', 'final.npz'}
    for index, t in enumerate(range(0, stop + 1, interval)):
        headroom()
        if t:
            advance(grid, interval)
        values, records, loops = measured(grid, manifest['registry'])
        sample = {'t': t, **values, 'cores': records,
                  'boundary_activity': bool(np.any(grid[[0, -1]]) or np.any(grid[:, [0, -1]]))}
        require(sample == result['samples'][index], f'{rid}@{t}: complete native sample')
        if t <= 1600:
            require({k: v for k, v in sample.items() if k != 'boundary_activity'} == original['samples'][index],
                    f'{rid}@{t}: preserved protocol 009 sample')
            counts['original_samples_verified'] += 1
        samples.append(sample)
        counts['world_samples_verified'] += 1
        if t in snapshot_times:
            name = f'grid-{t}.npz'
            expected_files.add(name)
            with np.load(folder / name, allow_pickle=False) as saved:
                require(saved.files == ['grid'], f'{rid}@{t}: source/delay array inventory')
                same(saved['grid'], grid, f'{rid}@{t}: full source/delay grid')
            counts['source_delay_grids_verified'] += 1
        if t in source_times:
            for label in cfg['sampling']['classes']:
                options = sorted((o for o in loops if identity_class(o['genotype'], manifest['registry']) == label),
                                 key=lambda o: tuple(o['core']))
                sid = f'{rid}-t{t}-{label}'
                strata.append({'stratum_id': sid, 'source_time': t, 'source_class': label,
                               'available_cores': len(options), 'selected_cores': int(bool(options))})
                counts['strata_verified'] += 1
                if not options:
                    counts['empty_strata_verified'] += 1
                    continue
                o = options[0]
                target = {'observation_id': sid, 'run_id': rid, 'state': spec['state'],
                    'treatment': spec['treatment'], 'source_time': t, 'source_class': label,
                    'source_identity': o['genotype'], 'source_identity_unknown': o['genotype'] is None,
                    'core': o['core'], 'delays': []}
                targets.append(target)
        for target in targets:
            delay = t - target['source_time']
            if delay not in delays:
                continue
            o = next((o for o in loops if o['core'] == target['core']), None)
            window = [s for s in samples if s['t'] >= target['source_time']]
            lost = any(not any(c['core'] == target['core'] for c in s['cores']) for s in window)
            patch = o['isolation_snapshot'] if o is not None else None
            if lost:
                status = 'sampled_target_lost'
            elif patch is None:
                raw_status = o['extraction_status'] if o is not None else 'missing_complete_component'
                status = raw_status if raw_status in ('shared_component', 'noncontractible_component') else 'missing_complete_component'
            elif max(patch.shape) + 20 > cfg['search']['isolation_shape'][0]:
                status = 'component_too_large'
            else:
                status = 'eligible'
            delayed_identity = o['genotype'] if o is not None else None
            filename = (str((folder / f'{target["observation_id"]}-delay{delay}.npz').relative_to(OUT))
                        if status == 'eligible' else None)
            record = {'delay': delay, 't': t, 'delayed_identity': delayed_identity,
                'delayed_class': identity_class(delayed_identity, manifest['registry']) if o is not None else None,
                'delayed_core_present': o is not None, 'extraction_status': status,
                'snapshot_hash': digest(patch) if status == 'eligible' else None,
                'extraction_bbox': o.get('extraction_bbox') if o is not None else None,
                'snapshot_file': filename}
            if status == 'eligible':
                expected_files.add(Path(filename).name)
                with np.load(OUT / filename, allow_pickle=False) as saved:
                    require(saved.files == ['snapshot'], f'{rid}@{t}: delayed component inventory')
                    complete_component(grid, o, saved['snapshot'], counts)
                counts['eligible_delay_components_verified'] += 1
            target['delays'].append(record)
            counts['delay_selections_verified'] += 1
    for target in targets:
        labels = native_labels({'t': target['source_time'], 'core': target['core'],
                                'identity': target['source_identity']}, samples,
                               cfg['native']['continuation_horizon_from_source'], interval)
        target['native_continuation'] = labels
        counts['native_continuations_verified'] += 1
    require(result['strata'] == strata, f'{rid}: class availability and first lexicographic selection')
    require(result['observations'] == targets, f'{rid}: complete observation/delay/native labels')
    with np.load(folder / 'final.npz', allow_pickle=False) as saved:
        require(saved.files == ['grid'], f'{rid}: final inventory')
        same(saved['grid'], grid, f'{rid}: complete final state')
    require(digest(grid) == result['final_hash'], f'{rid}: final physical hash')
    require({p.name for p in folder.iterdir() if p.is_file() and not p.name.endswith('.tmp')} == expected_files,
            f'{rid}: complete world evidence inventory')
    counts['full_world_trajectories_verified'] += 1
    counts['dense_world_updates_replayed'] += stop
    print('verified coverage world', rid, 'selected', len(targets), flush=True)


def exact_gate(scored, baselines, states):
    """Integer thresholds with empty state denominators explicitly unresolved."""
    def confirmed(observation):
        return any(d['delay'] == 0 and d['outcome'] is not None and
                   d['outcome']['status'] == 'confirmed' for d in observation['delays'])
    by_state = [{'state': state, 'selected': sum(o['state'] == state for o in scored),
                 'confirmed': sum(o['state'] == state and confirmed(o) for o in scored)}
                for state in states]
    numerator = sum(confirmed(o) for o in scored)
    controls = sum(b['outcome']['status'] == 'confirmed' for b in baselines)
    overall = Fraction(numerator, len(scored)) >= Fraction(9, 10) if scored else None
    per_state = [Fraction(s['confirmed'], s['selected']) >= Fraction(4, 5)
                 if s['selected'] else None for s in by_state]
    checks = {'all_phase_controls': controls == 30, 'overall_scored_delay0': overall,
              'each_starting_state_delay0': None if any(v is None for v in per_state) else all(per_state)}
    passed = None if any(v is None for v in checks.values()) else all(checks.values())
    return {'checks': checks, 'passed': passed, 'phase_controls_confirmed': controls,
            'phase_controls_total': len(baselines), 'scored_delay0_confirmed': numerator,
            'scored_selected': len(scored), 'by_state': by_state}


def verify_fates(raw, observed, source_identity, registry, cfg):
    """Validate delayed identity links and separate reproduction/transmission labels."""
    require(all(observed[k] == value for k, value in raw.items()), 'raw native/recovery delay link')
    outcome = observed['outcome']
    eligible = raw['extraction_status'] == 'eligible'
    require((outcome is not None) == eligible, 'eligible searches and exclusions must all be retained')
    if not eligible:
        require(observed['search_dir'] is None, 'excluded delay must not have isolation folder')
    confirmation = outcome['confirmation'] if outcome is not None else None
    identity = confirmation['identity'] if confirmation is not None else None
    confirmed = confirmation is not None
    reproduction = bool(outcome['nodes'][0]['outcome']['children']) if outcome is not None else None
    extinct = ([n['node'] for n in outcome['nodes'] if n['outcome']['status'] == 'assay_extinct']
               if outcome is not None else [])
    expected = {'status': 'confirmed_stable_descendant' if confirmed else
                         'unresolved_search' if eligible else raw['extraction_status'],
        'root_reproduction_observed': reproduction, 'isolated_grid_extinction_nodes': extinct,
        'transmission_confirmed': confirmed, 'confirmed_identity': identity,
        'confirmed_identity_in_registry': identity in registry if confirmed else None,
        'same_as_source_identity': identity == source_identity if confirmed and source_identity is not None else None,
        'search_censoring': censoring(outcome, cfg),
        'inheritance_unresolved': not confirmed, 'ancestry_ambiguous': True,
        'benefit_pending': True if confirmed else None}
    require(all(observed[k] == value for k, value in expected.items()), 'separate recovery/fate labels')
    return confirmed


def censoring(outcome, cfg):
    if outcome is None:
        return []
    answer = list(outcome['truncations'])
    for node in outcome['nodes']:
        report = node['outcome']
        if len(report['children']) == cfg['offspring_per_generation']:
            answer.append({'reason': 'offspring_cap', 'node': node['node']})
        elif report['status'] == 'unresolved_at_horizon':
            answer.append({'reason': 'generation_horizon', 'node': node['node']})
    return answer


def selected_counts(observations):
    """One union per source, with every declared delay in the main denominator."""
    confirmed = lambda d: bool(d['outcome'] is not None and d['outcome']['status'] == 'confirmed')
    delays = [d for o in observations for d in o['delays']]
    require(all([d['delay'] for d in o['delays']] == [0, 100, 400] for o in observations),
            'all three delays must remain in each selected observation')
    return {'selected': len(observations), 'confirmed_any_delay': sum(
                any(confirmed(d) for d in o['delays']) for o in observations),
            'planned_delays': 3 * len(observations),
            'eligible_delays': sum(d['extraction_status'] == 'eligible' for d in delays),
            'confirmed_delays': sum(confirmed(d) for d in delays),
            'by_delay': [{'delay': delay, 'selected': len(observations),
                'eligible': sum(d['delay'] == delay and d['extraction_status'] == 'eligible' for d in delays),
                'confirmed': sum(d['delay'] == delay and confirmed(d) for d in delays)} for delay in (0, 100, 400)]}


def analysis_summary(recovery, manifest, results):
    """Derive all union counts from raw graph confirmations, never summary labels."""
    observations = recovery['observations']
    cfg = manifest['config']
    confirmed = lambda d: d['outcome'] is not None and d['outcome']['confirmation'] is not None
    union = lambda o: any(confirmed(d) for d in o['delays'])
    def summarize(rows):
        ds = [d for o in rows for d in o['delays']]
        expected = {'selected': len(rows), 'confirmed': sum(union(o) for o in rows),
            'eligible_observations': sum(any(d['extraction_status'] == 'eligible' for d in o['delays']) for o in rows),
            'planned_delays': 3 * len(rows), 'eligible_delays': sum(d['extraction_status'] == 'eligible' for d in ds),
            'confirmed_delays': sum(confirmed(d) for d in ds),
            'root_reproduction_delays': sum(d['outcome'] is not None and bool(d['outcome']['nodes'][0]['outcome']['children']) for d in ds),
            'delay_statuses': dict(Counter(d['status'] for d in ds)),
            'confirmed_registered_descendant_observations': sum(any(confirmed(d) and d['outcome']['confirmation']['identity'] in manifest['registry'] for d in o['delays']) for o in rows),
            'confirmed_outside_registry_descendant_observations': sum(any(confirmed(d) and d['outcome']['confirmation']['identity'] not in manifest['registry'] for d in o['delays']) for o in rows)}
        return expected
    scored = [o for o in observations if o['source_class'] == 'scored']
    gate = exact_gate(scored, recovery['baselines'], cfg['states'])
    checks = {'phase_controls': gate['checks']['all_phase_controls'],
        'overall_scored_delay0': gate['checks']['overall_scored_delay0'],
        'each_state_scored_delay0': gate['checks']['each_starting_state_delay0']}
    omitted = [o for o in observations if o['source_class'] != 'scored']
    ds = [d for o in observations for d in o['delays']]
    reports = [d['outcome'] for d in ds if d['outcome'] is not None] + [b['outcome'] for b in recovery['baselines']]
    breakdown = []
    run_lookup = {r['run_id']: r for r in manifest['runs']}
    def value_of(o, dimension):
        if dimension == 'condition':
            return run_lookup[o['run_id']]['condition']['id']
        if dimension == 'split':
            return run_lookup[o['run_id']]['split']
        return o[dimension]
    for dimension, values in (('state', cfg['states']), ('treatment', cfg['treatments']),
                             ('source_time', cfg['sampling']['source_times']),
                             ('condition', cfg['conditions']), ('split', ['development', 'confirmation']),
                             ('run_id', [r['run_id'] for r in manifest['runs']])):
        for value in values:
            for label in cfg['sampling']['classes']:
                breakdown.append({'dimension': dimension, 'value': value, 'source_class': label,
                    **summarize([o for o in observations if value_of(o, dimension) == value and o['source_class'] == label])})
    by_delay = []
    for delay in cfg['native']['maturation_delays']:
        for label in cfg['sampling']['classes']:
            rows = [(o, d) for o in observations if o['source_class'] == label
                    for d in o['delays'] if d['delay'] == delay]
            by_delay.append({'delay': delay, 'source_class': label, 'planned': len(rows),
                'eligible': sum(d['extraction_status'] == 'eligible' for _, d in rows),
                'confirmed': sum(confirmed(d) for _, d in rows),
                'identity_preserving': sum(confirmed(d) and o['source_identity'] is not None and
                    d['outcome']['confirmation']['identity'] == o['source_identity'] for o, d in rows),
                'statuses': dict(Counter(d['status'] for _, d in rows))})
    return {'experiment_id': manifest['experiment_id'], 'complete_worlds': len(recovery['worlds']),
        'phase_controls': {'confirmed': gate['phase_controls_confirmed'], 'selected': len(recovery['baselines'])},
        'gate_status': 'unresolved' if gate['passed'] is None else 'passed' if gate['passed'] else 'failed',
        'gate_checks': checks,
        'scored_delay0': {'confirmed': gate['scored_delay0_confirmed'], 'selected': len(scored),
            'per_state': [{'state': s['state'], 'selected': s['selected'], 'confirmed_delay0': s['confirmed']} for s in gate['by_state']]},
        'by_class': [{'source_class': label, **summarize([o for o in observations if o['source_class'] == label])} for label in cfg['sampling']['classes']],
        'by_delay': by_delay,
        'breakdown': breakdown, 'omitted': summarize(omitted),
        'omitted_recoverability_observed': any(union(o) for o in omitted),
        'generation_simulations': sum(r['generation_simulations'] for r in reports), 'search_roots': len(reports),
        'search_censoring': dict(Counter(c['reason'] for d in ds for c in censoring(d['outcome'], cfg['search']))),
        'phase_control_search_censoring': dict(Counter(c['reason'] for b in recovery['baselines']
            for c in censoring(b['outcome'], cfg['search']))),
        'isolated_extinction_nodes': sum(n['outcome']['status'] == 'assay_extinct' for r in reports for n in r['nodes']),
        'native_target_loss_observations': sum(o['native_continuation']['fixed_core_first_loss_t'] is not None for o in observations),
        'native_target_recurrence_observations': sum(o['native_continuation']['fixed_core_first_recurrence_t'] is not None for o in observations),
        'benefit': 'not_assayed; prior registry and outcomes unchanged',
        'scope': 'finite coordinate-selected diagnostic observations; not total viable population or independent histories',
        'strata': [s for spec in manifest['runs'] for s in results[spec['run_id']]['strata']],
        'recovery_sha256': sha(OUT / 'recovery.json'), 'readiness_sha256': sha(OUT / 'readiness.json')}


def audit(report):
    require(not sys.flags.optimize, 'generation_check assertions require ordinary Python, not -O')
    from scripts.coverage_protocol import verify as verify_design
    manifest = verify_design()
    require(manifest['rule_hash'] == RULE_HASH, 'frozen rule hash')
    ready = read(OUT / 'readiness.json')
    require(ready['manifest_sha256'] == sha(OUT / 'manifest.json'), 'readiness design hash')
    expected_code = {'scripts/coverage_assay.py', 'scripts/verify_coverage.py',
        'tests/test_coverage_assay.py', 'tests/test_verify_coverage.py',
        'scripts/verify_ecological.py', 'scripts/verify_fresh.py',
        'scripts/verify_impact.py', 'scripts/memory_guard.py'}
    require(set(ready['code_hashes']) == expected_code and
            all(sha(ROOT / name) == value for name, value in ready['code_hashes'].items()),
            'implementation changed after readiness')
    require(ready['validation_sha256'] == sha(OUT / 'validation.txt'), 'readiness validation bytes')
    source_dir = Path(manifest['config']['source_manifest']).parent
    source_paths = {str(source_dir / spec['split'] / spec['run_id'] / 'result.json')
                    for spec in manifest['runs']}
    require(set(ready['source_records_sha256']) == source_paths and
            all(sha(ROOT / name) == value for name, value in ready['source_records_sha256'].items()),
            'all original response records bound before acquisition')
    require(ready['execution'] == manifest['config']['execution'], 'readiness execution contract')
    benchmark = read(OUT / 'benchmark.json')
    require(benchmark['status'] == 'passed' and benchmark['workers'] == 1
            and benchmark['readiness_sha256'] == sha(OUT / 'readiness.json'), 'benchmark readiness gate')
    recovery = read(OUT / 'recovery.json')
    analysis = read(OUT / 'analysis.json')
    require(recovery['experiment_id'] == manifest['experiment_id'] and
            recovery['readiness_sha256'] == sha(OUT / 'readiness.json'), 'recovery experiment/readiness')
    counts = report['counts']
    cfg = manifest['config']
    results = {}
    expected_worlds = []
    expected_observations = []
    for spec in manifest['runs']:
        rid = spec['run_id']
        folder = OUT / 'worlds' / rid
        source_result = ROOT / Path(cfg['source_manifest']).parent / spec['split'] / rid / 'result.json'
        binding = {'manifest_sha256': sha(OUT / 'manifest.json'),
                   'readiness_sha256': sha(OUT / 'readiness.json'),
                   'initial_hash': spec['initial_hash'], 'run_id': rid}
        receipt(folder, binding)
        proven('world', rid, [folder, ROOT / spec['initial_file'], source_result],
               spec['initial_hash'], counts, lambda spec=spec: world(spec, manifest, counts))
        result = read(folder / 'result.json')
        results[rid] = result
        expected_worlds.append({'run_id': rid, 'result_sha256': sha(folder / 'result.json')})
        expected_observations.extend(result['observations'])
    require(len(results) == 40 and expected_worlds == recovery['worlds'], 'all 40 complete world source links')
    require(len(expected_observations) == len(recovery['observations']), 'selected observation inventory')
    for raw, recorded in zip(expected_observations, recovery['observations']):
        require(all(recorded[k] == value for k, value in raw.items() if k != 'delays'),
                'immutable source class/identity/core/native labels')
        require(len(recorded['delays']) == 3, 'all three planned delays retained')
        for raw_delay, delayed in zip(raw['delays'], recorded['delays']):
            verify_fates(raw_delay, delayed, raw['source_identity'], manifest['registry'], cfg['search'])
            if raw_delay['extraction_status'] == 'eligible':
                name = f'{raw["observation_id"]}-delay{raw_delay["delay"]}'
                folder = OUT / 'searches' / name
                require(delayed['search_dir'] == str(folder.relative_to(OUT)), 'canonical search folder')
                with np.load(OUT / raw_delay['snapshot_file'], allow_pickle=False) as saved:
                    patch = saved['snapshot'].copy()
                require(digest(patch) == raw_delay['snapshot_hash'], 'complete delayed root hash')
                identity = raw_delay['delayed_identity']
                # Initial identity is measured from the actual delayed patch,
                # including unknown-source snapshots that mature before isolation.
                prepared = isolated(patch, cfg['search']['isolation_shape'])
                initial = detect(prepared)
                require(len(initial) == 1 and initial[0]['genotype'] == identity, 'delayed search identity')
                binding = {'manifest_sha256': sha(OUT / 'manifest.json'),
                    'readiness_sha256': sha(OUT / 'readiness.json'), 'snapshot_hash': digest(patch),
                    'input_identity': identity, 'original_endpoint': False, 'search_config': cfg['search']}
                receipt(folder, binding)
                proven('search', name, [folder, OUT / raw_delay['snapshot_file']], digest(patch), counts,
                       lambda d=delayed, f=folder, p=patch, gt=identity: search(d['outcome'], f, p, gt, False, cfg['search'], counts))
            else:
                counts['ineligible_delays_verified'] += 1
            counts['selected_delays_verified'] += 1
        counts['selected_observations_verified'] += 1
    require(len(recovery['baselines']) == len(manifest['phase_controls']) == 30, 'all 30 fixed phase controls')
    for phase, baseline in zip(manifest['phase_controls'], recovery['baselines']):
        expected = {k: phase[k] for k in ('name', 'state', 'age', 'identity', 'snapshot_hash')}
        require(all(baseline[k] == value for k, value in expected.items()), 'fixed phase control source link')
        folder = OUT / 'controls' / phase['name']
        require(baseline['search_dir'] == str(folder.relative_to(OUT)), 'canonical phase search folder')
        with np.load(ROOT / phase['file'], allow_pickle=False) as saved:
            patch = saved['snapshot'].copy()
        require(digest(patch) == phase['snapshot_hash'], 'complete original phase control patch')
        binding = {'manifest_sha256': sha(OUT / 'manifest.json'), 'readiness_sha256': sha(OUT / 'readiness.json'),
            'snapshot_hash': digest(patch), 'input_identity': phase['identity'],
            'original_endpoint': True, 'search_config': cfg['search']}
        receipt(folder, binding)
        proven('search', f'control-{phase["name"]}', [folder, ROOT / phase['file']], digest(patch), counts,
               lambda b=baseline, f=folder, p=patch, gt=phase['identity']: search(b['outcome'], f, p, gt, True, cfg['search'], counts))
        counts['phase_controls_verified'] += 1
    require(analysis == analysis_summary(recovery, manifest, results), 'independent exact gate, union, denominator or breakdown differs')
    counts['exact_gate_and_unions_verified'] += 1
    report.update({'status': 'passed', 'mismatches': 0, 'experiment_id': manifest['experiment_id'],
        'rule_hash': RULE_HASH, 'manifest_sha256': sha(OUT / 'manifest.json'),
        'readiness_sha256': sha(OUT / 'readiness.json'), 'auditor_sha256': sha(Path(__file__)),
        'evidence_sha256': {name: sha(OUT / name) for name in ('recovery.json', 'analysis.json')},
        'gate_status': analysis['gate_status'], 'omitted': analysis['omitted']})


def main():
    global FRESH
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fresh', action='store_true', help='replay instead of reusing passed hash-bound proofs')
    FRESH = parser.parse_args().fresh
    started = time.perf_counter()
    report = {'status': 'running', 'counts': Counter(),
        'scope': 'all 40 complete 2800-update native worlds, original source records through 1600, all class selections and delays, full sampled loss/recurrence labels, complete component extraction, all executed isolated nodes and child admission schedules, exact integer gate and observation unions; no native genetic ancestry or total viable population'}
    try:
        audit(report)
    except BaseException as error:
        interrupted = isinstance(error, (KeyboardInterrupt, MemoryHeadroomError))
        report.update({'status': 'interrupted' if interrupted else 'failed',
            'mismatches': 0 if interrupted else 1,
            'error_type': type(error).__name__, 'error': str(error),
            'seconds': time.perf_counter() - started,
            'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
        temporary = OUT / 'integrity.json.tmp'
        write_json(temporary, report)
        temporary.replace(OUT / 'integrity.json')
        if isinstance(error, MemoryHeadroomError):
            raise SystemExit(75) from error
        raise
    report.update({'seconds': time.perf_counter() - started,
                   'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
    temporary = OUT / 'integrity.json.tmp'
    write_json(temporary, report)
    temporary.replace(OUT / 'integrity.json')
    print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    main()
