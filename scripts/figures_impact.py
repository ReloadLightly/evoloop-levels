"""Impact-matched population figures from frozen grids and completed observations.

These are constructed microcolonies and structural registry scores. The renderer
never advances the CA, assigns ancestry, or changes scientific classifications.
"""
import argparse
import gc
import hashlib
import json
from fractions import Fraction

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from evoloop.engine import ROOT, digest
from scripts.figures import (
    FIG, STYLE, THEMES, CMAP, NORM, PALETTE, FONT_PATH,
    theme, save, legend, quantitative_cmap, annotation_color,
)
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.ticker import MaxNLocator

OUT = ROOT/'data/impact-v1'
PREFIX = 'impact1-'
COMMAND = 'OPENBLAS_NUM_THREADS=1 python -m scripts.figures_impact'
BASE = [OUT/'manifest.json', ROOT/'configs/impact-v1.json', ROOT/'protocols/009-impact-matched-paired-assay.md']


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_hashes(paths):
    return {str(p.relative_to(ROOT)): sha(p) for p in sorted(set(paths))}


def export(fig, name, dark, artifacts, experiments, paths, metadata=None):
    save(fig, PREFIX+name, dark, artifacts, experiments,
         {'command': COMMAND, 'source_sha256': source_hashes(BASE+paths), **(metadata or {})})
    gc.collect()


def conditions(m, split=None):
    return [c for c in m['config']['conditions'] if split is None or c['split']==split]


def fraction(record):
    return None if record is None else Fraction(record['numerator'],record['denominator'])


def value(record):
    f = fraction(record)
    return np.nan if f is None else float(f)


def matrix(ax, values, texts, states, column_labels, *, upper=None, font=9):
    cmap = quantitative_cmap().copy(); cmap.set_bad(STYLE['status']['missing'])
    finite = values[np.isfinite(values)]
    maximum = max(1.,float(finite.max())) if len(finite) else 1.
    im = ax.imshow(values,cmap=cmap,vmin=0,vmax=upper or maximum,interpolation='nearest',aspect='auto')
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            color = annotation_color(cmap(values[i,j]/im.norm.vmax)) if np.isfinite(values[i,j]) else plt.rcParams['text.color']
            if not np.isfinite(values[i,j]):
                ax.add_patch(Rectangle((j-.5,i-.5),1,1,fill=False,edgecolor=color,hatch='///',lw=0,alpha=.25))
            ax.text(j,i,texts[i][j],ha='center',va='center',fontsize=font,color=color)
    ax.set_xticks(range(len(column_labels)),column_labels); ax.set_yticks(range(len(states)),states)
    return im


