"""Independent dense preparation/trajectory/search audit of EXP-impact-001.

Run after both acquisitions and analyses:
    OPENBLAS_NUM_THREADS=1 python -m scripts.verify_impact

Production microcolony, impact, and analysis helpers are deliberately not used.
The frozen periodic detector is the measurement reference. Search graph replay
uses the independently validated ecological verifier and original dense kernel.
"""
import argparse
import json
import resource
import sys
import time
from collections import Counter, deque
from fractions import Fraction
from pathlib import Path

import numpy as np

from evoloop.engine import ROOT, RULE_HASH, advance, digest
from evoloop.periodic_tracking import detect
from scripts.atlas import write_json
from scripts.verify_ecological import (graph, isolated, measured, native_window,
                                       read, require, same, sha)

OUT = ROOT/'data/impact-v1'


def components(grid):
    """Independent 4-neighbor occupied flood fill, including torus edges."""
    h, w = grid.shape; unseen = set(map(tuple, np.argwhere(grid != 0)))
    answer = []
    while unseen:
        start = min(unseen); unseen.remove(start); queue = deque([start]); cells = [start]
        while queue:
            y, x = queue.popleft()
            for p in (((y-1)%h, x), ((y+1)%h, x), (y, (x-1)%w), (y, (x+1)%w)):
                if p in unseen:
                    unseen.remove(p); queue.append(p); cells.append(p)
        mask = np.zeros(grid.shape, bool)
        yy, xx = zip(*cells); mask[yy, xx] = True; answer.append(mask)
    return answer


def mask_for(grid, organism):
    patch = organism['isolation_snapshot']; require(patch is not None, 'missing component')
    y, x, h, w = organism['extraction_bbox']
    rows = (np.arange(h)+y)%grid.shape[0]; cols = (np.arange(w)+x)%grid.shape[1]
    mask = np.zeros(grid.shape, bool); mask[np.ix_(rows, cols)] = patch != 0
    same(grid[np.ix_(rows, cols)][patch != 0], patch[patch != 0], 'complete component cell values')
    return mask


def equivalence(a, b):
    """Exhaust all four rotations and torus shifts, anchoring a rare state."""
    if a.shape != b.shape or not np.array_equal(np.bincount(a.ravel(), minlength=9),
                                               np.bincount(b.ravel(), minlength=9)):
        return None
    counts = np.bincount(a.ravel(), minlength=9)
    populated = [i for i in range(1, 9) if counts[i]]
    if not populated:
        return {'rotation': 0, 'translation': [0, 0]}
    color = min(populated, key=lambda i: counts[i]); destinations = np.argwhere(b == color)
    for k in range(4):
        rotated = np.rot90(a, k); source = np.argwhere(rotated == color)[0]
        for target in destinations:
            shift = target-source
            if np.array_equal(np.roll(rotated, tuple(shift), axis=(0, 1)), b):
                return {'rotation': k, 'translation': [int(v)%a.shape[i] for i, v in enumerate(shift)]}
    return None


