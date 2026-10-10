"""Recorded-pixel and provenance checks for protocol 010 publication figures.

Run sequentially after rendering, never during acquisition or native replay:
    OPENBLAS_NUM_THREADS=1 .venv/bin/python -m scripts.verify_coverage_figures
SVG embedded rasters are checked at every recorded cell; PNG panel coordinates
are checked independently with declared overlay regions excluded. This performs
no simulation and does not modify frozen evidence or prior figure artifacts.
"""
import base64
import hashlib
import io
import json
import re
import subprocess
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
from PIL import Image

from evoloop.engine import ROOT
from scripts.figures import FIG, STYLE, THEMES, theme, quantitative_cmap, annotation_color

BASELINE = '3aa73b85892e3d06115e738978ccef1bc54bf53d'
OUT = ROOT / 'data/coverage-v1'
COMMAND = 'OPENBLAS_NUM_THREADS=1 .venv/bin/python -m scripts.verify_coverage_figures'
NS = {'svg': 'http://www.w3.org/2000/svg'}
XLINK = '{http://www.w3.org/1999/xlink}href'


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def array(path, key):
    with np.load(path, allow_pickle=False) as saved:
        return saved[key].copy()


def panels(recovery):
    """Reconstruct illustration selection from raw completed recovery records."""
    native = []
    for label in ('valid_unregistered', 'unknown_identity'):
        observation = next(o for o in recovery['observations'] if o['source_class'] == label)
        for delayed in observation['delays']:
            path = OUT / 'worlds' / observation['run_id'] / f'grid-{delayed["t"]}.npz'
            native.append({'array': array(path, 'grid'), 'file': str(path.relative_to(ROOT)),
                           'key': 'grid', 'example': observation['observation_id'],
                           'core': observation['core'], 't': delayed['t']})
    inheritance = []
    examples = []
    identities = set()
    for observation in recovery['observations']:
        if observation['source_class'] == 'scored':
            continue
        delayed = observation['delays'][0]
        identity = delayed['confirmed_identity']
        if not delayed['transmission_confirmed'] or identity in identities:
            continue
        require(observation['source_identity'] is None,
                'inheritance caption claims unknown source genotype; selected source must agree')
        require(delayed['confirmed_identity_in_registry'] is True,
                'inheritance title claims registered descendants; selected confirmation must agree')
        identities.add(identity)
        examples.append(observation['observation_id'])
        path = OUT / delayed['snapshot_file']
        inheritance.append({'array': array(path, 'snapshot'), 'file': str(path.relative_to(ROOT)),
                            'key': 'snapshot', 'example': observation['observation_id']})
        branch = delayed['outcome']['confirmation']['path']
        for depth, child in enumerate(branch):
            node = next(n for n in delayed['outcome']['nodes'] if n['path'] == branch[:depth])
            path = OUT / delayed['search_dir'] / f'node-{node["node"]:02d}.npz'
            key = f'child{child}'
            inheritance.append({'array': array(path, key), 'file': str(path.relative_to(ROOT)),
                                'key': key, 'example': observation['observation_id']})
    require(len(native) == 6 and len(inheritance) == 12, 'expected six native and twelve inheritance panels')
    return native, inheritance, examples


def bitmap(element):
    encoded = element.attrib[XLINK]
    require(encoded.startswith('data:image/png;base64,'), 'embedded raster must be lossless PNG')
    pixels = np.asarray(Image.open(io.BytesIO(base64.b64decode(encoded.split(',', 1)[1]))).convert('RGBA'))
    require(np.all(pixels[:, :, 3] == 255), 'cell raster must be fully opaque')
    transform = element.attrib.get('transform', '')
    require(re.fullmatch(r'scale\(1 -1\) translate\(0 -[\d.]+\)', transform) is not None,
            'unrecognized cell-image geometry transform')
    # SVG uses a vertical coordinate flip; its encoded image has bottom-first rows.
    return np.flipud(pixels[:, :, :3])


