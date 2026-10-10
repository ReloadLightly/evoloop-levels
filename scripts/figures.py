"""Chromatic Fields figures from raw evidence; no illustrative simulation data."""
import hashlib
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR',str(Path(__file__).resolve().parents[1]/'.cache/matplotlib'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap,BoundaryNorm,LinearSegmentedColormap,to_rgb
from matplotlib.font_manager import findfont
from PIL import Image,ImageDraw,ImageFont
from evoloop.engine import ROOT,advance,digest
from evoloop.tracking import detect

FIG=ROOT/'figures';STYLE=json.loads((ROOT/'configs/style.json').read_text())
CMAP=ListedColormap(STYLE['cell_states']);NORM=BoundaryNorm(np.arange(-.5,9.5),9)
THEMES=tuple(name=='dark' for name in STYLE['export_themes'])
QUANTITATIVE_CMAP=LinearSegmentedColormap.from_list(STYLE['quantitative_colormap'],STYLE['quantitative_stops'])

def quantitative_cmap():
    return QUANTITATIVE_CMAP

def annotation_color(fill):
    """Choose the more legible blue-family foreground for a labeled cell."""
    def luminance(color):
        rgb=np.array(to_rgb(color));linear=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4)
        return float(linear @ np.array([.2126,.7152,.0722]))
    background=luminance(fill)
    def contrast(color):
        foreground=luminance(color)
        return (max(background,foreground)+.05)/(min(background,foreground)+.05)
    return max((STYLE['ink'],STYLE['text']),key=contrast)
FONT_PATH='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
if not Path(FONT_PATH).exists():FONT_PATH=findfont('DejaVu Sans')
FONT=ImageFont.truetype(FONT_PATH,18);SMALL=ImageFont.truetype(FONT_PATH,14)
PALETTE=np.array([tuple(bytes.fromhex(c[1:])) for c in STYLE['cell_states']],dtype=np.uint8)

def theme(dark):
    bg=STYLE['ink'] if dark else STYLE['paper'];fg=STYLE['text'] if dark else STYLE['ink']
    heading=STYLE['heading'] if dark else STYLE['ink']
    plt.rcParams.update({'font.family':STYLE['font'],'font.size':10,'figure.facecolor':bg,
                         'axes.facecolor':bg,'axes.labelcolor':fg,'text.color':fg,'xtick.color':fg,
                         'ytick.color':fg,'axes.edgecolor':STYLE['axis'],'axes.titlecolor':heading,
                         'axes.prop_cycle':plt.cycler(color=list(STYLE['series'].values())),
                         'svg.fonttype':'none','pdf.fonttype':42})
    return bg,fg

