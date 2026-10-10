"""Freeze, execute and resume the calibrated ecological comparison."""
import argparse
import hashlib
import json
import platform
import resource
import time

import numpy as np
import scipy

from evoloop.engine import ROOT, RULE_HASH, advance, digest
from evoloop.ecology import prepared_grid, observation, remove_block, chosen_cores
from evoloop.fate import expanded_search
from evoloop.periodic_assays import offspring_generation
from scripts.atlas import write_json

OUT = ROOT/'data/ecological-v1'
CFG = ROOT/'configs/ecological-v1.json'
PROTOCOL = ROOT/'protocols/007-ecological-calibration-and-benefit.md'
FILES = ['evoloop/kernel.c', 'evoloop/engine.py', 'evoloop/tracking.py',
         'evoloop/periodic_tracking.py', 'evoloop/periodic_assays.py', 'evoloop/fate.py',
         'evoloop/ecology.py', 'scripts/ecological_assay.py', 'scripts/analyze_ecological.py']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def code_hashes():
    return {name: sha(ROOT/name) for name in FILES}


def benchmark():
    """Timing only on a verified control; no main outcomes are collected."""
    snapshot = np.load(ROOT/'data/panel-v2/V01.npz')['snapshot']
    grid = prepared_grid(snapshot, [192,192], 0)
    identity = observation(grid, [])[1][0]['identity']
    then = time.perf_counter()
    for _ in range(10):
        advance(grid, 20)
        observation(grid, [identity])
    report = {'control': 'V01', 'updates': 200, 'observations': 10,
              'seconds': time.perf_counter()-then,
              'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              'workers': 1, 'scope': 'short control timing; not a full dense-colony runtime estimate'}
    OUT.mkdir(parents=True, exist_ok=True)
    write_json(OUT/'benchmark.json', report); print(json.dumps(report), flush=True)


def freeze():
    assert not (OUT/'manifest.json').exists(), 'use a new version to change a frozen experiment'
    cfg = json.loads(CFG.read_text())
    atlas = json.loads((ROOT/cfg['benefit_source']).read_text())
    benefit = atlas['benefit']
    discovery = json.loads((ROOT/'data/panel-v2/discovery.json').read_text())
    catalogue = json.loads((ROOT/'data/atlas-v2/confirmed/catalogue.json').read_text())
    panel = {p['id']: p for p in discovery['panel']}
    variants = {p['id']: p for p in catalogue['entries']}
    source_files = [cfg['benefit_source'], 'data/panel-v2/discovery.json',
                    'data/atlas-v2/manifest.json', 'data/atlas-v2/inheritance.json',
                    'data/atlas-v2/confirmed/catalogue.json']
    states = {}; snapshots = {}
    for pid in cfg['states']:
        file = f'data/panel-v2/{pid}.npz' if pid in panel else f'data/atlas-v2/{variants[pid]["snapshot_file"]}'
        snapshots[pid] = np.load(ROOT/file)['snapshot'].copy()
        identity = panel[pid]['stable_identity'] if pid in panel else variants[pid]['identity']
        states[pid] = {'id': pid, 'identity': identity, 'snapshot_file': file,
                       'snapshot_hash': digest(snapshots[pid]),
                       'shape': list(snapshots[pid].shape),
                       'preparation': 'complete third detached descendant; no added phase advancement',
                       'source': panel[pid]['source'] if pid in panel else variants[pid]['representative']}
        source_files.append(file)
        if pid in variants:
            assert states[pid]['snapshot_hash'] == variants[pid]['snapshot_hash']
    registry = sorted({p['identity'] for p in states.values()})
    assert len(registry) == 4
    (OUT/'initial').mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT/'snapshots.npz', **snapshots)
    runs = []
    conditions = [('calibration', x) for x in cfg['calibration']['conditions']]
    for split in ('development', 'confirmation'):
        conditions += [(split, {'id': f'{split}-{i}', **c}) for i, c in enumerate(benefit[split])]
    for split, condition in conditions:
        for pid in cfg['states']:
            grid = prepared_grid(snapshots[pid], benefit['shape'], condition['rotation'])
            counts, records, _ = observation(grid, registry)
            assert counts['scored_cores'] == counts['closed_cores'] == 1
            assert records[0]['identity'] == states[pid]['identity']
            rid = f'{split}-{pid}-{condition["id"]}'
            np.savez_compressed(OUT/'initial'/f'{rid}.npz', grid=grid)
            runs.append({'run_id': rid, 'split': split, 'state': pid, 'condition': condition,
                         'initial_hash': digest(grid), 'initial_core': records[0]['core']})
    assert len(runs) == 30 and len({r['initial_hash'] for r in runs}) == 20
    # Calibration schedules differ although some complete initial grids repeat.
    write_json(OUT/'manifest.json', {
        'calibration_experiment_id': cfg['calibration_experiment_id'],
        'benefit_experiment_id': cfg['benefit_experiment_id'], 'config': cfg, 'benefit': benefit,
        'states': states, 'registry': registry, 'runs': runs, 'rule_hash': RULE_HASH,
        'code_hashes': code_hashes(), 'config_sha256': sha(CFG), 'protocol_sha256': sha(PROTOCOL),
        'source_sha256': {file: sha(ROOT/file) for file in source_files},
        'environment': {'python': platform.python_version(), 'numpy': np.__version__,
                        'scipy': scipy.__version__, 'platform': platform.platform()},
    })
    print('Frozen 10 calibration and 20 benefit configurations', flush=True)


