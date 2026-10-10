"""Freeze the age×geometry experiment after independent metric assessment."""
import json
from itertools import combinations
import numpy as np
from evoloop.engine import ROOT,RULE_HASH,digest
from evoloop.microcolony import assemble,equivalent
from scripts.coverage_assay import atomic_json,atomic_npz
from scripts.coverage_protocol import sha,require

OUT=ROOT/'data/crossed-v1'
def read(p):return json.loads(p.read_text())
def main():
 require(not (OUT/'manifest.json').exists(),'immutable cross freeze already exists')
 cfg=read(ROOT/'configs/crossed-v1.json');metric=read(ROOT/'data/developmental-v1/manifest.json')
 integrity=read(ROOT/cfg['calibration_integrity']);assessment=read(ROOT/cfg['calibration_assessment'])
 require(integrity['status']=='passed' and integrity['mismatches']==0,'independent metric assessment must pass before design freeze')
 require(integrity['evidence_sha256']['analysis.json']==sha(ROOT/cfg['calibration_assessment']),'assessment linkage changed')
 require((OUT/'validation.txt').is_file() and (OUT/'validation.txt').read_text().rstrip().endswith('OK'),'crossed design preflight tests must pass')
 old=read(ROOT/'data/impact-v1/manifest.json');runs=[];preparations=[];files=set(metric['source_file_sha256'])
 files.update(['configs/crossed-v1.json',cfg['protocol'],'scripts/freeze_crossed.py','scripts/verify_crossed_design.py','tests/test_crossed_design_audit.py','data/developmental-v1/manifest.json',
  cfg['calibration_integrity'],cfg['calibration_assessment'],'data/developmental-v1/results.json','data/impact-v1/manifest.json','data/crossed-v1/validation.txt'])
 for state in cfg['states']:
  for age in cfg['ages']:
   phase=next(p for p in old['phases'] if p['state']==state and p['age']==age)
   path=f'data/impact-v1/phase/{phase["name"]}.npz';files.add(path)
   with np.load(ROOT/path,allow_pickle=False) as a:
    patch=a['snapshot'].copy();require(np.count_nonzero(patch)==np.count_nonzero(a['grid']),'disconnected phase residual')
    require(digest(patch)==phase['snapshot_hash'],'phase physical hash')
   for geometry in cfg['geometries']:
    pre,post,mask,impact=assemble(patch,phase['offset'],geometry['sites'],geometry['remove_index'],cfg['shape'],old['registry'])
    hb=np.bincount(pre.ravel(),minlength=9).tolist();ha=np.bincount(post.ravel(),minlength=9).tolist()
    require(all(hb[i]==3*(hb[i]-ha[i]) for i in range(1,9)),'fractional occupied-state loss')
    pair=f'{state}-age{age}-{geometry["id"]}';fp=f'data/crossed-v1/prepared/{pair}.npz'
    atomic_npz(ROOT/fp,before=pre,after=post,mask=mask);files.add(fp)
    preparations.append({'pair_id':pair,'state':state,'age':age,'geometry':geometry,'phase':phase['name'],
      'file':fp,'impact':impact,'histogram_before':hb,'histogram_after':ha})
    for treatment,g in [('D',post),('U',pre)]:
     rid=f'{pair}-{treatment}';ip=f'data/crossed-v1/initial/{rid}.npz';atomic_npz(ROOT/ip,grid=g);files.add(ip)
     runs.append({'run_id':rid,'state':state,'age':age,'geometry':geometry['id'],'split':geometry['split'],
      'treatment':treatment,'initial_file':ip,'initial_hash':digest(g),'pair_id':pair})
 checks=[];aliases=[]
 references=[('protocol009',r) for r in old['runs']]+[('calibration011',r) for r in metric['runs']]
 for run in runs:
  with np.load(ROOT/run['initial_file'],allow_pickle=False) as a:grid=a['grid']
  for group,prior in references:
   p=prior.get('initial_file',f'data/impact-v1/initial/{prior["run_id"]}.npz');files.add(p)
   with np.load(ROOT/p,allow_pickle=False) as b:eq=equivalent(grid,b['grid'])
   entry={'run_id':run['run_id'],'reference_group':group,'reference_run_id':prior['run_id'],'transform':eq}
   if run['split']=='confirmation':require(eq is None,'reserved effective state already observed');checks.append(entry)
   elif eq is not None:aliases.append(entry)
 for a,b in combinations(runs,2):
  with np.load(ROOT/a['initial_file'],allow_pickle=False) as x,np.load(ROOT/b['initial_file'],allow_pickle=False) as y:eq=equivalent(x['grid'],y['grid'])
  entry={'run_id':a['run_id'],'reference_group':'crossed012','reference_run_id':b['run_id'],'transform':eq}
  if a['split']!=b['split']:require(eq is None,'reserved state repeats development');checks.append(entry)
  elif eq is not None:aliases.append(entry)
 require(len(runs)==160 and len(preparations)==80,'complete Cartesian crossing')
 atomic_json(OUT/'manifest.json',{'experiment_id':cfg['experiment_id'],'config':cfg,'measure_config':metric['config'],
  'rule_hash':RULE_HASH,'registry':old['registry'],'states':old['states'],'runs':runs,'preparations':preparations,
  'controls':metric['controls'],
  'calibration_gate_status':assessment['gate_status'],'calibration_gate_checks':assessment['gate_checks'],
  'calibration_analysis_sha256':sha(ROOT/cfg['calibration_assessment']),
  'calibration_integrity_sha256':sha(ROOT/cfg['calibration_integrity']),
  'reserved_equivalence_checks':checks,'development_and_within_panel_aliases':aliases,
  'exposure_verified':True,'distinct_confirmation_verified':True,
  'source_file_sha256':{p:sha(ROOT/p) for p in sorted(files)},
  'acquisition_status':'not started; implementation readiness and benchmark required',
  'interpretation':'new measure qualification frozen; previous gate failures/outcomes unchanged; no independent populations'})
 print('Frozen160 worlds/80pairs; calibration',assessment['gate_status'],'; responses not acquired',flush=True)
if __name__=='__main__':main()
