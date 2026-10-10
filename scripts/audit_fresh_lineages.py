"""Link fresh-atlas raw source states and every serial-isolation graph edge.

Run after acquisition and inheritance finish:
    OPENBLAS_NUM_THREADS=1 python -m scripts.audit_fresh_lineages

This complements scripts.verify_fresh, which replays individual generations.
Here candidate native states are replayed once per run with the ORIGINAL dense
kernel and provenance, and isolated stage inputs are reconstructed independently
from the captured source or their parent's actual child array. It does not infer
native genetic ancestry or certify exhaustive search of unvisited branches.
First-observation evidence is retained even when no component was extractable;
this preserves the reported sampled observation, not proof of exact onset.
"""
import hashlib
import json
import time
import numpy as np
from evoloop.engine import ROOT,RULE_HASH,advance,digest
from evoloop.periodic_tracking import detect
from scripts.atlas import write_json

OUT=ROOT/'data/atlas-v2'


def require(condition,message):
    if not condition:raise AssertionError(message)


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def same_array(actual,expected,context):
    require(actual.dtype==expected.dtype and actual.shape==expected.shape
            and np.array_equal(actual,expected),context)


def word(identity):return identity.split(':',1)[1]


def isolated_grid(snapshot,shape):
    """Independent reconstruction, without the production placement helper."""
    require(snapshot.ndim==2 and snapshot.dtype==np.uint8,'invalid component array')
    require(len(shape)==2 and shape[0]==shape[1],'audited assay expects square arena')
    if max(snapshot.shape)+20>shape[0]:return None
    grid=np.zeros(shape,np.uint8)
    y=shape[0]//2-snapshot.shape[0]//2
    x=shape[1]//2-snapshot.shape[1]//2
    grid[y:y+snapshot.shape[0],x:x+snapshot.shape[1]]=snapshot
    return grid