def preparations(m, counts):
    cfg = m['config']; patches = {}; prepared = {}; independently = []
    with np.load(OUT/'snapshots.npz', allow_pickle=False) as saved:
        require(set(saved.files) == set(cfg['states']), 'source snapshot inventory')
        for pid in cfg['states']:
            state = m['states'][pid]
            with np.load(ROOT/state['snapshot_file'], allow_pickle=False) as source:
                same(saved[pid], source['snapshot'], f'{pid}: source snapshot')
            require(digest(saved[pid]) == state['snapshot_hash'], f'{pid}: source hash')
        for phase in m['phases']:
            pid = phase['state']; grid = isolated(saved[pid], cfg['shape'])
            require(grid is not None, 'source fits preparation arena'); advance(grid, phase['age'])
            loops = detect(grid); cc = components(grid)
            require(len(loops) == len(cc) == 1 and loops[0]['genotype'] == m['states'][pid]['identity'],
                    f'{phase["name"]}: exactly one original core and whole occupied component')
            organism = loops[0]; patch = organism['isolation_snapshot']
            require(patch is not None and np.array_equal(mask_for(grid, organism), cc[0]),
                    f'{phase["name"]}: all occupied cells retained')
            y, x, _, _ = organism['extraction_bbox']
            offset = [(organism['core'][0]-y)%grid.shape[0], (organism['core'][1]-x)%grid.shape[1]]
            require(offset == phase['offset'] and digest(grid) == phase['grid_hash']
                    and digest(patch) == phase['snapshot_hash'], f'{phase["name"]}: hashes and core offset')
            with np.load(OUT/'phase'/f'{phase["name"]}.npz', allow_pickle=False) as source:
                same(source['grid'], grid, 'phase dense replay'); same(source['snapshot'], patch, 'phase complete patch')
            patches[phase['name']] = patch.copy(); counts['phase_states_verified'] += 1
            counts['dense_phase_updates_replayed'] += phase['age']
    require([(p['state'], p['age']) for p in m['phases']] ==
            [(pid, c['age']) for pid in cfg['states'] for c in cfg['conditions']], 'all 30 fixed phases')
    for p in m['preparations']:
        c = p['condition']; patch = patches[p['phase']]
        phase = next(q for q in m['phases'] if q['name'] == p['phase']); offset = phase['offset']
        grid = np.zeros(cfg['shape'], np.uint8); clone_masks = []
        for site in c['sites']:
            y, x = site[0]-offset[0], site[1]-offset[1]; h, w = patch.shape
            require(y >= 0 and x >= 0 and y+h <= grid.shape[0] and x+w <= grid.shape[1], 'clone inside arena')
            area = grid[y:y+h, x:x+w]; require(not np.any((area != 0) & (patch != 0)), 'clone nonoverlap')
            area[patch != 0] = patch[patch != 0]
            mask = np.zeros(grid.shape, bool); mask[y:y+h, x:x+w] = patch != 0; clone_masks.append(mask)
        cc = components(grid); require(len(cc) == 3 and all(any(np.array_equal(a, b) for b in cc) for a in clone_masks),
                                       f'{p["pair_id"]}: three independently complete disconnected clones')
        loops = detect(grid)
        require(len(loops) == 3 and sorted(o['core'][:2] for o in loops) == sorted(c['sites'])
                and all(o['genotype'] == m['states'][p['state']]['identity'] for o in loops), 'clone core anchors and identities')
        mask = clone_masks[c['remove_index']]; after = grid.copy(); after[mask] = 0
        target = next(o for o in loops if o['core'][:2] == c['sites'][c['remove_index']])
        remaining = detect(after)
        require(len(remaining) == len(components(after)) == 2, 'exact 3 to 2 core/component deletion')
        require(np.count_nonzero(grid) == 3*int(mask.sum()) and
                np.array_equal(np.bincount(grid[grid != 0], minlength=9), 3*np.bincount(grid[mask], minlength=9)),
                'exact one-third occupied-cell and state-histogram loss')
        beforelist = sorted((tuple(o['core']), o['genotype'], digest(o['isolation_snapshot'])) for o in loops if o is not target)
        afterlist = sorted((tuple(o['core']), o['genotype'], digest(o['isolation_snapshot'])) for o in remaining)
        require(beforelist == afterlist, 'other complete components unchanged')
        impact = {'removed_core': target['core'], 'removed_identity': target['genotype'],
            'removed_snapshot_hash': digest(patch), 'removed_occupied_cells': int(mask.sum()),
            'occupied_before': int(np.count_nonzero(grid)), 'registered_before': 3, 'registered_after': 2,
            'remaining_components_unchanged': True, 'before_hash': digest(grid), 'after_hash': digest(after),
            'mask_hash': digest(mask.astype(np.uint8)), 'matched_impact': True}
        require(p['impact'] == impact, 'independent exposure report')
        with np.load(OUT/'prepared'/f'{p["pair_id"]}.npz', allow_pickle=False) as data:
            same(data['before'], grid, 'independent clone placement'); same(data['after'], after, 'independent whole-component removal')
            same(data['mask'], mask.astype(np.uint8), 'independent removal mask')
        prepared[p['pair_id']] = {'before': grid, 'after': after, 'mask': mask.astype(np.uint8)}
        counts['preparations_verified'] += 1
    for pid in cfg['states']:
        for d in [p for p in m['preparations'] if p['state'] == pid and p['condition']['split'] == 'development']:
            for c in [p for p in m['preparations'] if p['state'] == pid and p['condition']['split'] == 'confirmation']:
                proof = {k: equivalence(prepared[d['pair_id']][k], prepared[c['pair_id']][k]) for k in ('before', 'after', 'mask')}
                independently.append({'state': pid, 'development': d['pair_id'], 'confirmation': c['pair_id'], **proof})
    require(independently == m['equivalence_checks'] and all(p['before'] is None and p['after'] is None for p in independently),
            'exact complete-state development/confirmation inequivalence')
    aliases = []
    for c in cfg['conditions']:
        for i, pid in enumerate(cfg['states']):
            for q in cfg['states'][i+1:]:
                for key in ('before', 'after'):
                    eq = equivalence(prepared[f'{pid}-{c["id"]}'][key], prepared[f'{q}-{c["id"]}'][key])
                    if eq is not None:
                        aliases.append({'condition': c['id'], 'states': [pid, q], 'grid': key, 'transform': eq})
    require(aliases == m['cross_state_aliases'], 'cross-state complete preparation aliases')
    counts['dev_confirmation_equivalence_pairs_verified'] = len(independently)
    counts['cross_state_equivalence_pairs_verified'] = len(cfg['conditions'])*10*2
    return patches, prepared


