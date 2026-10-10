"""Exploratory discovery evidence, including selection shortfall."""
import hashlib,json,os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR',str(Path(__file__).resolve().parents[1]/'.cache/matplotlib'))
import collections
import numpy as np
import matplotlib.pyplot as plt
from evoloop.engine import ROOT
from scripts.figures import FIG,STYLE,theme,save,legend,CMAP,NORM,animation,THEMES
from scripts.atlas import write_json
OUT=ROOT/'data/panel-v2';EXP='EXP-panel-discovery-002';COMMAND='OPENBLAS_NUM_THREADS=1 python -m scripts.figures_panel'

def render(manifest):
    d=json.loads((OUT/'discovery.json').read_text());reason=collections.Counter(t['reason'] for t in d['trials'])
    for dark in THEMES:
        theme(dark);fig,axes=plt.subplots(len(d['histories']),4,figsize=(12,3.1*len(d['histories'])+1.4),squeeze=False)
        for row,h in enumerate(d['histories']):
            a=np.load(OUT/f'{h["id"]}-world.npz');indices=np.linspace(0,len(a['frames'])-1,4,dtype=int)
            for ax,k in zip(axes[row],indices):
                g=a['frames'][k];ax.imshow(g,cmap=CMAP,norm=NORM,interpolation='nearest');ax.set_title(f'{h["id"]} · t={a["times"][k]:,}',fontsize=10)
                ax.set_xticks([0,g.shape[1]//2,g.shape[1]-1]);ax.set_yticks([0,g.shape[0]//2,g.shape[0]-1]);ax.set_xlabel('column / cells')
            axes[row,0].set_ylabel('row / cells')
        fig.suptitle('Native discovery histories · fixed initial configurations')
        fig.subplots_adjust(bottom=.16,top=.93,wspace=.27,hspace=.48);legend(fig)
        save(fig,'panel2-native-worlds',dark,manifest,[EXP],{'command':COMMAND,'source':'data/panel-v2/*-world.npz'})
        theme(dark);fig,ax=plt.subplots(figsize=(10,4.6));labels=['Admitted\n(native word retained)','Reproduced\na different word','Unresolved /\nidentity changed','Other exclusions']
        counts=[reason['verified'],reason['stable_word_not_native_source_word'],reason['unresolved_or_identity_changed'],sum(v for k,v in reason.items() if k not in ('verified','stable_word_not_native_source_word','unresolved_or_identity_changed'))]
        ax.bar(range(4),counts,color=[STYLE['status'][key] for key in ('confirmed','candidate','unresolved','excluded')])
        for i,v in enumerate(counts):ax.text(i,v+.7,str(v),ha='center')
        ax.set_xticks(range(4),labels);ax.set_ylim(0,max(counts)+10);ax.set_ylabel('Verification trials\n(selected component snapshots)')
        ax.set_title(f'Exploratory input selection · {len(d["panel"])}/3 eligible identities · {len(d["trials"])} trials')
        fig.text(.5,.03,'Original native N01 reverified; all 79 selected trials retained.\nSelected snapshots within three histories, not independent populations or encounter-yield estimates.',ha='center',fontsize=9)
        fig.tight_layout(rect=(0,.12,1,1));save(fig,'panel2-selection',dark,manifest,[EXP],{'command':COMMAND,'source':'data/panel-v2/discovery.json'})
    h=d['histories'][-1];a=np.load(OUT/f'{h["id"]}-world.npz');chosen=np.unique(np.linspace(0,len(a['frames'])-1,min(45,len(a['frames'])),dtype=int))
    path=FIG/'panel2-native-world.webp';animation(a['frames'][chosen],a['times'][chosen],path,'CHROMATIC FIELDS / Native discovery',f'{EXP} | {h["id"]} | actual sampled periodic world',scale=2)
    manifest.append({'file':path.name,'experiments':[EXP],'command':COMMAND,'source':f'data/panel-v2/{h["id"]}-world.npz','times':a['times'][chosen].tolist(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})

def main():
    m=json.loads((FIG/'manifest.json').read_text());m['artifacts']=[a for a in m['artifacts'] if not a['file'].startswith('panel2-')];render(m['artifacts']);write_json(FIG/'manifest.json',m)
if __name__=='__main__':main()
