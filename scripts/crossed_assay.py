"""Hash-bound, one-worker acquisition of the frozen crossed source assay."""
import argparse
import hashlib
import json
import platform
import resource
import subprocess
import time
from collections import Counter
from fractions import Fraction

import numpy as np

from evoloop.engine import ROOT, RULE_HASH, advance, digest
from evoloop.ecology import observation
from evoloop.fate import expanded_search
from evoloop.periodic_assays import offspring_generation
from evoloop.developmental import conjunction, fraction, partition, strict_interval_superiority
from evoloop.crossed import comparisons
from scripts.coverage_assay import atomic_json, atomic_npz, receipt, verify_receipt, search_fields
from scripts.coverage_protocol import sha, require
from scripts.developmental_measure import classify

OUT = ROOT / 'data/crossed-v1'
IMPLEMENTATION = ['evoloop/crossed.py', 'scripts/crossed_assay.py', 'scripts/verify_crossed.py',
                  'tests/test_crossed_assay.py', 'tests/test_crossed_audit.py',
                  'scripts/verify_developmental.py', 'scripts/memory_guard.py']
RESPONSE_NAMES = ('worlds', 'searches', 'roots', 'results.json', 'analysis.json',
                  'benchmark.json', 'acquisition.json', 'integrity.json', 'integrity-proofs')
ORIGIN_RECORDS = ['data/atlas-v2/manifest.json', 'data/atlas-v2/analysis.json',
                  'data/atlas-v2/confirmed/catalogue.json']


def read(path):
    return json.loads(path.read_text())


