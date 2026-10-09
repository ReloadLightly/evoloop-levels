"""Finite-panel census: pair outcomes, additive contributions, interaction contrasts."""
import csv
import json
from collections import Counter,defaultdict
import numpy as np
from evoloop.engine import ROOT
from scripts.atlas import OUT,load_manifest,write_json

def main():
    m=load_manifest();ih=json.loads((OUT/'inheritance.json').read_text());byrun=defaultdict(list)
    for item in ih['items']:byrun[item['run_id']].append(item)
    rows=[]
    for s in m['runs']:
        r=json.loads((OUT/'runs'/s['run_id']/'result.json').read_text());checks=byrun[s['run_id']]
        input_words={m['panel'][pid]['genotype'].split(':',1)[1] for pid in (s['focal'],s['partner']) if pid}
        signal_candidates=[c for c in r['candidates'] if c['genotype'].split(':',1)[1] not in input_words]
        signal_checks=[c for c in checks if c['encounter_genotype'].split(':',1)[1] not in input_words]
        confirmed_signal=any(o['stable_novel_vs_both_inputs'] and o['stable_genotype'].split(':',1)[1] not in input_words
                             for c in signal_checks for o in c['outcomes'])
        stable={o['stable_genotype'] for c in checks for o in c['outcomes'] if o['stable_novel_vs_both_inputs']}
        rows.append({'run_id':s['run_id'],'treatment':s['treatment'],'split':s['split'],
                     'focal':s['focal'],'partner':s['partner'],'phase':s['phase'],'geometry':s['geometry']['id'],
                     'contact':r['contact_t'] is not None,'contact_t':r['contact_t'],
                     'candidate':bool(r['candidates']),'eligible':any(c['snapshots'] for c in r['candidates']),
                     'confirmed':any(c['confirmed_novel'] for c in checks),
                     'candidate_signal':bool(signal_candidates),'eligible_signal':any(c['snapshots'] for c in signal_candidates),
                     'confirmed_signal':confirmed_signal,'morphology_only_candidates':len(r['candidates'])-len(signal_candidates),
                     'candidate_genotypes':len(r['candidates']),'confirmed_stable_genotypes':len(stable),
                     'unresolved_candidates':sum(not c['confirmed_novel'] for c in checks),
                     'assay_extinct_paths':sum(o['status']=='assay_extinct' for c in checks for o in c['outcomes']),
                     'isolation_attempts':sum(len(c['outcomes']) for c in checks),
                     'first_detached_offspring_paths':sum(o['generation1']['status']=='reproduced' for c in checks for o in c['outcomes']),
                     'second_generation_extinct_paths':sum(o['generation2']['status']=='extinct' for c in checks for o in c['outcomes']),
                     'final_closed_cores':r['metrics'][-1]['closed_cores'],'final_occupied_cells':r['metrics'][-1]['occupied_cells'],
                     'new_core_positions':r['new_core_count'],
                     'input_cores_present_at_horizon':sum(z['closed_core_present_at_horizon'] for z in r['input_structural_survival']),
                     'all_input_cores_lost':not any(z['closed_core_present_at_horizon'] for z in r['input_structural_survival']),
                     'boundary_t':r['boundary_first_t'],'benefit':'pending' if r['candidates'] else 'no_observed_candidate',
                     'confirmed_genotypes':sorted(stable)})
    (OUT/'outcomes.json').write_text(json.dumps(rows,indent=2)+'\n')
    with (OUT/'outcomes.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    def summarize(subset):
        return {'n':len(subset),**{key:sum(bool(r[key]) for r in subset) for key in
                                ['contact','candidate','eligible','confirmed','candidate_signal','eligible_signal','confirmed_signal','all_input_cores_lost']},
                'morphology_only_candidates':sum(r['morphology_only_candidates'] for r in subset),
                'unresolved_candidates':sum(r['unresolved_candidates'] for r in subset),
                'isolation_attempts':sum(r['isolation_attempts'] for r in subset),
                'assay_extinct_paths':sum(r['assay_extinct_paths'] for r in subset),
                'first_detached_offspring_paths':sum(r['first_detached_offspring_paths'] for r in subset),
                'second_generation_extinct_paths':sum(r['second_generation_extinct_paths'] for r in subset),
                'boundary_flagged_runs':sum(r['boundary_t'] is not None for r in subset),
                'beneficial_heritable_yield':None,'benefit_status':'pending_calibration_and_assay'}
    panels={}
    organisms=m['config']['organisms']
    for split in ('main','heldout'):
        sub=[r for r in rows if r['treatment']=='near' and r['split']==split]
        cells={};models={}
        for p in organisms:
            for q in organisms:cells[f'{p}|{q}']=summarize([r for r in sub if r['focal']==p and r['partner']==q])
        for outcome in ('candidate','confirmed','candidate_signal','confirmed_signal'):
            rates=np.array([[cells[f'{p}|{q}'][outcome]/cells[f'{p}|{q}']['n'] for q in organisms] for p in organisms])
            grand=rates.mean();focal=rates.mean(axis=1)-grand;partner=rates.mean(axis=0)-grand
            residual=rates-grand-focal[:,None]-partner[None,:]
            contrasts=rates[0,:]-rates[1,:]
            models[outcome]={'rates':rates.tolist(),'grand_mean':float(grand),
                             'focal_main_deviations':focal.tolist(),'partner_main_deviations':partner.tolist(),
                             'interaction_residuals':residual.tolist(),
                             'partner_specific_focal_contrasts':contrasts.tolist(),
                             'difference_of_differences':float(contrasts[0]-contrasts[1]),
                             'strict_rank_reversal':bool(contrasts[0]*contrasts[1]<0)}
        panels[split]={'summary':summarize(sub),'cells':cells,'models':models}
    near=[r for r in rows if r['treatment']=='near'];far=[r for r in rows if r['treatment']=='separated']
    solo=[r for r in rows if r['treatment']=='alone']
    matched={}
    for outcome in ('candidate','confirmed'):
        differences=[]
        for r in near:
            f=next(z for z in far if z['run_id']==r['run_id'].replace('near-','separated-',1))
            differences.append(int(r[outcome])-int(f[outcome]))
        matched[outcome]={'mean_near_minus_separated':sum(differences)/len(differences),
                         'near_only':differences.count(1),'separated_only':differences.count(-1),
                         'ties':differences.count(0),'n':len(differences)}
    summary={'experiment_id':m['experiment_id'],'near':summarize(near),'separated':summarize(far),
             'alone':summarize(solo),'panels':panels,'matched_separation':matched,
             'sampling':'finite deterministic panel; no inferential uncertainty intervals',
             'interpretation':'pair-level inherited novelty; useful/beneficial variation and H1/H3 unestablished'}
    summary['endpoint_audit']={'frozen':'composite identity (channel word + sorted dimensions)',
                               'added_during_acquisition':'signal-word novelty sensitivity endpoint; protocols/002-identity-audit.md'}
    write_json(OUT/'analysis.json',summary)
    text=['# Completed finite-panel atlas analysis','',f'Experiment: {m["experiment_id"]}. Distinct complete states are the census units.',
          'All rates retain nonproductive and lethal encounters. No statistical confidence intervals or p-values are estimated.','']
    for name in ('near','separated','alone'):
        z=summary[name];text.append(f'{name}: {z["n"]} states; contact {z["contact"]}; candidate {z["candidate"]}; eligible {z["eligible"]}; confirmed inherited novelty {z["confirmed"]}; unresolved run/genotype candidates {z["unresolved_candidates"]}; boundary flags {z["boundary_flagged_runs"]}.')
    text+=['','| Split | Focal | Partner | Candidate / n | Confirmed / n | Unresolved candidates |',
           '|---|---|---|---:|---:|---:|']
    for split,panel in panels.items():
        for key,c in panel['cells'].items():
            p,q=key.split('|');text.append(f'| {split} | {p} | {q} | {c["candidate"]}/{c["n"]} | {c["confirmed"]}/{c["n"]} | {c["unresolved_candidates"]} |')
    for split,panel in panels.items():
        for outcome,model in panel['models'].items():
            text+=['',f'{split}, {outcome}: partner-specific focal contrasts {model["partner_specific_focal_contrasts"]}; difference of differences {model["difference_of_differences"]:.3f}; strict rank reversal {model["strict_rank_reversal"]}.']
    text+=['','Benefit assays and individual viability calibration are pending. Beneficial-heritable-variant yield is unknown, not zero.',
           'Ancestry is conservative pair-level. These interactions do not identify a focal-specific genetic contribution.',
           'H1, H3, increased evolvability, and RSI remain untested/unestablished.']
    (OUT/'analysis.md').write_text('\n'.join(text)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
