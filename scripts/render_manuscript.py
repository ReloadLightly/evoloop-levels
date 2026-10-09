"""Readable working PDF using the existing Matplotlib toolchain.

This deliberately simple renderer avoids a TeX/pandoc installation diversion.
Markdown remains authoritative; figures are appended as full-page paper panels.
"""
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR',str(Path(__file__).resolve().parents[1]/'.cache/matplotlib'))
import re
import textwrap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image
from evoloop.engine import ROOT

WIDTH=90

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
        text=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'\1 (\2)',text)
        width=44 if style=='title' else 78 if style!='body' else WIDTH
        for line in textwrap.wrap(text,width=width,break_long_words=True,break_on_hyphens=False):add(line,style)
        add('','space')
    if lines:pages.append(lines)
    plt.rcParams.update({'font.family':'DejaVu Serif','pdf.fonttype':42})
    target=ROOT/'paper/manuscript.pdf'
    with PdfPages(target,metadata={'Title':'Where Does Evolvability Reside?','Subject':'Working first scientific checkpoint; benefit pending'}) as pdf:
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
        for name in ['world-overview','inheritance-path','outcome-matrix','evidence-stages','encounter-1','encounter-2','encounter-3',
                     'fate-calibration-matrix','fate-native-trajectories','fate-raw-comparison']:
            p=ROOT/f'figures/{name}-light.png'
            if not p.exists():continue
            fig=plt.figure(figsize=(11.69,8.27),facecolor='#EDE9DF');ax=fig.add_axes([.035,.07,.93,.86]);ax.imshow(Image.open(p));ax.axis('off')
            fig.text(.05,.03,f'Figure: {name}. Source and regeneration: figures/manifest.json.',fontsize=9,color='#101421')
            pdf.savefig(fig);plt.close(fig)
    print('Rendered',target,'from authoritative Markdown and recorded-data figures')

if __name__=='__main__':main()
