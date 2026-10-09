"""Optional provenance check; author archive is temporary and not redistributed.

Usage: python -m scripts.compare_author /tmp/evoloop-author/EvoLoopS-1.0
Implements the published algorithm independently, using its downloaded rule data.
"""
import itertools
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
from evoloop.engine import LUT, ROOT, seed13, digest

def main():
    p=Path(sys.argv[1]);explicit={}
    for line in (p/'rule_evolvable').read_text().splitlines():
        if not line.strip():continue
        *key,value=map(int,line.strip());c,*ns=key
        for j in range(4):
            k=(c,*ns[j:],*ns[:j])
            assert k not in explicit or explicit[k]==value
            explicit[k]=value
    lut=[]
    for k in itertools.product(range(9),repeat=5):
        c,*ns=k
        if k in explicit:value=explicit[k]
        elif c==8:value=0
        elif 8 in ns:
            if c in (0,1):value=8 if any(2<=n<=7 for n in ns) else c
            elif c in (2,3,5):value=0
            else:value=1
        else:value=0 if c==0 else 8
        lut.append(value)
    lines=(p/'13.img').read_text().splitlines();w=max(map(len,lines))
    seed=np.array([[int(c) if c.isdigit() else 0 for c in s.ljust(w)] for s in lines],dtype=np.uint8)
    report={'transitions':59049,'mismatches':int(np.count_nonzero(LUT!=lut)),
            'same_species13_seed':bool(np.array_equal(seed,seed13())),
            'author_rule_sha256':hashlib.sha256((p/'rule_evolvable').read_bytes()).hexdigest(),
            'selected_lut_sha256':digest(LUT),'license':'author archive inspected, not incorporated'}
    (ROOT/'data/author_comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    assert report['mismatches']==0 and report['same_species13_seed']
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
