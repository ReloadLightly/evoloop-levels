"""Recorded crossed source envelopes and interactions in Chromatic Fields."""
import argparse
import json

import numpy as np

from evoloop.engine import ROOT
from evoloop.crossed import value
from scripts.coverage_protocol import sha
from scripts.figures import (FIG, STYLE, THEMES, CMAP, NORM, theme, save, legend,
                             quantitative_cmap, annotation_color)
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

OUT = ROOT / 'data/crossed-v1'


def read(path):
    return json.loads(path.read_text())


def text_interval(row):
    if row['status'].startswith('undefined'):
        return 'missing'
    low = f'{float(value(row["lower"])):.2f}' if row['lower'] is not None else '−∞'
    high = f'{float(value(row["upper"])):.2f}' if row['upper'] is not None else '∞'
    return f'[{low}, {high}]'


def export(fig, name, artifacts, paths=()):
    sources = [OUT / n for n in ('manifest.json', 'readiness.json', 'analysis.json', 'integrity.json')]
    sources += [ROOT / p for p in ('scripts/figures_crossed.py', 'scripts/figures.py', 'configs/style.json')]
    sources += list(paths)
    extra = {}
    if name == 'paired-states':
        extra['raw_panel_selection'] = {'state': 'V01', 'age': 0, 'geometry': 'A',
            'treatments': ['D', 'U'], 'times': [0, 800, 1600],
            'rule': 'first declared crossed pair; previously observed protocol009 preparation, not selected on response'}
    save(fig, 'crossed1-' + name, True, artifacts, ['EXP-age-geometry-cross-001'], {
        'command': 'OPENBLAS_NUM_THREADS=1 python -m scripts.figures_crossed',
        'source_sha256': {str(p.relative_to(ROOT)): sha(p) for p in sorted(set(sources))},
        'status': 'completed finite crossed assay; operational source envelopes, not total viable population or confidence intervals', **extra})


def retention(analysis, artifacts):
    cfg = read(OUT / 'manifest.json')['config']
    columns = [(g, age) for g in cfg['geometries'] for age in cfg['ages']]
    lookup = {(c['state'], c['geometry'], c['age']): c for c in analysis['cells']}
    rows = [[lookup[state, g['id'], age]['retention'] for g, age in columns] for state in cfg['states']]
    matrix = np.array([[float(value(c['lower'])) if c['lower'] is not None else np.nan for c in row] for row in rows])
    for dark in THEMES:
        theme(dark)
        fig, ax = plt.subplots(figsize=(18, 7.8))
        cmap = quantitative_cmap().copy()
        cmap.set_bad(STYLE['status']['missing'])
        maximum = max(1, float(np.nanmax(matrix))) if np.any(np.isfinite(matrix)) else 1
        im = ax.imshow(matrix, vmin=0, vmax=maximum, cmap=cmap, aspect='auto', interpolation='nearest')
        for i, row in enumerate(rows):
            for j, bounds in enumerate(row):
                fill = cmap(matrix[i, j] / maximum) if np.isfinite(matrix[i, j]) else STYLE['status']['missing']
                ax.text(j, i, text_interval(bounds), ha='center', va='center', fontsize=8.5,
                        color=annotation_color(fill))
                if bounds['status'] != 'bounded':
                    ax.add_patch(Rectangle((j - .5, i - .5), 1, 1, fill=False,
                                          hatch='///', edgecolor=STYLE['axis']))
        ax.set_xticks(range(len(columns)), [str(age) for g, age in columns])
        ax.set_yticks(range(len(cfg['states'])), cfg['states'])
        for i, g in enumerate(cfg['geometries']):
            ax.text((i * 4 + 1.5) / 16, 1.045, f'{g["id"]} · {g["split"]}', transform=ax.transAxes,
                    ha='center', fontsize=11)
            if i:
                ax.axvline(i * 4 - .5, color=STYLE['text'], linewidth=1)
        ax.set_xlabel('Elapsed preparation age / updates; all four ages in each layout')
        ax.set_ylabel('Complete input representative')
        fig.colorbar(im, ax=ax, fraction=.025, pad=.025, label='Lower retention endpoint Q_D / C_U')
        fig.suptitle('Crossed recovery retention envelopes · EXP-age-geometry-cross-001', fontsize=16)
        fig.subplots_adjust(left=.07, right=.91, bottom=.26, top=.83)
        fig.text(.5, .085, '[Q_D/C_U, C_D/Q_U] from five census times 0/400/800/1200/1600; labels rounded only for display.\n'
            'All 80 state × age × layout conditions shown. Q confirms isolated source recovery; C includes every detected core; unresolved sources remain in C.\n'
            'Missing controls and infinite endpoints use labels and hatching. These envelopes concern detected source bodies; they are not viability bounds or confidence intervals.\n'
            'D removes one complete clone; U is undisturbed. A/B develop, E/F reserve distinct starts; earlier A-age0/B-age100 observations are repeated checks.',
            ha='center', fontsize=9)
        export(fig, 'retention', artifacts)


