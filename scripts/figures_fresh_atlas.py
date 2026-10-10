"""Chromatic Fields: fresh crossed outcomes and actual native replay evidence."""
import hashlib,json,os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR',str(Path(__file__).resolve().parents[1]/'.cache/matplotlib'))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from evoloop.engine import ROOT,advance,digest
from scripts.figures import FIG,STYLE,theme,save,legend,CMAP,NORM,animation
from scripts.atlas import write_json
EXP='EXP-atlas-002';OUT=ROOT/'data/atlas-v2';COMMAND='OPENBLAS_NUM_THREADS=1 python -m scripts.figures_fresh_atlas'

def export(fig,name,dark,manifest,extra=None):
    save(fig,name,dark,manifest,[EXP],{'command':COMMAND,'source':'data/atlas-v2/analysis.json',**(extra or {})})

def render(manifest):
    a=json.loads((OUT/'analysis.json').read_text());ids=a['ids']
    for dark in (False,True):
        theme(dark);fig,axes=plt.subplots(2,2,figsize=(10,9))
        for row,endpoint in enumerate(('candidate','inherited')):
            for col,split in enumerate(('main','heldout')):
                ax=axes[row,col];cells=a['splits'][split]['cells'];lookup={(c['focal'],c['partner']):c for c in cells}
                values=np.array([[lookup[p,q][endpoint]/lookup[p,q]['denominator'] for q in ids] for p in ids])
                im=ax.imshow(values,cmap='viridis',vmin=0,vmax=1,interpolation='nearest')
                for i,p in enumerate(ids):
                    for j,q in enumerate(ids):
                        c=lookup[p,q];v=values[i,j]
                        ax.text(j,i,f'{c[endpoint]}/{c["denominator"]}',ha='center',va='center',fontsize=17,color='white' if v<.5 else STYLE['ink'])
                ax.set_xticks(range(3),ids);ax.set_yticks(range(3),ids);ax.set_xlabel('partner');ax.set_ylabel('focal')
                ax.set_title(f'{split.capitalize()} · {"native novel word" if row==0 else "confirmed inherited word"}')
        fig.colorbar(im,ax=axes.ravel().tolist(),fraction=.025,pad=.03,label='fraction of all declared near configurations')
        fig.suptitle('Fresh crossed atlas · three separately verified identities',fontsize=15)
        fig.text(.45,.045,'Each cell retains all configurations, including lethal/nonproductive/no-contact states.\nInheritance zeros are tested search outcomes; unsearched fates remain unresolved.\nPair-level novelty; finite panel, no independent-history inference; benefit pending.',ha='center',fontsize=9)
        fig.subplots_adjust(left=.1,right=.82,top=.91,bottom=.16,hspace=.42,wspace=.3)
        export(fig,'atlas2-outcome-matrix',dark,manifest)
        theme(dark);fig,axes=plt.subplots(1,2,figsize=(10,4.6))
        for ax,split in zip(axes,('main','heldout')):
            s=a['splits'][split];vals=[s['candidate_runs'],s['confirmed_inherited_runs'],0];labels=['Native word\ncandidates','Confirmed\ninheritance','Benefit\nPENDING']
            ax.bar([0,1],vals[:2],color=[STYLE['amber'],STYLE['cobalt']],width=.6)
            ax.bar(2,s['total'],color='none',edgecolor=plt.rcParams['text.color'],hatch='///',width=.6,alpha=.3)
            for i,v in enumerate(vals[:2]):ax.text(i,v+.6,f'{v}/{s["total"]}',ha='center',va='bottom')
            ax.text(2,s['total']/2,'unknown',ha='center',va='center');ax.set_xticks(range(3),labels)
            ax.set_ylim(0,s['total']+6);ax.set_ylabel('configurations');ax.set_title(f'{split.capitalize()} · denominator {s["total"]}')
        fig.suptitle('Observed production, recovered transmission, unmeasured benefit')
        fig.text(.5,.03,'No benefit assay has run. Hatching indicates missing evidence, never a measured zero.',ha='center',fontsize=9)
        fig.tight_layout(rect=(0,.1,1,.93));export(fig,'atlas2-evidence-stages',dark,manifest)
    panel_figure(manifest)
    replays(manifest)


def panel_figure(manifest):
    d=json.loads((ROOT/'data/panel-v2/discovery.json').read_text())
    for dark in (False,True):
        theme(dark);fig,axes=plt.subplots(1,3,figsize=(11,5))
        for ax,p in zip(axes,d['panel']):
            snap=np.load(ROOT/f'data/panel-v2/{p["id"]}.npz')['snapshot']
            ax.imshow(snap,cmap=CMAP,norm=NORM,interpolation='nearest');ax.set_title(f'{p["id"]} · {p["stable_identity"].split(":")[0]} core')
            ax.set_xlabel('column / cells');ax.set_ylabel('row / cells')
            ax.text(.5,-.22,f'Native: {p["source"]["history"]}, t={p["source"]["t"]:,}\nThird isolated descendant; two stable transmissions',transform=ax.transAxes,ha='center',fontsize=8)
        fig.suptitle('Naturally generated input words · separately verified reproduction')
        fig.subplots_adjust(bottom=.3,top=.82,wspace=.35);legend(fig)
        export(fig,'atlas2-verified-panel',dark,manifest,{'source':'data/panel-v2/discovery.json','experiments':['EXP-panel-discovery-002',EXP]})
    # Full native world, compact sampled frames; no retrospective synthetic illustration.
    h=d['histories'][-1];arr=np.load(ROOT/f'data/panel-v2/{h["id"]}-world.npz');frames=arr['frames'];times=arr['times']
    if len(frames)>45:
        chosen=np.unique(np.linspace(0,len(frames)-1,45,dtype=int));frames=frames[chosen];times=times[chosen]
    path=FIG/'atlas2-discovery-world.webp';animation(frames,times,path,'CHROMATIC FIELDS / Natural panel discovery',f'EXP-panel-discovery-002 | {h["id"]} native world',scale=2 if frames.shape[1]>=320 else 4)
    manifest.append({'file':path.name,'experiments':['EXP-panel-discovery-002'],'command':COMMAND,'source':f'data/panel-v2/{h["id"]}-world.npz','sha256':hashlib.sha256(path.read_bytes()).hexdigest()})