def exposure(m, artifacts):
    states=m['config']['states']; cols=conditions(m)
    lookup={(p['state'],p['condition']['id']):p for p in m['preparations']}
    values=np.full((len(states),len(cols)),np.nan); texts=[]; paths=[]; successful=0
    for i,state in enumerate(states):
        row=[]
        for j,c in enumerate(cols):
            p=lookup[state,c['id']]; r=p['impact']; path=OUT/'prepared'/f'{p["pair_id"]}.npz'; paths.append(path)
            with np.load(path) as arrays:
                before=arrays['before']; after=arrays['after']; mask=arrays['mask']
                assert digest(before)==r['before_hash'] and digest(after)==r['after_hash'] and digest(mask)==r['mask_hash']
                assert np.array_equal(after,np.where(mask,0,before))
                assert int(np.count_nonzero(before)-np.count_nonzero(after))==r['removed_occupied_cells']
            success=r['matched_impact'] and r['remaining_components_unchanged']; successful+=success
            values[i,j]=r['removed_occupied_cells']/r['occupied_before'] if r['occupied_before'] else np.nan
            row.append(f'{r["registered_before"]}→{r["registered_after"]} cores\n{r["removed_occupied_cells"]}/{r["occupied_before"]} cells\n'+('MATCHED' if success else 'UNRESOLVED'))
        texts.append(row)
    checks=len(m['equivalence_checks']); distinct=sum(p['before'] is None and p['after'] is None for p in m['equivalence_checks'])
    labels=[c['id'].replace('development','dev').replace('confirmation','confirm').replace('calibration','cal')+f'\nage {c["age"]}' for c in cols]
    for dark in THEMES:
        theme(dark); fig,ax=plt.subplots(figsize=(13,6.8))
        im=matrix(ax,values,texts,states,labels,upper=1,font=9)
        ax.set_ylabel('representative complete state');ax.set_xlabel('fixed geometry and elapsed preparation age / updates')
        ax.axvline(1.5,color=STYLE['text'],lw=1);ax.axvline(3.5,color=STYLE['text'],lw=1)
        ax.set_title(f'Matched whole-component exposure · {m["benefit_experiment_id"]}',fontsize=14,pad=16)
        fig.subplots_adjust(left=.07,right=.87,bottom=.28,top=.88)
        cax=fig.add_axes([.90,.35,.018,.46]);fig.colorbar(im,cax=cax,label='occupied-cell fraction removed')
        fig.text(.5,.065,f'{successful}/{len(m["preparations"])} preparations matched: designated complete component removed, including arms; other components unchanged.\n'
                 f'{distinct}/{checks} within-state development/confirmation comparisons are nonequivalent in both complete U and D states; {len(m["cross_state_aliases"])} cross-state aliases recorded.\n'
                 'Three identical complete clones are constructed, not native histories. Ages are elapsed updates, not homologous biological phases.\n'
                 'One-third structural loss matches counts and cell fraction, not reproductive value, absolute cell counts, or future effects.',ha='center',fontsize=8.5)
        export(fig,'exposure',dark,artifacts,[m['calibration_experiment_id'],m['benefit_experiment_id']],paths,
               {'matched_preparations':successful,'denominator':len(m['preparations']),'distinct_confirmation_checks':distinct,'equivalence_check_count':checks})


def calibration(c,m,artifacts):
    states=m['config']['states']; conds=conditions(m,'calibration'); times=m['config']['calibration']['source_times'];gate=m['config']['calibration']['gate']
    cols=[(q,t) for q in conds for t in times]; lookup={}
    for s in c['strata']:
        cond=next(q['id'] for q in conds if '-'+q['id']+'-' in s['stratum_id'])
        lookup[s['state'],cond,s['t']]=s
    values=np.full((len(states),len(cols)),np.nan); texts=[]
    for i,state in enumerate(states):
        row=[]
        for j,(q,t) in enumerate(cols):
            s=lookup[state,q['id'],t]; n=s['selected_cores']
            if n:values[i,j]=s['confirmed']/n
            row.append(f'{s["confirmed"]}/{n}\n{s["available_cores"]} available' if n else 'EMPTY\n0 selected')
        texts.append(row)
    paths=[OUT/'calibration-analysis.json',OUT/'calibration.json']
    for dark in THEMES:
        theme(dark);fig,(ax,card)=plt.subplots(1,2,figsize=(13,7),gridspec_kw={'width_ratios':[5.6,2.3]})
        im=matrix(ax,values,texts,states,[q['id'].replace('calibration','cal')+f'\nt={t}' for q,t in cols],upper=1,font=8)
        ax.axvline(len(times)-.5,color=STYLE['text'],lw=1)
        ax.set_ylabel('representative complete state');ax.set_xlabel('selected calibration stratum / post-removal updates')
        ax.set_title('Original identity recovered / selected scored cores',fontsize=11)
        card.set_axis_off();card.add_patch(Rectangle((.02,.02),.96,.96,transform=card.transAxes,fill=False,edgecolor=STYLE['axis']))
        labels=[('all_baselines',f'all {gate["baseline_recoveries_required"]} phase controls'),('overall_recovery',f'overall ≥{gate["overall_scored_recovery_fraction"]:.0%}'),
                ('each_starting_state',f'each state ≥{gate["per_starting_state_recovery_fraction"]:.0%}'),('each_nonempty_stratum',f'each nonempty stratum\n≥{gate["minimum_confirmed_per_nonempty_scored_stratum"]} recovery')]
        lines=['CALIBRATION '+('PASSED' if c['gate_passed'] else 'NOT PASSED'),' ',f'{c["baseline_confirmed"]}/{c["baseline_total"]} phase controls recover',
               f'{c["scored_eligible"]}/{c["scored_selected"]} extractable selected cores',f'{c["scored_confirmed"]}/{c["scored_selected"]} original-identity recoveries',' ']
        lines += [('PASS' if c['gate_checks'][key] else 'FAIL')+': '+label for key,label in labels]
        lines += [' ']+[f'{r["state"]}: {r["confirmed"]}/{r["selected"]} recovered' for r in c['by_state']]
        card.text(.5,.50,'\n'.join(lines),transform=card.transAxes,ha='center',va='center',fontsize=9)
        fig.suptitle(f'Selected isolation recovery · {m["calibration_experiment_id"]}',fontsize=14)
        fig.subplots_adjust(left=.07,right=.97,top=.86,bottom=.25,wspace=.35)
        cax=fig.add_axes([.11,.135,.43,.018]);fig.colorbar(im,cax=cax,orientation='horizontal',label='confirmed / selected scored cores')
        fig.text(.5,.035,'First and last distinct cores selected prospectively. Ineligible and nonconfirming selections remain in denominators; empty ≠ failed.\n'
                 f'{c["unscored_confirmed"]}/{c["unscored_selected"]} unscored selections recovered any stable identity. Recovery is bounded serial isolation, not native viability proof.\n'
                 'Nested deterministic observations; unresolved searches are not proven nonviable. No confidence intervals or independent histories.',ha='center',fontsize=8)
        export(fig,'calibration',dark,artifacts,[m['calibration_experiment_id']],paths,{'gate':gate,'gate_passed':c['gate_passed'],'states':states,'stratum_columns':[(q['id'],t) for q,t in cols]})


