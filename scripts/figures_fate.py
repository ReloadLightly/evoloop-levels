"""Chromatic Fields calibration figures from recorded states and paired outcomes."""
import hashlib
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR',str(Path(__file__).resolve().parents[1]/'.cache/matplotlib'))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Rectangle
from evoloop.engine import ROOT,digest
from scripts.figures import FIG,STYLE,theme,save,legend,CMAP,NORM,THEMES,annotation_color

EXP='EXP-fate-calibration-001';OUT=ROOT/'data/fate-calibration'
COMMAND='OPENBLAS_NUM_THREADS=1 python -m scripts.figures_fate'


def export(fig,name,dark,manifest,extra=None):
    save(fig,name,dark,manifest,[EXP],{'command':COMMAND,'source':'data/fate-calibration/outcomes.json',**(extra or {})})


def render(manifest):
    m=json.loads((OUT/'manifest.json').read_text());rows=json.loads((OUT/'outcomes.json').read_text())
    ids=[s['id'] for s in m['sources']];delays=m['config']['delays'];lookup={(r['source_id'],r['delay']):r for r in rows}
    statuses=['eligible','target_lost','shared_component','unknown_identity','boundary_component','oversized_component','target_recurrence_after_loss']
    short={'eligible':'eligible','target_lost':'lost','shared_component':'shared','unknown_identity':'unknown',
           'boundary_component':'boundary','oversized_component':'oversize','target_recurrence_after_loss':'recurrence'}
    colors=[STYLE['status'][status] for status in statuses]
    for dark in THEMES:
        bg,fg=theme(dark);fig,axes=plt.subplots(1,3,figsize=(12,7),sharey=True)
        eligibility=np.array([[statuses.index(lookup[s,d]['target_status']) for d in delays] for s in ids])
        axes[0].imshow(eligibility,cmap=ListedColormap(colors),vmin=-.5,vmax=len(statuses)-.5,aspect='auto',interpolation='nearest')
        for i,s in enumerate(ids):
            for j,d in enumerate(delays):
                status=lookup[s,d]['target_status'];axes[0].text(j,i,short[status],ha='center',va='center',color=annotation_color(STYLE['status'][status]),fontsize=8)
        for ax,key,title in zip(axes[1:],['legacy_confirmed','expanded_confirmed'],['Legacy search','Expanded search']):
            values=np.array([[int(lookup[s,d][key]) if lookup[s,d]['target_status']=='eligible' else np.nan for d in delays] for s in ids])
            binary_colors=[STYLE['status']['unconfirmed'],STYLE['status']['confirmed']]
            cmap=ListedColormap(binary_colors);cmap.set_bad(STYLE['status']['missing'])
            ax.imshow(values,cmap=cmap,vmin=0,vmax=1,aspect='auto',interpolation='nearest')
            for i,s in enumerate(ids):
                for j,d in enumerate(delays):
                    ax.text(j,i,'—' if np.isnan(values[i,j]) else str(int(values[i,j])),ha='center',va='center',fontsize=11,
                            color=annotation_color(STYLE['status']['missing'] if np.isnan(values[i,j]) else binary_colors[int(values[i,j])]))
                    if np.isnan(values[i,j]):ax.add_patch(Rectangle((j-.5,i-.5),1,1,fill=False,hatch='///',edgecolor=fg,lw=0,alpha=.17))
            ax.set_title(title)
        axes[0].set_title('Fixed-target eligibility');axes[0].set_yticks(range(len(ids)),ids)
        for ax in axes:
            ax.set_xticks(range(len(delays)),[str(d) for d in delays]);ax.set_xlabel('maturation delay / updates')
            ax.axhline(6.5,color=fg,lw=1.4);ax.set_ylim(len(ids)-.5,-.5)
        fig.suptitle('Candidate-fate calibration · paired identical snapshots',fontsize=15)
        fig.text(.5,.12,'C01–C07: seven identities in six atlas states. P-S13 / P-N01: verified-parent controls.\n'
                 '0 = tested, no endpoint confirmation; 1 = confirmed; — / hatching = ineligible, never zero.\n'
                 'Candidate endpoint: stable novel word. Control endpoint: original composite identity.',ha='center',fontsize=9)
        fig.text(.5,.035,f'{EXP} · 28 candidate + 8 control delay observations · finite panel; no independent-history inference',ha='center',fontsize=8)
        fig.subplots_adjust(bottom=.25,top=.89,wspace=.12,left=.09,right=.98)
        export(fig,'fate-calibration-matrix',dark,manifest,{'source_ids':ids,'delays':delays})
    native_trajectories(m,manifest)
    raw_example(rows,m,manifest)


