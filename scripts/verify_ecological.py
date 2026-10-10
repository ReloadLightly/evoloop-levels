"""Independent dense replay, source-to-search links, and exact ecological scores.

Run only after both batches and analyses finish:
    OPENBLAS_NUM_THREADS=1 python -m scripts.verify_ecological

No production ecological helper or analyzer is used. The previously validated
periodic detector remains the measurement reference. Individual isolated stage
replays additionally use verify_fresh.generation_check. This verifies the
recorded intervention and calibration endpoint, not native genetic ancestry.
"""
import hashlib
import json
import resource
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

from evoloop.engine import ROOT, RULE_HASH, advance, digest
from evoloop.periodic_tracking import detect
from scripts.atlas import write_json
from scripts.verify_fresh import generation_check

OUT = ROOT/'data/ecological-v1'


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def same(actual, expected, context):
    require(actual.dtype == expected.dtype and actual.shape == expected.shape
            and np.array_equal(actual, expected), context)


def isolated(snapshot, shape):
    require(snapshot.ndim == 2 and snapshot.dtype == np.uint8, 'invalid component')
    if max(snapshot.shape)+20 > shape[0]:
        return None
    grid = np.zeros(shape, np.uint8)
    y = shape[0]//2-snapshot.shape[0]//2
    x = shape[1]//2-snapshot.shape[1]//2
    grid[y:y+snapshot.shape[0], x:x+snapshot.shape[1]] = snapshot
    return grid


def measured(grid, registry):
    loops = detect(grid)
    records = []
    for o in loops:
        component = o['isolation_snapshot']
        records.append({'core': o['core'], 'identity': o['genotype'],
            'scored': o['genotype'] in registry,
            'extraction_status': o['extraction_status'],
            'extraction_bbox': o.get('extraction_bbox'),
            'snapshot_hash': digest(component) if component is not None else None,
            'component_shape': list(component.shape) if component is not None else None})
    counts = {'scored_cores': sum(o['scored'] for o in records),
        'unscored_valid_cores': sum(o['identity'] is not None and not o['scored'] for o in records),
        'unknown_identity_cores': sum(o['identity'] is None for o in records),
        'closed_cores': len(records), 'occupied_cells': int(np.count_nonzero(grid))}
    return counts, records, loops


def native_window(target, samples, horizon, interval):
    window = [s for s in samples if target['t'] <= s['t'] <= target['t']+horizon]
    require(window[0]['t'] == target['t'] and window[-1]['t'] == target['t']+horizon,
            'native continuation window incomplete')
    present = [any(o['core'] == target['core'] for o in s['cores']) for s in window]
    loss = next((s['t'] for s, p in zip(window, present) if not p), None)
    recurrence = next((s['t'] for s, p in zip(window, present)
                       if loss is not None and s['t'] > loss and p), None)
    endpoint = next((o for o in window[-1]['cores'] if o['core'] == target['core']), None)
    word = target['identity'].split(':', 1)[1] if target['identity'] else None
    matched = [s['t'] for s in window if word and any(o['core'] != target['core']
        and o['identity'] and o['identity'].split(':', 1)[1] == word for o in s['cores'])]
    return {'horizon': horizon, 'sample_interval': interval,
        'fixed_core_first_loss_t': loss, 'fixed_core_first_recurrence_t': recurrence,
        'endpoint_identity': endpoint['identity'] if endpoint else None,
        'matching_word_elsewhere_first_t': matched[0] if matched else None,
        'interpretation': 'overlapping structural continuations; no native offspring or genetic ancestry assignment'}