def score_matrices(a,m,artifacts):
    states=m['config']['states']; conds=[q for q in conditions(m) if q['split']!='calibration']
    lookup={(r['state'],r['condition']):r for r in a['conditions']}
    retention=np.array([[value(lookup[s,q['id']]['retention']) for q in conds] for s in states])
    damaged=np.array([[lookup[s,q['id']]['D_mean'] for q in conds] for s in states])
    rt=[];dt=[]
    for s in states:
        rrow=[];drow=[]
        for q in conds:
            r=lookup[s,q['id']];f=fraction(r['retention'])
            rrow.append('UNDEFINED\nU sum = 0' if f is None else f'{float(f):.3f}\n{f.numerator}/{f.denominator}')
            drow.append(f'{r["D_mean"]:.3f}\nD={r["D_sum"]}; U={r["U_sum"]}')
        rt.append(rrow);dt.append(drow)
    labels=[q['id'].replace('development','dev').replace('confirmation','confirm')+f'\nage {q["age"]}' for q in conds]
    for dark in THEMES:
        theme(dark);fig,axes=plt.subplots(1,2,figsize=(13,6.6))
        fig.subplots_adjust(left=.065,right=.98,top=.85,bottom=.31,wspace=.28)
        for ax,values,texts,title,label in [(axes[0],retention,rt,'Per-condition retention R = D/U','registered-score retention ratio'),
                                          (axes[1],damaged,dt,'Absolute disturbed score','mean registered closed-core count')]:
            im=matrix(ax,values,texts,states,labels,font=9);ax.axvline(1.5,color=STYLE['text'],lw=1);ax.set_title(title,fontsize=12)
            ax.set_ylabel('complete representative state');ax.tick_params(axis='x',labelsize=8)
            box=ax.get_position();cax=fig.add_axes([box.x0, .16,box.width,.018]);fig.colorbar(im,cax=cax,orientation='horizontal',label=label)
        fig.suptitle(f'Paired registered-population scores · {a["experiment_id"]}',fontsize=14)
        fig.text(.5,.035,'D: one complete clone removed at t=0; U: unchanged matched three-clone colony. Each condition has 81 equal samples (0,20,…,1600).\n'
                 'Ratios display exact reduced fractions; zero U makes retention undefined, never zero. D/U>1 may reflect release from crowding.\n'
                 'Fixed four-identity structural registry; V01/RV01 share an identity. Unknown and unregistered types omitted; not total viable population.\n'
                 'Ages denote completed preparation updates. Finite constructed conditions, not independent ecological histories or evolvability measures.',ha='center',fontsize=8)
        export(fig,'score-matrices',dark,artifacts,[a['experiment_id']], [OUT/'analysis.json',OUT/'calibration-analysis.json'],
               {'states':states,'condition_order':[q['id'] for q in conds],'ratio':'exact per-condition integer D_sum/U_sum','sample_count_per_condition':81})


