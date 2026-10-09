"""Write or verify compact committed data artifacts; this is not a physics test."""
import argparse
import hashlib
from evoloop.engine import ROOT


def main():
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['write','verify']);args=parser.parse_args()
    target=ROOT/'data/SHA256SUMS'
    if args.command=='write':
        paths=sorted(p for p in (ROOT/'data').rglob('*') if p.is_file() and p.name!='SHA256SUMS')
        target.write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT)}\n' for p in paths))
    lines=target.read_text().splitlines()
    for line in lines:
        expected,path=line.split('  ',1)
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,f'artifact mismatch: {path}'
    print('Verified',len(lines),'data artifact checksums')

if __name__=='__main__':main()
