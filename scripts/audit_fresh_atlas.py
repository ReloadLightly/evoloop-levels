"""Join immutable acquisition records with completed inheritance evidence.

This review table does not change the frozen analysis or its endpoints. Missing
contact times are blank; unsearched candidate fates remain unresolved.
"""
import csv
import json
from evoloop.engine import ROOT

OUT = ROOT / 'data/atlas-v2'


def main():
    manifest = json.loads((OUT / 'manifest.json').read_text())
    inheritance = json.loads((OUT / 'inheritance.json').read_text())
    rows = []
    for spec in manifest['runs']:
        result = json.loads((OUT / 'runs' / spec['run_id'] / 'result.json').read_text())
        items = [i for i in inheritance['items'] if i['run_id'] == spec['run_id']]
        roots = [o for i in items for o in i['outcomes']]
        confirmed = sum(o['status'] == 'confirmed' for o in roots)
        last = result['metrics'][-1]
        assert last['t'] == result['horizon']
        rows.append({
            'run_id': spec['run_id'], 'treatment': spec['treatment'],
            'split': spec['split'], 'focal': spec['focal'], 'partner': spec['partner'],
            'initial_grid_sha256': result['initial_hash'],
            'final_grid_sha256': result['final_hash'],
            'horizon': result['horizon'], 'contact_t': result['contact_t'],
            'boundary_first_t': result['boundary_first_t'],
            'initial_cores_present_at_horizon': sum(s['closed_core_present_at_horizon']
                                                   for s in result['input_structural_survival']),
            'new_closed_core_positions': result['new_core_count'],
            'final_closed_cores': last['closed_cores'],
            'final_unknown_identity_cores': last['unknown_genotype_cores'],
            'final_occupied_cells': last['occupied_cells'],
            'candidate_composite_identities': len(result['candidates']),
            'shape_only_changed_identities': len(result['shape_only_changed_identities']),
            'isolation_roots': len(roots), 'confirmed_novel_roots': confirmed,
            'unresolved_roots': len(roots) - confirmed,
            'candidate_identities_without_extraction': sum(not i['outcomes'] for i in items),
            'inheritance_outcome': ('confirmed_novel' if confirmed else
                                    'unresolved_candidate_fates' if items else
                                    'no_candidate_within_horizon'),
            'benefit_assay_status': 'not_assayed; beneficial-heritable yield unknown',
            'ancestry': result['ancestry'],
            'observation_status': result['observation_status'],
        })
    assert len(rows) == manifest['expected_runs']
    with (OUT / 'outcomes.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f'Joined {len(rows)} complete records; new core positions are structural, not verified births.')


if __name__ == '__main__':
    main()
