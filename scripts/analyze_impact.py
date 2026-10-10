"""Frozen finite-panel gate and paired arithmetic; unknown benefit stays null."""
import argparse
import csv
import json
from collections import Counter

from evoloop.engine import ROOT
from fractions import Fraction
from evoloop.microcolony import retention_panel, rational
from scripts.atlas import write_json
from scripts.impact_assay import OUT, load_manifest, sha


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
    m=load_manifest(); c=json.loads((OUT/'calibration-analysis.json').read_text()); b=json.loads((OUT/'benefit.json').read_text())
    assert c['calibration_sha256']==sha(OUT/'calibration.json')
    lookup={}; runs=[]
    for spec in m['runs']:
        if spec['split']=='calibration': continue
        r=json.loads((OUT/spec['split']/spec['run_id']/'result.json').read_text())
        values=[s['scored_cores'] for s in r['samples']]
        assert len(values)==r['score_sample_count']==81 and sum(values)==r['score_sum']
        lookup[spec['state'],spec['condition']['id'],spec['treatment']]=r['score_sum']
        runs.append({'run_id':spec['run_id'],'state':spec['state'],'split':spec['split'],'condition':spec['condition']['id'],
                     'treatment':spec['treatment'],'score_sum':r['score_sum'],'score':r['score_sum']/81,
                     'mean_unscored_valid_cores':sum(s['unscored_valid_cores'] for s in r['samples'])/81,
                     'mean_unknown_identity_cores':sum(s['unknown_identity_cores'] for s in r['samples'])/81})
    assert len(runs)==len(b['runs'])==40
    panels={}; conditions=[]
    for pid in m['config']['states']:
        for split in ('development','confirmation'):
            rows=[]
            for i in range(2):
                cond=f'{split}-{i}'; d=lookup[pid,cond,'D']; u=lookup[pid,cond,'U']; rows.append((d,u))
                conditions.append({'state':pid,'condition':cond,'split':split,'D_sum':d,'U_sum':u,'D_mean':d/81,'U_mean':u/81,
                                   'D_minus_U':(d-u)/81,'retention':rational(Fraction(d,u)) if u else None})
            panels[pid,split]={'state':pid,'split':split,'D_sum':sum(d for d,u in rows),'U_sum':sum(u for d,u in rows),
                              'D_mean':sum(d for d,u in rows)/162,'U_mean':sum(u for d,u in rows)/162,
                              'retention':rational(retention_panel(rows))}
    pairs=[]
    valid=c['gate_passed'] and m['exposure_verified'] and m['distinct_confirmation_verified']
    def frac(item):
        r=item['retention']; return Fraction(r['numerator'],r['denominator']) if r else None
    for pair in m['config']['pairs']:
        pid=pair['candidate']; comparisons={}
        for split in ('development','confirmation'):
            allstates=[pid]+pair['inputs']; values={p:panels[p,split] for p in allstates}
            candidate=frac(values[pid]); parents=[frac(values[p]) for p in pair['inputs']]
            relative=all(candidate is not None and q is not None and candidate>q for q in parents)
            absolute=all(values[pid]['D_sum']>values[p]['D_sum'] for p in pair['inputs'])
            comparisons[split]={'states':values,'relative_advantage':relative,'absolute_advantage':absolute,
                  'candidate_minus_inputs_retention':{p:rational(candidate-frac(values[p])) if candidate is not None and frac(values[p]) is not None else None for p in pair['inputs']},
                  'candidate_minus_inputs_D':{p:(values[pid]['D_sum']-values[p]['D_sum'])/162 for p in pair['inputs']}}
        relative=all(p['relative_advantage'] for p in comparisons.values()); absolute=all(p['absolute_advantage'] for p in comparisons.values())
        joint=relative and absolute if valid else None
        pairs.append({**pair,'panels':comparisons,'relative_criterion':relative,'absolute_criterion':absolute,'joint_confirmed':joint,
                      'status':'joint_calibrated_population_advantage' if joint else 'criterion_not_met' if joint is False else 'unresolved_failed_validation',
                      'originating_encounter':m['states'][pid]['source']['run_id'],'ancestry':'pair-level conservative comparison; genetic parentage ambiguous'})
    n=sum(p['joint_confirmed'] is True for p in pairs) if valid else None
    result={'experiment_id':m['benefit_experiment_id'],'calibration':c,'runs':runs,'conditions':conditions,'panels':list(panels.values()),'pairs':pairs,
            'joint_confirmed_encounters':n,'yield':{label:{'confirmed':n if label!='heldout' else 0 if n is not None else None,'denominator':den,
            'value':(n if label!='heldout' else 0)/den if n is not None else None} for label,den in [('main',36),('heldout',18),('overall',54)]},
            'unresolved_other_candidate_encounters':16,'scope':'finite-panel fixed-registry population performance, not evolvability; selected isolation recovery is not total native viability',
            'uncertainty':'deterministic condition contrasts; no independent histories, confidence intervals or p-values',
            'calibration_sha256':sha(OUT/'calibration.json'),'benefit_sha256':sha(OUT/'benefit.json')}
    write_json(OUT/'analysis.json',result)
    with (OUT/'scores.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(runs[0]));writer.writeheader();writer.writerows(runs)
    lines=['# Impact-matched paired assay','',f'Calibration gate: {c["gate_passed"]}; scored recovery {c["scored_confirmed"]}/{c["scored_selected"]}; phase controls {c["baseline_confirmed"]}/{c["baseline_total"]}.','',
           '| Candidate | Panel | Retention (candidate; both inputs) | Absolute D means | Relative / absolute |','|---|---|---|---|---|']
    for p in pairs:
        for split,v in p['panels'].items():
            ret='; '.join(f'{s}: {x["retention"]["value"]:.4f}' if x['retention'] else f'{s}: undefined' for s,x in v['states'].items())
            means='; '.join(f'{s}: {x["D_mean"]:.4f}' for s,x in v['states'].items())
            lines.append(f'| {p["candidate"]} | {split} | {ret} | {means} | {v["relative_advantage"]} / {v["absolute_advantage"]} |')
        lines.extend(['',f'{p["candidate"]}: {p["status"]}.',''])
    lines.extend([f'Conditional joint-confirmed originating encounters: {n}/54; other16 candidate encounters unresolved. Registry counts are structural; phases are elapsed ages; constructed colonies are not native histories.',''])
    (OUT/'analysis.md').write_text('\n'.join(lines)); print(json.dumps({'pairs':[{k:p[k] for k in ('candidate','relative_criterion','absolute_criterion','joint_confirmed')} for p in pairs],'yield':result['yield']},indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['calibration','benefit']);args=parser.parse_args()
    {'calibration':calibration,'benefit':benefit}[args.command]()