def world(spec, m, prepared, counts):
    rid = spec['run_id']; folder = OUT/spec['split']/rid; result = read(folder/'result.json'); cfg = m['config']
    require(all(result[k] == v for k, v in spec.items()), f'{rid}: manifest fields')
    require(result['rule_hash'] == RULE_HASH, 'world rule hash')
    with np.load(OUT/'initial'/f'{rid}.npz', allow_pickle=False) as data: grid = data['grid'].copy()
    same(grid, prepared[spec['pair_id']]['after' if spec['treatment'] == 'D' else 'before'], 'declared treatment initial')
    require(digest(grid) == spec['initial_hash'], 'initial hash')
    calibration = spec['split'] == 'calibration'; interval = cfg['sample_interval']
    stop = max(cfg['calibration']['source_times'])+cfg['calibration']['native_continuation_horizon'] if calibration else cfg['horizon']
    require(result['completed_updates'] == stop and len(result['samples']) == stop//interval+1, 'complete observation horizon')
    events = [{'type': 'disturbance', 't': 0, **spec['impact']}] if spec['treatment'] == 'D' else []
    samples = []; strata = []; targets = []; previous = {}; replay = None
    capture = not calibration and {'state': spec['state'], 'condition': spec['condition']['id']} in cfg['replays']
    require((folder/'replay.npz').exists() == capture, 'prospective animation inventory')
    if capture:
        with np.load(folder/'replay.npz', allow_pickle=False) as data:
            replay = {int(t): g.copy() for t, g in zip(data['times'], data['frames'])}
        require(list(replay) == list(range(0, stop+1, cfg['replay_interval'])), 'animation time inventory')
    for index, t in enumerate(range(0, stop+1, interval)):
        if t: advance(grid, interval)
        values, records, loops = measured(grid, m['registry']); sample = {'t': t, **values, 'cores': records}
        require(sample == result['samples'][index], f'{rid}@{t}: full sample records'); samples.append(sample)
        counts['world_samples_verified'] += 1
        now = {tuple(o['core']): o['identity'] for o in records}
        for core, identity in now.items():
            if core not in previous: events.append({'type': 'core_appearance', 't': t, 'core': list(core), 'identity': identity})
            elif previous[core] != identity: events.append({'type': 'identity_change_at_core', 't': t, 'core': list(core), 'before': previous[core], 'after': identity})
        for core in sorted(previous.keys()-now.keys()): events.append({'type': 'core_loss', 't': t, 'core': list(core)})
        previous = now
        if replay is not None and t in replay:
            same(replay[t], grid, 'dense replay animation frame'); counts['animation_frames_verified'] += 1
        if calibration and t in cfg['calibration']['source_times']:
            with np.load(folder/f'source-{t}.npz', allow_pickle=False) as data: same(data['grid'], grid, 'calibration source dense replay')
            counts['source_frames_verified'] += 1
            for scored in (True, False):
                options = sorted([o for o in loops if (o['genotype'] in m['registry']) == scored], key=lambda o: tuple(o['core']))
                chosen = options[:1] if len(options) < 2 else [options[0], options[-1]]
                label = 'scored' if scored else 'unscored'; sid = f'{rid}-t{t}-{label}'
                strata.append({'stratum_id': sid, 't': t, 'scored': scored, 'available_cores': len(options), 'selected_cores': len(chosen)})
                for rank, o in enumerate(chosen):
                    patch = o['isolation_snapshot']; name = f'target-{t}-{label}-{rank}'
                    status = o['extraction_status'] if patch is None else 'ineligible_component_size' if max(patch.shape)+20 > cfg['search']['isolation_shape'][0] else 'eligible'
                    target = {'target_id': name, 'stratum_id': sid, 't': t, 'core': o['core'], 'identity': o['genotype'], 'scored': scored,
                        'extraction_status': status, 'snapshot_hash': digest(patch) if patch is not None else None,
                        'extraction_bbox': o.get('extraction_bbox'), 'snapshot_file': f'{name}.npz' if patch is not None else None}
                    if patch is not None:
                        with np.load(folder/target['snapshot_file'], allow_pickle=False) as data: same(data['snapshot'], patch, 'selected complete source component')
                        require(any(np.array_equal(mask_for(grid, o), cc) for cc in components(grid)), 'independent selected component connectivity')
                        counts['source_components_verified'] += 1
                    targets.append(target)
    for target in targets:
        target['native_continuation'] = native_window(target, samples, cfg['calibration']['native_continuation_horizon'], interval)
        counts['native_continuations_verified'] += 1
    require(events == result['events'] and strata == result['strata'] and targets == result['targets'], 'native events/selection/continuation records')
    require({p.name for p in folder.glob('target-*.npz')} == {t['snapshot_file'] for t in targets if t['snapshot_file']}, 'target inventory')
    values = [s['scored_cores'] for s in samples if s['t'] <= cfg['horizon']]
    require(len(values) == result['score_sample_count'] == 81 and sum(values) == result['score_sum'] and sum(values)/81 == result['score'], 'exact condition score')
    with np.load(folder/'final.npz', allow_pickle=False) as data: same(data['grid'], grid, 'dense native final replay')
    require(digest(grid) == result['final_hash'], 'native final hash')
    counts['full_world_trajectories_verified'] += 1; counts['dense_world_updates_replayed'] += stop
    print('verified impact world', rid, 'targets', len(targets), flush=True)
    return result


def rational(value):
    return None if value is None else {'numerator': value.numerator, 'denominator': value.denominator, 'value': float(value)}


def analyses(m, calibration, results, counts):
    cfg = m['config']; ca = read(OUT/'calibration-analysis.json')
    confirmed = lambda o: bool(o.get('outcome') and o['outcome']['status'] == 'confirmed')
    scored = [o for o in calibration['observations'] if o['scored']]
    unscored = [o for o in calibration['observations'] if not o['scored']]
    by_state = [{'state': pid, 'selected': sum(o['state'] == pid for o in scored),
        'eligible': sum(o['state'] == pid and o['extraction_status'] == 'eligible' for o in scored),
        'confirmed': sum(o['state'] == pid and confirmed(o) for o in scored)} for pid in cfg['states']]
    strata = [{**s, 'state': spec['state'], 'confirmed': sum(o['stratum_id'] == s['stratum_id'] and confirmed(o) for o in scored)}
        for spec in m['runs'] if spec['split'] == 'calibration' for s in results[spec['run_id']]['strata'] if s['scored']]
    n = sum(confirmed(o) for o in scored); base = sum(confirmed(o) for o in calibration['baselines']); gate = cfg['calibration']['gate']
    checks = {'all_baselines': base == gate['baseline_recoveries_required'],
        'overall_recovery': bool(scored) and Fraction(n, len(scored)) >= Fraction(str(gate['overall_scored_recovery_fraction'])),
        'each_starting_state': all(s['selected'] and Fraction(s['confirmed'], s['selected']) >= Fraction(str(gate['per_starting_state_recovery_fraction'])) for s in by_state),
        'each_nonempty_stratum': all(s['confirmed'] >= gate['minimum_confirmed_per_nonempty_scored_stratum'] for s in strata if s['available_cores'])}
    allroots = calibration['baselines']+calibration['observations']
    summary = {'gate_checks': checks, 'gate_passed': all(checks.values()), 'baseline_confirmed': base,
        'baseline_total': len(calibration['baselines']), 'scored_selected': len(scored),
        'scored_eligible': sum(o['extraction_status'] == 'eligible' for o in scored), 'scored_confirmed': n,
        'unscored_selected': len(unscored), 'unscored_confirmed': sum(confirmed(o) for o in unscored),
        'by_state': by_state, 'strata': strata,
        'scored_statuses': dict(Counter('confirmed' if confirmed(o) else 'unresolved_search' if o['outcome'] else o['extraction_status'] for o in scored)),
        'unscored_confirmed_identities': sorted({o['outcome']['confirmation']['identity'] for o in unscored if confirmed(o)}),
        'truncations': dict(Counter(t['reason'] for o in allroots if o.get('outcome') for t in o['outcome']['truncations'])),
        'offspring_cap_nodes': sum(len(node['outcome']['children']) == cfg['search']['offspring_per_generation'] for o in allroots if o.get('outcome') for node in o['outcome']['nodes']),
        'generation_simulations': sum(o['outcome']['generation_simulations'] for o in allroots if o.get('outcome'))}
    require(all(ca[k] == v for k, v in summary.items()), 'independent exact calibration gate/counts')
    require(ca['calibration_sha256'] == sha(OUT/'calibration.json'), 'calibration source hash')
    benefit = read(OUT/'benefit.json'); analysis = read(OUT/'analysis.json')
    require(benefit['calibration_passed'] == summary['gate_passed'] and analysis['calibration'] == ca, 'paired calibration status')
    require(analysis['calibration_sha256'] == sha(OUT/'calibration.json') and analysis['benefit_sha256'] == sha(OUT/'benefit.json'), 'analysis source hashes')
    lookup = {}; inventory = []; rows = []
    # Acquisition groups development before confirmation, whereas the manifest
    # is ordered state then condition. Verify both declared orders explicitly.
    for split in ('development', 'confirmation'):
        for spec in m['runs']:
            if spec['split'] == split:
                r = results[spec['run_id']]
                inventory.append({'run_id': spec['run_id'], 'score_sum': r['score_sum'], 'final_hash': r['final_hash']})
    for spec in m['runs']:
        if spec['split'] == 'calibration': continue
        r = results[spec['run_id']]; lookup[spec['state'], spec['condition']['id'], spec['treatment']] = r['score_sum']
        rows.append({'run_id': spec['run_id'], 'state': spec['state'], 'split': spec['split'], 'condition': spec['condition']['id'],
            'treatment': spec['treatment'], 'score_sum': r['score_sum'], 'score': r['score_sum']/81,
            'mean_unscored_valid_cores': sum(s['unscored_valid_cores'] for s in r['samples'])/81,
            'mean_unknown_identity_cores': sum(s['unknown_identity_cores'] for s in r['samples'])/81})
    require(benefit['runs'] == inventory and analysis['runs'] == rows and len(rows) == 40, 'all paired state inventory and summaries')
    panels = {}; conditions = []
    for pid in cfg['states']:
        for split in ('development', 'confirmation'):
            pairs = []
            for i in range(2):
                name = f'{split}-{i}'; d = lookup[pid, name, 'D']; u = lookup[pid, name, 'U']; pairs.append((d, u))
                conditions.append({'state': pid, 'condition': name, 'split': split, 'D_sum': d, 'U_sum': u,
                    'D_mean': d/81, 'U_mean': u/81, 'D_minus_U': (d-u)/81, 'retention': rational(Fraction(d, u)) if u else None})
            ret = sum((Fraction(d, u) for d, u in pairs), Fraction(0))/2 if all(u for d, u in pairs) else None
            panels[pid, split] = {'state': pid, 'split': split, 'D_sum': sum(d for d, u in pairs), 'U_sum': sum(u for d, u in pairs),
                'D_mean': sum(d for d, u in pairs)/162, 'U_mean': sum(u for d, u in pairs)/162, 'retention': rational(ret)}
    require(analysis['conditions'] == conditions and analysis['panels'] == list(panels.values()), 'exact per-condition ratios and mean-of-ratios panels')
    valid = summary['gate_passed'] and m['exposure_verified'] and m['distinct_confirmation_verified']; comparisons = []
    def fraction(p):
        item = p['retention']; return Fraction(item['numerator'], item['denominator']) if item else None
    for spec in cfg['pairs']:
        pid = spec['candidate']; reported = {}
        for split in ('development', 'confirmation'):
            values = {p: panels[p, split] for p in [pid]+spec['inputs']}; candidate = fraction(values[pid])
            relative = all(candidate is not None and fraction(values[p]) is not None and candidate > fraction(values[p]) for p in spec['inputs'])
            absolute = all(values[pid]['D_sum'] > values[p]['D_sum'] for p in spec['inputs'])
            reported[split] = {'states': values, 'relative_advantage': relative, 'absolute_advantage': absolute,
                'candidate_minus_inputs_retention': {p: rational(candidate-fraction(values[p])) if candidate is not None and fraction(values[p]) is not None else None for p in spec['inputs']},
                'candidate_minus_inputs_D': {p: (values[pid]['D_sum']-values[p]['D_sum'])/162 for p in spec['inputs']}}
        relative = all(p['relative_advantage'] for p in reported.values()); absolute = all(p['absolute_advantage'] for p in reported.values())
        joint = relative and absolute if valid else None
        comparisons.append({**spec, 'panels': reported, 'relative_criterion': relative, 'absolute_criterion': absolute,
            'joint_confirmed': joint, 'status': 'joint_calibrated_population_advantage' if joint else 'criterion_not_met' if joint is False else 'unresolved_failed_validation',
            'originating_encounter': m['states'][pid]['source']['run_id'], 'ancestry': 'pair-level conservative comparison; genetic parentage ambiguous'})
    require(analysis['pairs'] == comparisons, 'strict paired relative/absolute/joint criteria, ties and undefined values')
    n = sum(p['joint_confirmed'] is True for p in comparisons) if valid else None
    require(analysis['joint_confirmed_encounters'] == n and analysis['yield'] == {
        label: {'confirmed': n if label != 'heldout' else 0 if n is not None else None, 'denominator': den,
                'value': (n if label != 'heldout' else 0)/den if n is not None else None}
        for label, den in [('main', 36), ('heldout', 18), ('overall', 54)]}, 'conditional encounter denominators and nulls')
    require(analysis['unresolved_other_candidate_encounters'] == 16, 'unresolved originating encounters')
    counts['calibration_gate_verified'] += 1; counts['paired_comparisons_verified'] += len(comparisons)


def audit(report):
    require(not sys.flags.optimize, 'generation_check assertions require unoptimized Python')
    for name in ('calibration.json', 'calibration-analysis.json', 'benefit.json', 'analysis.json'):
        require((OUT/name).exists(), f'{name} missing; wait for complete batches and analyses')
    m = read(OUT/'manifest.json'); cfg = m['config']; counts = report['counts']
    require(m['rule_hash'] == RULE_HASH and m['config'] == m['benefit'], 'rule/config/benefit definition')
    require(m['config_sha256'] == sha(ROOT/'configs/impact-v1.json') and m['protocol_sha256'] == sha(ROOT/'protocols/009-impact-matched-paired-assay.md'), 'frozen config/protocol')
    for path, value in {**m['code_hashes'], **m['source_sha256']}.items(): require(sha(ROOT/path) == value, f'frozen source changed: {path}')
    require(len(m['runs']) == len({r['run_id'] for r in m['runs']}) == 50 and
            Counter(r['split'] for r in m['runs']) == {'calibration': 10, 'development': 20, 'confirmation': 20}, 'all50 worlds')
    require(len(m['phases']) == len(m['preparations']) == 30 and len(m['registry']) == 4 and
            m['registry'] == sorted({s['identity'] for s in m['states'].values()}), 'phase/preparation/deduplicated registry inventory')
    require(m['exposure_verified'] is True and m['distinct_confirmation_verified'] is True, 'exposure/confirmation gates')
    report.update({'rule_hash': RULE_HASH, 'manifest_sha256': sha(OUT/'manifest.json'),
        'calibration_experiment_id': m['calibration_experiment_id'], 'benefit_experiment_id': m['benefit_experiment_id'],
        'auditor_sha256': sha(Path(__file__)), 'reused_verifier_sha256': {p: sha(ROOT/p) for p in ('scripts/verify_ecological.py', 'scripts/verify_fresh.py')},
        'evidence_sha256': {p: sha(OUT/p) for p in ('calibration.json', 'calibration-analysis.json', 'benefit.json', 'analysis.json')}})
    patches, prepared = preparations(m, counts)
    results = {r['run_id']: world(r, m, prepared, counts) for r in m['runs']}
    calibration = read(OUT/'calibration.json')
    require(calibration['experiment_id'] == m['calibration_experiment_id'] and len(calibration['baselines']) == 30, 'calibration and30 control inventory')
    for phase, base in zip(m['phases'], calibration['baselines']):
        require({k: base[k] for k in phase} == phase, 'phase-to-positive-control linkage')
        folder = OUT/'calibration'/'baseline'/phase['name']; require(OUT/base['folder'] == folder, 'positive control folder')
        graph(base['outcome'], folder, patches[phase['name']], m['states'][phase['state']]['identity'], True, cfg['search'], counts)
        counts['baseline_controls_verified'] += 1
    expected = [(r, target) for r in m['runs'] if r['split'] == 'calibration' for target in results[r['run_id']]['targets']]
    require(len(expected) == len(calibration['observations']), 'selected-root inventory')
    for (spec, target), observation in zip(expected, calibration['observations']):
        require({k: observation[k] for k in target} == target and observation['run_id'] == spec['run_id'] and observation['state'] == spec['state'], 'source-target-search link')
        folder = OUT/'calibration'/spec['run_id']
        if target['extraction_status'] == 'eligible':
            require(observation['outcome'] is not None and OUT/observation['folder'] == folder/f'{target["target_id"]}-search', 'eligible source search')
            with np.load(folder/target['snapshot_file'], allow_pickle=False) as data:
                graph(observation['outcome'], OUT/observation['folder'], data['snapshot'].copy(), target['identity'], target['scored'], cfg['search'], counts)
        else:
            require(observation['outcome'] is None and observation['folder'] is None, 'ineligible source missing outcome retained')
            counts['ineligible_observations_verified'] += 1
        counts['selected_observations_verified'] += 1
    analyses(m, calibration, results, counts)
    report.update({'status': 'passed', 'mismatches': 0})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--preparations-only', action='store_true', help='replay phases and exposure only, before responses')
    args = parser.parse_args()
    start = time.perf_counter(); report = {'status': 'running', 'counts': Counter(),
        'scope': 'all50 dense native trajectories;30 autonomous phase preparations and controls; complete component connectivity, clone placements, one-third removal, exact symmetry, selections, serial-search graphs and every generation; exact Fraction paired retention and joint endpoint. Not genetic ancestry, total viable population, or independent histories.'}
    destination = OUT/('preparation-integrity.json' if args.preparations_only else 'integrity.json')
    try:
        if args.preparations_only:
            m = read(OUT/'manifest.json')
            require(m['rule_hash'] == RULE_HASH, 'preparation rule hash')
            for path, value in {**m['code_hashes'], **m['source_sha256']}.items():
                require(sha(ROOT/path) == value, f'frozen preparation source changed: {path}')
            require(m['config_sha256'] == sha(ROOT/'configs/impact-v1.json') and
                    m['protocol_sha256'] == sha(ROOT/'protocols/009-impact-matched-paired-assay.md'), 'preparation config/protocol')
            preparations(m, report['counts'])
            report.update({'status': 'passed', 'mismatches': 0, 'scope': 'preparation-only, no post-removal response data read',
                'manifest_sha256': sha(OUT/'manifest.json'), 'auditor_sha256': sha(Path(__file__)),
                'rule_hash': RULE_HASH, 'frozen_code_hashes': m['code_hashes'],
                'command': 'OPENBLAS_NUM_THREADS=1 python -m scripts.verify_impact --preparations-only'})
        else:
            audit(report)
    except Exception as error:
        report.update({'status': 'failed', 'mismatches': 1, 'error_type': type(error).__name__, 'error': str(error)})
        report.update({'seconds': time.perf_counter()-start, 'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
        write_json(destination, report); raise
    report.update({'seconds': time.perf_counter()-start, 'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
    write_json(destination, report); print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    main()