def interactions(analysis, artifacts, measure='retention'):
    cfg = read(OUT / 'manifest.json')['config']
    selected = [c for c in analysis['contrasts'] if c['kind'] == 'interaction']
    for dark in THEMES:
        theme(dark)
        fig, axes = plt.subplots(2, 2, figsize=(12, 9))
        finite = [float(value(c[measure][end])) for c in selected for end in ('lower', 'upper')
                  if c[measure][end] is not None]
        span = max([.1] + [abs(v) for v in finite]) * 1.2
        for i, split in enumerate(('development', 'confirmation')):
            for j, ages in enumerate(cfg['contrasts']['age_pairs']):
                ax = axes[i, j]
                ax.axvline(0, color=STYLE['axis'], linestyle='--')
                for k, state in enumerate(cfg['states']):
                    row = next(c for c in selected if c['state'] == state and c['split'] == split and c['age_pair'] == ages)
                    bounds = row[measure]
                    if bounds['lower'] is not None and bounds['upper'] is not None:
                        low, high = (float(value(bounds[end])) for end in ('lower', 'upper'))
                        ax.plot([low, high], [k, k], color=STYLE['series']['primary'], linewidth=3)
                        ax.plot([low, high], [k, k], '|', color=STYLE['series']['tertiary'], markersize=10)
                    else:
                        ax.text(0, k, bounds['status'], ha='center', fontsize=8)
                geometries = cfg['contrasts']['geometry_pairs'][split]
                ax.set_yticks(range(len(cfg['states'])), cfg['states'])
                ax.invert_yaxis()
                ax.set_xlim(-span, span)
                ax.set_title(f'{split}: {geometries[1]}−{geometries[0]} · age {ages[1]}−{ages[0]}', fontsize=11)
                ax.set_xlabel('Difference of age differences in ' + ('retention' if measure == 'retention' else 'disturbed census mean'))
        label = 'Retention' if measure == 'retention' else 'Absolute disturbed count'
        fig.suptitle(label + ': age × spatial challenge · EXP-age-geometry-cross-001', fontsize=14)
        fig.subplots_adjust(left=.08, right=.97, bottom=.22, top=.88, hspace=.4, wspace=.22)
        fig.text(.5, .075, '(B_late−B_early)−(A_late−A_early), or (F_late−F_early)−(E_late−E_early); all 20 declared contrasts.\n'
            'Each interval subtraction uses [l₁−u₀, u₁−l₀]; bounds retain unresolved detected sources.\n'
            + ('Inputs: per-condition [Q_D/C_U, C_D/Q_U] retention envelopes.\n' if measure == 'retention' else
               'Inputs: [Σ Q_D/5, Σ C_D/5] over five censuses; units: detected source observations per census.\n') +
            'An interval excluding zero supports a signed contrast within these operational envelopes, not independent-population uncertainty.\n'
            'Each layout includes its removed-clone position; A/B and E/F are different spatial contrasts. Elapsed ages are not homologous phases.\n'
            'Five census times per world, 160 deterministic worlds; recovery/population comparisons do not establish H1, H3, evolvability or RSI.',
            ha='center', fontsize=9)
        export(fig, 'interactions' if measure == 'retention' else 'disturbed-interactions', artifacts)