def load_manifest():
    m = json.loads((OUT/'manifest.json').read_text())
    assert m['rule_hash'] == RULE_HASH and m['code_hashes'] == code_hashes()
    assert m['config_sha256'] == sha(CFG) and m['protocol_sha256'] == sha(PROTOCOL)
    assert all(sha(ROOT/f) == value for f, value in m['source_sha256'].items())
    return m


def run_ecology(spec, m):
    calibration = spec['split'] == 'calibration'
    folder = OUT/spec['split']/spec['run_id']
    folder.mkdir(parents=True, exist_ok=True)
    grid = np.load(OUT/'initial'/f'{spec["run_id"]}.npz')['grid'].copy()
    assert digest(grid) == spec['initial_hash']
    benefit = m['benefit']; cfg = m['config']; registry = m['registry']
    stop = max(cfg['calibration']['source_times'])+cfg['calibration']['native_continuation_horizon'] if calibration else benefit['horizon']
    samples = []; events = []; strata = []; targets = []; previous = {}
    frames = []; frame_times = []; then = time.perf_counter()
    capture = not calibration and spec['condition']['id'] == 'development-0' and spec['state'] in ('V01','RV01','RV02')
    for t in range(0, stop+1, benefit['sample_interval']):
        if t:
            advance(grid, benefit['sample_interval'])
        if t in benefit['disturbance_times']:
            pre_counts, _, _ = observation(grid, registry)
            before, report = remove_block(grid, spec['condition']['block'], benefit['block_size'])
            post_counts, _, _ = observation(grid, registry)
            np.savez_compressed(folder/f'disturbance-{t}.npz', before=before, after=grid)
            events.append({'type': 'disturbance', 't': t, **report,
                           'pre_counts': pre_counts, 'post_counts': post_counts})
        counts, records, loops = observation(grid, registry)
        samples.append({'t': t, **counts, 'cores': records})
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
        if capture and t % 40 == 0:
            frames.append(grid.copy()); frame_times.append(t)
        if calibration and t in cfg['calibration']['source_times']:
            np.savez_compressed(folder/f'source-{t}.npz', grid=grid)
            for scored in (True, False):
                chosen = chosen_cores(loops, scored, registry)
                stratum = f'{spec["run_id"]}-t{t}-{ "scored" if scored else "unscored"}'
                strata.append({'stratum_id': stratum, 't': t, 'scored': scored,
                                'available_cores': sum((o['genotype'] in registry) == scored for o in loops),
                                'selected_cores': len(chosen)})
                for i, o in enumerate(chosen):
                    snap = o['isolation_snapshot']
                    status = o['extraction_status'] if snap is None else 'ineligible_component_size' if max(snap.shape)+20 > cfg['search']['isolation_shape'][0] else 'eligible'
                    name = f'target-{t}-{ "scored" if scored else "unscored"}-{i}'
                    if snap is not None:
                        np.savez_compressed(folder/f'{name}.npz', snapshot=snap)
                    targets.append({'target_id': name, 'stratum_id': stratum, 't': t,
                                    'core': o['core'], 'identity': o['genotype'], 'scored': scored,
                                    'extraction_status': status, 'snapshot_hash': digest(snap) if snap is not None else None,
                                    'extraction_bbox': o.get('extraction_bbox'),
                                    'snapshot_file': f'{name}.npz' if snap is not None else None})
    np.savez_compressed(folder/'final.npz', grid=grid)
    if capture:
        np.savez_compressed(folder/'replay.npz', frames=np.array(frames), times=np.array(frame_times))
    score_samples = [s['scored_cores'] for s in samples if s['t'] <= benefit['horizon']]
    assert len(score_samples) == 81
    result = {**spec, 'rule_hash': RULE_HASH, 'completed_updates': stop,
              'final_hash': digest(grid), 'samples': samples, 'events': events,
              'score': sum(score_samples)/len(score_samples), 'score_sum': sum(score_samples), 'score_sample_count': len(score_samples),
              'score_scope': 'fixed known-identity closed-core structural population',
              'strata': strata, 'targets': targets, 'seconds': time.perf_counter()-then}
    if calibration:
        for target in targets:
            window = [s for s in samples if target['t'] <= s['t'] <= target['t']+cfg['calibration']['native_continuation_horizon']]
            present = [any(o['core'] == target['core'] for o in s['cores']) for s in window]
            loss = next((s['t'] for s, p in zip(window, present) if not p), None)
            recurrence = next((s['t'] for s, p in zip(window, present) if loss is not None and s['t'] > loss and p), None)
            endpoint = next((o for o in window[-1]['cores'] if o['core'] == target['core']), None)
            word = target['identity'].split(':',1)[1] if target['identity'] else None
            matched = [s['t'] for s in window if word and any(o['core'] != target['core'] and o['identity'] and o['identity'].split(':',1)[1] == word for o in s['cores'])]
            target['native_continuation'] = {'horizon': cfg['calibration']['native_continuation_horizon'],
                'sample_interval': benefit['sample_interval'], 'fixed_core_first_loss_t': loss,
                'fixed_core_first_recurrence_t': recurrence, 'endpoint_identity': endpoint['identity'] if endpoint else None,
                'matching_word_elsewhere_first_t': matched[0] if matched else None,
                'interpretation': 'overlapping structural continuations; no native offspring or genetic ancestry assignment'}
    write_json(folder/'result.json', result)
    print('ECOLOGY', spec['run_id'], f'{result["seconds"]:.2f}s', flush=True)
    return result