def svg_pixels(path, expected, palette):
    tree = ET.parse(path).getroot()
    images = tree.findall('.//svg:image', NS)
    require(len(images) == len(expected), f'{path.name}: complete embedded image inventory')
    viewbox = [float(v) for v in tree.attrib['viewBox'].split()]
    require(viewbox[:2] == [0, 0], 'SVG viewbox origin')
    reports = []
    geometry = []
    for index, (element, panel) in enumerate(zip(images, expected)):
        grid = panel['array']
        require(grid.dtype == np.uint8 and grid.ndim == 2 and grid.max() <= 8, 'literal recorded cell array')
        raster = bitmap(element)
        h, w = grid.shape
        ys = np.minimum(((np.arange(h) + .5) * raster.shape[0] / h).astype(int), raster.shape[0] - 1)
        xs = np.minimum(((np.arange(w) + .5) * raster.shape[1] / w).astype(int), raster.shape[1] - 1)
        centers = raster[np.ix_(ys, xs)]
        require(np.array_equal(centers, palette[grid]), f'{path.name}/panel{index}: recorded-cell centers differ')
        colors = np.unique(raster.reshape(-1, 3), axis=0)
        require(all(any(np.array_equal(color, state) for state in palette) for color in colors),
                f'{path.name}/panel{index}: interpolated or undeclared cell color')
        width, height = float(element.attrib['width']), float(element.attrib['height'])
        cell_x, cell_y = width / w, height / h
        tolerance = .4 / min(h, w) + 1e-6  # At most one 180-dpi pixel of edge rounding.
        require(abs(cell_x - cell_y) <= tolerance, f'{path.name}/panel{index}: non-square cells')
        geometry.append({'x': float(element.attrib['x']), 'y': -float(element.attrib['y']),
                         'width': width, 'height': height, 'cell_x': cell_x, 'cell_y': cell_y,
                         'tolerance': tolerance})
        reports.append({'panel': index, 'recorded_file': panel['file'], 'array_key': panel['key'],
                        'shape': [h, w], 'cells_verified': h * w,
                        'occupied_cells_verified': int(np.count_nonzero(grid)),
                        'cell_scale_points': [cell_x, cell_y]})
    median = float(np.median([g['cell_x'] for g in geometry]))
    require(all(abs(g['cell_x'] - median) <= g['tolerance'] for g in geometry),
            f'{path.name}: shared cell scale differs between panels')
    return reports, geometry, viewbox


def png_pixels(path, expected, geometry, viewbox, palette):
    raster = np.asarray(Image.open(path).convert('RGB'))
    ink = np.array(tuple(bytes.fromhex(STYLE['ink'][1:])), dtype=np.uint8)
    require(np.array_equal(raster[0, 0], ink), f'{path.name}: dark navy export background')
    sx = raster.shape[1] / viewbox[2]
    sy = raster.shape[0] / viewbox[3]
    reports = []
    for index, (panel, box) in enumerate(zip(expected, geometry)):
        grid = panel['array']
        h, w = grid.shape
        expected_rgb = palette[grid]
        mask = np.ones(grid.shape, bool)
        if 'core' in panel:
            # The declared fixed-target outline and labeled ten-cell scale are
            # annotations; embedded SVG pixels above still verify every cell.
            y, x, ch, cw = panel['core']
            rows, cols = np.indices(grid.shape)
            yy, xx = (rows - y) % h, (cols - x) % w
            outline = ((yy <= ch + 1) & ((xx <= 1) | (xx >= cw - 1) & (xx <= cw + 1))) | \
                      ((xx <= cw + 1) & ((yy <= 1) | (yy >= ch - 1) & (yy <= ch + 1)))
            mask[outline] = False
            mask[169:186, 4:35] = False
        sample_y = (box['y'] + (np.arange(h) + .5) * box['height'] / h) * sy
        sample_x = (box['x'] + (np.arange(w) + .5) * box['width'] / w) * sx
        best = None
        # Different SVG/PNG font metrics can shift tight bounding boxes slightly.
        # One global translation per panel is allowed; the recorded cell scale
        # and orientation remain fixed by the independently checked SVG geometry.
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                ys = np.rint(sample_y + dy).astype(int)
                xs = np.rint(sample_x + dx).astype(int)
                if ys.min() < 0 or xs.min() < 0 or ys.max() >= raster.shape[0] or xs.max() >= raster.shape[1]:
                    continue
                match = np.all(raster[np.ix_(ys, xs)] == expected_rgb, axis=2)
                occupied = mask & (grid != 0)
                occupied_fraction = float(match[occupied].mean()) if np.any(occupied) else 1.0
                fraction = float(match[mask].mean())
                score = (occupied_fraction, fraction)
                if best is None or score > best[0]:
                    best = (score, dx, dy, int(mask.sum()), int(occupied.sum()))
        require(best is not None and best[0][0] >= .98 and best[0][1] >= .99,
                f'{path.name}/panel{index}: PNG recorded-pixel alignment differs: {best}')
        reports.append({'panel': index, 'matching_occupied_fraction': best[0][0],
                        'matching_all_fraction': best[0][1], 'alignment_pixels': [best[1], best[2]],
                        'tested_cell_centers': best[3], 'tested_occupied_cell_centers': best[4]})
    return reports


