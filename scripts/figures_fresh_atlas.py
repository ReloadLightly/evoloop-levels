"""Chromatic Fields: fresh crossed outcomes and actual native replay evidence."""
import hashlib,json,os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR',str(Path(__file__).resolve().parents[1]/'.cache/matplotlib'))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from evoloop.engine import ROOT,advance,digest
from evoloop.periodic_tracking import detect
from scripts.figures import FIG,STYLE,theme,save,legend,CMAP,NORM,animation,THEMES,quantitative_cmap,annotation_color
from scripts.atlas import write_json
EXP='EXP-atlas-002';OUT=ROOT/'data/atlas-v2';COMMAND='OPENBLAS_NUM_THREADS=1 python -m scripts.figures_fresh_atlas'

def export(fig,name,dark,manifest,extra=None):
    save(fig,name,dark,manifest,[EXP],{'command':COMMAND,'source':'data/atlas-v2/analysis.json',**(extra or {})})

def render(manifest):
    a=json.loads((OUT/'analysis.json').read_text());ids=a['ids']
    for dark in THEMES:
        theme(dark);fig,axes=plt.subplots(2,2,figsize=(10,9))
        for row,endpoint in enumerate(('candidate','inherited')):
            for col,split in enumerate(('main','heldout')):
                ax=axes[row,col];cells=a['splits'][split]['cells'];lookup={(c['focal'],c['partner']):c for c in cells}
                values=np.array([[lookup[p,q][endpoint]/lookup[p,q]['denominator'] for q in ids] for p in ids])
                cmap=quantitative_cmap()
                im=ax.imshow(values,cmap=cmap,vmin=0,vmax=1,interpolation='nearest')
                for i,p in enumerate(ids):
                    for j,q in enumerate(ids):
                        c=lookup[p,q];v=values[i,j]
                        ax.text(j,i,f'{c[endpoint]}/{c["denominator"]}',ha='center',va='center',fontsize=17,color=annotation_color(cmap(v)))
                ax.set_xticks(range(len(ids)),ids);ax.set_yticks(range(len(ids)),ids);ax.set_xlabel('partner');ax.set_ylabel('focal')
                ax.set_title(f'{split.capitalize()} · {"native novel word" if row==0 else "confirmed inherited word"}')
        fig.suptitle(f'Fresh crossed atlas · {EXP}',fontsize=15)
        fig.text(.45,.045,'Each cell retains all configurations, including lethal/nonproductive/no-contact states.\nConfirmed counts do not resolve unsearched candidate fates. Inheritance uses serial isolation.\nPair-level novelty; finite panel, no independent-history inference; benefit not assayed.',ha='center',fontsize=9)
        fig.subplots_adjust(left=.1,right=.82,top=.91,bottom=.16,hspace=.42,wspace=.3)
        cax=fig.add_axes([.87,.24,.025,.58])
        fig.colorbar(im,cax=cax,label='fraction of all declared near configurations')
        export(fig,'atlas2-outcome-matrix',dark,manifest)
        bg,fg=theme(dark);fig,(main_ax,held_ax,pending)=plt.subplots(1,3,figsize=(11,4.6),gridspec_kw={'width_ratios':[3,3,1.6]})
        axes=(main_ax,held_ax)
        for ax,split in zip(axes,('main','heldout')):
            s=a['splits'][split];vals=[s['candidate_runs'],s['confirmed_inherited_runs']];labels=['Native word\ncandidates','Confirmed isolated\ninheritance']
            ax.bar([0,1],vals,color=[STYLE['status']['candidate'],STYLE['status']['confirmed']],width=.6)
            for i,v in enumerate(vals):ax.text(i,v+.6,f'{v}/{s["total"]}',ha='center',va='bottom')
            ax.set_xticks(range(2),labels)
            ax.set_ylim(0,max(1,max(vals))+4);ax.set_ylabel('configurations');ax.set_title(f'{split.capitalize()} · denominator {s["total"]}')
        pending.set_axis_off()
        pending.add_patch(Rectangle((.03,.18),.94,.64,transform=pending.transAxes,fill=False,edgecolor=fg,hatch='///',alpha=.3))
        pending.text(.5,.5,'BENEFIT\nNOT ASSAYED\n\nYield unknown',transform=pending.transAxes,ha='center',va='center',fontsize=10,fontweight='bold')
        fig.suptitle(f'Observed production and isolated transmission · {EXP}')
        fig.text(.5,.03,'Unconfirmed candidate fates remain unresolved; the separate benefit card has no quantitative scale.',ha='center',fontsize=9)
        fig.tight_layout(rect=(0,.1,1,.93));export(fig,'atlas2-evidence-stages',dark,manifest)
    panel_figure(manifest)
    replays(manifest)
    inheritance_path(manifest)