def search_one(snapshot, identity, m, folder, original):
    folder.mkdir(parents=True, exist_ok=True)
    if (folder/'result.json').exists():
        return json.loads((folder/'result.json').read_text())
    def persist(node, arrays):
        name = 'confirmation' if 'confirmation' in node else f'node-{node["node"]:02d}'
        write_json(folder/f'{name}.json', node)
        np.savez_compressed(folder/f'{name}.npz', **arrays)
    accept = (lambda gt: gt == identity) if original else (lambda gt: True)
    report = expanded_search(snapshot, identity, m['config']['search'], accept,
                             persist, generation=offspring_generation)
    write_json(folder/'result.json', report)
    return report


def calibrate():
    m = load_manifest(); then = time.perf_counter(); baselines = []; observations = []
    snapshots = np.load(OUT/'snapshots.npz')
    for pid in m['config']['states']:
        folder = OUT/'calibration'/'baseline'/pid
        report = search_one(snapshots[pid], m['states'][pid]['identity'], m, folder, True)
        baselines.append({'state': pid, 'folder': str(folder.relative_to(OUT)), 'outcome': report})
    for spec in m['runs']:
        if spec['split'] != 'calibration':
            continue
        folder = OUT/'calibration'/spec['run_id']
        result = json.loads((folder/'result.json').read_text()) if (folder/'result.json').exists() else run_ecology(spec, m)
        for target in result['targets']:
            report = None; path = folder/f'{target["target_id"]}-search'
            if target['extraction_status'] == 'eligible':
                snapshot = np.load(folder/target['snapshot_file'])['snapshot']
                assert digest(snapshot) == target['snapshot_hash']
                report = search_one(snapshot, target['identity'], m, path, target['scored'])
            observations.append({'run_id': spec['run_id'], 'state': spec['state'], **target,
                                 'folder': str(path.relative_to(OUT)) if report else None,
                                 'outcome': report})
        print('CALIBRATION', spec['run_id'], 'targets', len(result['targets']), flush=True)
    write_json(OUT/'calibration.json', {'experiment_id': m['calibration_experiment_id'],
        'baselines': baselines, 'observations': observations,
        'seconds_this_invocation': time.perf_counter()-then,
        'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})


def benefit():
    m = load_manifest()
    calibration = json.loads((OUT/'calibration-analysis.json').read_text())
    assert calibration['calibration_sha256'] == sha(OUT/'calibration.json')
    then = time.perf_counter(); runs = []
    for split in ('development','confirmation'):
        for spec in m['runs']:
            if spec['split'] != split:
                continue
            folder = OUT/split/spec['run_id']
            result = json.loads((folder/'result.json').read_text()) if (folder/'result.json').exists() else run_ecology(spec, m)
            runs.append({'run_id': spec['run_id'], 'score': result['score'],
                         'final_hash': result['final_hash']})
    write_json(OUT/'benefit.json', {'experiment_id': m['benefit_experiment_id'],
        'calibration_passed': calibration['gate_passed'],
        'status': 'calibrated_proxy_assay' if calibration['gate_passed'] else 'structural_diagnostics; benefit_confirmation_blocked',
        'runs': runs, 'seconds_this_invocation': time.perf_counter()-then,
        'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('command', choices=['benchmark','freeze','calibrate','benefit'])
    args = parser.parse_args(); {'benchmark': benchmark, 'freeze': freeze, 'calibrate': calibrate, 'benefit': benefit}[args.command]()