def main():
    started = time.perf_counter()
    integrity = read(OUT / 'integrity.json')
    require(integrity['status'] == 'passed' and integrity['mismatches'] == 0, 'scientific audit must pass before publication validation')
    require(THEMES == (True,), 'coverage publication uses dark exports only')
    # Import the shared quantitative and annotation roles even though this check
    # only samples literal-state pixels; no validator-local visualization palette.
    require(quantitative_cmap() is not None and annotation_color(STYLE['ink']) in (STYLE['ink'], STYLE['text']),
            'shared style roles')
    palette = np.array([tuple(bytes.fromhex(c[1:])) for c in STYLE['cell_states']], dtype=np.uint8)
    baseline = json.loads(subprocess.check_output(['git', 'show', f'{BASELINE}:figures/manifest.json'], cwd=ROOT))
    current = read(FIG / 'manifest.json')
    require({k: v for k, v in current.items() if k != 'artifacts'} ==
            {k: v for k, v in baseline.items() if k != 'artifacts'}, 'prior manifest style/font metadata changed')
    require(len(baseline['artifacts']) == 108, 'prior artifact denominator changed')
    prior_by_name = {r['file']: r for r in baseline['artifacts']}
    now_by_name = {r['file']: r for r in current['artifacts']}
    require(len(now_by_name) == len(current['artifacts']), 'duplicate manifest entries')
    require(all(now_by_name.get(name) == record for name, record in prior_by_name.items()), 'prior 108 manifest entries changed')
    require(all(sha(FIG / name) == record['sha256'] for name, record in prior_by_name.items()), 'prior 108 artifact bytes changed')
    names = {f'coverage1-{kind}-dark.{ext}' for kind in ('recovery', 'state-unions', 'native-targets', 'inheritance') for ext in ('svg', 'pdf', 'png')}
    require(set(now_by_name) - set(prior_by_name) == names, 'exactly twelve new coverage artifacts required')
    require(current['style_sha256'] == sha(ROOT / 'configs/style.json'), 'manifest shared style hash')
    require(not list(FIG.glob('coverage1-*-light.*')), 'obsolete light coverage exports')
    for name in sorted(names):
        record = now_by_name[name]
        require(record['sha256'] == sha(FIG / name) and record['style_sha256'] == current['style_sha256'], f'{name}: artifact/style bytes')
        require(record['experiments'] == ['EXP-score-coverage-001'] and record['command'] == 'OPENBLAS_NUM_THREADS=1 python -m scripts.figures_coverage', f'{name}: experiment/command provenance')
        require(all(sha(ROOT / p) == value for p, value in record['source_sha256'].items()), f'{name}: recorded source bytes')
    recovery = read(OUT / 'recovery.json')
    native, inheritance, inheritance_examples = panels(recovery)
    require(now_by_name['coverage1-native-targets-dark.svg']['examples'] == list(dict.fromkeys(p['example'] for p in native)), 'native illustration selection')
    require(now_by_name['coverage1-inheritance-dark.svg']['examples'] == inheritance_examples, 'inheritance illustration selection')
    results = {}
    for kind, expected in (('native-targets', native), ('inheritance', inheritance)):
        svg = FIG / f'coverage1-{kind}-dark.svg'
        png = FIG / f'coverage1-{kind}-dark.png'
        cell_reports, geometry, viewbox = svg_pixels(svg, expected, palette)
        results[kind] = {'cell_pixels': cell_reports,
                         'png_pixels': png_pixels(png, expected, geometry, viewbox, palette)}
    report = {'status': 'passed', 'mismatches': 0, 'experiment_id': 'EXP-score-coverage-001',
        'baseline_commit': BASELINE, 'prior_artifacts_preserved': 108, 'new_artifacts_verified': 12,
        'native_panels_verified': len(native), 'inheritance_panels_verified': len(inheritance),
        'commands': {'render': 'OPENBLAS_NUM_THREADS=1 .venv/bin/python -m scripts.figures_coverage', 'verify': COMMAND},
        'validator_sha256': sha(Path(__file__)), 'figure_manifest_sha256': sha(FIG / 'manifest.json'),
        'results': results, 'seconds': time.perf_counter() - started,
        'scope': 'recorded SVG raster cell centers and palettes, square/shared geometry, PNG cell-center alignment excluding declared native annotations, provenance and prior artifact preservation; separate visual review remains required'}
    target = OUT / 'figure-integrity.json'
    temp = target.with_suffix('.json.tmp')
    temp.write_text(json.dumps(report, indent=2) + '\n')
    temp.replace(target)
    print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    main()