def native_trajectories(m,manifest):
    # Overlapping native windows must give identical measurements at shared times.
    traces={};boundary_times={}
    for source in m['sources']:
        trace={}
        for delay in m['config']['delays']:
            r=json.loads((OUT/f'runs/{source["id"]}-d{delay:03d}/result.json').read_text())
            if r['native']['boundary_first_t'] is not None:
                edge_time=delay+r['native']['boundary_first_t']
                boundary_times[source['id']]=min(edge_time,boundary_times.get(source['id'],edge_time))
            for sample in r['native']['samples']:
                t=delay+sample['t'];value=(sample['original_word_cores'],sample['target_present'])
                if t in trace:assert trace[t]==value,'overlapping deterministic windows disagree'
                trace[t]=value
        traces[source['id']]=trace
    for dark in THEMES:
        bg,fg=theme(dark);fig,axes=plt.subplots(3,3,figsize=(12,8),sharex=True)
        for ax,s in zip(axes.flat,m['sources']):
            trace=traces[s['id']];times=sorted(trace);counts=[trace[t][0] for t in times]
            linecolor=STYLE['quantitative_line']['dark' if dark else 'light']
            ax.step(times,counts,where='post',color=linecolor,lw=1.6)
            if s['id'] in boundary_times:
                ax.axvspan(boundary_times[s['id']],max(times),color=fg,alpha=.06,hatch='///',lw=0)
            for delay in m['config']['delays']:ax.axvline(delay,color=STYLE['annotation']['delay'],ls=':',lw=.7,alpha=.8)
            max_count=max(1,max(counts))
            absent=np.array([not trace[t][1] for t in times])
            ax.fill_between(times,-.10*max_count,-.04*max_count,where=absent,step='post',color=STYLE['annotation']['absent'],alpha=.8)
            ax.plot(np.array(times)[absent],np.full(int(absent.sum()),-.07*max_count),'|',
                    color=STYLE['annotation']['absent'],markersize=4,markeredgewidth=.7)
            ax.set_ylim(-.13*max_count,max_count*1.15);ax.set_title(f'{s["id"]} · {s["identity"].split(":",1)[0]} core',fontsize=10)
            ax.set_yticks(np.unique(np.rint(np.linspace(0,max_count,4))).astype(int))
            ax.spines[['top','right']].set_visible(False)
            ax.tick_params(labelsize=8)
        for ax in axes[-1]:ax.set_xlabel('updates since source observation')
        for ax in axes[:,0]:ax.set_ylabel('original-word cores')
        fig.suptitle('Native continuation · word presence is structural evidence',fontsize=15)
        fig.text(.5,.035,'Curve: original signal-word cores anywhere. Strip below zero: fixed target absent at sampled time.\n'
                 'Dotted lines: extraction delays. Overlapping windows agree exactly; they are not independent replicates.\n'
                 'Shading after first boundary flag: seam-crossing cores may be missed (16/28 candidate, 2/8 control windows).\n'
                 f'{EXP} · ten-update sampling · new matching cores do not establish ancestry or inheritance.',ha='center',fontsize=8.5)
        fig.tight_layout(rect=(0,.16,1,.94));export(fig,'fate-native-trajectories',dark,manifest,
                 {'sources':'data/fate-calibration/runs/*/result.json','sampling_interval':10,'boundary_first_times_since_source':boundary_times})


def raw_example(rows,m,manifest):
    eligible=[r for r in rows if r['kind']=='candidate' and r['target_status']=='eligible']
    if not eligible:return
    # Illustrated after analysis; select maximal searched case, deterministic tie-break.
    row=sorted(eligible,key=lambda r:(-r['generation_simulations'],r['case_id']))[0]
    folder=OUT/f'runs/{row["case_id"]}';r=json.loads((folder/'result.json').read_text());a=np.load(folder/'native.npz');b=np.load(folder/'node-00.npz')
    assert digest(a['native_final'])==r['native']['final_hash']
    assert digest(b['final'])==r['expanded']['nodes'][0]['outcome']['final_hash']
    grids=[a['native_initial'],a['native_final'],b['initial'],b['final']]
    times=[0,1600,0,r['expanded']['nodes'][0]['outcome']['completed_updates']]
    titles=['Native at extraction','Native continuation','Isolated same component','Isolated generation 1']
    for dark in THEMES:
        theme(dark);fig,axes=plt.subplots(1,4,figsize=(13,5.1))
        for k,(ax,g,t,title) in enumerate(zip(axes,grids,times,titles)):
            ax.imshow(g,cmap=CMAP,norm=NORM,interpolation='nearest');ax.set_title(f'{title}\nt = {t} after extraction',fontsize=10)
            ax.set_xlabel('column / cells');ax.set_xticks([0,g.shape[1]//2,g.shape[1]-1]);ax.set_yticks([0,g.shape[0]//2,g.shape[0]-1])
            if k<2:
                y,x,h,w=r['target_core'];ax.add_patch(Rectangle((x-.5,y-.5),w,h,fill=False,edgecolor=STYLE['annotation']['target'],lw=1))
                ax.annotate('target locus',xy=(x+w/2,y+h/2),xytext=(.78,.82),textcoords='axes fraction',
                            ha='center',fontsize=8,color=STYLE['annotation']['target'],
                            arrowprops={'arrowstyle':'->','color':STYLE['annotation']['target'],'lw':.8})
        axes[0].set_ylabel('row / cells')
        fig.suptitle(f'{row["source_id"]} · delay {row["delay"]} · actual native / isolated states',fontsize=15)
        fig.text(.5,.17,f'{row["case_id"]} · {row["run_id"]}\n'
                 'Outline/arrow: fixed source core location, not lineage. Literal state colors; grid extents differ.\n'
                 'First isolated generation stops at third eligible offspring or horizon; displayed times are explicit.',ha='center',fontsize=8)
        fig.subplots_adjust(bottom=.34,top=.83,wspace=.3);legend(fig)
        export(fig,'fate-raw-comparison',dark,manifest,{'case_id':row['case_id'],'grid_files':[str((folder/'native.npz').relative_to(ROOT)),str((folder/'node-00.npz').relative_to(ROOT))],
               'selection':'post-analysis maximal expanded simulation count, then lexicographic case ID','panel_times':times})


def main():
    target=FIG/'manifest.json';m=json.loads(target.read_text())
    artifacts=[r for r in m['artifacts'] if EXP not in r['experiments']];render(artifacts);m['artifacts']=artifacts
    target.write_text(json.dumps(m,indent=2)+'\n');print('Rendered calibration exports; figure manifest now',len(artifacts),'artifacts')

if __name__=='__main__':main()
