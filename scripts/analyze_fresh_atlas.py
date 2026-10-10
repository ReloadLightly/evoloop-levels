"""Descriptive full crossed-panel analysis; no pseudoreplicated uncertainty."""
import itertools,json
import numpy as np
from evoloop.engine import ROOT
from scripts.atlas import write_json
OUT=ROOT/'data/atlas-v2'

def main():
    m=json.loads((OUT/'manifest.json').read_text());inherit=json.loads((OUT/'inheritance.json').read_text())
    records=[json.loads((OUT/'runs'/s['run_id']/'result.json').read_text()) for s in m['runs']]
    inherited={i['run_id'] for i in inherit['items'] if i['confirmed_novel']}
    ids=m['config']['organisms'];splits={};tables=[]
    for split in ('main','heldout'):
        rs=[r for r in records if r['treatment']=='near' and r['split']==split]
        values={};cells=[]
        for p,q in itertools.product(ids,repeat=2):
            group=[r for r in rs if r['focal']==p and r['partner']==q];n=len(group)
            cand=sum(bool(r['candidates']) for r in group);confirmed=sum(r['run_id'] in inherited for r in group)
            values[p,q]={'candidate':cand/n,'inherited':confirmed/n}
            cells.append({'focal':p,'partner':q,'denominator':n,'candidate':cand,'inherited':confirmed,'unresolved_candidate_runs':cand-confirmed,'benefit':None})
        model={}
        for endpoint in ('candidate','inherited'):
            matrix=np.array([[values[p,q][endpoint] for q in ids] for p in ids]);grand=float(matrix.mean())
            rows=matrix.mean(1);cols=matrix.mean(0);residual=matrix-rows[:,None]-cols[None,:]+grand
            interactions=[]
            for p1,p2 in itertools.combinations(ids,2):
                for q1,q2 in itertools.combinations(ids,2):
                    d1=values[p1,q1][endpoint]-values[p2,q1][endpoint];d2=values[p1,q2][endpoint]-values[p2,q2][endpoint]
                    interactions.append({'focals':[p1,p2],'partners':[q1,q2],'focal_contrasts':[d1,d2],'difference_of_differences':d1-d2,'strict_rank_reversal':d1*d2<0})
            model[endpoint]={'grand_mean':grand,'focal_marginal_means':dict(zip(ids,rows.tolist())),'partner_marginal_means':dict(zip(ids,cols.tolist())),
                'pair_residual_from_additive_model':residual.tolist(),'interaction_contrasts':interactions}
        splits[split]={'cells':cells,'model':model,'total':len(rs),'candidate_runs':sum(bool(r['candidates']) for r in rs),'confirmed_inherited_runs':sum(r['run_id'] in inherited for r in rs),
            'contact_runs':sum(r['contact_t'] is not None for r in rs),'contact_range':[min(r['contact_t'] for r in rs if r['contact_t'] is not None),max(r['contact_t'] for r in rs if r['contact_t'] is not None)] if any(r['contact_t'] is not None for r in rs) else None}
    transfer=[]
    for ep in ('candidate','inherited'):
        a=splits['main']['model'][ep]['interaction_contrasts'];b=splits['heldout']['model'][ep]['interaction_contrasts']
        for main,held in zip(a,b):
            transfer.append({'endpoint':ep,'focals':main['focals'],'partners':main['partners'],'main_reversal':main['strict_rank_reversal'],'heldout_reversal':held['strict_rank_reversal'],
                'same_rank_reversal':bool(main['strict_rank_reversal'] and held['strict_rank_reversal'] and all(x*y>0 for x,y in zip(main['focal_contrasts'],held['focal_contrasts']))),
                'main_interaction':main['difference_of_differences'],'heldout_interaction':held['difference_of_differences']})
    controls={}
    for treatment in ('separated','alone'):
        group=[r for r in records if r['treatment']==treatment]
        controls[treatment]={'total':len(group),'contact':sum(r['contact_t'] is not None for r in group),'candidate':sum(bool(r['candidates']) for r in group),'inherited':sum(r['run_id'] in inherited for r in group)}
    outcomes=[o for i in inherit['items'] for o in i['outcomes']]
    counts={'run_identity_candidates':len(inherit['items']),'isolation_roots':len(outcomes),'generation_simulations':sum(o['generation_simulations'] for o in outcomes),
        'confirmed_roots':sum(o['status']=='confirmed' for o in outcomes),'unextractable_candidate_identities':sum(not i['outcomes'] for i in inherit['items']),
        'search_truncations':[t for o in outcomes for t in o['truncations']],
        'offspring_collection_cap_nodes':sum(len(n['outcome']['children'])>=m['config']['offspring_per_generation'] for o in outcomes for n in o['nodes'])}
    near=[r for r in records if r['treatment']=='near'];far={r['run_id'].replace('separated-','near-',1):r for r in records if r['treatment']=='separated'}
    paired={'candidate_near_minus_separated':sum(int(bool(r['candidates']))-int(bool(far[r['run_id']]['candidates'])) for r in near)/len(near),
        'inherited_near_minus_separated':sum(int(r['run_id'] in inherited)-int(far[r['run_id']]['run_id'] in inherited) for r in near)/len(near)}
    report={'experiment_id':m['experiment_id'],'ids':ids,'completed_runs':len(records),'splits':splits,'controls':controls,'inheritance':counts,'heldout_transfer':transfer,'paired':paired,
        'benefit_status':'pending; beneficial-heritable yield unknown','boundary_touched_runs':sum(r['boundary_first_t'] is not None for r in records),
        'uncertainty':'finite-panel descriptive contrasts; deterministic states are not population replicates'}
    write_json(OUT/'analysis.json',report)
    lines=['# Fresh crossed encounter atlas: EXP-atlas-002','',f'{len(records)} completed distinct frozen starting states; all states retained. Three naturally generated, separately verified channel identities.','',
        'Native candidate words differ from both inputs. Inherited endpoints require two consecutive stable composite transmissions through the bounded serial-isolation search. Benefits remain pending; zero confirmed inheritance is a measured search result, not proof that every fate is nonheritable.','',
        '| Split | Focal × partner | Candidate / configurations | Inherited / configurations |','|---|---|---:|---:|']
    for split,s in splits.items():
        for c in s['cells']:lines.append(f'| {split} | {c["focal"]} × {c["partner"]} | {c["candidate"]}/{c["denominator"]} | {c["inherited"]}/{c["denominator"]} |')
    lines+=['',f'Controls: {controls}.',f'Paired contrasts: {paired}.',f'Search: {len(outcomes)} roots, {counts["generation_simulations"]} generation simulations, {counts["confirmed_roots"]} confirmed roots; {counts["unextractable_candidate_identities"]} identities lacked an extractable phase.',
        f'{len(counts["search_truncations"])} depth/size/simulation truncations; {counts["offspring_collection_cap_nodes"]} nodes reached the three-offspring collection cap. Unsearched branches remain unresolved.','',
        '## Interaction and held-out configurations','',
        '| Endpoint | Focal contrast | Partner columns | Main difference of differences | Held-out difference of differences | Main reversal persists |','|---|---|---|---:|---:|---|']
    for t in transfer:lines.append(f'| {t["endpoint"]} | {" − ".join(t["focals"])} | {"; ".join(t["partners"])} | {t["main_interaction"]:+.3f} | {t["heldout_interaction"]:+.3f} | {t["same_rank_reversal"]} |')
    lines+=['','All nine contrasts are descriptive, without selected-significance claims. Additive focal/partner means and pair residuals are in analysis.json. Pair novelty and causal provenance do not identify focal genetic parentage. Native cores do not alone demonstrate viable population size. H1/H3 remain untested.']
    (OUT/'analysis.md').write_text('\n'.join(lines)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ('splits','heldout_transfer','inheritance')},indent=2))

if __name__=='__main__':main()