def contrasts(a,m,artifacts):
    paths=[OUT/'analysis.json',OUT/'calibration-analysis.json']; metrics=[('candidate_minus_inputs_retention','candidate − input panel retention'),('candidate_minus_inputs_D','candidate − input absolute D mean')]
    for dark in THEMES:
        theme(dark);fig,axes=plt.subplots(2,2,figsize=(12,9),squeeze=False)
        for column,(key,label) in enumerate(metrics):
            allvals=[value(v) if column==0 else v for p in a['pairs'] for panel in p['panels'].values() for v in panel[key].values()]
            finite=[v for v in allvals if np.isfinite(v)];low=min([0]+finite);high=max([0]+finite);padding=max(.02,(high-low)*.2)
            for row,p in enumerate(a['pairs']):
                ax=axes[row,column];x=np.arange(len(p['inputs']))
                for offset,split,color,hatch in [(-.18,'development',STYLE['series']['primary'],None),(.18,'confirmation',STYLE['series']['tertiary'],'//')]:
                    values=[value(p['panels'][split][key][s]) if column==0 else p['panels'][split][key][s] for s in p['inputs']]
                    for j,v in enumerate(values):
                        if not np.isfinite(v):ax.text(j+offset,0,'UNDEFINED',ha='center',va='bottom',fontsize=7,rotation=90);continue
                        ax.bar(j+offset,v,width=.32,color=color,hatch=hatch,edgecolor=STYLE['axis'],label=split if j==0 else None)
                        ax.annotate(f'{v:+.4g}',(j+offset,v),xytext=(0,5 if v>=0 else -5),textcoords='offset points',ha='center',va='bottom' if v>=0 else 'top',fontsize=9)
                ax.axhline(0,color=STYLE['annotation']['target'],lw=1);ax.set_ylim(low-padding,high+padding);ax.set_xticks(x,[f'minus {s}' for s in p['inputs']]);ax.set_ylabel(label,fontsize=9)
                ax.set_title(f'{p["candidate"]}: '+('relative retention' if column==0 else 'absolute disturbed score'),fontsize=12)
                keycriterion='relative_criterion' if column==0 else 'absolute_criterion'
                ax.text(.5,-.20,'Strict both-input / both-panel criterion: '+('MET' if p[keycriterion] else 'NOT MET'),transform=ax.transAxes,ha='center',fontsize=8)
                if row==0:ax.legend(loc='upper center',bbox_to_anchor=(.5,1.25),ncol=2,fontsize=8,frameon=False)
        outcomes='; '.join(p['candidate']+': '+('UNRESOLVED' if p['joint_confirmed'] is None else 'JOINT MET' if p['joint_confirmed'] else 'JOINT NOT MET') for p in a['pairs'])
        fig.suptitle(f'Both-input exact panel contrasts · {a["experiment_id"]}',fontsize=14)
        fig.text(.5,.06,outcomes+f'. Calibration: {"PASSED" if a["calibration"]["gate_passed"] else "NOT PASSED"}.\n'
                 'Panel retention = arithmetic mean of two exact D/U fractions, not pooled D/U. Absolute D panel means use 162 samples.\n'
                 'Exact strict signs determine criteria; ties fail. Joint requires relative + absolute advantage and passed recovery/exposure/non-equivalence.\n'
                 'Conditional structural population performance, not evolvability. Genetic ancestry ambiguous; finite deterministic contrasts, no confidence intervals.',ha='center',fontsize=8.2)
        fig.subplots_adjust(left=.08,right=.98,top=.83,bottom=.24,hspace=.65,wspace=.27)
        export(fig,'contrasts',dark,artifacts,[a['experiment_id'],m['calibration_experiment_id']],paths,
               {'retention_aggregation':'arithmetic mean of two exact per-condition ratios','criteria':'strict both inputs in both panels; exact ties fail','joint_status':{p['candidate']:p['joint_confirmed'] for p in a['pairs']}})


