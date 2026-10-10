"""Run one resumable batch while retaining at least the declared memory headroom."""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

def available_mib():
    for line in Path('/proc/meminfo').read_text().splitlines():
        if line.startswith('MemAvailable:'):
            return int(line.split()[1])/1024
    raise RuntimeError('Linux MemAvailable is unavailable')

def main():
    p=argparse.ArgumentParser();p.add_argument('--log',required=True);p.add_argument('--minimum',type=int,default=200);p.add_argument('--reserve',type=int,default=100);p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
    assert a.command
    samples=[];child=None;start=time.time();minimum=available_mib()
    with Path(a.log).open('a') as log:
        def emit(status,**kw):
            log.write(json.dumps({'utc_epoch':time.time(),'status':status,'available_mib':available_mib(),**kw})+'\n');log.flush()
        if available_mib()<a.minimum+a.reserve:
            emit('not_started_insufficient_launch_headroom',command=a.command);raise SystemExit(75)
        emit('start',command=a.command);child=subprocess.Popen(a.command)
        while child.poll() is None:
            now=available_mib();minimum=min(minimum,now)
            if now<a.minimum:
                emit('terminated_headroom_below_minimum',minimum_mib=minimum);child.terminate()
                try:child.wait(timeout=5)
                except subprocess.TimeoutExpired:child.kill();child.wait()
                raise SystemExit(75)
            time.sleep(.5)
        emit('complete',exit_code=child.returncode,minimum_available_mib=minimum,seconds=time.time()-start)
        raise SystemExit(child.returncode)

if __name__=='__main__':
    retry='--retry' in sys.argv
    if retry: sys.argv.remove('--retry')
    while True:
        try:
            main()
        except SystemExit as error:
            if retry and error.code==75:
                time.sleep(15)
                continue
            raise