def raw(analysis, artifacts):
    m = read(OUT / 'manifest.json')
    result_hashes = {r['run_id']: r['result_sha256'] for r in read(OUT / 'results.json')['worlds']}
    specs = [r for r in m['runs'] if r['state'] == 'V01' and r['age'] == 0 and r['geometry'] == 'A']
    paths = []
    for dark in THEMES:
        theme(dark)
        fig, axes = plt.subplots(2, 3, figsize=(12, 11))
        for i, spec in enumerate(specs):
            directory = OUT / 'worlds' / spec['run_id']
            report_path = directory / 'result.json'
            assert sha(report_path) == result_hashes[spec['run_id']]
            receipt = read(directory / 'receipt.json')
            proof_path = OUT / 'integrity-proofs' / 'world' / f'{spec["run_id"]}.json'
            proof = read(proof_path)
            assert proof['status'] == 'passed' and proof['mismatches'] == 0
            report = read(report_path)
            paths.extend([report_path, directory / 'receipt.json', proof_path])
            for j, t in enumerate((0, 800, 1600)):
                path = directory / f'grid-{t}.npz'
                assert sha(path) == receipt['artifact_sha256'][path.name]
                assert sha(path) == proof['provenance']['physical_source_sha256'][str(path.relative_to(ROOT))]
                paths.append(path)
                with np.load(path, allow_pickle=False) as saved:
                    grid = saved['grid']
                row = next(c for c in report['snapshot_counts'] if c['t'] == t)
                ax = axes[i, j]
                ax.imshow(grid, cmap=CMAP, norm=NORM, interpolation='nearest', extent=(-.5, 191.5, 191.5, -.5))
                ax.set_aspect('equal')
                for spine in ax.spines.values():
                    spine.set_position(('outward', 2))
                ax.set_xticks([0, 191])
                ax.set_yticks([0, 191])
                ax.set_title(f't={t}; Q={row["Q"]}, R={row["R"]}, C={row["C"]}', fontsize=10)
                if j == 0:
                    ax.set_ylabel(spec['run_id'], fontsize=9)
                ax.plot([.02, .02 + 10 / 192], [-.11, -.11], transform=ax.transAxes,
                        color=STYLE['text'], linewidth=2, clip_on=False)
                ax.text(.10, -.11, '10 cells', transform=ax.transAxes, va='center', fontsize=8)
        fig.suptitle('First declared crossed D/U pair · EXP-age-geometry-cross-001', fontsize=14)
        fig.subplots_adjust(left=.08, right=.98, bottom=.27, top=.90, hspace=.36)
        legend(fig)
        fig.text(.5, .13, 'V01, elapsed age 0, layout A; full 192×192 periodic grids and literal nine-state colors.\n'
            'D removes one complete clone: one third of occupied cells and of each occupied-state count; cores 3→2. U retains all three.\n'
            'This complete preparation was observed under protocol009; replay is a deterministic check, not a new confirmation.\n'
            'Q/R/C classify the source census through separate isolation assays; native ancestry and total viable population remain unresolved.',
            ha='center', fontsize=9)
        export(fig, 'paired-states', artifacts, paths)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--only', choices=('retention', 'interactions', 'disturbed-interactions', 'raw'))
    args = parser.parse_args()
    audit = read(OUT / 'integrity.json')
    assert audit['status'] == 'passed' and audit['mismatches'] == 0
    assert all(sha(OUT / name) == audit['evidence_sha256'][name]
               for name in ('analysis.json', 'results.json'))
    analysis = read(OUT / 'analysis.json')
    artifacts = []
    for name, render in (('retention', retention), ('interactions', interactions),
                         ('disturbed-interactions', lambda a, r: interactions(a, r, 'disturbed_mean')), ('raw', raw)):
        if args.only in (None, name):
            render(analysis, artifacts)
    path = FIG / 'manifest.json'
    manifest = read(path)
    names = {r['file'] for r in artifacts}
    manifest['artifacts'] = [r for r in manifest['artifacts'] if r['file'] not in names] + artifacts
    temporary = path.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(manifest, indent=2) + '\n')
    temporary.replace(path)
    print('Rendered', len(artifacts), 'crossed artifacts', flush=True)


if __name__ == '__main__':
    main()