def result_records(m):
    specs=[r for r in m['runs'] if r['split']!='calibration'];records={};paths=[]
    for s in specs:
        path=OUT/s['split']/s['run_id']/'result.json';paths.append(path);records[s['state'],s['condition']['id'],s['treatment']]=read(path)
    return records,paths


def curves(m,artifacts):
    states=m['config']['states'];conds=[q for q in conditions(m) if q['split']!='calibration'];records,paths=result_records(m)
    maximum=max(sample['scored_cores'] for r in records.values() for sample in r['samples'])
    for dark in THEMES:
        theme(dark);fig,axes=plt.subplots(len(states),len(conds),figsize=(13,11),squeeze=False,sharex=True,sharey=True)
        for i,s in enumerate(states):
            for j,c in enumerate(conds):
                ax=axes[i,j]
                for treatment,color,ls in [('D',STYLE['series']['primary'],'-'),('U',STYLE['series']['tertiary'],'--')]:
                    r=records[s,c['id'],treatment];xs=[p['t'] for p in r['samples']];ys=[p['scored_cores'] for p in r['samples']]
                    ax.step(xs,ys,where='post',color=color,ls=ls,lw=1.25,label=treatment)
                ax.set_ylim(0,maximum+1);ax.set_xlim(0,m['config']['horizon']);ax.set_xticks([0,800,1600]);ax.yaxis.set_major_locator(MaxNLocator(nbins=4,integer=True));ax.tick_params(labelsize=8)
                if i==0:ax.set_title(c['id']+f'\nage {c["age"]}',fontsize=10)
                if j==0:ax.set_ylabel(s+'\nregistered cores',fontsize=9)
                if i==len(states)-1:ax.set_xlabel('post-removal updates',fontsize=9)
        handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,['D: component removed at t=0','U: matched undisturbed'],loc='lower center',bbox_to_anchor=(.5,.065),ncol=2,frameon=False,fontsize=9)
        fig.suptitle(f'Paired CA continuation of constructed colonies · {m["benefit_experiment_id"]}',fontsize=14)
        fig.text(.5,.023,'Sampled counts every 20 updates; step segments only locate observations, not exact event times. All 40 worlds shown on common count axes.\n'
                 'Recognized fixed-registry closed cores, not certified native viability or ancestry. No further interventions; no independent-history uncertainty.',ha='center',fontsize=8)
        fig.subplots_adjust(left=.07,right=.98,top=.89,bottom=.14,wspace=.15,hspace=.25)
        export(fig,'paired-curves',dark,artifacts,[m['benefit_experiment_id']],paths,{'metric':'sampled registered closed cores','sampling_interval':m['config']['sample_interval'],'run_ids':[r['run_id'] for r in m['runs'] if r['split']!='calibration']})


def replay_records(m,selection):
    c=next(c for c in conditions(m) if c['id']==selection['condition']);state=selection['state'];pair=f'{state}-{c["id"]}'
    prepared=OUT/'prepared'/f'{pair}.npz'
    with np.load(prepared) as a:before=a['before'].copy();after=a['after'].copy();mask=a['mask'].copy()
    paths=[prepared];grids={};times=None
    for treatment in ('D','U'):
        folder=OUT/c['split']/f'{pair}-{treatment}';path=folder/'replay.npz';paths.extend([path,folder/'result.json'])
        with np.load(path) as a:
            grids[treatment]=a['frames'].copy();tt=a['times'].copy()
        if times is None:times=tt
        else:assert np.array_equal(times,tt)
    assert np.array_equal(grids['D'][0],after) and np.array_equal(grids['U'][0],before)
    return c,pair,before,after,mask,grids,times,paths


