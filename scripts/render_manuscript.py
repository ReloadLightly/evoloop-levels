"""Readable working PDF using the existing Matplotlib toolchain.

This deliberately simple renderer avoids a TeX/pandoc installation diversion.
Markdown remains authoritative. Verified vector figure PDFs are appended with
Ghostscript, keeping raster pages out of the Matplotlib PDF cache.
"""
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR',str(Path(__file__).resolve().parents[1]/'.cache/matplotlib'))
import re
import json
import subprocess
import tempfile
import signal
import textwrap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from evoloop.engine import ROOT

WIDTH=90
STYLE=json.loads((ROOT/'configs/style.json').read_text())

def assemble_vectors(command):
    """Terminate the decoder too when the memory guard stops this renderer."""
    child=None
    def terminate_child():
        if child is not None and child.poll() is None:
            child.terminate()
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()
    def stop(signum, frame):
        terminate_child()
        raise SystemExit(128+signum)
    previous=signal.signal(signal.SIGTERM,stop)
    try:
        child=subprocess.Popen(command)
        return_code=child.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code,command)
    finally:
        terminate_child()
        signal.signal(signal.SIGTERM,previous)

def main():
    source=(ROOT/'paper/manuscript.md').read_text();pages=[];lines=[];y=0
    def add(text,style='body'):
        nonlocal lines,y
        height={'title':28,'heading':20,'subheading':17,'body':13,'table':13,'space':8}[style]
        if y+height>690:pages.append(lines);lines=[];y=0
        lines.append((text,style,y));y+=height
    for paragraph in source.split('\n\n'):
        if paragraph.strip().startswith('|'):
            rows=[line.strip().strip('|').split('|') for line in paragraph.splitlines()
                  if not re.match(r'^\|[-| :]+\|$',line)]
            rows=[[cell.strip() for cell in row] for row in rows]
            widths=[max(len(row[i]) for row in rows) for i in range(len(rows[0]))]
            # Keep these short results tables together, including their header.
            # A split table otherwise leaves counts on a page without labels.
            if y+len(rows)*13+8>690 and lines:
                pages.append(lines);lines=[];y=0
            for row in rows:
                add('| '+' | '.join(cell.ljust(width) for cell,width in zip(row,widths))+' |','table')
            add('','space');continue
        paragraph=' '.join(paragraph.splitlines()).strip()
        if not paragraph:continue
        if paragraph.startswith('### '):text=paragraph[4:];style='subheading'
        elif paragraph.startswith('## '):text=paragraph[3:];style='heading'
        elif paragraph.startswith('# '):text=paragraph[2:];style='title'
        else:text=paragraph;style='body'
        text=text.replace('**','').replace('`','')
        text=re.sub(r'!\[([^\]]+)\]\(([^)]+)\)',r'Figure: \1 (see appended figure pages).',text)
        if text.startswith('*') and text.endswith('*'):
            text=text[1:-1]
        text=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'\1 (\2)',text)
        width=44 if style=='title' else 78 if style!='body' else WIDTH
        for line in textwrap.wrap(text,width=width,break_long_words=True,break_on_hyphens=False):add(line,style)
        add('','space')
    if lines:pages.append(lines)
    plt.rcParams.update({'font.family':'DejaVu Serif','pdf.fonttype':42})
    target=ROOT/'paper/manuscript.pdf'
    work_root=ROOT/'.cache'
    work_root.mkdir(exist_ok=True)
    work=tempfile.TemporaryDirectory(prefix='manuscript-',dir=work_root)
    text_target=Path(work.name)/'text.pdf'
    with PdfPages(text_target,metadata={'Title':'Where Does Evolvability Reside?','Subject':'Production and transmission of variation in controlled encounters'}) as pdf:
        for page_number,page in enumerate(pages,1):
            fig=plt.figure(figsize=(8.27,11.69),facecolor='white');ax=fig.add_axes([0,0,1,1]);ax.set_axis_off()
            for text,style,yp in page:
                ax.text(.085,.935-yp/842,text,ha='left',va='top',fontsize={'title':17,'heading':13,'subheading':11,'body':9,'table':8,'space':9}[style],
                        fontfamily='DejaVu Sans Mono' if style=='table' else 'DejaVu Serif',
                        weight='bold' if style in ('title','heading','subheading') else 'normal',color='#101421')
            ax.text(.085,.04,'Evoloop Levels · Working manuscript · 10 October 2026',fontsize=8,color='#555555')
            ax.text(.915,.04,str(page_number),ha='right',fontsize=8,color='#555555');pdf.savefig(fig);plt.close(fig)
        # Render human-readable bibliography from the verified source review table.
        bib=(ROOT/'paper/references.bib').read_text();refs=[]
        for block in re.split(r'@\w+\{',bib)[1:]:
            key=block.split(',',1)[0]
            # This bibliography uses one nested level for protected capitalization.
            fields={k:v.replace('{','').replace('}','') for k,v in
                    re.findall(r'(\w+)\s*=\s*\{((?:[^{}]|\{[^{}]*\})*)\}',block)}
            refs.append(f'[{key}] {fields.get("author","")} ({fields.get("year","")}). {fields.get("title","")}. {fields.get("journal","")} {fields.get("volume","")}: {fields.get("pages","")}. DOI/URL: {fields.get("doi",fields.get("url",""))}')
        fig=plt.figure(figsize=(8.27,11.69),facecolor='white');ax=fig.add_axes([0,0,1,1]);ax.set_axis_off();yp=.93
        ax.text(.085,yp,'Verified references',fontsize=13,weight='bold');yp-=.04
        for ref in refs:
            wrapped=textwrap.wrap(ref,width=91)
            if yp-len(wrapped)*.017<.075:
                pdf.savefig(fig);plt.close(fig);fig=plt.figure(figsize=(8.27,11.69),facecolor='white');ax=fig.add_axes([0,0,1,1]);ax.set_axis_off();yp=.93
            for line in wrapped:ax.text(.085,yp,line,fontsize=8.5,va='top');yp-=.017
            yp-=.018
        pdf.savefig(fig);plt.close(fig)
    # Concatenation preserves native vector geometry and avoids retaining every
    # raster figure in PdfPages. Install nothing: gs is the existing decoder.
    names=['world-overview','inheritance-path','outcome-matrix','evidence-stages','encounter-1','encounter-2','encounter-3',
                     'fate-calibration-matrix','fate-native-trajectories','fate-raw-comparison',
                     'panel2-native-worlds','panel2-selection','atlas2-verified-panel','atlas2-outcome-matrix',
                     'atlas2-evidence-stages','atlas2-inheritance-path','atlas2-encounter-1','atlas2-encounter-2','atlas2-encounter-3',
                     'eco1-calibration-recovery','eco1-calibration-strata','eco1-score-matrix','eco1-paired-margins',
                     'eco1-evidence-stages','eco1-disturbance-states',
                     'impact1-exposure','impact1-calibration','impact1-score-matrices','impact1-contrasts',
                     'impact1-paired-curves','impact1-raw-states',
                     'coverage1-recovery','coverage1-state-unions','coverage1-native-targets','coverage1-inheritance',
                     'developmental1-resolution','developmental1-paired-states']
    figure_pdfs=[ROOT/f'figures/{name}-dark.pdf' for name in names]
    missing=[str(p) for p in figure_pdfs if not p.exists()]
    if missing:
        raise FileNotFoundError('Required figure PDFs missing: '+', '.join(missing))
    assembled=Path(work.name)/'assembled.pdf'
    assemble_vectors(['gs','-q','-dNOPAUSE','-dBATCH','-sDEVICE=pdfwrite',
                    '-sOutputFile='+str(assembled),str(text_target),
                    *map(str,figure_pdfs)])
    os.replace(assembled,target)
    work.cleanup()
    print('Rendered',target,'from authoritative Markdown and recorded-data figures')

if __name__=='__main__':main()
