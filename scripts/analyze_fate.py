"""Finite-panel paired calibration analysis, specified before acquisition."""
import csv
import json
from collections import Counter
from evoloop.engine import ROOT
from scripts.fate_calibration import OUT,manifest
from scripts.atlas import write_json


def summarize(rows):
    eligible=[r for r in rows if r['target_status']=='eligible']
    paired=Counter((r['legacy_confirmed'],r['expanded_confirmed']) for r in eligible)
    return {'n':len(rows),'eligible':len(eligible),'target_status_counts':dict(Counter(r['target_status'] for r in rows)),
            'legacy_confirmed':sum(r['legacy_confirmed'] for r in rows),
            'expanded_confirmed':sum(r['expanded_confirmed'] for r in rows),
            'paired_eligible_counts':{f'legacy_{int(a)}_expanded_{int(b)}':paired[a,b] for a in (False,True) for b in (False,True)},
            'native_new_original_word_core_observations':sum(r['native_new_original_word_core'] for r in rows),
            'native_original_word_at_horizon':sum(r['native_original_word_at_horizon'] for r in rows),
            'native_boundary_flagged':sum(r['native_boundary_flagged'] for r in rows),
            'budget_truncated':sum(r['budget_truncated'] for r in rows),
            'depth_truncated':sum(r['depth_truncated'] for r in rows),
            'root_assay_extinct':sum(r['root_assay_extinct'] for r in rows)}


def main():
    m=manifest();rows=[];sources={s['id']:s for s in m['sources']}
    for s in m['sources']:
        for delay in m['config']['delays']:
            r=json.loads((OUT/f'runs/{s["id"]}-d{delay:03d}/result.json').read_text());x=r['expanded'];legacy=r['legacy']
            assert r['config_sha256']==m['config_sha256']
            rows.append({'case_id':r['case_id'],'source_id':s['id'],'kind':s['kind'],'run_id':s['run_id'],
                         'organism':s.get('organism'),'source_t':s['source_t'],'delay':delay,'target_status':r['target_status'],
                         'source_identity':s['identity'],'delayed_identity':r['delayed_identity'],
                         'delayed_identity_changed':r['delayed_identity'] is not None and r['delayed_identity']!=s['identity'],
                         'legacy_confirmed':bool(legacy and legacy['endpoint_confirmed']),
                         'legacy_stable_any':bool(legacy and legacy['status']=='confirmed'),
                         'expanded_confirmed':bool(x and x['status']=='confirmed'),
                         'expanded_stable_any':bool(x and x['stable_observations']),
                         'stable_identity':x['confirmation']['identity'] if x and x['confirmation'] else None,
                         'generation_simulations':x['generation_simulations'] if x else 0,
                         'budget_truncated':bool(x and any(t['reason']=='simulation_budget' for t in x['truncations'])),
                         'depth_truncated':bool(x and any(t['reason']=='depth_limit' for t in x['truncations'])),
                         'root_assay_extinct':bool(x and x['nodes'][0]['outcome']['status']=='assay_extinct'),
                         'native_target_at_horizon':r['native']['samples'][-1]['target_present'],
                         'native_original_word_at_horizon':r['native']['samples'][-1]['original_word_cores']>0,
                         'native_new_original_word_core':bool(r['native']['new_original_word_core_locations']),
                         'native_boundary_flagged':r['native']['boundary_first_t'] is not None})
    assert len(rows)==m['expected_cases']
    summary={'experiment_id':m['experiment_id'],'unit':'originating configuration; nested identity/delay diagnostics, finite-panel census',
             'candidate':summarize([r for r in rows if r['kind']=='candidate']),
             'control':summarize([r for r in rows if r['kind']=='control']),
             'by_delay':{str(d):{k:summarize([r for r in rows if r['delay']==d and r['kind']==k])
                                for k in ('candidate','control')} for d in m['config']['delays']},
             'by_source':{s:summarize([r for r in rows if r['source_id']==s]) for s in sources},
             'by_originating_configuration':{},'benefit_status':'not_assayed','H1_H3':'untested',
             'native_interpretation':'new original-word core appearance is structural; ancestry/inheritance unresolved'}
    for rid in sorted({s['run_id'] for s in m['sources'] if s['kind']=='candidate'}):
        z=[r for r in rows if r['run_id']==rid]
        summary['by_originating_configuration'][rid]={'identity_count':len({r['source_id'] for r in z}),
                       'any_eligible':any(r['target_status']=='eligible' for r in z),
                       'any_legacy_novel_confirmation':any(r['legacy_confirmed'] for r in z),
                       'any_expanded_novel_confirmation':any(r['expanded_confirmed'] for r in z),
                       'any_native_new_original_word_core':any(r['native_new_original_word_core'] for r in z)}
    write_json(OUT/'analysis.json',summary);write_json(OUT/'outcomes.json',rows)
    with (OUT/'outcomes.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    lines=['# Completed candidate-fate calibration','',f'Experiment: {m["experiment_id"]}. Seven identities nested in six originating configurations; two known-parent controls.',
           'All delays and ineligible targets retained. Native core appearances are not ancestry or inheritance evidence. No inferential intervals or p-values.','',
           '| Kind | Delay | Eligible / n | Legacy confirmation / n | Expanded confirmation / n | Native new original-word core / n |',
           '|---|---:|---:|---:|---:|---:|']
    for d,panel in summary['by_delay'].items():
        for kind,z in panel.items():
            lines.append(f'| {kind} | {d} | {z["eligible"]}/{z["n"]} | {z["legacy_confirmed"]}/{z["n"]} | {z["expanded_confirmed"]}/{z["n"]} | {z["native_new_original_word_core_observations"]}/{z["n"]} |')
    lines+=['','Candidate endpoint: stable word novel against both original inputs. Control endpoint: original composite identity.','',
            f'Paired eligible candidate results: {summary["candidate"]["paired_eligible_counts"]}.',
            f'Paired eligible control results: {summary["control"]["paired_eligible_counts"]}.',
            f'Candidate target statuses: {summary["candidate"]["target_status_counts"]}.',
            f'Control target statuses: {summary["control"]["target_status_counts"]}.','',
            'Same-snapshot comparisons address search sensitivity. Delay comparisons combine maturation with continued ecology.',
            'Stable paths are serial-isolation intervention outcomes, potentially assay-derived. Native ancestry remains unresolved.',
            'The atlas endpoint is unchanged. Benefit is not assayed; H1/H3/RSI remain unestablished.']
    (OUT/'analysis.md').write_text('\n'.join(lines)+'\n');print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