def save(fig,name,dark,manifest,experiment,extra=None):
    suffix='dark' if dark else 'light'
    if fig._suptitle is not None:fig._suptitle.set_color(STYLE['heading'] if dark else STYLE['ink'])
    for ext in ('svg','pdf','png'):
        path=FIG/f'{name}-{suffix}.{ext}';fig.savefig(path,dpi=180,bbox_inches='tight',facecolor=fig.get_facecolor())
        manifest.append({'file':path.name,'experiments':experiment,'command':'OPENBLAS_NUM_THREADS=1 python -m scripts.figures',
                         'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'style_sha256':hashlib.sha256((ROOT/'configs/style.json').read_bytes()).hexdigest(),**(extra or {})})
    plt.close(fig)

def legend(fig):
    names=STYLE['cell_state_meaning'];handles=[plt.Line2D([0],[0],color=STYLE['cell_states'][i],marker='s',linestyle='',markersize=7,
                                                           markeredgecolor=plt.rcParams['text.color'],markeredgewidth=.5,
                                                           label=f'{i} {names[i]}') for i in range(9)]
    fig.legend(handles=handles,loc='lower center',ncol=5,fontsize=8,frameon=False)

def animation(frames,times,path,title,subtitle,scale=3,contact_t=None):
    images=[]
    for g,t in zip(frames,times):
        raw=Image.fromarray(PALETTE[g]).resize((g.shape[1]*scale,g.shape[0]*scale),resample=Image.Resampling.NEAREST)
        canvas_width=max(640,raw.width);offset=(canvas_width-raw.width)//2
        canvas=Image.new('RGB',(canvas_width,raw.height+168),STYLE['ink']);canvas.paste(raw,(offset,80))
        draw=ImageDraw.Draw(canvas);draw.text((18,12),title,font=FONT,fill=STYLE['heading'])
        if offset:draw.rectangle((offset-1,79,offset+raw.width,80+raw.height),outline=STYLE['cobalt'],width=1)
        state='before contact' if contact_t is not None and t<contact_t else f'contact first observed t={contact_t}' if contact_t is not None else 'synchronous original evoloop'
        draw.text((18,40),f't = {int(t):,} updates  |  {state}',font=SMALL,fill=STYLE['text'])
        draw.text((18,60),subtitle,font=SMALL,fill=STYLE['text'])
        draw.text((18,raw.height+85),f'literal state colors | {g.shape[1]} × {g.shape[0]} cells | 10-cell scale',font=SMALL,fill=STYLE['text'])
        draw.line((canvas_width-50,raw.height+94,canvas_width-50+10*scale,raw.height+94),fill=STYLE['text'],width=2)
        shorts=['quiescent','carrier','sheath','junction','turn','messenger','cord','growth','dissolve']
        for state,short in enumerate(shorts):
            col=state%5;row=state//5;xx=12+col*(canvas_width//5);yy=raw.height+112+row*23
            draw.rectangle((xx,yy+2,xx+10,yy+12),fill=STYLE['cell_states'][state],outline=STYLE['text'],width=1)
            draw.text((xx+14,yy),f'{state} {short}',font=ImageFont.truetype(FONT_PATH,11),fill=STYLE['text'])
        images.append(canvas)
    images[0].save(path,save_all=True,append_images=images[1:],duration=130,loop=0,lossless=True,method=6)

def overview(manifest):
    a=np.load(ROOT/'data/exploration/world.npz');frames=a['frames'];times=a['times']
    path=FIG/'world-overview.webp'
    animation(frames,times,path,'CHROMATIC FIELDS / Natural exploratory history','EXP-discovery-001 | S13 lineage | 160 × 160 periodic world',scale=4)
    manifest.append({'file':path.name,'experiments':['EXP-discovery-001'],'command':'OPENBLAS_NUM_THREADS=1 python -m scripts.figures',
                     'source':'data/exploration/world.npz','sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    for dark in THEMES:
        theme(dark);fig,axes=plt.subplots(1,4,figsize=(13,4.7))
        indices=np.linspace(0,len(frames)-1,4,dtype=int)
        for ax,k in zip(axes,indices):
            ax.imshow(frames[k],cmap=CMAP,norm=NORM,interpolation='nearest');ax.set_title(f't = {times[k]:,}')
            ax.set_xticks([0,80,159]);ax.set_yticks([0,80,159]);ax.set_xlabel('column / cells')
        axes[0].set_ylabel('row / cells')
        fig.suptitle('Natural exploratory history · EXP-discovery-001',fontsize=15)
        fig.subplots_adjust(bottom=.27,top=.84,wspace=.26);legend(fig)
        save(fig,'world-overview',dark,manifest,['EXP-discovery-001'])

def exploratory_inheritance(manifest):
    d=json.loads((ROOT/'data/exploration/discovery.json').read_text());p=d['panel'][1]
    a=np.load(ROOT/'data/exploration/N01.npz');test=p['isolation']
    arrays=[a['source_grid'],a['first_generation'],a['second_generation'],a['third_generation']]
    cores=[p['core']]+[test[f'generation{i}']['core'] for i in (1,2,3)]
    labels=['Natural transient','Isolated stable descendant','Stable transmission 1','Stable transmission 2']
    ts=[p['t']]+[test[f'generation{i}']['detached_first_seen_t'] for i in (1,2,3)]
    for dark in THEMES:
        theme(dark);fig,axes=plt.subplots(1,4,figsize=(12,4.8))
        for ax,g,core,label,t in zip(axes,arrays,cores,labels,ts):
            y,x,h,w=core;sy=max(0,y-6);sx=max(0,x-6);ey=min(g.shape[0],y+h+6);ex=min(g.shape[1],x+w+6)
            ax.imshow(g[sy:ey,sx:ex],cmap=CMAP,norm=NORM,interpolation='nearest',extent=(sx-.5,ex-.5,ey-.5,sy-.5))
            ax.set_title(f'{label}\nt={t}, core {h}×{w}',fontsize=10);ax.set_xlabel('column / cells')
        axes[0].set_ylabel('row / cells')
        fig.suptitle('A natural changed word survives morphological stabilization',fontsize=14)
        fig.text(.5,.21,'EXP-discovery-001 · source uses world time; descendant clocks restart at isolation · 10-update detection\nSource 11×13 and stable 12×12 share a signal word, different from S13.',ha='center',fontsize=8)
        fig.subplots_adjust(bottom=.36,top=.8,wspace=.32);legend(fig)
        save(fig,'inheritance-path',dark,manifest,['EXP-discovery-001'])

def matrix_and_funnel(analysis,manifest):
    organisms=['S13','N01']
    for dark in THEMES:
        bg,fg=theme(dark);fig,axes=plt.subplots(2,2,figsize=(10,8.7))
        for row,(outcome,name) in enumerate([('candidate_signal','candidate signal novelty'),('confirmed_signal','confirmed isolated inheritance')]):
            for col,split in enumerate(['main','heldout']):
                ax=axes[row,col];panel=analysis['panels'][split];mat=np.array(panel['models'][outcome]['rates'])
                im=ax.imshow(mat,vmin=0,vmax=1,cmap=quantitative_cmap())
                ax.set_xticks([0,1],organisms);ax.set_yticks([0,1],organisms);ax.set_xlabel('partner');ax.set_ylabel('focal slot')
                ax.set_title(f'{split.capitalize()} · {name}',fontsize=10)
                for i,p in enumerate(organisms):
                    for j,q in enumerate(organisms):
                        c=panel['cells'][f'{p}|{q}'];color=annotation_color(quantitative_cmap()(mat[i,j]))
                        ax.text(j,i,f'{c[outcome]} / {c["n"]}\n{mat[i,j]:.1%}',ha='center',va='center',color=color,fontsize=12)
                dd=panel['models'][outcome]['difference_of_differences']
                ax.text(.5,-.24,f'Interaction contrast ΔΔ = {dd:+.3f}',transform=ax.transAxes,ha='center',fontsize=9)
        fig.subplots_adjust(left=.09,right=.81,bottom=.13,top=.9,hspace=.68,wspace=.3)
        cax=fig.add_axes([.87,.22,.024,.54]);fig.colorbar(im,cax=cax,label='fraction of complete starting configurations')
        fig.suptitle('Pair-level outcomes · EXP-atlas-001',fontsize=15)
        fig.text(.5,.025,'Signal-word audit added during acquisition; composite endpoint agrees here.\nZero confirmations leave 7 run/identity candidates unresolved. Finite panel; ancestry ambiguous; benefit pending.',ha='center',fontsize=7.5)
        save(fig,'outcome-matrix',dark,manifest,['EXP-atlas-001'])
        fig,(ax,pending)=plt.subplots(1,2,figsize=(9,4.6),gridspec_kw={'width_ratios':[3,1]});z=analysis['near'];n=z['n']
        labels=['Candidate\nchannel novelty','Complete component\navailable','Confirmed isolated\ninheritance']
        vals=[z['candidate_signal'],z['eligible_signal'],z['confirmed_signal']]
        ax.bar(np.arange(3),vals,color=[STYLE['status']['candidate'],STYLE['status']['eligible'],STYLE['status']['confirmed']],width=.62)
        for i,v in enumerate(vals):ax.text(i,v+.15,f'{v}/{n}',ha='center',fontweight='bold')
        ax.set_ylim(0,max(vals)+1.3);ax.set_xticks(np.arange(3),labels);ax.set_ylabel('near configurations (main + held-out)')
        pending.set_axis_off()
        pending.add_patch(plt.Rectangle((.04,.12),.92,.7,transform=pending.transAxes,fill=False,edgecolor=fg,hatch='///',alpha=.3))
        pending.text(.5,.47,'BENEFIT\nNOT ASSAYED\n\nYield unknown',transform=pending.transAxes,ha='center',va='center',fontweight='bold',fontsize=10)
        fig.suptitle('Novelty → inheritance → ecological benefit',fontsize=15)
        ax.spines[['top','right']].set_visible(False)
        fig.text(.5,.02,f'EXP-atlas-001 · all {n} near states retained · {z["unresolved_candidates"]} unresolved run/genotype candidates',ha='center',fontsize=9)
        fig.tight_layout(rect=(0,.06,1,.94));save(fig,'evidence-stages',dark,manifest,['EXP-atlas-001'])

def replays(rows,manifest):
    near=[r for r in rows if r['treatment']=='near'];selected=[]
    # Selection is for illustrations AFTER analysis, not the statistical panel.
    for criterion in (lambda r:r['candidate'] and r['first_detached_offspring_paths']>0,
                      lambda r:r['final_closed_cores']==0,
                      lambda r:not r['candidate'] and r['final_closed_cores']>0 and r['contact']):
        eligible=[r for r in near if criterion(r) and r['run_id'] not in selected]
        if eligible:selected.append(sorted(eligible,key=lambda r:r['run_id'])[0]['run_id'])
    if len(selected)<3:selected.extend(r['run_id'] for r in near if r['run_id'] not in selected)
    for idx,rid in enumerate(selected[:3],1):
        result=json.loads((ROOT/f'data/atlas/runs/{rid}/result.json').read_text())
        row=next(r for r in rows if r['run_id']==rid);g=np.load(ROOT/f'data/atlas/initial/{rid}.npz')['grid'].copy()
        # Full replay regeneration verifies final state; crop is FIXED across frames.
        times=np.arange(0,1601,20);frames=[]
        for t in times:
            if t:advance(g,20)
            frames.append(g.copy())
        assert digest(g)==result['final_hash']
        occupied=np.any(np.array(frames)!=0,axis=0);y,x=np.nonzero(occupied)
        sy=max(0,int(y.min())-6);sx=max(0,int(x.min())-6);ey=min(g.shape[0],int(y.max())+7);ex=min(g.shape[1],int(x.max())+7)
        views=[f[sy:ey,sx:ex] for f in frames]
        path=FIG/f'encounter-{idx}.webp'
        status='isolated inherited novelty confirmed' if row['confirmed'] else 'candidate / inheritance unresolved' if row['candidate'] else 'no observed channel novelty'
        animation(views,times,path,f'{row["focal"]} × {row["partner"]} / {row["geometry"]}',f'EXP-atlas-001 | {status}',scale=3,contact_t=result['contact_t'])
        manifest.append({'file':path.name,'experiments':['EXP-atlas-001'],'run_id':rid,'crop':[sy,sx,ey-sy,ex-sx],
                         'command':'OPENBLAS_NUM_THREADS=1 python -m scripts.figures','selection':'post-analysis illustrative selection',
                         'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        candidate_time=min((c['first_observed_t'] for c in result['candidates']),default=1600)
        target_times=[0,result['contact_t'] or 0,candidate_time]
        for dark in THEMES:
            theme(dark);fig,axes=plt.subplots(1,3,figsize=(13,5.7))
            for ax,t,label in zip(axes,target_times,['Inputs','Operational contact','First candidate' if candidate_time<1600 else 'Observation horizon']):
                a=np.load(ROOT/f'data/atlas/initial/{rid}.npz')['grid'].copy();advance(a,t)
                ax.imshow(a[sy:ey,sx:ex],cmap=CMAP,norm=NORM,interpolation='nearest',extent=(sx-.5,ex-.5,ey-.5,sy-.5))
                ax.set_title(f'{label} · t={t}');ax.set_xlabel('column / cells')
                for o in detect(a):
                    y0,x0,h,w=o['bbox'];color=STYLE['annotation']['novel_core'] if o['genotype'] not in [z['genotype'] for z in result['initial_cores']] else STYLE['annotation']['known_core']
                    ax.add_patch(plt.Rectangle((x0-.5,y0-.5),w,h,fill=False,edgecolor=color,lw=.8,alpha=.8))
                if t==0:
                    for slot,(box,tag,color) in enumerate(zip(result['input_boxes'],['focal','partner'],[STYLE['lineage_overlay']['focal'],STYLE['lineage_overlay']['partner']])):
                        if box is None:continue
                        y0,x0,h,w=box;ax.add_patch(plt.Rectangle((x0-.5,y0-.5),w,h,fill=False,edgecolor=color,lw=1.2,linestyle='--'))
                        ax.text(.03,.95-slot*.075,tag,transform=ax.transAxes,fontsize=8,color=color,va='top')
            axes[0].set_ylabel('row / cells')
            fig.suptitle(f'{row["focal"]} × {row["partner"]} · {row["geometry"]} · phase +{row["phase"]}',fontsize=15)
            fig.text(.5,.19,f'{rid}\n{status}; benefit pending. Dashed boxes: input slots. Solid boxes: detected cores (brighter blue novel/unknown).',ha='center',fontsize=8)
            fig.subplots_adjust(bottom=.34,top=.86,wspace=.25);legend(fig)
            save(fig,f'encounter-{idx}',dark,manifest,['EXP-atlas-001'],{'run_id':rid,'crop':[sy,sx,ey-sy,ex-sx]})

def main():
    FIG.mkdir(exist_ok=True);manifest=[];overview(manifest);exploratory_inheritance(manifest)
    if (ROOT/'data/atlas/analysis.json').exists():
        analysis=json.loads((ROOT/'data/atlas/analysis.json').read_text());rows=json.loads((ROOT/'data/atlas/outcomes.json').read_text())
        matrix_and_funnel(analysis,manifest);replays(rows,manifest)
    if (ROOT/'data/fate-calibration/analysis.json').exists():
        from scripts.figures_fate import render
        render(manifest)
    if (ROOT/'data/panel-v2/discovery.json').exists():
        from scripts.figures_panel import render as render_panel
        render_panel(manifest)
    if (ROOT/'data/atlas-v2/analysis.json').exists():
        from scripts.figures_fresh_atlas import render as render_fresh
        render_fresh(manifest)
    # Remove obsolete generated light variants after the canonical render succeeds.
    if STYLE['export_themes']==['dark']:
        for obsolete in FIG.glob('*-light.*'):obsolete.unlink()
    (FIG/'manifest.json').write_text(json.dumps({'style':'configs/style.json','style_sha256':hashlib.sha256((ROOT/'configs/style.json').read_bytes()).hexdigest(),
                                               'font_sha256':hashlib.sha256(Path(FONT_PATH).read_bytes()).hexdigest(),
                                               'font_license':'docs/font-license.txt','artifacts':manifest},indent=2)+'\n')
    print('Rendered',len(manifest),'traceable artifacts')

if __name__=='__main__':main()
