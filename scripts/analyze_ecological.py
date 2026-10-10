"""Frozen finite-panel gate and paired arithmetic; unknown benefit stays null."""
import argparse
import csv
import json
from collections import Counter

from evoloop.engine import ROOT
from evoloop.ecology import panel_summary, strict_advantage
from scripts.atlas import write_json
from scripts.ecological_assay import OUT, load_manifest, sha


def recovered(row):
    return bool(row.get('outcome') and row['outcome']['status'] == 'confirmed')


def calibration():
    m = load_manifest(); c = json.loads((OUT/'calibration.json').read_text())
    scored = [r for r in c['observations'] if r['scored']]
    unscored = [r for r in c['observations'] if not r['scored']]
    baselines = sum(recovered(r) for r in c['baselines'])
    count = sum(recovered(r) for r in scored)
    by_state = []
    for pid in m['config']['states']:
        rows = [r for r in scored if r['state'] == pid]
        by_state.append({'state': pid, 'selected': len(rows),
                         'eligible': sum(r['extraction_status'] == 'eligible' for r in rows),
                         'confirmed': sum(recovered(r) for r in rows)})
    strata = []
    for spec in m['runs']:
        if spec['split'] != 'calibration':
            continue
        r = json.loads((OUT/'calibration'/spec['run_id']/'result.json').read_text())
        for s in r['strata']:
            if not s['scored']:
                continue
            rows = [o for o in scored if o['stratum_id'] == s['stratum_id']]
            assert len(rows) == s['selected_cores']
            strata.append({**s, 'state': spec['state'], 'confirmed': sum(recovered(o) for o in rows)})
    gate = m['config']['calibration']['gate']
    checks = {
        'all_baselines': baselines == gate['baseline_recoveries_required'],
        'overall_recovery': bool(scored) and count/len(scored) >= gate['overall_scored_recovery_fraction'],
        'each_starting_state': all(s['selected'] and s['confirmed']/s['selected'] >= gate['per_starting_state_recovery_fraction'] for s in by_state),
        'each_nonempty_stratum': all(s['confirmed'] >= gate['minimum_confirmed_per_nonempty_scored_stratum'] for s in strata if s['available_cores']),
    }
    caps = Counter(t['reason'] for r in c['baselines']+c['observations'] if r.get('outcome') for t in r['outcome']['truncations'])
    result = {
        'experiment_id': m['calibration_experiment_id'], 'calibration_sha256': sha(OUT/'calibration.json'),
        'gate_passed': all(checks.values()), 'gate_checks': checks,
        'baseline_confirmed': baselines, 'baseline_total': len(c['baselines']),
        'scored_selected': len(scored), 'scored_eligible': sum(r['extraction_status'] == 'eligible' for r in scored),
        'scored_confirmed': count, 'scored_statuses': dict(Counter('confirmed' if recovered(r) else 'unresolved_search' if r['outcome'] else r['extraction_status'] for r in scored)),
        'unscored_selected': len(unscored), 'unscored_confirmed': sum(recovered(r) for r in unscored),
        'unscored_confirmed_identities': sorted({r['outcome']['confirmation']['identity'] for r in unscored if recovered(r)}),
        'by_state': by_state, 'strata': strata, 'truncations': dict(caps),
        'offspring_cap_nodes': sum(len(n['outcome']['children']) == m['config']['search']['offspring_per_generation'] for r in c['baselines']+c['observations'] if r.get('outcome') for n in r['outcome']['nodes']),
        'generation_simulations': sum(r['outcome']['generation_simulations'] for r in c['baselines']+c['observations'] if r.get('outcome')),
        'interpretation': 'finite selected isolation recovery, not native reproduction proof; ineligible/nonconfirming cores remain unresolved',
    }
    write_json(OUT/'calibration-analysis.json', result)
    print(json.dumps({k: v for k,v in result.items() if k not in ('strata','interpretation')}, indent=2), flush=True)
    return result