def world(spec, manifest, counts):
    rid = spec['run_id']; folder = OUT/spec['split']/rid
    result = read(folder/'result.json'); cfg = manifest['config']; benefit = manifest['benefit']
    for key, value in spec.items():
        require(result[key] == value, f'{rid}: result/manifest {key}')
    require(result['rule_hash'] == RULE_HASH, f'{rid}: rule hash')
    with np.load(OUT/'initial'/f'{rid}.npz', allow_pickle=False) as saved:
        grid = saved['grid'].copy()
    require(digest(grid) == spec['initial_hash'], f'{rid}: initial hash')
    with np.load(OUT/'snapshots.npz', allow_pickle=False) as saved:
        snapshot = np.ascontiguousarray(np.rot90(saved[spec['state']], spec['condition']['rotation']))
    prepared = np.zeros(benefit['shape'], np.uint8)
    y = prepared.shape[0]//2-snapshot.shape[0]//2
    x = prepared.shape[1]//2-snapshot.shape[1]//2
    prepared[y:y+snapshot.shape[0], x:x+snapshot.shape[1]] = snapshot
    same(grid, prepared, f'{rid}: preparation independent reconstruction')
    require(measured(grid, manifest['registry'])[1][0]['core'] == spec['initial_core'],
            f'{rid}: initial core')
    calibration = spec['split'] == 'calibration'; interval = benefit['sample_interval']
    stop = max(cfg['calibration']['source_times'])+cfg['calibration']['native_continuation_horizon'] if calibration else benefit['horizon']
    require(result['completed_updates'] == stop, f'{rid}: horizon')
    require(len(result['samples']) == stop//interval+1, f'{rid}: sample inventory')
    samples = []; events = []; strata = []; targets = []; previous = {}
    replay_path = folder/'replay.npz'
    replay = None
    capture = not calibration and spec['condition']['id'] == 'development-0' and spec['state'] in ('V01', 'RV01', 'RV02')
    require(replay_path.exists() == capture, f'{rid}: declared replay-capture inventory')
    if replay_path.exists():
        with np.load(replay_path, allow_pickle=False) as saved:
            replay = {int(t): frame.copy() for t, frame in zip(saved['times'], saved['frames'])}
        require(list(replay) == list(range(0, stop+1, 40)), f'{rid}: replay times')
    for index, t in enumerate(range(0, stop+1, interval)):
        if t:
            advance(grid, interval)
        if t in benefit['disturbance_times']:
            before = grid.copy(); pre_counts, _, _ = measured(before, manifest['registry'])
            y, x = spec['condition']['block']; size = benefit['block_size']
            removed = int(np.count_nonzero(grid[y:y+size, x:x+size]))
            grid[y:y+size, x:x+size] = 0
            post_counts, _, _ = measured(grid, manifest['registry'])
            with np.load(folder/f'disturbance-{t}.npz', allow_pickle=False) as saved:
                same(saved['before'], before, f'{rid}@{t}: pre-disturbance replay')
                same(saved['after'], grid, f'{rid}@{t}: post-disturbance replay')
            events.append({'type': 'disturbance', 't': t, 'block': [y, x], 'block_size': size,
                'removed_occupied_cells': removed, 'before_hash': digest(before), 'after_hash': digest(grid),
                'pre_counts': pre_counts, 'post_counts': post_counts})
            counts['disturbances_verified'] += 1
        values, records, loops = measured(grid, manifest['registry'])
        sample = {'t': t, **values, 'cores': records}
        require(result['samples'][index] == sample, f'{rid}@{t}: complete score/core record')
        samples.append(sample); counts['world_samples_verified'] += 1
        now = {tuple(o['core']): o['identity'] for o in records}
        for core, identity in now.items():
            if core not in previous:
                events.append({'type': 'core_appearance', 't': t, 'core': list(core), 'identity': identity})
            elif previous[core] != identity:
                events.append({'type': 'identity_change_at_core', 't': t, 'core': list(core),
                    'before': previous[core], 'after': identity})
        for core in sorted(previous.keys()-now.keys()):
            events.append({'type': 'core_loss', 't': t, 'core': list(core)})
        previous = now
        if replay is not None and t in replay:
            same(replay[t], grid, f'{rid}@{t}: recorded animation frame')
            counts['animation_frames_verified'] += 1
        if calibration and t in cfg['calibration']['source_times']:
            with np.load(folder/f'source-{t}.npz', allow_pickle=False) as saved:
                same(saved['grid'], grid, f'{rid}@{t}: calibration source replay')
            counts['source_frames_verified'] += 1
            for scored in (True, False):
                eligible_class = sorted([o for o in loops if (o['genotype'] in manifest['registry']) == scored],
                                        key=lambda o: tuple(o['core']))
                chosen = eligible_class[:1] if len(eligible_class) < 2 else [eligible_class[0], eligible_class[-1]]
                label = 'scored' if scored else 'unscored'
                sid = f'{rid}-t{t}-{label}'
                strata.append({'stratum_id': sid, 't': t, 'scored': scored,
                    'available_cores': len(eligible_class), 'selected_cores': len(chosen)})
                for rank, o in enumerate(chosen):
                    component = o['isolation_snapshot']; name = f'target-{t}-{label}-{rank}'
                    status = o['extraction_status'] if component is None else 'ineligible_component_size' if max(component.shape)+20 > cfg['search']['isolation_shape'][0] else 'eligible'
                    target = {'target_id': name, 'stratum_id': sid, 't': t, 'core': o['core'],
                        'identity': o['genotype'], 'scored': scored, 'extraction_status': status,
                        'snapshot_hash': digest(component) if component is not None else None,
                        'extraction_bbox': o.get('extraction_bbox'),
                        'snapshot_file': f'{name}.npz' if component is not None else None}
                    if component is not None:
                        with np.load(folder/target['snapshot_file'], allow_pickle=False) as saved:
                            same(saved['snapshot'], component, f'{rid}@{t}: selected complete component')
                        counts['source_components_verified'] += 1
                    targets.append(target)
    require(result['events'] == events, f'{rid}: complete native event history')
    require(result['strata'] == strata, f'{rid}: first/last selection strata')
    for target in targets:
        target['native_continuation'] = native_window(target, samples,
            cfg['calibration']['native_continuation_horizon'], interval)
        counts['native_continuations_verified'] += 1
    require(result['targets'] == targets, f'{rid}: selected targets and native continuations')
    values = [s['scored_cores'] for s in samples if s['t'] <= benefit['horizon']]
    require(len(values) == result['score_sample_count'] == 81, f'{rid}: score sample count')
    require(sum(values) == result['score_sum'] and sum(values)/81 == result['score'], f'{rid}: exact condition score')
    with np.load(folder/'final.npz', allow_pickle=False) as saved:
        same(saved['grid'], grid, f'{rid}: full final replay')
    require(digest(grid) == result['final_hash'], f'{rid}: final hash')
    require({p.name for p in folder.glob('target-*.npz')} ==
            {t['snapshot_file'] for t in targets if t['snapshot_file']}, f'{rid}: target file inventory')
    counts['full_world_trajectories_verified'] += 1
    counts['dense_world_updates_replayed'] += stop
    print('verified full ecology', rid, 'targets', len(targets), flush=True)
    return result


def graph(outcome, folder, snapshot, identity, original, cfg, counts):
    """Reconstruct DFS order, all links, resets, truncations, and first acceptance."""
    require(read(folder/'result.json') == outcome, f'{folder}: standalone search result')
    nodes = outcome['nodes']; arrays = []; cursor = 0; stable = []; cuts = []; confirmation = None
    require(0 < len(nodes) == outcome['generation_simulations'] <= cfg['max_generation_simulations_per_root'],
            f'{folder}: simulation count')
    def visit(component, gt, streak, depth, parent=None, edge=None, path=()):
        nonlocal cursor, confirmation
        if cursor >= cfg['max_generation_simulations_per_root']:
            cuts.append({'reason': 'simulation_budget', 'path': list(path), 'depth': depth})
            return
        number = cursor; cursor += 1
        require(number < len(nodes), f'{folder}: missing prescribed DFS node')
        node = nodes[number]; context = f'{folder.name}/node-{number:02d}'
        expected_meta = {'node': number, 'parent_node': parent, 'incoming_child': edge,
            'path': list(path), 'depth': depth, 'input_identity': gt,
            'input_snapshot_hash': digest(component), 'incoming_streak': streak}
        require({k: node[k] for k in expected_meta} == expected_meta, f'{context}: parent/child/identity/depth/streak link')
        require(read(folder/f'node-{number:02d}.json') == node, f'{context}: persisted node')
        with np.load(folder/f'node-{number:02d}.npz', allow_pickle=False) as saved:
            data = {key: saved[key].copy() for key in saved.files}
        arrays.append(data)
        expected = isolated(component, cfg['isolation_shape']); report = node['outcome']
        if expected is None:
            require(report == {'status': 'ineligible_component_size', 'children': []} and not data,
                    f'{context}: oversized empty stage')
            counts['oversized_empty_nodes_verified'] += 1
        else:
            same(data['initial'], expected, f'{context}: independent isolated preparation')
            require(digest(expected) == report['initial_hash'], f'{context}: initial hash')
            initial = detect(expected)
            require(len(initial) == 1 and initial[0]['genotype'] == gt, f'{context}: single input core identity')
            initial_cores = {tuple(o['core']) for o in initial}
            children = report['children']
            require(report['horizon'] == cfg['generation_horizon']
                    and report['sampling_interval'] == cfg['detection_interval'], f'{context}: generation schedule')
            require(report['status'] == ('offspring_observed' if children else
                    'unresolved_at_horizon' if np.any(data['final']) else 'assay_extinct'),
                    f'{context}: generation outcome status')
            require(len(children) <= cfg['offspring_per_generation'], f'{context}: offspring cap')
            require(len({tuple(c['core']) for c in children}) == len(children), f'{context}: repeated admitted core')
            keys = {'initial', 'final'}
            for i, child in enumerate(children):
                keys.update((f'child{i}', f'selection_grid{i}'))
                require(tuple(child['core']) not in initial_cores, f'{context}: original core counted as child')
                require(0 <= child['closure_first_seen_t'] <= child['detached_t'] <= report['completed_updates'] <= cfg['generation_horizon'],
                        f'{context}: child timing')
                require(child['detached_t'] % cfg['detection_interval'] == 0, f'{context}: child observation cadence')
                require(child['size_eligible'] == (max(data[f'child{i}'].shape)+20 <= cfg['isolation_shape'][0]),
                        f'{context}: descendant eligibility')
                selected = next((o for o in detect(data[f'selection_grid{i}'])
                                 if o['core'] == child['core'] and o['genotype'] == child['identity']), None)
                require(selected is not None and selected.get('extraction_bbox') == child['extraction_bbox'],
                        f'{context}: child extraction geometry')
            require(set(data) == keys, f'{context}: stage array inventory')
            # Required independent original-dense selection and terminal replay.
            generation_check(folder/f'node-{number:02d}.npz', report)
            counts['isolated_generation_states_replayed'] += 1
            counts['child_selection_states_replayed'] += len(children)
            counts['dense_isolation_updates_replayed'] += report['completed_updates']+sum(c['detached_t'] for c in children)
        counts['search_nodes_verified'] += 1
        if parent is not None:
            counts['parent_child_edges_verified'] += 1
        order = sorted(range(len(report['children'])), key=lambda i: (
            report['children'][i]['detached_t'], tuple(report['children'][i]['core']), report['children'][i]['snapshot_hash']))
        for i in order:
            child = report['children'][i]; new_gt = child['identity']
            new_streak = streak+1 if new_gt == gt else 0
            accepted = new_gt == identity if original else True
            if new_streak >= cfg['stable_transmissions']:
                stable.append({'identity': new_gt, 'node': number, 'child': i,
                    'accepted_endpoint': accepted, 'path': list(path+(i,))})
            if new_streak >= cfg['stable_transmissions'] and accepted:
                confirmation = {'identity': new_gt, 'node': number, 'child': i,
                    'transmission_streak': new_streak, 'path': list(path+(i,)), 'snapshot_hash': child['snapshot_hash']}
                require(read(folder/'confirmation.json') == {'confirmation': confirmation}, f'{context}: confirmation metadata')
                with np.load(folder/'confirmation.npz', allow_pickle=False) as saved:
                    require(saved.files == ['stable_snapshot'], f'{context}: confirmation array keys')
                    same(saved['stable_snapshot'], data[f'child{i}'], f'{context}: confirmation linked child')
                counts['confirmations_verified'] += 1
                return
            if not child['size_eligible']:
                cuts.append({'reason': 'component_size', 'path': list(path+(i,)), 'depth': depth+1})
                continue
            if depth >= cfg['max_depth']:
                cuts.append({'reason': 'depth_limit', 'path': list(path+(i,)), 'depth': depth+1})
                continue
            visit(data[f'child{i}'], new_gt, new_streak, depth+1, number, i, path+(i,))
            if confirmation:
                return
    visit(snapshot, identity, 0, 1)
    require(cursor == len(nodes), f'{folder}: unvisited or trailing graph nodes')
    require(outcome['stable_observations'] == stable and outcome['truncations'] == cuts,
            f'{folder}: complete search observations/truncations')
    require(outcome['confirmation'] == confirmation, f'{folder}: first accepted confirmation')
    require(outcome['status'] == ('confirmed' if confirmation else 'unresolved'), f'{folder}: search status')
    counts['search_roots_verified'] += 1


def analyses(manifest, calibration, results, counts):
    ca = read(OUT/'calibration-analysis.json'); cfg = manifest['config']
    scored = [o for o in calibration['observations'] if o['scored']]
    unscored = [o for o in calibration['observations'] if not o['scored']]
    def confirmed(o):
        return bool(o.get('outcome') and o['outcome']['status'] == 'confirmed')
    by_state = [{'state': pid, 'selected': sum(o['state'] == pid for o in scored),
        'eligible': sum(o['state'] == pid and o['extraction_status'] == 'eligible' for o in scored),
        'confirmed': sum(o['state'] == pid and confirmed(o) for o in scored)} for pid in cfg['states']]
    strata = []
    for spec in manifest['runs']:
        if spec['split'] == 'calibration':
            for s in results[spec['run_id']]['strata']:
                if s['scored']:
                    strata.append({**s, 'state': spec['state'], 'confirmed': sum(
                        o['stratum_id'] == s['stratum_id'] and confirmed(o) for o in scored)})
    n = sum(confirmed(o) for o in scored); base = sum(confirmed(o) for o in calibration['baselines'])
    gate = cfg['calibration']['gate']
    checks = {'all_baselines': base == gate['baseline_recoveries_required'],
        'overall_recovery': bool(scored) and n/len(scored) >= gate['overall_scored_recovery_fraction'],
        'each_starting_state': all(s['selected'] and s['confirmed']/s['selected'] >= gate['per_starting_state_recovery_fraction'] for s in by_state),
        'each_nonempty_stratum': all(s['confirmed'] >= gate['minimum_confirmed_per_nonempty_scored_stratum']
                                    for s in strata if s['available_cores'])}
    summaries = {'gate_checks': checks, 'gate_passed': all(checks.values()),
        'baseline_confirmed': base, 'baseline_total': len(calibration['baselines']),
        'scored_selected': len(scored), 'scored_eligible': sum(o['extraction_status'] == 'eligible' for o in scored),
        'scored_confirmed': n, 'unscored_selected': len(unscored),
        'unscored_confirmed': sum(confirmed(o) for o in unscored), 'by_state': by_state, 'strata': strata,
        'scored_statuses': dict(Counter('confirmed' if confirmed(o) else 'unresolved_search' if o['outcome'] else o['extraction_status'] for o in scored)),
        'unscored_confirmed_identities': sorted({o['outcome']['confirmation']['identity'] for o in unscored if confirmed(o)}),
        'truncations': dict(Counter(t['reason'] for o in calibration['baselines']+calibration['observations']
                                    if o.get('outcome') for t in o['outcome']['truncations'])),
        'offspring_cap_nodes': sum(len(node['outcome']['children']) == cfg['search']['offspring_per_generation']
            for o in calibration['baselines']+calibration['observations'] if o.get('outcome') for node in o['outcome']['nodes']),
        'generation_simulations': sum(o['outcome']['generation_simulations'] for o in calibration['baselines']+calibration['observations'] if o.get('outcome'))}
    require(all(ca[key] == value for key, value in summaries.items()), 'independent calibration gate or counts differ')
    require(ca['calibration_sha256'] == sha(OUT/'calibration.json'), 'calibration analysis source hash')
    benefit = read(OUT/'benefit.json'); analysis = read(OUT/'analysis.json')
    require(benefit['calibration_passed'] == summaries['gate_passed'], 'paired acquisition gate status')
    require(analysis['calibration'] == ca, 'paired analysis calibration copy')
    require(analysis['calibration_sha256'] == sha(OUT/'calibration.json')
            and analysis['benefit_sha256'] == sha(OUT/'benefit.json'), 'paired analysis evidence hashes')
    lookup = {}; expected_runs = []; expected_analysis_runs = []
    for spec in manifest['runs']:
        if spec['split'] == 'calibration':
            continue
        r = results[spec['run_id']]; lookup[spec['state'], spec['split'], spec['condition']['id']] = r['score_sum']
        expected_runs.append({'run_id': spec['run_id'], 'score': r['score'], 'final_hash': r['final_hash']})
        expected_analysis_runs.append({'run_id': spec['run_id'], 'state': spec['state'], 'split': spec['split'],
            'condition': spec['condition']['id'], 'score': r['score'], 'score_sum': r['score_sum'],
            'mean_unscored_valid_cores': sum(s['unscored_valid_cores'] for s in r['samples'])/81,
            'mean_unknown_identity_cores': sum(s['unknown_identity_cores'] for s in r['samples'])/81,
            'deleted_occupied_cells': sum(e['removed_occupied_cells'] for e in r['events'] if e['type'] == 'disturbance')})
    require(benefit['runs'] == expected_runs and analysis['runs'] == expected_analysis_runs, 'paired run inventory/score/removal summaries')
    require(len(analysis['pairs']) == len(cfg['pairs']) == 2, 'paired comparison inventory')
    for spec, reported in zip(cfg['pairs'], analysis['pairs']):
        pid = spec['candidate']; require(reported['candidate'] == pid and reported['inputs'] == spec['inputs'], 'comparison inputs')
        passes = []
        for split in ('development', 'confirmation'):
            totals = {q: sum(lookup[q, split, f'{split}-{i}'] for i in range(2)) for q in [pid]+spec['inputs']}
            passed = all(totals[pid] > totals[q] for q in spec['inputs']); passes.append(passed)
            panel = reported['panels'][split]
            require(panel['scores'] == {q: v/162 for q, v in totals.items()}, f'{pid}: panel display means')
            require(panel['exact_totals'] == {q: {'score_sum': v, 'sample_count': 162, 'mean': v/162} for q, v in totals.items()}, f'{pid}: exact panel totals')
            require(panel['candidate_minus_inputs'] == {q: (totals[pid]-totals[q])/162 for q in spec['inputs']}, f'{pid}: exact paired contrasts')
            require(panel['strict_advantage'] == passed, f'{pid}: strict integer criterion, ties fail')
        advantage = all(passes); require(reported['structural_advantage_both_panels'] == advantage, f'{pid}: both panels')
        require(reported['confirmed_benefit'] == (advantage if summaries['gate_passed'] else None), f'{pid}: calibration-blocked benefit')
        require(reported['originating_encounters'] == manifest['states'][pid]['source']['run_id'], f'{pid}: originating encounter')
        for record in reported['conditions']:
            split = record['condition'].split('-')[0]; name = record['condition']
            require(record['candidate'] == lookup[pid, split, name]/81
                    and record['inputs'] == {q: lookup[q, split, name]/81 for q in spec['inputs']}
                    and record['candidate_minus_inputs'] == {q: (lookup[pid, split, name]-lookup[q, split, name])/81 for q in spec['inputs']},
                    f'{pid}: individual paired condition scores')
    n = sum(p['confirmed_benefit'] is True for p in analysis['pairs']) if summaries['gate_passed'] else None
    require(analysis['confirmed_beneficial_encounters'] == n, 'confirmed benefit encounter count')
    require(analysis['yield'] == {'main': {'confirmed': n, 'denominator': 36, 'yield': n/36 if n is not None else None},
        'heldout': {'confirmed': 0 if n is not None else None, 'denominator': 18, 'yield': 0.0 if n is not None else None},
        'overall': {'confirmed': n, 'denominator': 54, 'yield': n/54 if n is not None else None}}, 'encounter denominators and unknown yields')
    counts['paired_comparisons_verified'] = len(cfg['pairs'])
    counts['calibration_gate_verified'] = 1


def audit(report):
    require(not sys.flags.optimize, 'generation_check uses assertions; do not run python -O')
    for name in ('calibration.json', 'calibration-analysis.json', 'benefit.json', 'analysis.json'):
        require((OUT/name).exists(), f'{name} missing; wait for all batches and analyses')
    manifest = read(OUT/'manifest.json'); cfg = manifest['config']; counts = report['counts']
    require(manifest['rule_hash'] == RULE_HASH, 'rule hash')
    require(manifest['config_sha256'] == sha(ROOT/'configs/ecological-v1.json')
            and manifest['protocol_sha256'] == sha(ROOT/'protocols/007-ecological-calibration-and-benefit.md'), 'protocol/config source hashes')
    for name, value in {**manifest['code_hashes'], **manifest['source_sha256']}.items():
        require(sha(ROOT/name) == value, f'frozen source changed: {name}')
    require(manifest['benefit'] == read(ROOT/cfg['benefit_source'])['benefit'], 'pre-atlas frozen benefit definition')
    require(len(manifest['runs']) == 30 and len({r['run_id'] for r in manifest['runs']}) == 30, 'world inventory')
    require(len({r['initial_hash'] for r in manifest['runs']}) == 20, 'physical initial-state distinctness')
    require(Counter(r['split'] for r in manifest['runs']) == {'calibration': 10, 'development': 10, 'confirmation': 10}, 'split inventory')
    require(manifest['registry'] == sorted({s['identity'] for s in manifest['states'].values()})
            and len(manifest['registry']) == 4, 'deduplicated fixed registry')
    report.update({'rule_hash': RULE_HASH, 'manifest_sha256': sha(OUT/'manifest.json'),
        'calibration_experiment_id': manifest['calibration_experiment_id'],
        'benefit_experiment_id': manifest['benefit_experiment_id'],
        'auditor_sha256': sha(Path(__file__)), 'generation_verifier_sha256': sha(ROOT/'scripts/verify_fresh.py'),
        'evidence_sha256': {name: sha(OUT/name) for name in ('calibration.json', 'calibration-analysis.json', 'benefit.json', 'analysis.json')}})
    with np.load(OUT/'snapshots.npz', allow_pickle=False) as saved:
        require(set(saved.files) == set(cfg['states']), 'prepared-state snapshot inventory')
        for pid in cfg['states']:
            state = manifest['states'][pid]
            with np.load(ROOT/state['snapshot_file'], allow_pickle=False) as source:
                same(saved[pid], source['snapshot'], f'{pid}: source snapshot copy')
            require(digest(saved[pid]) == state['snapshot_hash'], f'{pid}: source snapshot hash')
    results = {s['run_id']: world(s, manifest, counts) for s in manifest['runs']}
    calibration = read(OUT/'calibration.json')
    require(calibration['experiment_id'] == manifest['calibration_experiment_id'], 'calibration experiment ID')
    require([b['state'] for b in calibration['baselines']] == cfg['states'], 'baseline inventory')
    with np.load(OUT/'snapshots.npz', allow_pickle=False) as saved:
        for baseline in calibration['baselines']:
            pid = baseline['state']; folder = OUT/'calibration'/'baseline'/pid
            require(OUT/baseline['folder'] == folder, f'{pid}: baseline folder')
            graph(baseline['outcome'], folder, saved[pid].copy(), manifest['states'][pid]['identity'],
                  True, cfg['search'], counts)
            counts['baseline_controls_verified'] += 1
    expected = []
    for spec in manifest['runs']:
        if spec['split'] == 'calibration':
            for target in results[spec['run_id']]['targets']:
                expected.append((spec, target))
    require(len(expected) == len(calibration['observations']), 'selected observation inventory')
    for (spec, target), observation in zip(expected, calibration['observations']):
        require({k: observation[k] for k in target} == target and observation['run_id'] == spec['run_id']
                and observation['state'] == spec['state'], 'native source/aggregate calibration link')
        folder = OUT/'calibration'/spec['run_id']; outcome = observation['outcome']
        if target['extraction_status'] == 'eligible':
            require(outcome is not None and OUT/observation['folder'] == folder/f'{target["target_id"]}-search', 'eligible source search folder')
            with np.load(folder/target['snapshot_file'], allow_pickle=False) as saved:
                graph(outcome, OUT/observation['folder'], saved['snapshot'].copy(), target['identity'],
                      target['scored'], cfg['search'], counts)
        else:
            require(outcome is None and observation['folder'] is None, 'ineligible source must remain missing')
            counts['ineligible_observations_verified'] += 1
        counts['selected_observations_verified'] += 1
    analyses(manifest, calibration, results, counts)
    report.update({'status': 'passed', 'mismatches': 0})


def main():
    started = time.perf_counter()
    names = ['full_world_trajectories_verified', 'dense_world_updates_replayed', 'world_samples_verified',
        'disturbances_verified', 'animation_frames_verified', 'source_frames_verified',
        'source_components_verified', 'native_continuations_verified', 'search_roots_verified',
        'search_nodes_verified', 'parent_child_edges_verified', 'isolated_generation_states_replayed',
        'child_selection_states_replayed', 'dense_isolation_updates_replayed', 'oversized_empty_nodes_verified',
        'confirmations_verified', 'baseline_controls_verified', 'selected_observations_verified',
        'ineligible_observations_verified', 'paired_comparisons_verified', 'calibration_gate_verified']
    report = {'status': 'running', 'counts': {name: 0 for name in names},
        'scope': 'all 30 native/paired trajectories, complete sampled records, interventions, selections, source extractions, linked bounded searches and individual isolated generations, exact integer gate/paired arithmetic; not native genetic ancestry or total viable population'}
    try:
        audit(report)
    except Exception as error:
        report.update({'status': 'failed', 'mismatches': 1, 'error_type': type(error).__name__,
                       'error': str(error), 'seconds': time.perf_counter()-started,
                       'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
        write_json(OUT/'integrity.json', report)
        raise
    report.update({'seconds': time.perf_counter()-started,
                   'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
    write_json(OUT/'integrity.json', report)
    print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    main()