def replays(manifest):
    m=json.loads((OUT/'manifest.json').read_text());rows=[json.loads((OUT/'runs'/r['run_id']/'result.json').read_text()) for r in m['runs'] if r['treatment']=='near']
    # Illustration selection is deterministic and explicit, not an inferential endpoint.
    candidates=sorted([r for r in rows if r['candidates']],key=lambda r:(min(c['first_observed_t'] for c in r['candidates']),r['run_id']))
    selected=[]
    for r in candidates+sorted(rows,key=lambda r:r['run_id']):
        if r['run_id'] not in {s['run_id'] for s in selected}:
            selected.append(r)
        if len(selected)==3:break
    for idx,r in enumerate(selected,1):
        rid=r['run_id'];initial=np.load(OUT/'initial'/f'{rid}.npz');g=initial['grid'].copy();lab=initial['labels'].copy()
        outcome_t=min((c['first_observed_t'] for c in r['candidates']),default=m['config']['horizon'])
        keytimes=sorted(set([0,r['contact_t'] or 0,outcome_t,min(1600,outcome_t+100)]));frames=[];times=[];states={}
        for t in range(1601):
            if t:advance(g,1,lab)
            if t%40==0 or t in keytimes:frames.append(g.copy());times.append(t)
            if t in keytimes:states[t]=g.copy()
        assert digest(g)==r['final_hash']
        # Fixed replay crop covers occupied union at annotated times; preserve exact geometry.
        yy,xx=np.where(np.any(np.array(list(states.values()))!=0,axis=0));sy=max(0,int(yy.min())-8);sx=max(0,int(xx.min())-8);ey=min(640,int(yy.max())+9);ex=min(640,int(xx.max())+9)
        box=[sy,sx,ey-sy,ex-sx];folder=OUT/'replays';folder.mkdir(exist_ok=True)
        np.savez_compressed(folder/f'encounter-{idx}.npz',frames=np.array([f[sy:ey,sx:ex] for f in frames]),times=np.array(times),annotated_frames=np.array([states[t][sy:ey,sx:ex] for t in keytimes]),annotated_times=np.array(keytimes),crop=np.array(box))
        path=FIG/f'atlas2-encounter-{idx}.webp';animation([f[sy:ey,sx:ex] for f in frames],times,path,f'CHROMATIC FIELDS / {r["focal"]} × {r["partner"]}',f'{rid} | crop row{sy},col{sx}',scale=2,contact_t=r['contact_t'])
        manifest.append({'file':path.name,'experiments':[EXP],'command':COMMAND,'run_id':rid,'crop':box,'source':f'data/atlas-v2/replays/encounter-{idx}.npz','sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        for dark in (False,True):
            theme(dark);fig,axes=plt.subplots(1,len(keytimes),figsize=(13,5))
            for ax,t in zip(np.atleast_1d(axes),keytimes):
                ax.imshow(states[t][sy:ey,sx:ex],cmap=CMAP,norm=NORM,interpolation='nearest',extent=(sx-.5,ex-.5,ey-.5,sy-.5))
                caption='inputs' if t==0 else 'first contact' if t==r['contact_t'] else 'candidate first observed' if t==outcome_t and r['candidates'] else 'later state'
                ax.set_title(f't={t} · {caption}',fontsize=9);ax.set_xlabel('column / cells')
                if t==0:
                    for input_idx,b in enumerate(r['input_boxes']):
                        if b:
                            y,x,h,w=b;ax.add_patch(Rectangle((x-.5,y-.5),w,h,fill=False,edgecolor=STYLE['cyan'] if input_idx==0 else STYLE['magenta'],lw=1.1))
            axes[0].set_ylabel('row / cells');fig.suptitle(f'{r["focal"]} × {r["partner"]} · actual encounter states')
            fig.text(.5,.13,f'{rid}\nInput outlines encode placement only; literal cell states retain shared palette. Candidate ≠ confirmed inheritance.',ha='center',fontsize=8)
            fig.subplots_adjust(bottom=.26,top=.83,wspace=.25);legend(fig)
            export(fig,f'atlas2-encounter-{idx}',dark,manifest,{'run_id':rid,'crop':box,'annotated_times':keytimes})


def main():
    manifest=json.loads((FIG/'manifest.json').read_text());manifest['artifacts']=[x for x in manifest['artifacts'] if not x['file'].startswith('atlas2-')]
    render(manifest['artifacts']);write_json(FIG/'manifest.json',manifest);print('Fresh figures added; total',len(manifest['artifacts']))
if __name__=='__main__':main()