def benefit():
    m = load_manifest(); c = json.loads((OUT/'calibration-analysis.json').read_text())
    assert c['calibration_sha256'] == sha(OUT/'calibration.json')
    b = json.loads((OUT/'benefit.json').read_text()); lookup = {}; runs = []
    for spec in m['runs']:
        if spec['split'] == 'calibration':
            continue
        r = json.loads((OUT/spec['split']/spec['run_id']/'result.json').read_text())
        values = [s['scored_cores'] for s in r['samples'] if s['t'] <= m['benefit']['horizon']]
        assert len(values) == r['score_sample_count'] == 81 and sum(values) == r['score_sum'] and sum(values)/81 == r['score']
        lookup[spec['state'], spec['split'], spec['condition']['id']] = r['score_sum']
        runs.append({'run_id': spec['run_id'], 'state': spec['state'], 'split': spec['split'],
                     'condition': spec['condition']['id'], 'score': r['score'], 'score_sum': r['score_sum'],
                     'mean_unscored_valid_cores': sum(s['unscored_valid_cores'] for s in r['samples'])/81,
                     'mean_unknown_identity_cores': sum(s['unknown_identity_cores'] for s in r['samples'])/81,
                     'deleted_occupied_cells': sum(e['removed_occupied_cells'] for e in r['events'] if e['type'] == 'disturbance')})
    assert len(runs) == 20 == len(b['runs'])
    pairs = []
    for pair in m['config']['pairs']:
        pid = pair['candidate']; panels = {}; conditions = []
        for split in ('development', 'confirmation'):
            totals = {state: panel_summary([lookup[state, split, f'{split}-{i}'] for i in range(2)]) for state in [pid]+pair['inputs']}
            scores = {state: total['mean'] for state,total in totals.items()}
            panels[split] = {'scores': scores, 'exact_totals': totals,
                             'candidate_minus_inputs': {q: (totals[pid]['score_sum']-totals[q]['score_sum'])/162 for q in pair['inputs']},
                             'strict_advantage': strict_advantage(totals[pid]['score_sum'], [totals[q]['score_sum'] for q in pair['inputs']])}
            for i in range(2):
                condition = f'{split}-{i}'
                conditions.append({'condition': condition, 'candidate': lookup[pid,split,condition]/81,
                                   'inputs': {q: lookup[q,split,condition]/81 for q in pair['inputs']},
                                   'candidate_minus_inputs': {q: (lookup[pid,split,condition]-lookup[q,split,condition])/81 for q in pair['inputs']}})
        advantage = all(p['strict_advantage'] for p in panels.values())
        pairs.append({**pair, 'panels': panels, 'conditions': conditions,
                      'structural_advantage_both_panels': advantage,
                      'confirmed_benefit': advantage if c['gate_passed'] else None,
                      'benefit_status': 'confirmed_calibrated_proxy_advantage' if c['gate_passed'] and advantage else 'criterion_not_met' if c['gate_passed'] else 'blocked_failed_calibration; unknown',
                      'originating_encounters': m['states'][pid]['source']['run_id'],
                      'ancestry': 'conservative comparison against both inputs; no genetic parent assignment'})
    n = sum(p['confirmed_benefit'] is True for p in pairs) if c['gate_passed'] else None
    analysis = {'experiment_id': m['benefit_experiment_id'], 'calibration': c, 'runs': runs, 'pairs': pairs,
                'confirmed_beneficial_encounters': n,
                'yield': {'main': {'confirmed': n, 'denominator': 36, 'yield': n/36 if n is not None else None},
                          'heldout': {'confirmed': 0 if n is not None else None, 'denominator': 18, 'yield': 0.0 if n is not None else None},
                          'overall': {'confirmed': n, 'denominator': 54, 'yield': n/54 if n is not None else None}},
                'unresolved_other_candidate_encounters': 16,
                'metric_scope': 'fixed known-identity population; unregistered viable types may be omitted',
                'uncertainty': 'descriptive paired condition panels; nested deterministic observations, no p-values or confidence intervals',
                'calibration_sha256': sha(OUT/'calibration.json'), 'benefit_sha256': sha(OUT/'benefit.json')}
    write_json(OUT/'analysis.json', analysis)
    with (OUT/'scores.csv').open('w') as f:
        writer = csv.DictWriter(f, fieldnames=list(runs[0])); writer.writeheader(); writer.writerows(runs)
    text = ['# Ecological calibration and frozen paired assay', '',
            f'Calibration gate: **{"PASS" if c["gate_passed"] else "NOT PASSED"}**. Original-identity recovery '
            f'{c["scored_confirmed"]}/{c["scored_selected"]} selected scored cores; '
            f'{c["baseline_confirmed"]}/{c["baseline_total"]} baseline controls. Ineligible and nonconfirming fates remain unresolved.', '',
            'All 20 frozen benefit configurations completed. Scores concern recognized, fixed-registry closed cores, not total viable population.', '',
            '| Candidate / inputs | Development means | Confirmation means | Strict structural advantage in both | Confirmed benefit |',
            '|---|---|---|---|---|']
    for p in pairs:
        means = ['; '.join(f'{q}: {v:.3f}' for q,v in p['panels'][split]['scores'].items()) for split in ('development','confirmation')]
        text.append(f'| {p["candidate"]} / {", ".join(p["inputs"])} | {means[0]} | {means[1]} | {p["structural_advantage_both_panels"]} | {p["benefit_status"]} |')
    text += ['', 'If calibration is not passed, structural score contrasts cannot confirm benefit: beneficial-heritable yield remains **unknown**, not zero.',
             'All encounter denominators are retained (36 main,18 held-out,54 total). Other 16 candidate-producing encounters remain unresolved under the earlier bounded search.',
             'The four condition scores and both-input contrasts are retained in analysis.json. Ties do not meet the frozen strict-advantage criterion.',
             'Native continuation observations do not identify offspring ancestry. H1/H3 and recursive self-improvement remain untested/unestablished.', '']
    (OUT/'analysis.md').write_text('\n'.join(text))
    print('Benefit analysis complete; confirmed yield', analysis['yield'], flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('command', choices=['calibration','benefit'])
    args = parser.parse_args(); {'calibration': calibration, 'benefit': benefit}[args.command]()