def graph_audit(outcome,folder,root_snapshot,root_identity,input_words,cfg,counts):
    nodes=outcome['nodes'];limit=cfg['max_generation_simulations_per_root']
    require(len(nodes)==outcome['generation_simulations']<=limit,f'{folder}: node count/cap')
    require(bool(nodes),f'{folder}: no root node')
    arrays=[];identities=[];streaks=[]
    for number,node in enumerate(nodes):
        context=f'{folder.name}/node-{number:02d}'
        require(node['node']==number,f'{context}: node index')
        require(json.loads((folder/f'node-{number:02d}.json').read_text())==node,
                f'{context}: standalone JSON differs from graph')
        parent=node['parent_node'];incoming=node['incoming_child']
        if number==0:
            require(parent is None and incoming is None,f'{context}: root parent')
            snapshot=root_snapshot;identity=root_identity;sequence=[identity]
            depth=1;path=[];streak=0
        else:
            require(isinstance(parent,int) and 0<=parent<number,f'{context}: parent index')
            require(isinstance(incoming,int) and 0<=incoming<len(nodes[parent]['outcome']['children']),
                    f'{context}: incoming child index')
            child=nodes[parent]['outcome']['children'][incoming]
            snapshot=arrays[parent][f'child{incoming}'];identity=child['identity']
            require(child['size_eligible'],f'{context}: visited ineligible child')
            depth=nodes[parent]['depth']+1;path=nodes[parent]['path']+[incoming]
            sequence=identities[parent]+[identity]
            streak=streaks[parent]+1 if identity==nodes[parent]['input_identity'] else 0
            counts['parent_child_edges_verified']+=1
        require(node['input_identity']==identity,f'{context}: input identity link')
        require(node['input_snapshot_hash']==digest(snapshot),f'{context}: input snapshot hash')
        require(node['depth']==depth<=cfg['max_depth'],f'{context}: depth')
        require(node['path']==path,f'{context}: branch path')
        require(node['incoming_streak']==streak,f'{context}: transmission streak')
        expected=isolated_grid(snapshot,cfg['isolation_shape'])
        report=node['outcome']
        with np.load(folder/f'node-{number:02d}.npz',allow_pickle=False) as raw:
            saved={key:raw[key].copy() for key in raw.files}
        arrays.append(saved);identities.append(sequence);streaks.append(streak)
        if expected is None:
            require(number==0,f'{context}: oversized descendant was visited')
            require(report=={'status':'ineligible_component_size','children':[]},
                    f'{context}: oversized report')
            require(not saved,f'{context}: oversized node NPZ must be empty')
            counts['oversized_empty_nodes_verified']+=1
            continue
        require('initial_hash' in report,f'{context}: eligible node lacks initial hash')
        same_array(saved['initial'],expected,f'{context}: isolated initial construction')
        require(digest(expected)==report['initial_hash'],f'{context}: isolated initial hash')
        require(digest(saved['final'])==report['final_hash'],f'{context}: final self-hash')
        loops=detect(expected)
        require(len(loops)==1 and loops[0]['genotype']==identity,
                f'{context}: input component identity/single core')
        counts['isolated_initials_verified']+=1
        children=report['children']
        require(len(children)<=cfg['offspring_per_generation'],f'{context}: offspring cap')
        require(len({tuple(child['core']) for child in children})==len(children),
                f'{context}: repeated offspring core')
        for child_number,child in enumerate(children):
            component=saved[f'child{child_number}']
            require(digest(component)==child['snapshot_hash'],f'{context}: child byte hash')
            require(child['size_eligible']==(max(component.shape)+20<=cfg['isolation_shape'][0]),
                    f'{context}: child size eligibility')
            require(0<=child['closure_first_seen_t']<=child['detached_t']<=report['completed_updates'],
                    f'{context}: offspring times')
            counts['child_arrays_verified']+=1
    counts['expanded_nodes_verified']+=len(nodes)
    for observation in outcome['stable_observations']:
        number=observation['node'];child_number=observation['child']
        require(0<=number<len(nodes),f'{folder}: stable-observation node')
        require(0<=child_number<len(nodes[number]['outcome']['children']),
                f'{folder}: stable-observation child')
        child=nodes[number]['outcome']['children'][child_number]
        streak=streaks[number]+1 if child['identity']==nodes[number]['input_identity'] else 0
        require(streak>=cfg['stable_transmissions'],f'{folder}: stable-observation streak')
        require(observation['identity']==child['identity'],f'{folder}: stable identity')
        require(observation['path']==nodes[number]['path']+[child_number],f'{folder}: stable path')
        require(observation['accepted_endpoint']==(word(child['identity']) not in input_words),
                f'{folder}: stable-word acceptance')
        counts['stable_observations_verified']+=1
    confirmation=outcome['confirmation']
    require((outcome['status']=='confirmed')==(confirmation is not None),f'{folder}: confirmation status')
    if confirmation is None:return
    number=confirmation['node'];child_number=confirmation['child']
    require(0<=number<len(nodes),f'{folder}: confirmation node')
    require(0<=child_number<len(nodes[number]['outcome']['children']),f'{folder}: confirmation child')
    child=nodes[number]['outcome']['children'][child_number]
    identity=child['identity'];sequence=identities[number]+[identity]
    # Independently count identical transmissions backward along linked inputs,
    # rather than trusting the recorded or recursively recomputed streak.
    actual_streak=0
    for left,right in zip(reversed(sequence[:-1]),reversed(sequence[1:])):
        if left!=identity or right!=identity:break
        actual_streak+=1
    require(actual_streak>=cfg['stable_transmissions'],f'{folder}: fewer than two linked stable transmissions')
    require(confirmation['transmission_streak']==actual_streak,f'{folder}: confirmation streak')
    require(confirmation['identity']==identity and word(identity) not in input_words,
            f'{folder}: confirmed identity/novelty against both inputs')
    require(confirmation['path']==nodes[number]['path']+[child_number],f'{folder}: confirmation path')
    require(confirmation['snapshot_hash']==child['snapshot_hash'],f'{folder}: confirmation child hash')
    require(json.loads((folder/'confirmation.json').read_text())=={'confirmation':confirmation},
            f'{folder}: standalone confirmation metadata')
    with np.load(folder/'confirmation.npz',allow_pickle=False) as saved:
        require(saved.files==['stable_snapshot'],f'{folder}: confirmation array keys')
        same_array(saved['stable_snapshot'],arrays[number][f'child{child_number}'],
                   f'{folder}: confirmation array differs from linked child')
        require(digest(saved['stable_snapshot'])==confirmation['snapshot_hash'],
                f'{folder}: confirmation snapshot hash')
    counts['confirmations_verified']+=1


