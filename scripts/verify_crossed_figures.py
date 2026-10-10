"""Independent recorded-pixel, label and provenance checks for crossed exports."""
import json
import subprocess
import time
import xml.etree.ElementTree as ET

import numpy as np

from evoloop.engine import ROOT
from scripts.figures import FIG, STYLE, THEMES, theme, quantitative_cmap, annotation_color
from scripts.verify_coverage_figures import (NS, array, bitmap, png_pixels, read,
                                            require, sha, svg_pixels)

BASELINE = '169f9b56b9eb328d2b285f28e4e3b5df00b01f3b'
OUT = ROOT / 'data/crossed-v1'


def main():
    start = time.perf_counter()
    scientific = read(OUT / 'integrity.json')
    require(scientific['status'] == 'passed' and scientific['mismatches'] == 0, 'independent scientific audit first')
    require(all(sha(OUT / name) == scientific['evidence_sha256'][name]
                for name in ('analysis.json', 'results.json')), 'published input bytes match passed scientific audit')
    require(THEMES == (True,), 'dark canonical exports only')
    require(annotation_color(STYLE['ink']) == STYLE['text'], 'configured annotation roles')
    prior = json.loads(subprocess.check_output(['git', 'show', f'{BASELINE}:figures/manifest.json'], cwd=ROOT))
    now = read(FIG / 'manifest.json')
    before = {a['file']: a for a in prior['artifacts']}
    after = {a['file']: a for a in now['artifacts']}
    require(len(before) == 126 and len(after) == len(now['artifacts']), 'prior and current artifact denominators')
    require({k: v for k, v in prior.items() if k != 'artifacts'} ==
            {k: v for k, v in now.items() if k != 'artifacts'}, 'shared figure metadata unchanged')
    require(all(after.get(k) == v and sha(FIG / k) == v['sha256'] for k, v in before.items()), 'all126 prior exports preserved')
    expected = {f'crossed1-{kind}-dark.{ext}' for kind in ('retention', 'interactions', 'disturbed-interactions', 'paired-states')
                for ext in ('svg', 'pdf', 'png')}
    require(set(after) - set(before) == expected, 'exactly twelve new artifacts')
    require(not list(FIG.glob('crossed1-*-light.*')), 'no obsolete light exports')
    for name in expected:
        record = after[name]
        require(record['sha256'] == sha(FIG / name) and record['style_sha256'] == sha(ROOT / 'configs/style.json'), 'artifact/style bytes')
        require(record['experiments'] == ['EXP-age-geometry-cross-001'] and
                record['command'] == 'OPENBLAS_NUM_THREADS=1 python -m scripts.figures_crossed', 'experiment/regeneration provenance')
        require(all(sha(ROOT / path) == h for path, h in record['source_sha256'].items()), 'exact source inventory')
        if 'paired-states' in name:
            require(record['raw_panel_selection'] == {'state': 'V01', 'age': 0, 'geometry': 'A',
                'treatments': ['D', 'U'], 'times': [0, 800, 1600],
                'rule': 'first declared crossed pair; previously observed protocol009 preparation, not selected on response'},
                'declared response-independent raw selection and shown times')
    manifest = read(OUT / 'manifest.json')
    panels = []
    for spec in manifest['runs']:
        if spec['state'] == 'V01' and spec['age'] == 0 and spec['geometry'] == 'A':
            proof = read(OUT / 'integrity-proofs' / 'world' / f'{spec["run_id"]}.json')
            require(proof['status'] == 'passed' and proof['mismatches'] == 0, 'raw native pair independently audited')
            for t in (0, 800, 1600):
                path = OUT / 'worlds' / spec['run_id'] / f'grid-{t}.npz'
                require(sha(path) == proof['provenance']['physical_source_sha256'][str(path.relative_to(ROOT))],
                        'raw native bytes match independent replay proof')
                panels.append({'array': array(path, 'grid'), 'file': str(path.relative_to(ROOT)), 'key': 'grid'})
    require(len(panels) == 6, 'first declared paired native panels')
    palette = np.array([tuple(bytes.fromhex(c[1:])) for c in STYLE['cell_states']], dtype=np.uint8)
    centers, geometry, viewbox = svg_pixels(FIG / 'crossed1-paired-states-dark.svg', panels, palette)
    png = png_pixels(FIG / 'crossed1-paired-states-dark.png', panels, geometry, viewbox, palette)
    analysis = read(OUT / 'analysis.json')
    cfg = manifest['config']
    lookup = {(c['state'], c['geometry'], c['age']): c['retention'] for c in analysis['cells']}
    bounds = [[lookup[state, g['id'], age] for g in cfg['geometries'] for age in cfg['ages']] for state in cfg['states']]
    def number(record):
        return record['numerator'] / record['denominator'] if record is not None else np.nan
    matrix = np.array([[number(b['lower']) for b in row] for row in bounds])
    maximum = max(1, float(np.nanmax(matrix))) if np.any(np.isfinite(matrix)) else 1
    cmap = quantitative_cmap().copy()
    cmap.set_bad(STYLE['status']['missing'])
    # Matplotlib quantizes floating RGB channels by truncation in raster export.
    colors = (cmap(matrix / maximum)[:, :, :3] * 255).astype(np.uint8)
    tree = ET.parse(FIG / 'crossed1-retention-dark.svg').getroot()
    raster = bitmap(tree.findall('.//svg:image', NS)[0])
    ys = ((np.arange(5) + .5) * raster.shape[0] / 5).astype(int)
    xs = ((np.arange(16) + .5) * raster.shape[1] / 16).astype(int)
    require(np.array_equal(raster[np.ix_(ys, xs)], colors), 'all80 heatmap lower endpoints use declared shared scale')
    text = [''.join(element.itertext()) for element in tree.findall('.//svg:text', NS)]
    expected_labels = []
    for row in bounds:
        for b in row:
            low = f'{number(b["lower"]):.2f}' if b['lower'] is not None else '−∞'
            high = f'{number(b["upper"]):.2f}' if b['upper'] is not None else '∞'
            expected_labels.append('missing' if b['status'].startswith('undefined') else f'[{low}, {high}]')
    for label in set(expected_labels):
        require(text.count(label) == expected_labels.count(label), f'exact displayed interval-label multiplicity: {label}')
    report = {'status': 'passed', 'mismatches': 0, 'experiment_id': manifest['experiment_id'],
        'baseline_commit': BASELINE, 'prior_artifacts_preserved': 126, 'new_artifacts_verified': 12,
        'retention_cells_verified': 80, 'retention_interval_labels_verified': 80,
        'cell_pixels': centers, 'png_pixels': png,
        'figure_manifest_sha256': sha(FIG / 'manifest.json'),
        'validator_sha256': sha(ROOT / 'scripts/verify_crossed_figures.py'),
        'seconds': time.perf_counter() - start,
        'scope': 'all recorded SVG cells and literal palette; PNG geometry; retention lower colors and interval labels; source hashes and preservation; visual review separate'}
    (OUT / 'figure-integrity.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Verified126 prior and12 new artifacts;221184 native cell centers and80 retention cells', flush=True)


if __name__ == '__main__':
    main()
