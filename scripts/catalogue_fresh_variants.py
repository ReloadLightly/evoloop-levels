"""Export all confirmed stable identities, without fitness-based selection."""
import hashlib
import json
from pathlib import Path

import numpy as np

from evoloop.engine import ROOT, digest
from scripts.atlas import write_json


def main():
    out = ROOT / 'data/atlas-v2'
    manifest = json.loads((out / 'manifest.json').read_text())
    inheritance = json.loads((out / 'inheritance.json').read_text())
    known = {p['genotype']: pid for pid, p in manifest['panel'].items()}
    by_identity = {}
    for item in inheritance['items']:
        for outcome in item['outcomes']:
            c = outcome['confirmation']
            if c is None:
                continue
            identity = c['identity']
            by_identity.setdefault(identity, []).append({
                'run_id': item['run_id'], 'folder': outcome['folder'],
                'encounter_identity': item['encounter_genotype'],
                'native_capture_t': outcome['source']['t'],
                'source': outcome['source'], 'confirmation': c,
                'stable_word_observed_natively': outcome['stable_word_observed_natively'],
            })
    folder = out / 'confirmed'
    folder.mkdir(exist_ok=True)
    entries = []
    # All identities are retained. Ordering affects labels only, not admission.
    for n, identity in enumerate(sorted(by_identity), 1):
        origins = sorted(by_identity[identity], key=lambda o: (
            o['native_capture_t'], o['run_id'], o['folder']))
        origin = origins[0]
        path = out / origin['folder'] / 'confirmation.npz'
        snapshot = np.load(path)['stable_snapshot']
        assert digest(snapshot) == origin['confirmation']['snapshot_hash']
        label = f'RV{n:02d}'
        np.savez_compressed(folder / f'{label}.npz', snapshot=snapshot)
        entry = {
            'id': label, 'identity': identity, 'snapshot_hash': digest(snapshot),
            'snapshot_file': f'confirmed/{label}.npz',
            'known_panel_identity': known.get(identity),
            'novel_to_input_catalogue': identity.split(':', 1)[1] not in {
                gt.split(':', 1)[1] for gt in known},
            'selection': 'all confirmed stable identities; earliest native capture, '
                         'then run ID and root folder chooses representative',
            'representative': origin, 'confirmation_origins': origins,
            'independent_encounter_states': sorted({o['run_id'] for o in origins}),
            'ancestry': 'ambiguous pair; no genetic parent assignment',
            'benefit_status': 'not assayed; unknown',
        }
        write_json(folder / f'{label}.json', entry)
        entries.append(entry)
    write_json(folder / 'catalogue.json', {
        'experiment_id': manifest['experiment_id'], 'entries': entries,
        'inheritance_sha256': hashlib.sha256((out / 'inheritance.json').read_bytes()).hexdigest(),
        'command': 'python -m scripts.catalogue_fresh_variants',
        'scope': 'pair-relative operational identities, not published species identifiers; '
                 'roots and repeated phases are not independent evolutionary histories',
    })
    print(f'Exported {len(entries)} stable identities from '
          f'{len({r for e in entries for r in e["independent_encounter_states"]})} encounter states')


if __name__ == '__main__':
    main()