def raw_states(m,artifacts):
    selected=m['config']['replays'];cases=[];paths=[]
    for selection in selected:
        c,pair,before,after,mask,grids,times,source=replay_records(m,selection);paths.extend(source)
        impact=next(p['impact'] for p in m['preparations'] if p['pair_id']==pair)
        cases.append((selection,c,pair,before,after,mask,grids,times,impact))
    for dark in THEMES:
        theme(dark);fig,axes=plt.subplots(len(cases),4,figsize=(13,10.8),squeeze=False)
        for i,(sel,c,pair,before,after,mask,grids,times,impact) in enumerate(cases):
            selectedgrids=[before,after,grids['D'][-1],grids['U'][-1]]
            names=['U / shared pre-removal · t=0','D / after removal · t=0',f'D / t={int(times[-1])}',f'U / t={int(times[-1])}']
            for j,(grid,title) in enumerate(zip(selectedgrids,names)):
                ax=axes[i,j];ax.imshow(grid,cmap=CMAP,norm=NORM,interpolation='nearest');ax.set_title(f'{sel["state"]} · {title}',fontsize=9)
                if j<2:ax.contour(mask,levels=[.5],colors=[STYLE['annotation']['target']],linewidths=.65,linestyles='--')
                ax.set_xticks([0,96,191]);ax.set_yticks([0,96,191]);ax.set_xlabel('column / cells',fontsize=8)
                if j==0:ax.set_ylabel('row / cells',fontsize=8)
            axes[i,0].text(0,-.32,f'{pair}; age {c["age"]}; actual removal {impact["removed_occupied_cells"]}/{impact["occupied_before"]} occupied cells, 3→2 cores.',transform=axes[i,0].transAxes,ha='left',fontsize=8)
        fig.suptitle(f'Predeclared matched removal and paired endpoints · {m["benefit_experiment_id"]}',fontsize=14)
        fig.text(.5,.10,'Dashed outline: exact removed occupied-cell mask, retaining arms; it does not recolor literal cell states. U at t=0 equals the common pre-state.\n'
                 'Full 192×192 periodic domains and recorded endpoints. Three clones were placed externally; component removal is a declared treatment.\n'
                 'Replay selection was frozen before outcomes. Age is preparation time; t is continuation time after preparation/removal. No native ancestry assignment.',ha='center',fontsize=8)
        fig.subplots_adjust(left=.07,right=.98,top=.91,bottom=.23,wspace=.26,hspace=.64);legend(fig)
        export(fig,'raw-states',dark,artifacts,[m['benefit_experiment_id']],paths,{'selection':selected,'selection_rule':'configuration-declared before responses','grid_encoding':'literal cells; separate dashed occupied-mask perimeter'})


