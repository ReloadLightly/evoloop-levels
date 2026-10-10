"""Readable tables from the unchanged, audited crossed assessment."""
import csv
import json

from evoloop.engine import ROOT
from evoloop.crossed import value
from scripts.coverage_protocol import sha

OUT = ROOT / 'data/crossed-v1'


def read(path):
    return json.loads(path.read_text())


def endpoint(record):
    if record is None:
        return 'missing'
    exact = value(record)
    return f'{exact.numerator}/{exact.denominator} ({float(exact):.4f})'


def bounds(row):
    if row['status'].startswith('undefined'):
        return f'undefined control · {row["status"]}'
    lower = endpoint(row['lower']) if row['lower'] is not None else '−∞'
    upper = endpoint(row['upper']) if row['upper'] is not None else '+∞'
    return f'[{lower}, {upper}] · {row["status"]}'


def export_csv(name, records):
    fields = list(dict.fromkeys(key for row in records for key in row))
    with (OUT / name).open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in records:
            writer.writerow({k: json.dumps(v, sort_keys=True) if isinstance(v, (dict, list)) else v
                             for k, v in row.items()})


def main():
    audit = read(OUT / 'integrity.json')
    assert audit['status'] == 'passed' and audit['mismatches'] == 0
    assert all(sha(OUT / name) == audit['evidence_sha256'][name]
               for name in ('analysis.json', 'results.json'))
    analysis = read(OUT / 'analysis.json')
    manifest = read(OUT / 'manifest.json')
    results = read(OUT / 'results.json')
    assert all(sha(OUT / 'worlds' / world['run_id'] / 'result.json') == world['result_sha256']
               for world in results['worlds'])
    worlds = [read(OUT / 'worlds' / spec['run_id'] / 'result.json') for spec in manifest['runs']]
    rows = [r for world in worlds for r in world['sources']]
    unknown = [r for r in rows if r['source_identity'] is None and r['transmission_confirmed']]
    total = analysis['total']
    lines = ['# Crossed preparation age and complete spatial challenge', '',
        f'EXP-age-geometry-cross-001 completes {analysis["complete_worlds"]} worlds, '
        f'{analysis["snapshot_strata"]} census snapshots and 80 D/U pairs. '
        f'Q={total["Q"]} confirmed source observations, C={total["C"]} detected cores, R={total["R"]} unresolved.', '',
        'Q confirms recovery under the declared isolated descendant search. C retains all detected cores; '
        '[Q,C] is an operational envelope over detected source bodies, not total viable population. '
        'Snapshot/core observations are nested in deterministic worlds; repeated complete inputs retain '
        'multiplicity without supplying independent replication.', '',
        '| Source class | Q | R | C |', '|---|---:|---:|---:|']
    lines += [f'| {row["source_class"]} | {row["Q"]} | {row["R"]} | {row["C"]} |' for row in analysis['by_class']]
    controls = analysis['controls']
    lines += ['', f'Original phase controls: {controls["phase_confirmed"]}/{controls["phase_selected"]}; '
        f'known omitted-input controls: {controls["omitted_confirmed"]}/{controls["omitted_selected"]}. '
        f'Frozen protocol011 calibration status: {manifest["calibration_gate_status"]}. '
        'Protocol010 remains failed; all previous classifications stay unchanged.', '',
        'Main crossed registry-scored recovery is 5,418/6,048, below the numerical 90% threshold '
        'used for protocol011 calibration. That earlier frozen calibration supplies the declared '
        'protocol012 gate; its passed classification is neither reapplied to nor inferred from '
        'these main worlds. Valid-unregistered recovery is 4/124. Prior qualification does not '
        'establish complete source coverage or total viable population.', '',
        '| Joint gate | Passed |', '|---|---|']
    lines += [f'| {key} | {result} |' for key, result in analysis['gate_checks'].items()]
    lines += ['', '## Exact panel envelopes', '',
        'Each panel averages eight per-condition retention fractions (four ages × two layouts), '
        'rather than pooling counts. Disturbed count means average five censuses per condition. '
        'Missing controls, infinite upper endpoints and measured zero stay distinct.', '',
        '| State | Panel | Mean retention envelope | Mean disturbed [Q,C] |', '|---|---|---|---|']
    lines += [f'| {p["state"]} | {p["split"]} | {bounds(p["retention"])} | {bounds(p["disturbed_mean"])} |'
              for p in analysis['panels']]
    lines += ['', '| Candidate | Relative robust criterion | Absolute robust criterion | Joint confirmed | Biological advantage |',
        '|---|---|---|---|---|']
    lines += [f'| {b["candidate"]} | {b["relative_robust_superiority"]} | {b["absolute_robust_superiority"]} | '
              f'{b["joint_confirmed"]} | {b["biological_advantage"]} |' for b in analysis['benefits']]
    lines += ['', 'Strict superiority compares each candidate lower endpoint with both originating-input upper '
        'endpoints in both panels. Ties fail. A criterion not met does not establish zero true benefit; '
        'overlap and missingness retain unresolved biological advantage. Confirmed originating-encounter '
        'fractions keep all atlas encounters in their denominators; their numerator is not total biological yield:', '']
    lines += [f'- {row["split"]}: {row["confirmed"]}/{row["denominator"]}.' for row in analysis['yield']]
    lines += ['', 'Sixteen other candidate-producing atlas encounters retain unresolved inheritance.', '',
        '## Declared interaction contrasts', '',
        'Intervals use [l₁−u₀,u₁−l₀] subtraction, including for differences of age differences. '
        'These are deterministic condition contrasts, not confidence intervals. A layout includes its '
        'removed-clone site; contrasts do not isolate a pure distance effect. A/B and E/F are different '
        'spatial challenges; elapsed ages are not homologous reproductive phases.', '',
        '| State | Panel | Age difference | Retention interaction | Disturbed-count interaction |', '|---|---|---|---|---|']
    lines += [f'| {c["state"]} | {c["split"]} | {c["age_pair"][1]}−{c["age_pair"][0]} | '
              f'{bounds(c["retention"])} | {bounds(c["disturbed_mean"])} |'
              for c in analysis['contrasts'] if c['kind'] == 'interaction']
    lines += ['', '## All crossed cells', '', '| State | Age | Layout | D Q/R/C | U Q/R/C | Retention |',
              '|---|---:|---|---|---|---|']
    lines += [f'| {c["state"]} | {c["age"]} | {c["geometry"]} | '
              f'{c["D"]["Q"]}/{c["D"]["R"]}/{c["D"]["C"]} | '
              f'{c["U"]["Q"]}/{c["U"]["R"]}/{c["U"]["C"]} | {bounds(c["retention"])} |'
              for c in analysis['cells']]
    lines += ['', '## Recovery qualifications', '',
        f'Unknown-source confirmations: {len(unknown)} observations from '
        f'{len({r["search_key"] for r in unknown})} distinct complete input/search keys. '
        'Recovered descendant identity does not retroassign source genotype or native parentage.', '',
        f'Executed searches: {analysis["unique_searches"]}; generation simulations: {analysis["generation_simulations"]}. '
        f'Maximum locally admitted keys in a world: {max(w["admitted_distinct_keys"] for w in worlds)}. '
        'Cached complete inputs still consume local admission; all exclusions and unsearched bodies remain R.', '',
        'Source statuses: ' + json.dumps(analysis['source_statuses'], sort_keys=True) + '.', '',
        f'Root reproduction observations: {sum(r["root_reproduction_observed"] is True for r in rows)}; '
        f'isolated-root extinction observations: {sum(0 in r["isolated_grid_extinction_nodes"] for r in rows)}; '
        f'sources with any search censoring: {sum(bool(r["search_censoring"]) for r in rows)}. '
        'An isolated-grid extinction is not native lineage death; nonconfirmation is unresolved recovery.', '',
        'The 81-sample fixed-registry structural means are retained separately in cells.csv and analysis.json. '
        'Constructed colonies and ordinary growth/recovery do not establish H1, H3, increased evolvability, '
        'a crowding mechanism or RSI.', '']
    (OUT / 'analysis.md').write_text('\n'.join(lines))
    export_csv('cells.csv', analysis['cells'])
    export_csv('contrasts.csv', analysis['contrasts'])
    print('Wrote audited tables: 80 cells and 100 contrasts', flush=True)


if __name__ == '__main__':
    main()
