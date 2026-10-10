"""Optional verified execution route; leaves frozen scientific modules intact.

Commands: python -m scripts.cropped_fresh_atlas run|inherit
Execute only after cropped verification is reviewed and original acquisition is
stopped. The existing execution record is preserved; a separate record maps all
acquisition run IDs to their implementation at this switch.
"""
import argparse
import hashlib
import json
from evoloop.engine import ROOT,RULE_HASH
from evoloop.cropped_tracking import detect
from evoloop import periodic_assays
from scripts import fresh_atlas as atlas
from scripts import accelerated_fresh_atlas as tiled_driver
from scripts.atlas import write_json

PROOF=ROOT/'data/measurement-crop-verification/verification.json'
FILES=['evoloop/cropped_tracking.py','scripts/verify_cropped_tracking.py',
       'scripts/cropped_fresh_atlas.py']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def apply_verified_execution(command):
    manifest=atlas.load_manifest()
    proof=json.loads(PROOF.read_text())
    assert proof['mismatches']==0 and proof['rule_hash']==RULE_HASH
    assert proof['experiment_manifest_sha256']==sha(atlas.OUT/'manifest.json')
    for name,value in proof['source_hashes'].items():
        assert sha(ROOT/name)==value,'measurement verification source changed'
    tiled=json.loads((atlas.OUT/'tiled_verification.json').read_text())
    assert tiled['mismatches']==0 and tiled['rule_hash']==RULE_HASH
    assert tiled['optimization_hashes']==tiled_driver.hashes()
    existing=atlas.OUT/'execution.json'
    prior=json.loads(existing.read_text())
    completed={r['run_id'] for r in manifest['runs']
               if (atlas.OUT/'runs'/r['run_id']/'result.json').exists()}
    record=atlas.OUT/'cropped-execution.json'
    if not record.exists():
        original=set(prior['original_completed_runs'])
        implementations={r['run_id']:
            ('original frozen execution' if r['run_id'] in original else
             'verified tiled physics; reference measurement' if r['run_id'] in completed else
             'verified tiled physics; equivalent cropped measurement')
            for r in manifest['runs']}
        write_json(record,{
            'experiment_id':manifest['experiment_id'],
            'measurement_proof':str(PROOF.relative_to(ROOT)),
            'measurement_proof_sha256':sha(PROOF),
            'wrapper_hashes':{name:sha(ROOT/name) for name in FILES},
            'prior_execution_sha256':sha(existing),
            'completed_before_measurement_switch':sorted(completed),
            'acquisition_implementation_by_run_id':implementations,
            'inheritance_execution':'verified tiled physics; equivalent cropped measurement',
            'first_command':command,
            'scope':'execution implementation only; unchanged states, outcomes, search and denominators'})
    else:
        saved=json.loads(record.read_text())
        assert saved['measurement_proof_sha256']==sha(PROOF)
        assert saved['wrapper_hashes']=={name:sha(ROOT/name) for name in FILES}
        assert saved['prior_execution_sha256']==sha(existing)
    atlas.advance=tiled_driver.tiled
    atlas.detect=detect
    periodic_assays.advance=tiled_driver.tiled
    periodic_assays.detect=detect


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=['run','inherit'])
    args=parser.parse_args()
    apply_verified_execution(args.command)
    {'run':atlas.run,'inherit':atlas.inherit}[args.command]()
