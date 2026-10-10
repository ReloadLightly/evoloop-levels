"""Recorded prospective developmental-measure calibration under shared style."""
import argparse,json,hashlib
import numpy as np
from evoloop.engine import ROOT
from scripts.figures import FIG,STYLE,THEMES,CMAP,NORM,theme,save,legend,quantitative_cmap,annotation_color
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
OUT=ROOT/'data/developmental-v1'
def read(p):return json.loads(p.read_text())
def export(fig,name,artifacts,paths):
 paths=[OUT/x for x in ('manifest.json','analysis.json','integrity.json')]+paths+[ROOT/'scripts/figures_developmental.py',ROOT/'scripts/figures.py',ROOT/'configs/style.json']
 extra={'command':'OPENBLAS_NUM_THREADS=1 python -m scripts.figures_developmental',
        'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))},
        'status':'completed calibration; Q/R/C refer to detected source units, not total viable population'}
 save(fig,'developmental1-'+name,True,artifacts,['EXP-developmental-calibration-001'],extra)
def resolution(analysis,artifacts):
 rows=analysis['resolution'];states=list(dict.fromkeys(x['state'] for x in rows));lookup={(x['state'],x['treatment']):x for x in rows}
 values=np.array([[lookup[s,t]['Q']/lookup[s,t]['C'] if lookup[s,t]['C'] else np.nan for t in ('D','U')] for s in states])
 for dark in THEMES:
  theme(dark);fig,ax=plt.subplots(figsize=(10.5,6.4));cmap=quantitative_cmap().copy();cmap.set_bad(STYLE['status']['missing'])
  im=ax.imshow(values,vmin=0,vmax=1,cmap=cmap,aspect='auto',interpolation='nearest')
  for i,s in enumerate(states):
   for j,t in enumerate(('D','U')):
    x=lookup[s,t];fill=cmap(values[i,j]) if x['C'] else STYLE['status']['missing']
    label=f"Q/C={x['Q']}/{x['C']}\nR={x['R']}; {'PASS' if x['passed'] else 'FAIL' if x['passed'] is False else 'MISSING'}"
    ax.text(j,i,label,ha='center',va='center',color=annotation_color(fill),fontsize=12)
    if not x['C']:ax.add_patch(Rectangle((j-.5,i-.5),1,1,fill=False,hatch='///',edgecolor=STYLE['text']))
  ax.set_xticks([0,1],['D: one complete clone removed','U: undisturbed twin']);ax.set_yticks(range(5),states)
  ax.set_title('Confirmed recoverable sources / all detected cores · EXP-developmental-calibration-001',pad=15,fontsize=13)
  ax.set_ylabel('Complete input representative; two new calibration layouts')
  fig.colorbar(im,ax=ax,fraction=.04,pad=.04,label='Q/C resolved share; threshold 4/5')
  fig.subplots_adjust(left=.13,right=.89,bottom=.29,top=.86)
  c=analysis['controls'];sc=analysis['scored']
  fig.text(.5,.065,f"Overall calibration gate: {analysis['gate_status'].upper()}; original phase controls {c['phase_confirmed']}/{c['phase_selected']}; omitted-input controls {c['omitted_confirmed']}/{c['omitted_selected']}.\n"
   f"Scored recovery {sc['Q']}/{sc['C']}; separate scored-state and resolved-share gates remain frozen.\n"
   'Five source times 0/400/800/1200/1600 per world; all shared, capped, nonproductive and ineligible sources remain unresolved R.\n'
   'Q counts delay-zero complete-component recovery, C all detected cores; [Q,C] does not bound all viable organisms.\n'
   'Finite deterministic sources; repeated inputs and controls are not independent populations. Unknown genotype does not prevent recovery.',ha='center',fontsize=9)
  export(fig,'resolution',artifacts,[])
def raw(analysis,artifacts):
 m=read(OUT/'manifest.json');runs=[r for r in m['runs'] if r['state']=='V01' and r['condition']['id']=='calibration-0'];paths=[]
 for dark in THEMES:
  theme(dark);fig,axes=plt.subplots(2,3,figsize=(12,10));times=[0,800,1600]
  for i,r in enumerate(runs):
   report=read(OUT/'worlds'/r['run_id']/'result.json');paths.append(OUT/'worlds'/r['run_id']/'result.json')
   for j,t in enumerate(times):
    p=OUT/'worlds'/r['run_id']/f'grid-{t}.npz';paths.append(p)
    with np.load(p,allow_pickle=False) as a:g=a['grid']
    x=next(x for x in report['snapshot_counts'] if x['t']==t);ax=axes[i,j]
    ax.imshow(g,cmap=CMAP,norm=NORM,interpolation='nearest',extent=(-.5,191.5,191.5,-.5));ax.set_aspect('equal')
    for spine in ax.spines.values():spine.set_visible(False)
    ax.set_xticks([0,191]);ax.set_yticks([0,191]);ax.set_title(f"native t={t}; Q={x['Q']}, R={x['R']}, C={x['C']}",fontsize=10)
    if j==0:ax.set_ylabel(r['run_id'],fontsize=9)
    # Scale outside the recorded grid; axes fractional width derives from192 cells.
    ax.plot([.02,.02+10/192],[-.11,-.11],transform=ax.transAxes,color=STYLE['text'],lw=2,clip_on=False)
    ax.text(.10,-.11,'10 cells',transform=ax.transAxes,va='center',fontsize=8)
  fig.suptitle('Recorded paired calibration worlds · EXP-developmental-calibration-001',fontsize=14)
  fig.subplots_adjust(left=.08,right=.98,bottom=.22,top=.90,hspace=.36);legend(fig)
  fig.text(.5,.13,'First declared state/layout; full 192×192 periodic grids, literal nine-state colors, nearest cells.\n'
   'Constructed three-copy colony at elapsed age 20; D removes one complete component, U has no removal.\n'
   'Q/R/C labels are subsequent isolated-assay classifications of source snapshots, not native ancestry or total viable population.',ha='center',fontsize=9)
  export(fig,'paired-states',artifacts,paths)
def main():
 p=argparse.ArgumentParser();p.add_argument('--only',choices=['resolution','raw']);args=p.parse_args()
 audit=read(OUT/'integrity.json');assert audit['status']=='passed' and audit['mismatches']==0
 analysis=read(OUT/'analysis.json');artifacts=[]
 if args.only in (None,'resolution'):resolution(analysis,artifacts)
 if args.only in (None,'raw'):raw(analysis,artifacts)
 path=FIG/'manifest.json';m=read(path);names={x['file'] for x in artifacts};m['artifacts']=[x for x in m['artifacts'] if x['file'] not in names]+artifacts
 temp=path.with_suffix('.json.tmp');temp.write_text(json.dumps(m,indent=2)+'\n');temp.replace(path);print('Rendered',len(artifacts),'developmental artifacts')
if __name__=='__main__':main()
