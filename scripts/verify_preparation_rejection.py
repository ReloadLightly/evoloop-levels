"""Post-freeze replay audit of the recorded pre-response preparation rejection."""
import json
import numpy as np
from evoloop.engine import ROOT, RULE_HASH, advance, digest
from evoloop.ecology import prepared_grid
from evoloop.periodic_tracking import detect
from evoloop.impact import complete_mask
from scripts.ecological_assay import sha
from scripts.atlas import write_json

def main():
    out=ROOT/'data/impact-exposure-v1/microcolony-attempt-01'
    source=ROOT/'data/ecological-v1/snapshots.npz';rows=[]
    with np.load(source) as snapshots:
        for pid in ['V01','V02','V03','RV01','RV02']:
            grid=prepared_grid(snapshots[pid],[192,192],0)
            for age in range(0,121,10):
                if age:advance(grid,10)
                loops=detect(grid);mask=complete_mask(grid,loops[0]) if len(loops)==1 else None
                count=int(np.count_nonzero(grid));complete=int(mask.sum()) if mask is not None else None
                rows.append({'state':pid,'age':age,'cores':len(loops),'occupied_cells':count,'component_cells':complete,
                             'all_cells_in_single_component':complete==count,'grid_hash':digest(grid)})
                if pid=='V03' and age in [40,80]:
                    assert count==complete+1
                    np.savez_compressed(out/f'rejected-V03-age{age}.npz',grid=grid,component_mask=mask.astype(np.uint8))
    common=[t for t in range(0,121,10) if all(r['all_cells_in_single_component'] and r['cores']==1 for r in rows if r['age']==t)]
    assert common==[0,10,20,30,100,110,120]
    write_json(out/'rejection-audit.json',{'status':'passed','scope':'post-freeze verification of pre-response preparation eligibility, never disturbed futures',
        'rule_hash':RULE_HASH,'source_sha256':sha(source),'provisional_config_sha256':sha(out/'provisional-config.json'),
        'script_sha256':sha(ROOT/'scripts/verify_preparation_rejection.py'),'common_eligible_ages':common,'rows':rows})
    print('Verified65 source-only phase states; two V03 rejected grids retain their disconnected cells')

if __name__=='__main__':main()