def paired_animation(m,selection,artifacts):
    c,pair,before,after,mask,grids,times,paths=replay_records(m,selection)
    scale=2;h,w=m['config']['shape'];rawheight=h*scale;gap=20;padding=16;width=2*w*scale+gap+2*padding;top=104
    font=ImageFont.truetype(FONT_PATH,17);small=ImageFont.truetype(FONT_PATH,12);tiny=ImageFont.truetype(FONT_PATH,10)
    images=[];rects=[]
    for index,t in enumerate(times):
        canvas=Image.new('RGB',(width,top+rawheight+112),STYLE['ink']);draw=ImageDraw.Draw(canvas)
        draw.text((padding,10),f'CHROMATIC FIELDS / {pair}',font=font,fill=STYLE['heading'])
        draw.text((padding,34),f'{m["benefit_experiment_id"]} | age {c["age"]} preparation updates | t = {int(t):,} continuation updates',font=small,fill=STYLE['text'])
        draw.text((padding,55),f'D: whole component removed at t=0 (3→2 cores); U: unchanged matched colony (3 cores).',font=small,fill=STYLE['text'])
        for j,treatment in enumerate(('D','U')):
            x=padding+j*(w*scale+gap);grid=grids[treatment][index]
            raw=Image.fromarray(PALETTE[grid]).resize((w*scale,h*scale),Image.Resampling.NEAREST)
            canvas.paste(raw,(x,top));draw.text((x,80),f'{treatment} / '+('disturbed' if treatment=='D' else 'undisturbed control'),font=small,fill=STYLE['heading'])
            draw.rectangle((x-1,top-1,x+w*scale,top+rawheight),outline=STYLE['axis'],width=1)
            if index==0:rects.append({'treatment':treatment,'left':x,'top':top,'width':w*scale,'height':h*scale})
        y=top+rawheight+8
        draw.text((padding,y),f'Literal states | each {w}×{h} periodic cells | recorded every {m["config"]["replay_interval"]} updates',font=small,fill=STYLE['text'])
        draw.line((width-64,y+8,width-64+10*scale,y+8),fill=STYLE['text'],width=2);draw.text((width-112,y+20),'10 cells',font=tiny,fill=STYLE['text'])
        names=['quiescent','carrier','sheath','junction','turn','messenger','cord','growth','dissolve']
        for state,name in enumerate(names):
            x=padding+(state%5)*((width-2*padding)//5);yy=y+33+(state//5)*21
            draw.rectangle((x,yy+2,x+10,yy+12),fill=STYLE['cell_states'][state],outline=STYLE['text'],width=1)
            draw.text((x+14,yy),f'{state} {name}',font=tiny,fill=STYLE['text'])
        draw.text((padding,y+80),'Constructed three-clone preparation; structural observations, not certified viability or assigned ancestry.',font=tiny,fill=STYLE['text'])
        images.append(canvas)
    path=FIG/f'{PREFIX}paired-{pair}.webp';images[0].save(path,save_all=True,append_images=images[1:],duration=160,loop=0,lossless=True,method=6)
    artifacts.append({'file':path.name,'experiments':[m['benefit_experiment_id']],'command':COMMAND,
                      'source_sha256':source_hashes(BASE+paths),'selection':'predeclared configuration replay','pair_id':pair,
                      'display_times':[int(t) for t in times],'pixels_per_cell':scale,'grid_rectangles':rects,
                      'sha256':sha(path),'style_sha256':sha(ROOT/'configs/style.json')})
    del images,grids;gc.collect()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--only',choices=['exposure','calibration','scores','contrasts','curves','raw','animations','all'],default='all')
    parser.add_argument('--case',type=int,choices=[0,1,2],help='single predeclared animation, for bounded process RSS');args=parser.parse_args()
    FIG.mkdir(exist_ok=True);m=read(OUT/'manifest.json');target=FIG/'manifest.json';existing=read(target)
    names={'exposure':['exposure'],'calibration':['calibration'],'scores':['score-matrices'],'contrasts':['contrasts'],'curves':['paired-curves'],'raw':['raw-states'],
           'animations':['paired-'+s['state']+'-'+s['condition'] for s in m['config']['replays']]}
    selected=list(names) if args.only=='all' else [args.only]
    if args.case is not None:
        assert args.only=='animations','--case requires --only animations'
        names['animations']=[names['animations'][args.case]]
    prefixes=tuple(PREFIX+name for group in selected for name in names[group])
    artifacts=[a for a in existing['artifacts'] if not a['file'].startswith(prefixes)]
    if 'exposure' in selected:exposure(m,artifacts);gc.collect()
    if 'calibration' in selected:calibration(read(OUT/'calibration-analysis.json'),m,artifacts);gc.collect()
    if 'scores' in selected:score_matrices(read(OUT/'analysis.json'),m,artifacts);gc.collect()
    if 'contrasts' in selected:contrasts(read(OUT/'analysis.json'),m,artifacts);gc.collect()
    if 'curves' in selected:curves(m,artifacts);gc.collect()
    if 'raw' in selected:raw_states(m,artifacts);gc.collect()
    if 'animations' in selected:
        for index,s in enumerate(m['config']['replays']):
            if args.case is None or index==args.case:paired_animation(m,s,artifacts)
    existing['artifacts']=artifacts;target.write_text(json.dumps(existing,indent=2)+'\n')
    print('Impact exports complete;',len(artifacts),'manifest artifacts',flush=True)


if __name__=='__main__':main()