def panel_figure(manifest):
    d=json.loads((ROOT/'data/panel-v2/discovery.json').read_text())
    for dark in THEMES:
        theme(dark);fig,axes=plt.subplots(1,3,figsize=(11,5))
        for ax,p in zip(axes,d['panel']):
            snap=np.load(ROOT/f'data/panel-v2/{p["id"]}.npz')['snapshot']
            ax.imshow(snap,cmap=CMAP,norm=NORM,interpolation='nearest');ax.set_title(f'{p["id"]} · {p["stable_identity"].split(":")[0]} core')
            ax.set_xlabel('column / cells');ax.set_ylabel('row / cells')
            ax.text(.5,-.35,f'Native: {p["source"]["history"]}, t={p["source"]["t"]:,}\nThird isolated descendant; two stable transmissions',transform=ax.transAxes,ha='center',fontsize=8)
        fig.suptitle(f'Naturally generated input words · {EXP}')
        fig.subplots_adjust(bottom=.38,top=.82,wspace=.35);legend(fig)
        export(fig,'atlas2-verified-panel',dark,manifest,{'source':'data/panel-v2/discovery.json','experiments':['EXP-panel-discovery-002',EXP]})
    # Full native world, compact sampled frames; no retrospective synthetic illustration.
    h=d['histories'][-1];arr=np.load(ROOT/f'data/panel-v2/{h["id"]}-world.npz');frames=arr['frames'];times=arr['times']
    if len(frames)>45:
        chosen=np.unique(np.linspace(0,len(frames)-1,45,dtype=int));frames=frames[chosen];times=times[chosen]
    path=FIG/'atlas2-discovery-world.webp';animation(frames,times,path,'CHROMATIC FIELDS / Natural panel discovery',f'EXP-panel-discovery-002 | {h["id"]} native periodic world',scale=2 if frames.shape[1]>=320 else 4)
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
        horizon=m['config']['horizon']
        keytimes=sorted(set([0,r['contact_t'] or 0,outcome_t,min(horizon,outcome_t+100)]));frames=[];times=[];states={}
        occupied=np.zeros(g.shape,dtype=bool)
        for t in range(horizon+1):
            if t:advance(g,1,lab)
            if t%40==0 or t in keytimes or t==horizon:
                frames.append(g.copy());times.append(t);occupied|=g!=0
            if t in keytimes:states[t]=g.copy()
        assert digest(g)==r['final_hash']
        # Fixed crop covers all recorded replay frames, including between annotations.
        yy,xx=np.where(occupied);sy=max(0,int(yy.min())-8);sx=max(0,int(xx.min())-8);ey=min(g.shape[0],int(yy.max())+9);ex=min(g.shape[1],int(xx.max())+9)
        box=[sy,sx,ey-sy,ex-sx];folder=OUT/'replays';folder.mkdir(exist_ok=True)
        np.savez_compressed(folder/f'encounter-{idx}.npz',frames=np.array([f[sy:ey,sx:ex] for f in frames]),times=np.array(times),annotated_frames=np.array([states[t][sy:ey,sx:ex] for t in keytimes]),annotated_times=np.array(keytimes),crop=np.array(box))
        # The retained replay samples every 40 updates; the browser animation
        # displays every second retained frame plus all annotation frames. This
        # bounds encoder memory while keeping cells and source geometry exact.
        display=sorted(set(range(0,len(frames),2)) | {
            k for k,t in enumerate(times) if t in keytimes or t==horizon})
        display_times=[times[k] for k in display]
        path=FIG/f'atlas2-encounter-{idx}.webp';animation([frames[k][sy:ey,sx:ex] for k in display],display_times,path,f'CHROMATIC FIELDS / {r["focal"]} × {r["partner"]}',f'{EXP} | periodic | {rid}',scale=1,contact_t=r['contact_t'])
        selection='earliest first candidate time, then run ID; noncandidate fallback by run ID'
        manifest.append({'file':path.name,'experiments':[EXP],'command':COMMAND,'run_id':rid,'crop':box,'source':f'data/atlas-v2/replays/encounter-{idx}.npz','selection':selection,'display_times':display_times,'pixels_per_cell':1,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        # Static panels share a second fixed crop covering every annotated state.
        # Later animation excursions do not determine the scale of early evidence.
        focused=np.zeros(g.shape,dtype=bool)
        for state in states.values():focused|=state!=0
        yy,xx=np.where(focused)
        fsy=max(0,int(yy.min())-8);fsx=max(0,int(xx.min())-8)
        fey=min(g.shape[0],int(yy.max())+9);fex=min(g.shape[1],int(xx.max())+9)
        focus_box=[fsy,fsx,fey-fsy,fex-fsx]
        for dark in THEMES:
            theme(dark);fig,axes=plt.subplots(1,len(keytimes),figsize=(13,5))
            for ax,t in zip(np.atleast_1d(axes),keytimes):
                ax.imshow(states[t][fsy:fey,fsx:fex],cmap=CMAP,norm=NORM,interpolation='nearest',extent=(fsx-.5,fex-.5,fey-.5,fsy-.5))
                labels=[]
                if t==0:labels.append('inputs')
                if t==r['contact_t']:labels.append('operational contact')
                if t==outcome_t:labels.append('first candidate' if r['candidates'] else 'observation horizon')
                if not labels:labels.append('later state')
                ax.set_title(f't={t}\n'+ ' + '.join(labels),fontsize=9);ax.set_xlabel('column / cells')
                if t==outcome_t and r['candidates']:
                    first_genotypes={c['genotype'] for c in r['candidates'] if c['first_observed_t']==t}
                    for o in detect(states[t]):
                        if o['genotype'] in first_genotypes:
                            y,x,h,w=o['bbox']
                            # Show each visible part if the annotated core crosses a torus seam.
                            for yy in (y,y-g.shape[0]):
                                for xx in (x,x-g.shape[1]):
                                    if yy+h>fsy and yy<fey and xx+w>fsx and xx<fex:
                                        ax.add_patch(Rectangle((xx-.5,yy-.5),w,h,fill=False,edgecolor=STYLE['annotation']['novel_core'],lw=1.3))
                if t==0:
                    for input_idx,b in enumerate(r['input_boxes']):
                        if b:
                            y,x,h,w=b;ax.add_patch(Rectangle((x-.5,y-.5),w,h,fill=False,edgecolor=STYLE['lineage_overlay']['focal' if input_idx==0 else 'partner'],lw=1.1,linestyle='-' if input_idx==0 else '--'))
            axes[0].set_ylabel('row / cells');fig.suptitle(f'{r["focal"]} × {r["partner"]} · {EXP} · periodic world')
            interval=m['config']['detection_interval']
            fig.text(.5,.13,f'{rid}\nSolid / dashed: focal / partner input placement. Outlined core: candidate; sampled every {interval} updates.\nOperational contact can coincide with candidate observation; outlines do not assign ancestry. Candidate ≠ confirmed inheritance.',ha='center',fontsize=8)
            fig.subplots_adjust(bottom=.26,top=.83,wspace=.25);legend(fig)
            export(fig,f'atlas2-encounter-{idx}',dark,manifest,{'run_id':rid,'crop':focus_box,'animation_crop':box,'annotated_times':keytimes,'selection':selection,'source':f'data/atlas-v2/replays/encounter-{idx}.npz'})


def inheritance_path(manifest):
    """Actual complete components along one declared path per recovered identity."""
    inheritance=json.loads((OUT/'inheritance.json').read_text())
    atlas=json.loads((OUT/'manifest.json').read_text())
    recovered={}
    for item in inheritance['items']:
        for outcome in item['outcomes']:
            if outcome['status']!='confirmed':continue
            identity=outcome['confirmation']['identity']
            recovered.setdefault(identity,[]).append((item,outcome))
    if not recovered:return
    rows=[]
    known={p['genotype']:pid for pid,p in atlas['panel'].items()}
    for number,identity in enumerate(sorted(recovered),1):
        item,outcome=min(recovered[identity],key=lambda pair:(pair[1]['source']['t'],pair[0]['run_id'],pair[0]['encounter_genotype'],pair[1]['source']['file']))
        source=outcome['source'];folder=OUT/outcome['folder']
        source_path=OUT/'runs'/item['run_id']/source['file']
        with np.load(source_path) as arrays:snapshot=arrays['snapshot'].copy()
        assert digest(snapshot)==source['snapshot_hash']
        snapshots=[snapshot];identities=[item['encounter_genotype']]
        stage_times=[source['t']];stage_files=[str(source_path.relative_to(ROOT))]
        stage_hashes=[source['snapshot_hash']];child_selections=[]
        prefix=[]
        for child_index in outcome['confirmation']['path']:
            node=next(n for n in outcome['nodes'] if n['path']==prefix)
            child=node['outcome']['children'][child_index]
            path=folder/f'node-{node["node"]:02d}.npz'
            with np.load(path) as arrays:
                component=arrays[f'child{child_index}'].copy()
            assert digest(component)==child['snapshot_hash']
            snapshots.append(component);identities.append(child['identity'])
            stage_times.append(child['detached_t']);stage_files.append(str(path.relative_to(ROOT)))
            stage_hashes.append(child['snapshot_hash'])
            child_selections.append({'node':node['node'],'child':child_index,'array_key':f'child{child_index}','detached_t':child['detached_t']})
            prefix=prefix+[child_index]
        assert identities[-1]==identity and stage_hashes[-1]==outcome['confirmation']['snapshot_hash']
        assert len(identities)>=3 and identities[-1]==identities[-2]==identities[-3]
        rows.append({'label':f'RV{number:02d}','identity':identity,'run_id':item['run_id'],
                     'known_panel_id':known.get(identity),'source':source,'snapshots':snapshots,
                     'identities':identities,'stage_times':stage_times,'stage_files':stage_files,
                     'stage_hashes':stage_hashes,'child_selections':child_selections,
                     'confirmation_path':outcome['confirmation']['path']})
    # Equal physical cell scale throughout: translate each complete saved component
    # onto a common padded canvas, with axes relative to its component origin.
    height=max(s.shape[0] for row in rows for s in row['snapshots'])+8
    width=max(s.shape[1] for row in rows for s in row['snapshots'])+8
    columns=max(len(row['snapshots']) for row in rows)
    for dark in THEMES:
        theme(dark);fig,axes=plt.subplots(len(rows),columns,figsize=(3.1*columns,3.4*len(rows)+1.8),squeeze=False)
        for row_number,row in enumerate(rows):
            for stage,(snapshot,identity,t) in enumerate(zip(row['snapshots'],row['identities'],row['stage_times'])):
                ax=axes[row_number,stage];canvas=np.zeros((height,width),dtype=np.uint8)
                canvas[4:4+snapshot.shape[0],4:4+snapshot.shape[1]]=snapshot
                ax.imshow(canvas,cmap=CMAP,norm=NORM,interpolation='nearest',extent=(-4.5,width-4.5,height-4.5,-4.5))
                if stage==0:title=f'{row["label"]} · native capture\nnative t={t}; core {identity.split(":",1)[0]}'
                else:
                    same=identity==row['identities'][stage-1]
                    role='stable transmission' if same else 'stabilized descendant'
                    title=f'{role}\nisolation +{t}; core {identity.split(":",1)[0]}'
                ax.set_title(title,fontsize=10);ax.set_xlabel('column / component cells',fontsize=9)
                ax.set_xticks([0,10,20]);ax.set_yticks([0,10,20])
                if stage==0:ax.set_ylabel('row / component cells',fontsize=9)
            for ax in axes[row_number,len(row['snapshots']):]:ax.set_axis_off()
            retained=all(i.split(':',1)[1]==row['identities'][0].split(':',1)[1] for i in row['identities'])
            novelty=f'known panel identity {row["known_panel_id"]}' if row['known_panel_id'] else 'absent from input catalogue'
            text=f'{row["label"]}: {novelty}; '+('native word retained' if retained else 'word changes after isolation')
            axes[row_number,0].text(0,-.28,text,transform=axes[row_number,0].transAxes,ha='left',fontsize=9)
        fig.suptitle(f'Actual recovered inheritance paths · {EXP}',fontsize=15)
        fig.text(.5,.16,'Complete occupied components and arms retained; same cell scale; coordinates relative to each component origin.\n'
                 'Native capture clock differs from each restarted isolation clock. Detachment sampled every 10 updates.\n'
                 'Final three components share one composite identity: two stable transmissions. Pair-level novelty; native ancestry ambiguous.\n'
                 'Serial isolation is an intervention. Benefit not assayed; these paths do not establish autonomous native inheritance.',ha='center',fontsize=8)
        fig.subplots_adjust(left=.07,right=.98,top=.89,bottom=.28,wspace=.27,hspace=.66);legend(fig)
        paths=[{k:v for k,v in row.items() if k!='snapshots'} for row in rows]
        export(fig,'atlas2-inheritance-path',dark,manifest,{'source':'data/atlas-v2/inheritance.json',
               'selection':'one per stable composite identity, sorted identity; earliest native capture, run ID, encounter identity, source file',
               'paths':paths,'shared_canvas_shape':[height,width],'cell_coordinate_origin':'complete component top-left before padding'})


def main():
    manifest=json.loads((FIG/'manifest.json').read_text());manifest['artifacts']=[x for x in manifest['artifacts'] if not x['file'].startswith('atlas2-')]
    render(manifest['artifacts']);write_json(FIG/'manifest.json',manifest);print('Fresh figures added; total',len(manifest['artifacts']))
if __name__=='__main__':main()