def audit(report):
    manifest=json.loads((OUT/'manifest.json').read_text());cfg=manifest['config']
    inheritance_path=OUT/'inheritance.json'
    require(inheritance_path.exists(),'inheritance is unfinished; run this audit after completion')
    inheritance=json.loads(inheritance_path.read_text())
    require(manifest['rule_hash']==RULE_HASH,'rule hash differs from dense reference')
    require(inheritance['experiment_id']==manifest['experiment_id'],'inheritance experiment ID')
    for name,value in manifest['code_hashes'].items():
        require(sha(ROOT/name)==value,f'frozen source changed: {name}')
    require(len(manifest['runs'])==manifest['expected_runs']==144,'expected complete 144-state atlas')
    require(len({r['run_id'] for r in manifest['runs']})==144,'duplicate run identifiers')
    require(len({r['initial_hash'] for r in manifest['runs']})==144,'duplicate physical initial states')
    report.update({'experiment_id':manifest['experiment_id'],'rule_hash':RULE_HASH,
        'manifest_sha256':sha(OUT/'manifest.json'),'inheritance_sha256':sha(inheritance_path),
        'auditor_sha256':sha(ROOT/'scripts/audit_fresh_lineages.py'),
        'dense_kernel_source_sha256':sha(ROOT/'evoloop/kernel.c')})
    counts=report['counts'];source_groups={};roots={};expected_items={};results={}
    report['retained_first_observation_frames']=[]
    for spec in manifest['runs']:
        rid=spec['run_id'];folder=OUT/'runs'/rid
        result=json.loads((folder/'result.json').read_text());results[rid]=result
        require(result['run_id']==rid and result['rule_hash']==RULE_HASH,f'{rid}: result identity/rule')
        require(result['config_sha256']==manifest['config_sha256'],f'{rid}: result config hash')
        with np.load(OUT/'initial'/f'{rid}.npz',allow_pickle=False) as initial:
            require(list(initial['grid'].shape)==spec['shape'] and initial['labels'].shape==initial['grid'].shape,
                    f'{rid}: initial shape')
            require(initial['grid'].dtype==np.uint8 and initial['labels'].dtype==np.uint8,
                    f'{rid}: initial dtype')
            require(digest(initial['grid'])==spec['initial_hash']==result['initial_hash'],f'{rid}: initial grid hash')
            require(digest(initial['labels'])==spec['initial_labels_hash']==result['initial_labels_hash'],
                    f'{rid}: initial provenance hash')
        with np.load(folder/'final.npz',allow_pickle=False) as final:
            require(list(final['grid'].shape)==spec['shape'] and final['labels'].shape==final['grid'].shape,
                    f'{rid}: final shape')
            require(final['grid'].dtype==np.uint8 and final['labels'].dtype==np.uint8,f'{rid}: final dtype')
            require(digest(final['grid'])==result['final_hash'],f'{rid}: final grid self-hash')
            require(digest(final['labels'])==result['final_labels_hash'],f'{rid}: final provenance self-hash')
        counts['initial_final_run_pairs_verified']+=1
        input_words={word(manifest['panel'][pid]['genotype'])
                     for pid in (spec['focal'],spec['partner']) if pid}
        for candidate in result['candidates']:
            key=(rid,candidate['genotype']);require(key not in expected_items,f'{rid}: duplicate candidate identity')
            require(word(candidate['genotype']) not in input_words,f'{rid}: nonnovel screened candidate')
            expected_items[key]=(candidate,input_words)
            t=candidate['first_observed_t']
            require(isinstance(t,int) and 0<=t<=cfg['horizon'] and t%cfg['detection_interval']==0,
                    f'{rid}: first-observation sampled time')
            source_groups.setdefault(rid,{}).setdefault(t,{'first_observations':[],'captures':[]})['first_observations'].append(candidate)
            for snapshot in candidate['snapshots']:
                require(0<=snapshot['t']<=cfg['horizon'],f'{rid}: source time')
                source_groups.setdefault(rid,{}).setdefault(snapshot['t'],{'first_observations':[],'captures':[]})['captures'].append((candidate,snapshot))
                require((rid,snapshot['file']) not in roots,f'{rid}: duplicate captured filename')
                roots[rid,snapshot['file']]=(candidate,snapshot)
        recorded={snap['file'] for candidate in result['candidates'] for snap in candidate['snapshots']}
        require(recorded=={path.name for path in folder.glob('candidate-*.npz')},
                f'{rid}: orphaned or missing captured source arrays')
    for rid,times in sorted(source_groups.items()):
        folder=OUT/'runs'/rid
        with np.load(OUT/'initial'/f'{rid}.npz',allow_pickle=False) as initial:
            grid=initial['grid'].copy();labels=initial['labels'].copy()
        last=0
        for t,group in sorted(times.items()):
            advance(grid,t-last,labels);last=t;counts['candidate_source_time_groups_verified']+=1
            loops=detect(grid)
            first_observations=[]
            for candidate in group['first_observations']:
                matching=[o for o in loops if o['genotype']==candidate['genotype']]
                require(bool(matching),f'{rid}@{t}: registered first-observed identity absent')
                require(word(candidate['genotype']) not in expected_items[rid,candidate['genotype']][1],
                        f'{rid}@{t}: first-observed word matches an input')
                first_observations.append({'genotype':candidate['genotype'],
                    'matching_cores':sorted([o['core'] for o in matching]),
                    'extractable_cores':sorted([o['core'] for o in matching if o['isolation_snapshot'] is not None])})
                counts['native_candidate_first_observations_verified']+=1
            if first_observations:
                metadata={'run_id':rid,'t':t,'rule_hash':RULE_HASH,
                    'config_sha256':manifest['config_sha256'],
                    'observations':sorted(first_observations,key=lambda o:o['genotype']),
                    'interpretation':'registered sampled first observation; genetic ancestry and exact onset unresolved'}
                metadata_text=json.dumps(metadata,sort_keys=True,separators=(',',':'))
                path=OUT/'candidate-observations'/f'{rid}-t{t:04d}.npz'
                path.parent.mkdir(parents=True,exist_ok=True)
                if path.exists():
                    with np.load(path,allow_pickle=False) as saved:
                        require(set(saved.files)=={'grid','labels','metadata'},f'{rid}@{t}: raw first-observation keys')
                        same_array(saved['grid'],grid,f'{rid}@{t}: retained first-observation grid')
                        same_array(saved['labels'],labels,f'{rid}@{t}: retained first-observation labels')
                        require(saved['metadata'].item()==metadata_text,f'{rid}@{t}: retained observation metadata')
                else:
                    temporary=path.with_suffix('.npz.tmp')
                    with temporary.open('wb') as stream:
                        np.savez_compressed(stream,grid=grid,labels=labels,metadata=np.asarray(metadata_text))
                    temporary.replace(path)
                report['retained_first_observation_frames'].append({'file':str(path.relative_to(OUT)),
                    'run_id':rid,'t':t,'identities':[o['genotype'] for o in metadata['observations']],
                    'grid_hash':digest(grid),'labels_hash':digest(labels),'file_sha256':sha(path)})
                counts['first_observation_raw_frames_retained']+=1
            for candidate,snapshot in group['captures']:
                with np.load(folder/snapshot['file'],allow_pickle=False) as saved:
                    same_array(saved['source_grid'],grid,f'{rid}@{t}: native source grid replay')
                    same_array(saved['source_labels'],labels,f'{rid}@{t}: native source provenance replay')
                    require(digest(saved['snapshot'])==snapshot['snapshot_hash'],f'{rid}@{t}: component hash')
                    organism=next((o for o in loops if o['core']==snapshot['core']
                                   and o['genotype']==candidate['genotype']),None)
                    require(organism is not None and organism['isolation_snapshot'] is not None,
                            f'{rid}@{t}: source identity/component')
                    same_array(saved['snapshot'],organism['isolation_snapshot'],f'{rid}@{t}: source extraction')
                    require(snapshot['extraction_bbox']==organism['extraction_bbox'],f'{rid}@{t}: source extraction box')
                counts['candidate_source_files_replayed']+=1
        counts['candidate_source_runs_replayed']+=1
        counts['original_dense_updates_replayed']+=last
        print('native source links verified',rid,'first observations',
              sum(len(x['first_observations']) for x in times.values()),
              'snapshots',sum(len(x['captures']) for x in times.values()),flush=True)
    require(counts['native_candidate_first_observations_verified']==len(expected_items),
            'not every native candidate identity has verified first-observation evidence')
    actual_keys=[(item['run_id'],item['encounter_genotype']) for item in inheritance['items']]
    require(len(actual_keys)==len(set(actual_keys)) and set(actual_keys)==set(expected_items),
            'inheritance candidate inventory differs from acquisition')
    for item in inheritance['items']:
        rid=item['run_id'];candidate,input_words=expected_items[rid,item['encounter_genotype']]
        captures={snap['file']:snap for snap in candidate['snapshots']}
        require(len(item['outcomes'])==len(captures),f'{rid}: inheritance capture count')
        seen=set();confirmed=False
        for outcome in item['outcomes']:
            source=outcome['source'];name=source['file']
            require(name in captures and name not in seen,f'{rid}: inheritance source filename')
            seen.add(name);require(source==captures[name],f'{rid}: inheritance source metadata')
            expected_folder=OUT/'runs'/rid/name.replace('.npz','-search')
            require(OUT/outcome['folder']==expected_folder,f'{rid}: search folder/source link')
            persisted=json.loads((expected_folder/'result.json').read_text())
            require({k:v for k,v in outcome.items() if k!='folder'}==persisted,
                    f'{rid}: aggregate/standalone search result mismatch')
            with np.load(OUT/'runs'/rid/name,allow_pickle=False) as saved:root=saved['snapshot'].copy()
            graph_audit(outcome,expected_folder,root,candidate['genotype'],input_words,cfg,counts)
            require(outcome['stable_novel_vs_both_inputs']==(outcome['status']=='confirmed'),
                    f'{rid}: search acceptance flag')
            confirmed=confirmed or outcome['status']=='confirmed'
            counts['captured_root_graphs_verified']+=1
        require(item['confirmed_novel']==confirmed,f'{rid}: candidate confirmation aggregate')
        require(item['status']==('confirmed' if confirmed else 'unresolved'),f'{rid}: candidate status aggregate')
        counts['candidate_identities_verified']+=1
    report['status']='passed';report['mismatches']=0


def main():
    started=time.perf_counter()
    counters=['initial_final_run_pairs_verified','candidate_source_runs_replayed',
        'candidate_source_time_groups_verified','candidate_source_files_replayed',
        'native_candidate_first_observations_verified','first_observation_raw_frames_retained',
        'original_dense_updates_replayed','captured_root_graphs_verified',
        'candidate_identities_verified','expanded_nodes_verified','parent_child_edges_verified',
        'isolated_initials_verified','oversized_empty_nodes_verified','child_arrays_verified',
        'stable_observations_verified','confirmations_verified']
    report={'status':'running','counts':{name:0 for name in counters},
        'scope':'registered first-observation and captured native-source replay plus linked serial-isolation graphs; final self-hashes, not all final trajectories; sampled first observation is not exact onset; native ancestry remains ambiguous'}
    try:
        audit(report)
    except Exception as error:
        report.update({'status':'failed','mismatches':1,'error_type':type(error).__name__,'error':str(error),
                       'seconds':time.perf_counter()-started})
        write_json(OUT/'lineage-integrity.json',report)
        raise
    report['seconds']=time.perf_counter()-started
    write_json(OUT/'lineage-integrity.json',report)
    print(json.dumps(report,indent=2),flush=True)


if __name__=='__main__':main()
