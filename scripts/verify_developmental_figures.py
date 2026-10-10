"""Check recorded pixels, provenance, and preservation of earlier figure exports."""
import json
import subprocess
import time
import numpy as np
from evoloop.engine import ROOT
from scripts.figures import FIG, STYLE, THEMES, theme, quantitative_cmap, annotation_color
from scripts.verify_coverage_figures import require, read, sha, array, svg_pixels, png_pixels

BASELINE = '1bae4a102737d72b725974ffdaa6535ec0d4907d'
OUT = ROOT / 'data/developmental-v1'

def main():
    start = time.perf_counter()
    audit = read(OUT / 'integrity.json')
    require(audit['status'] == 'passed' and audit['mismatches'] == 0, 'scientific audit first')
    require(THEMES == (True,), 'dark exports only')
    require(quantitative_cmap() is not None and annotation_color(STYLE['ink']) in (STYLE['ink'], STYLE['text']), 'shared style roles')
    before = json.loads(subprocess.check_output(['git', 'show', f'{BASELINE}:figures/manifest.json'], cwd=ROOT))
    current = read(FIG / 'manifest.json')
    prior = {r['file']: r for r in before['artifacts']}
    now = {r['file']: r for r in current['artifacts']}
    require(len(prior) == 120 and len(now) == len(current['artifacts']), 'artifact denominators')
    require({k:v for k,v in before.items() if k != 'artifacts'} == {k:v for k,v in current.items() if k != 'artifacts'}, 'shared metadata preserved')
    require(all(now.get(k) == v and sha(FIG/k) == v['sha256'] for k,v in prior.items()), 'all120 prior artifacts preserved')
    names = {f'developmental1-{kind}-dark.{ext}' for kind in ('resolution','paired-states') for ext in ('svg','pdf','png')}
    require(set(now)-set(prior) == names, 'exactly six new artifacts')
    require(not list(FIG.glob('developmental1-*-light.*')), 'no obsolete light exports')
    for name in names:
        r = now[name]
        require(r['sha256'] == sha(FIG/name) and r['style_sha256'] == sha(ROOT/'configs/style.json'), 'artifact and style bytes')
        require(r['experiments'] == ['EXP-developmental-calibration-001'] and r['command'] == 'OPENBLAS_NUM_THREADS=1 python -m scripts.figures_developmental', 'experiment and regeneration command')
        require(all(sha(ROOT/p) == value for p,value in r['source_sha256'].items()), 'source bytes')
    m = read(OUT/'manifest.json')
    panels = []
    for run in m['runs']:
        if run['state'] != 'V01' or run['condition']['id'] != 'calibration-0':
            continue
        for t in (0,800,1600):
            p = OUT/'worlds'/run['run_id']/f'grid-{t}.npz'
            panels.append({'array':array(p,'grid'),'file':str(p.relative_to(ROOT)),'key':'grid'})
    require(len(panels) == 6, 'first-declared six complete native panels')
    palette = np.array([tuple(bytes.fromhex(c[1:])) for c in STYLE['cell_states']],dtype=np.uint8)
    centers, geometry, viewbox = svg_pixels(FIG/'developmental1-paired-states-dark.svg',panels,palette)
    png = png_pixels(FIG/'developmental1-paired-states-dark.png',panels,geometry,viewbox,palette)
    report = {'status':'passed','mismatches':0,'experiment_id':m['experiment_id'],
        'baseline_commit':BASELINE,'prior_artifacts_preserved':120,'new_artifacts_verified':6,
        'cell_pixels':centers,'png_pixels':png,'figure_manifest_sha256':sha(FIG/'manifest.json'),
        'validator_sha256':sha(ROOT/'scripts/verify_developmental_figures.py'),'seconds':time.perf_counter()-start,
        'scope':'all recorded SVG cell centers, literal palette and square/shared geometry; PNG center alignment with no in-grid annotations; provenance; visual review separate'}
    (OUT/'figure-integrity.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Verified120 prior and6 new artifacts;221184 recorded cell centers',flush=True)

if __name__ == '__main__':main()