def search_key(snapshot, identity, cfg, original=False):
    binding = {'snapshot_hash': digest(snapshot), 'snapshot_shape': list(snapshot.shape),
               'snapshot_dtype': str(snapshot.dtype), 'input_identity': identity,
               'rule_hash': RULE_HASH, 'search_config': cfg, 'original_endpoint': original}
    return hashlib.sha256(json.dumps(binding, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def execution_manifest(manifest):
    measure = manifest['measure_config']
    return {**manifest, 'config': {**manifest['config'], 'search': measure['search'],
                                  'extraction': measure['extraction']}}


def verify_design():
    m = read(OUT / 'manifest.json')
    require(m['config'] == read(ROOT / 'configs/crossed-v1.json') and m['rule_hash'] == RULE_HASH,
            'frozen configuration/rule changed')
    require(m['measure_config'] == read(ROOT / m['config']['measure_config']), 'frozen measure changed')
    require(all(sha(ROOT / p) == h for p, h in m['source_file_sha256'].items()),
            'frozen source/input/calibration changed')
    proof = read(OUT / 'design-integrity.json')
    require(proof['status'] == 'passed' and proof['mismatches'] == 0 and
            proof['manifest_sha256'] == sha(OUT / 'manifest.json') and
            proof['auditor_sha256'] == sha(ROOT / 'scripts/verify_crossed_design.py') and
            proof['counts']['complete_initial_states_verified'] == 160 and
            proof['counts']['complete_preparations_verified'] == 80 and
            proof['all_equivalence_pairs_verified'] == 23920,
            'complete independent design proof required')
    return m


def freeze_readiness():
    m = verify_design()
    require(not (OUT / 'readiness.json').exists(), 'immutable readiness already exists')
    inventory = {name: (OUT / name).exists() for name in RESPONSE_NAMES}
    require(not any(inventory.values()), 'response evidence must be absent before readiness freeze')
    validation = (OUT / 'implementation-validation.txt').read_text()
    require(validation.rstrip().endswith('OK') and 'FAILED' not in validation,
            'implementation validation must pass first')
    review = ROOT / 'docs/crossed-implementation-review.md'
    require(review.is_file() and 'Status: accepted' in review.read_text(), 'independent implementation review required')
    for name in ('manifest.json', 'design-integrity.json'):
        committed = subprocess.check_output(['git', 'show', f'HEAD:data/crossed-v1/{name}'], cwd=ROOT)
        require(hashlib.sha256(committed).hexdigest() == sha(OUT / name), 'design and audit must already be committed')
    atomic_json(OUT / 'readiness.json', {'schema_version': 1, 'status': 'ready_before_main_acquisition',
        'experiment_id': m['experiment_id'], 'manifest_sha256': sha(OUT / 'manifest.json'),
        'design_integrity_sha256': sha(OUT / 'design-integrity.json'),
        'code_hashes': {p: sha(ROOT / p) for p in IMPLEMENTATION},
        'source_records_sha256': {p: sha(ROOT / p) for p in ORIGIN_RECORDS},
        'validation_sha256': sha(OUT / 'implementation-validation.txt'),
        'review_sha256': sha(review), 'pre_acquisition_inventory': inventory,
        'environment': {'python': platform.python_version(), 'numpy': np.__version__},
        'execution': m['config']['execution'], 'main_outcomes': 'not acquired'})
    print('Implementation readiness frozen; responses unacquired', flush=True)


def verify():
    m = verify_design()
    r = read(OUT / 'readiness.json')
    require(r['status'] == 'ready_before_main_acquisition' and r['manifest_sha256'] == sha(OUT / 'manifest.json') and
            r['design_integrity_sha256'] == sha(OUT / 'design-integrity.json'), 'design/readiness changed')
    require(r['code_hashes'] == {p: sha(ROOT / p) for p in IMPLEMENTATION}, 'implementation changed after freeze')
    require(r['source_records_sha256'] == {p: sha(ROOT / p) for p in ORIGIN_RECORDS}, 'originating encounter evidence changed')
    require(r['validation_sha256'] == sha(OUT / 'implementation-validation.txt') and
            r['review_sha256'] == sha(ROOT / 'docs/crossed-implementation-review.md'), 'validation/review changed')
    return execution_manifest(m)


def common_binding():
    return {'manifest_sha256': sha(OUT / 'manifest.json'), 'readiness_sha256': sha(OUT / 'readiness.json')}


def verify_committed_freeze(commit):
    ready = read(OUT / 'readiness.json')
    paths = {**ready['code_hashes'], **ready['source_records_sha256'],
        'data/crossed-v1/manifest.json': ready['manifest_sha256'],
        'data/crossed-v1/design-integrity.json': ready['design_integrity_sha256'],
        'data/crossed-v1/readiness.json': sha(OUT / 'readiness.json'),
        'data/crossed-v1/implementation-validation.txt': ready['validation_sha256'],
        'docs/crossed-implementation-review.md': ready['review_sha256']}
    for path, expected in paths.items():
        committed = subprocess.check_output(['git', 'show', f'{commit}:{path}'], cwd=ROOT)
        require(hashlib.sha256(committed).hexdigest() == expected, f'freeze commit must bind {path}')


def search(snapshot, identity, m, original=False):
    cfg = m['config']['search']
    key = search_key(snapshot, identity, cfg, original)
    folder = OUT / 'searches' / key
    binding = {**common_binding(), 'snapshot_hash': digest(snapshot), 'input_identity': identity,
               'snapshot_shape': list(snapshot.shape), 'snapshot_dtype': str(snapshot.dtype),
               'original_endpoint': original, 'search_config': cfg, 'rule_hash': RULE_HASH}
    if not verify_receipt(folder, binding):
        def persist(node, arrays):
            name = 'confirmation' if 'confirmation' in node else f'node-{node["node"]:02d}'
            atomic_json(folder / f'{name}.json', node)
            atomic_npz(folder / f'{name}.npz', **arrays)
        outcome = expanded_search(snapshot, identity, cfg,
            (lambda gt: gt == identity) if original else (lambda gt: True), persist,
            generation=offspring_generation)
        atomic_json(folder / 'result.json', outcome)
        receipt(folder, binding)
    return key, read(folder / 'result.json')


def control(spec, m):
    with np.load(ROOT / spec['file'], allow_pickle=False) as saved:
        patch = saved['snapshot'].copy()
    require(digest(patch) == spec['snapshot_hash'], 'control physical hash changed')
    key, outcome = search(patch, spec['identity'], m, spec['kind'] == 'phase')
    return {**spec, 'snapshot_file': spec['file'], 'search_key': key, 'search_dir': f'searches/{key}',
        'transmission_confirmed': outcome['confirmation'] is not None,
        'confirmed_identity': outcome['confirmation']['identity'] if outcome['confirmation'] else None}


def benchmark():
    m = verify()
    require(not (OUT / 'benchmark.json').exists(), 'preserve completed benchmark')
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    verify_committed_freeze(commit)
    start = time.perf_counter()
    result = control(m['controls'][0], m)
    require(result['transmission_confirmed'], 'first positive control failed')
    record = {'status': 'passed', 'control': result['name'], 'seconds': time.perf_counter() - start,
        'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, 'workers': 1,
        **common_binding(), 'scope': 'one repeated control; timing, not replication'}
    atomic_json(OUT / 'benchmark.json', record)
    print(record, flush=True)


def world(spec, m):
    folder = OUT / 'worlds' / spec['run_id']
    binding = {**common_binding(), 'initial_hash': spec['initial_hash'], 'run_id': spec['run_id']}
    if verify_receipt(folder, binding):
        print('REUSE WORLD', spec['run_id'], flush=True)
        return read(folder / 'result.json')
    with np.load(ROOT / spec['initial_file'], allow_pickle=False) as saved:
        grid = saved['grid'].copy()
    require(digest(grid) == spec['initial_hash'], 'complete initial physical hash changed')
    cfg = m['config']
    samples, sources, totals, admitted = [], [], [], set()
    start = time.perf_counter()
    for t in range(0, cfg['horizon'] + 1, cfg['structural_sample_interval']):
        if t:
            advance(grid, cfg['structural_sample_interval'])
        counts, records, loops = observation(grid, m['registry'])
        samples.append({'t': t, **counts, 'cores': records})
        if t not in cfg['source_times']:
            continue
        atomic_npz(folder / f'grid-{t}.npz', grid=grid)
        rows = []
        for organism in sorted(loops, key=lambda row: tuple(row['core'])):
            patch = organism['isolation_snapshot']
            eligible = patch is not None and max(patch.shape) + cfg['extraction']['minimum_empty_margin_total'] <= cfg['shape'][0]
            status = ('eligible' if eligible else 'component_too_large' if patch is not None
                      else organism['extraction_status'])
            extraction_status = status
            key = search_key(patch, organism['genotype'], cfg['search']) if eligible else None
            rootfile = f'roots/{key}.npz' if eligible else None
            outcome, directory = None, None
            if eligible:
                rootpath = OUT / rootfile
                if rootpath.exists():
                    with np.load(rootpath, allow_pickle=False) as saved:
                        require(saved['snapshot'].dtype == patch.dtype and np.array_equal(saved['snapshot'], patch),
                                'cached complete root changed')
                else:
                    atomic_npz(rootpath, snapshot=patch)
                if key not in admitted and len(admitted) >= cfg['limits']['unique_admitted_keys_per_world']:
                    status = 'unsearched_budget'
                else:
                    admitted.add(key)
                    key, outcome = search(patch, organism['genotype'], m)
                    directory = f'searches/{key}'
                    status = 'confirmed' if outcome['confirmation'] else 'unresolved_search'
            row = {'run_id': spec['run_id'], 'state': spec['state'], 'treatment': spec['treatment'], 't': t,
                'core': organism['core'], 'source_identity': organism['genotype'],
                'source_class': classify(organism['genotype'], m['registry']),
                'extraction_status': extraction_status, 'snapshot_hash': digest(patch) if eligible else None,
                'snapshot_shape': list(patch.shape) if eligible else None,
                'snapshot_dtype': str(patch.dtype) if eligible else None,
                'snapshot_file': rootfile, 'search_key': key, 'search_dir': directory, 'status': status,
                **search_fields(outcome, organism['genotype'], m['registry'])}
            rows.append(row)
            sources.append(row)
        totals.append({'t': t, **partition(rows)})
    atomic_npz(folder / 'final.npz', grid=grid)
    result = {**spec, 'rule_hash': RULE_HASH, 'completed_updates': cfg['horizon'], 'final_hash': digest(grid),
              'samples': samples, 'sources': sources, 'snapshot_counts': totals,
              'admitted_distinct_keys': len(admitted), 'seconds': time.perf_counter() - start}
    atomic_json(folder / 'result.json', result)
    receipt(folder, binding)
    print('WORLD', spec['run_id'], 'Q/C', sum(r['Q'] for r in totals), sum(r['C'] for r in totals), flush=True)
    return result


def summary(m, worlds, controls):
    cfg = m['config']
    rows = [r for w in worlds for r in w['sources']]
    cells, panels, contrasts = comparisons(cfg, worlds)
    lookup = {(p['state'], p['split']): p for p in panels}
    phase, omitted = ([c for c in controls if c['kind'] == kind] for kind in ('phase', 'omitted'))
    gates = {'frozen_calibration': m['calibration_gate_status'] == 'passed',
        'repeated_phase_controls': sum(c['transmission_confirmed'] for c in phase) == 30,
        'repeated_omitted_controls': sum(c['transmission_confirmed'] for c in omitted) == 3,
        'matched_exposure': m['exposure_verified'], 'distinct_confirmation': m['distinct_confirmation_verified']}
    benefits = []
    for pair in cfg['pairs']:
        details = []
        for split in ('development', 'confirmation'):
            candidate = lookup[pair['candidate'], split]
            inputs = [lookup[state, split] for state in pair['inputs']]
            details.append({'split': split,
                'relative_robust_superiority': strict_interval_superiority(candidate['retention'], [i['retention'] for i in inputs]),
                'absolute_robust_superiority': strict_interval_superiority(candidate['disturbed_mean'], [i['disturbed_mean'] for i in inputs])})
        relative = conjunction(p['relative_robust_superiority'] for p in details)
        absolute = conjunction(p['absolute_robust_superiority'] for p in details)
        joint = conjunction([relative, absolute, *gates.values()])
        benefits.append({**pair, 'panels': details, 'relative_robust_superiority': relative,
            'absolute_robust_superiority': absolute, 'joint_confirmed': joint is True,
            'originating_encounter': m['states'][pair['candidate']]['source']['run_id'],
            'classification': 'joint_confirmed' if joint is True else 'robust_criterion_unresolved' if joint is None else 'robust_criterion_not_met',
            'biological_advantage': 'conditional_assay_advantage' if joint is True else 'unresolved'})
    keys = {r['search_key'] for r in rows if r['search_dir']} | {c['search_key'] for c in controls}
    confirmed = {b['originating_encounter'] for b in benefits if b['joint_confirmed']}
    denominators = cfg['benefit']['originating_encounter_denominators']
    yields = []
    for split, denominator in denominators.items():
        n = len(confirmed) if split == 'overall' else sum(
            ('near-main-' in rid) if split == 'main' else ('near-heldout-' in rid) for rid in confirmed)
        yields.append({'split': split, 'confirmed': n, 'denominator': denominator,
                       'fraction': fraction(Fraction(n, denominator))})
    return {'experiment_id': m['experiment_id'], 'complete_worlds': len(worlds),
        'snapshot_strata': sum(len(w['snapshot_counts']) for w in worlds), 'total': partition(rows),
        'by_class': [{'source_class': label, **partition([r for r in rows if r['source_class'] == label])}
                     for label in ('scored', 'valid_unregistered', 'unknown_identity')],
        'source_statuses': dict(Counter(r['status'] for r in rows)), 'unique_searches': len(keys),
        'generation_simulations': sum(read(OUT / 'searches' / key / 'result.json')['generation_simulations'] for key in keys),
        'controls': {'phase_confirmed': sum(c['transmission_confirmed'] for c in phase), 'phase_selected': len(phase),
                     'omitted_confirmed': sum(c['transmission_confirmed'] for c in omitted), 'omitted_selected': len(omitted)},
        'gate_checks': gates, 'cells': cells, 'panels': panels, 'contrasts': contrasts, 'benefits': benefits,
        'originating_encounter_denominators': cfg['benefit']['originating_encounter_denominators'],
        'joint_confirmed_encounters': len(confirmed), 'yield': yields,
        'unresolved_other_candidate_encounters': 16,
        'earlier_outcomes': 'protocols007/009/010 unchanged',
        'scope': 'detected-source recovery/population envelopes; nested deterministic configurations, not total viable population, independent histories, H1/H3 or RSI'}


def run(commit):
    m = verify()
    b = read(OUT / 'benchmark.json')
    require(b['status'] == 'passed' and all(b[k] == v for k, v in common_binding().items()), 'bound benchmark first')
    require(commit and subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == commit,
            'frozen acquisition commit must be current HEAD')
    verify_committed_freeze(commit)
    record = {'freeze_commit': commit, **common_binding()}
    if (OUT / 'acquisition.json').exists():
        require(read(OUT / 'acquisition.json') == record, 'preserve acquisition provenance on resume')
    else:
        atomic_json(OUT / 'acquisition.json', record)
    start = time.perf_counter()
    controls = [control(c, m) for c in m['controls']]
    worlds = [world(r, m) for r in m['runs']]
    result = {'experiment_id': m['experiment_id'], **common_binding(),
        'worlds': [{'run_id': w['run_id'], 'result_sha256': sha(OUT / 'worlds' / w['run_id'] / 'result.json')} for w in worlds],
        'controls': controls, 'seconds': time.perf_counter() - start,
        'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    atomic_json(OUT / 'results.json', result)
    atomic_json(OUT / 'analysis.json', summary(m, worlds, controls))
    print('COMPLETE', len(worlds), 'worlds', flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('freeze-readiness', 'verify', 'benchmark', 'run'))
    parser.add_argument('--freeze-commit')
    args = parser.parse_args()
    if args.command == 'freeze-readiness':
        freeze_readiness()
    elif args.command == 'verify':
        print('Verified design and readiness bindings', len(verify()['runs']), 'worlds', flush=True)
    elif args.command == 'benchmark':
        benchmark()
    else:
        run(args.freeze_commit)


if __name__ == '__main__':
    main()
