"""Exact finite-panel contrasts for the frozen crossed recovery assay."""
from fractions import Fraction

from evoloop.developmental import fraction, panel_bounds, retention_bounds


def value(record):
    return None if record is None else Fraction(record['numerator'], record['denominator'])


def interval(lower, upper, undefined=False):
    if undefined:
        return {'status': 'undefined', 'lower': None, 'upper': None}
    status = ('bounded' if lower is not None and upper is not None else
              'unbounded_both' if lower is None and upper is None else
              'unbounded_lower' if lower is None else 'unbounded_upper')
    return {'status': status, 'lower': fraction(lower), 'upper': fraction(upper)}


def subtract(later, earlier):
    """Interval subtraction; missing controls are distinct from infinite bounds."""
    if any(row['status'].startswith('undefined') for row in (later, earlier)):
        return interval(None, None, undefined=True)
    a, b = value(later['lower']), value(later['upper'])
    c, d = value(earlier['lower']), value(earlier['upper'])
    return interval(a - d if a is not None and d is not None else None,
                    b - c if b is not None and c is not None else None)


def population_mean(total, samples):
    return interval(Fraction(total['Q'], samples), Fraction(total['C'], samples))


def panel(cells):
    n = len(cells)
    assert n
    return {'retention': panel_bounds([(c['D'], c['U']) for c in cells]),
            'disturbed_mean': interval(
                sum((value(c['disturbed_mean']['lower']) for c in cells), Fraction()) / n,
                sum((value(c['disturbed_mean']['upper']) for c in cells), Fraction()) / n)}


def cell_totals(world):
    return {name: sum(row[name] for row in world['snapshot_counts']) for name in ('Q', 'R', 'C')}


def comparisons(cfg, worlds):
    """Keep all crossed cells, then average fractions and subtract intervals."""
    by_id = {w['run_id']: w for w in worlds}
    cells = []
    for state in cfg['states']:
        for age in cfg['ages']:
            for geometry in cfg['geometries']:
                pair = f'{state}-age{age}-{geometry["id"]}'
                twins = {t: by_id[f'{pair}-{t}'] for t in cfg['treatments']}
                totals = {t: cell_totals(w) for t, w in twins.items()}
                registry = {}
                for t, w in twins.items():
                    total = sum(s['scored_cores'] for s in w['samples'])
                    registry[t] = {'total': total, 'samples': len(w['samples']),
                                   'mean': fraction(Fraction(total, len(w['samples'])))}
                cells.append({'pair_id': pair, 'state': state, 'age': age, 'geometry': geometry['id'],
                    'split': geometry['split'], **totals, 'retention': retention_bounds(totals['D'], totals['U']),
                    'disturbed_mean': population_mean(totals['D'], len(cfg['source_times'])),
                    'registry_diagnostic': registry})
    lookup = {(c['state'], c['age'], c['geometry']): c for c in cells}
    panels = [{'state': state, 'split': split, 'conditions': 8,
               **panel([c for c in cells if c['state'] == state and c['split'] == split])}
              for state in cfg['states'] for split in ('development', 'confirmation')]
    contrasts = []
    measures = ('retention', 'disturbed_mean')
    for state in cfg['states']:
        for geometry in cfg['geometries']:
            for ages in cfg['contrasts']['age_pairs']:
                first, second = (lookup[state, age, geometry['id']] for age in ages)
                contrasts.append({'state': state, 'kind': 'age', 'geometry': geometry['id'],
                    'split': geometry['split'], 'age_pair': ages,
                    **{m: subtract(second[m], first[m]) for m in measures}})
        for split, geometries in cfg['contrasts']['geometry_pairs'].items():
            for age in cfg['ages']:
                first, second = (lookup[state, age, g] for g in geometries)
                contrasts.append({'state': state, 'kind': 'geometry', 'split': split,
                    'geometry_pair': geometries, 'age': age,
                    **{m: subtract(second[m], first[m]) for m in measures}})
            for ages in cfg['contrasts']['age_pairs']:
                a0, a1 = (lookup[state, age, geometries[0]] for age in ages)
                b0, b1 = (lookup[state, age, geometries[1]] for age in ages)
                contrasts.append({'state': state, 'kind': 'interaction', 'split': split,
                    'geometry_pair': geometries, 'age_pair': ages,
                    **{m: subtract(subtract(b1[m], b0[m]), subtract(a1[m], a0[m])) for m in measures}})
    return cells, panels, contrasts
