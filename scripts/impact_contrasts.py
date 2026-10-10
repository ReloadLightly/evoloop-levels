"""Transparent per-condition contrasts; no new outcome rule or winner selection."""
import hashlib
import json
from fractions import Fraction
from evoloop.engine import ROOT
from evoloop.microcolony import rational
from scripts.atlas import write_json

def main():
    out=ROOT/'data/impact-v1';path=out/'analysis.json';a=json.loads(path.read_text())
    rows={(r['state'],r['condition']):r for r in a['conditions']};contrasts=[]
    for pair in a['pairs']:
        pid=pair['candidate']
        for condition in ('development-0','development-1','confirmation-0','confirmation-1'):
            c=rows[pid,condition]
            for parent in pair['inputs']:
                p=rows[parent,condition]
                def retention(r):
                    v=r['retention'];return Fraction(v['numerator'],v['denominator']) if v else None
                cr,pr=retention(c),retention(p)
                contrasts.append({'candidate':pid,'input':parent,'condition':condition,
                    'retention_difference':rational(cr-pr) if cr is not None and pr is not None else None,
                    'D_mean_difference':rational(Fraction(c['D_sum']-p['D_sum'],81)),
                    'U_mean_difference':rational(Fraction(c['U_sum']-p['U_sum'],81)),
                    'disturbance_difference':rational(Fraction((c['D_sum']-c['U_sum'])-(p['D_sum']-p['U_sum']),81))})
    write_json(out/'contrasts.json',{'analysis_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'script_sha256':hashlib.sha256((ROOT/'scripts/impact_contrasts.py').read_bytes()).hexdigest(),
        'scope':'descriptive per-condition paired differences from frozen outcomes; no additional selection criterion',
        'contrasts':contrasts})
    lines=['# Per-condition paired contrasts','', '| Candidate | Input | Condition | R difference | D difference | U difference | (D-U) difference |', '|---|---|---|---|---|---|---|']
    for r in contrasts:
        fmt=lambda x:'undefined' if x is None else f'{x["numerator"]}/{x["denominator"]} ({x["value"]:.4f})'
        lines.append('| '+' | '.join([r['candidate'],r['input'],r['condition']]+[fmt(r[k]) for k in ['retention_difference','D_mean_difference','U_mean_difference','disturbance_difference']])+' |')
    (out/'contrasts.md').write_text('\n'.join(lines)+'\n')
    # Presentation-only repair: keep both candidates inside one readable table.
    summary=['# Impact-matched paired assay','',
        f'Calibration gate: {a["calibration"]["gate_passed"]}; scored recovery {a["calibration"]["scored_confirmed"]}/{a["calibration"]["scored_selected"]}; phase controls {a["calibration"]["baseline_confirmed"]}/{a["calibration"]["baseline_total"]}.','',
        '| Candidate | Panel | Retention (candidate; both inputs) | Absolute D means | Relative / absolute |','|---|---|---|---|---|']
    for pair in a['pairs']:
        for split,v in pair['panels'].items():
            rs='; '.join(f'{state}: {item["retention"]["value"]:.4f}' if item['retention'] else f'{state}: undefined' for state,item in v['states'].items())
            ds='; '.join(f'{state}: {item["D_mean"]:.4f}' for state,item in v['states'].items())
            summary.append(f'| {pair["candidate"]} | {split} | {rs} | {ds} | {v["relative_advantage"]} / {v["absolute_advantage"]} |')
    summary+=['']+[f'{pair["candidate"]}: {pair["status"]}.' for pair in a['pairs']]
    summary+=['',f'Conditional joint-confirmed originating encounters: {a["joint_confirmed_encounters"]}/54. Sixteen other candidate encounters retain unresolved inheritance. This is not zero true beneficial variation.','',
        'Registered-core counts are structural proxies; omitted valid/unknown cores have untested viability. Ages are elapsed updates, and constructed colonies are not native histories. The frozen analysis.json remains unchanged.','']
    (out/'analysis.md').write_text('\n'.join(summary))
    print('Saved16 exact per-condition contrasts and formatted frozen-outcome summary')

if __name__=='__main__':main()
