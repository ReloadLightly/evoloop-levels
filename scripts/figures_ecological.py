"""Recorded ecological calibration and paired proxy comparisons; no invented data."""
import argparse
import gc
import hashlib
import json

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from evoloop.engine import ROOT, digest
from scripts.figures import (
    FIG, STYLE, THEMES, CMAP, NORM, PALETTE, FONT, SMALL, FONT_PATH,
    theme, save, legend, quantitative_cmap, annotation_color,
)
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

OUT = ROOT/'data/ecological-v1'
COMMAND = 'OPENBLAS_NUM_THREADS=1 python -m scripts.figures_ecological'
PREFIX = 'eco1-'


def read_json(path):
    return json.loads(path.read_text())


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path):
    return str(path.relative_to(ROOT))


def sources_metadata(paths):
    return {relative(path): file_hash(path) for path in sorted(set(paths))}


def impact_summary(m):
    """All frozen paired clearings, including zero-impact interventions."""
    by_run = {}; events = []; paths = []
    for spec in m['runs']:
        if spec['split'] == 'calibration':
            continue
        path = OUT/spec['split']/spec['run_id']/'result.json'
        paths.append(path)
        selected = [e for e in read_json(path)['events'] if e['type'] == 'disturbance']
        assert [e['t'] for e in selected] == m['benefit']['disturbance_times']
        by_run[spec['run_id']] = selected
        events.extend(selected)
    zero = sum(e['removed_occupied_cells'] == 0 for e in events)
    changed = sum(e['pre_counts']['scored_cores'] != e['post_counts']['scored_cores'] for e in events)
    return by_run, paths, f'{zero}/{len(events)} clearings removed zero occupied cells; {changed}/{len(events)} immediately changed registered core counts.'


def export(fig, name, dark, artifacts, experiments, paths, extra=None):
    save(fig, PREFIX+name, dark, artifacts, experiments,
         {'command': COMMAND, 'source_sha256': sources_metadata(paths), **(extra or {})})
    gc.collect()


def calibration_figures(c, m, artifacts):
    experiment = m['calibration_experiment_id']
    gates = m['config']['calibration']['gate']
    source_paths = [OUT/'calibration-analysis.json', OUT/'calibration.json', OUT/'manifest.json']
    states = m['config']['states']
    lookup = {s['state']: s for s in c['by_state']}
    for dark in THEMES:
        bg, fg = theme(dark)
        fig, (ax, overall, status) = plt.subplots(
            1, 3, figsize=(13, 5.1), gridspec_kw={'width_ratios': [4.4, 2.4, 2.3]})
        x = np.arange(len(states))
        for offset, key, label, color in (
            (-.17, 'eligible', 'extractable component / selected scored cores', STYLE['status']['eligible']),
            (.17, 'confirmed', 'original identity recovered / selected scored cores', STYLE['status']['confirmed']),
        ):
            values = [lookup[s][key]/lookup[s]['selected'] if lookup[s]['selected'] else np.nan for s in states]
            bars = ax.bar(x+offset, np.nan_to_num(values), width=.31, color=color, label=label)
            for bar, state, value in zip(bars, states, values):
                count = lookup[state][key]; n = lookup[state]['selected']
                if np.isnan(value):
                    ax.text(bar.get_x()+bar.get_width()/2, .08, 'NO\nSELECTION', ha='center', fontsize=7)
                else:
                    ax.text(bar.get_x()+bar.get_width()/2, value+.025, f'{count}/{n}', ha='center', va='bottom', fontsize=8, rotation=90)
        ax.axhline(gates['per_starting_state_recovery_fraction'], color=STYLE['annotation']['delay'], ls='--', lw=1.2,
                   label=f'per-state recovery gate ≥{gates["per_starting_state_recovery_fraction"]:.0%}')
        ax.set_xticks(x, states); ax.set_ylim(0, 1.25); ax.set_yticks([0, .2, .4, .6, .8, 1])
        ax.set_ylabel('fraction of selected scored cores'); ax.set_title('Starting-state recovery and eligibility')
        ax.legend(loc='upper center', bbox_to_anchor=(.5, -.15), fontsize=7.5, frameon=False)
        totals = [('baseline', c['baseline_confirmed'], c['baseline_total']),
                  ('scored\nselection', c['scored_confirmed'], c['scored_selected'])]
        for index, (_, count, n) in enumerate(totals):
            value = count/n if n else np.nan
            if n:overall.bar(index, value, width=.55, color=STYLE['status']['confirmed'])
            overall.text(index, (value if n else 0)+.03, f'{count}/{n}' if n else 'NONE\nSELECTED', ha='center', fontsize=10)
        overall.set_xticks([0, 1], [t[0] for t in totals]); overall.set_ylim(0, 1.25)
        overall.set_yticks([0, .5, 1]); overall.set_ylabel('recovery fraction')
        overall.hlines(gates['overall_scored_recovery_fraction'], .6, 1.4, colors=STYLE['annotation']['delay'], linestyles='--')
        overall.hlines(1, -.4, .4, colors=STYLE['annotation']['target'], linestyles=':')
        overall.set_title(f'All baselines; overall ≥{gates["overall_scored_recovery_fraction"]:.0%}')
        status.set_axis_off()
        passed = c['gate_passed']
        status.add_patch(Rectangle((.03, .08), .94, .85, transform=status.transAxes, fill=False,
                                   edgecolor=fg, hatch=None if passed else '///', alpha=.35))
        checks = [('all_baselines', f'all {gates["baseline_recoveries_required"]} baselines'),
                  ('overall_recovery', f'overall ≥{gates["overall_scored_recovery_fraction"]:.0%}'),
                  ('each_starting_state', f'each state ≥{gates["per_starting_state_recovery_fraction"]:.0%}'),
                  ('each_nonempty_stratum', f'each nonempty stratum\n≥{gates["minimum_confirmed_per_nonempty_scored_stratum"]} recovery')]
        lines = ['CALIBRATION', 'PASSED' if passed else 'NOT PASSED', '']
        lines += [f'{"PASS" if c["gate_checks"][key] else "FAIL"}: {label}' for key, label in checks]
        status.text(.5, .53, '\n'.join(lines), transform=status.transAxes, ha='center', va='center', fontsize=9)
        fig.suptitle(f'Exact-identity isolation recovery · {experiment}', fontsize=14)
        fig.text(.5, .035, 'All selected scored cores remain in recovery denominators, including ineligible and nonconfirming fates.\n'
                 'Recovery is a bounded serial-isolation endpoint, not proof of native viability. Selected cores and strata are nested deterministic observations.',
                 ha='center', fontsize=8)
        fig.subplots_adjust(top=.82, bottom=.28, left=.07, right=.98, wspace=.48)
        export(fig, 'calibration-recovery', dark, artifacts, [experiment], source_paths,
               {'gate_thresholds': gates, 'gate_passed': passed})

        conditions = m['config']['calibration']['conditions']
        times = m['config']['calibration']['source_times']
        columns = [(condition['id'], t) for condition in conditions for t in times]
        strata = {}
        for stratum in c['strata']:
            condition = next(cond['id'] for cond in conditions if f'-{cond["id"]}-t' in stratum['stratum_id'])
            strata[stratum['state'], condition, stratum['t']] = stratum
        values = np.full((len(states), len(columns)), np.nan)
        for i, state in enumerate(states):
            for j, (condition, t) in enumerate(columns):
                s = strata[state, condition, t]
                if s['selected_cores']:values[i, j] = s['confirmed']/s['selected_cores']
        cmap = quantitative_cmap().copy(); cmap.set_bad(STYLE['status']['missing'])
        fig, ax = plt.subplots(figsize=(13, 6.6))
        im = ax.imshow(values, cmap=cmap, vmin=0, vmax=1, interpolation='nearest', aspect='auto')
        for i, state in enumerate(states):
            for j, (condition, t) in enumerate(columns):
                s = strata[state, condition, t]; n = s['selected_cores']
                if n:
                    label = f'{s["confirmed"]}/{n}\n{ s["available_cores"]} available'
                    color = annotation_color(cmap(values[i, j]))
                else:
                    label = 'EMPTY\n0 selected'; color = fg
                    ax.add_patch(Rectangle((j-.5, i-.5), 1, 1, fill=False, edgecolor=fg, hatch='///', lw=0, alpha=.2))
                ax.text(j, i, label, ha='center', va='center', color=color, fontsize=9)
        ax.set_xticks(range(len(columns)), [f'{condition}\nt={t}' for condition, t in columns]); ax.set_yticks(range(len(states)), states)
        ax.set_ylabel('prepared starting state'); ax.set_xlabel('declared sampling stratum')
        ax.axvline(len(times)-.5, color=fg, lw=1.2)
        ax.set_title(f'Original-identity recoveries / selected scored cores · {experiment}', fontsize=13, pad=18)
        fig.subplots_adjust(left=.07, right=.86, top=.89, bottom=.22)
        cax = fig.add_axes([.89, .28, .018, .53]); fig.colorbar(im, cax=cax, label='recovery / selected scored cores')
        fig.text(.5, .065, f'Gate: ≥{gates["minimum_confirmed_per_nonempty_scored_stratum"]} original-identity recovery in every nonempty scored stratum.\n'
                 'First and last distinct core coordinates selected prospectively; ineligible selections retained.\n'
                 'Empty strata are unselected, not tested recovery zero. No confidence intervals or independent-history inference.', ha='center', fontsize=9)
        export(fig, 'calibration-strata', dark, artifacts, [experiment], source_paths,
               {'columns': columns, 'states': states, 'denominator': 'selected scored cores per stratum'})


def benefit_figures(a, m, artifacts):
    experiment = m['benefit_experiment_id']
    paths = [OUT/'analysis.json', OUT/'calibration-analysis.json', OUT/'manifest.json']
    if (OUT/'symmetry-audit.json').exists():
        paths.append(OUT/'symmetry-audit.json')
    impacts, impact_paths, impact_note = impact_summary(m)
    paths += impact_paths
    identical_panels = all(
        p['panels']['development']['exact_totals'][state]['score_sum'] ==
        p['panels']['confirmation']['exact_totals'][state]['score_sum']
        for p in a['pairs'] for state in [p['candidate']]+p['inputs'])
    panel_note = ('Development and confirmation panel means are identical.' if identical_panels
                  else 'Development and confirmation panel means differ.')
    states = m['config']['states']
    conditions = [f'{split}-{i}' for split in ('development', 'confirmation') for i in range(2)]
    lookup = {(r['state'], r['condition']): r for r in a['runs']}
    matrix = np.array([[lookup[state, condition]['score'] for condition in conditions] for state in states])
    for dark in THEMES:
        bg, fg = theme(dark)
        fig, ax = plt.subplots(figsize=(10, 6.2)); cmap = quantitative_cmap()
        upper = max(1., float(matrix.max())); im = ax.imshow(matrix, cmap=cmap, vmin=0, vmax=upper, interpolation='nearest', aspect='auto')
        for i, state in enumerate(states):
            for j, condition in enumerate(conditions):
                r = lookup[state, condition]
                removed = '+'.join(str(e['removed_occupied_cells']) for e in impacts[r['run_id']])
                color=annotation_color(cmap(matrix[i,j]/upper))
                ax.text(j, i-.14, f'{matrix[i,j]:.3f}', ha='center', va='center', fontsize=14,color=color)
                ax.text(j, i+.18, f'removed {removed} occupied cells', ha='center', va='center', fontsize=8,color=color)
        ax.set_xticks(range(4), ['Development\ncondition 0', 'Development\ncondition 1', "Frozen 'confirmation'\ncondition 0", "Frozen 'confirmation'\ncondition 1"])
        ax.set_yticks(range(len(states)), states); ax.set_ylabel('complete prepared state')
        ax.axvline(1.5, color=fg, lw=1.2)
        ax.set_title(f'Known-identity structural population proxy · {experiment}', fontsize=13, pad=15)
        fig.subplots_adjust(left=.08, right=.84, top=.88, bottom=.31)
        cax = fig.add_axes([.89, .36, .024, .43]); fig.colorbar(im, cax=cax, label='mean registered closed-core count')
        fig.text(.5, .045, 'Each mean uses 81 equally weighted samples (t=0,20,…,1600); occupied-cell removals shown at t=600+1000.\n'
                 +impact_note+'\n'+panel_note+'\n'
                 "Frozen 'confirmation' states are rotational symmetry duplicates; independent exposure confirmation remains unresolved.\n"
                 'Fixed four-identity registry; V01/RV01 share an identity. Other valid and unknown identities are excluded.\n'
                 'Deterministic conditions; no population replication, ancestry assignment, total viable-population or disturbance-resilience claim.', ha='center', fontsize=8)
        export(fig, 'score-matrix', dark, artifacts, [experiment], paths,
               {'states': states, 'conditions': conditions, 'sample_count_per_condition': 81,
                'metric': 'mean fixed-registry recognized closed-core count; structural proxy',
                'disturbance_impact': impact_note, 'identical_panel_means': identical_panels})

        fig, axes = plt.subplots(1, 3, figsize=(13, 5.7), gridspec_kw={'width_ratios': [3.4, 3.4, 2.5]})
        all_margins = [v for pair in a['pairs'] for split in ('development', 'confirmation')
                       for v in pair['panels'][split]['candidate_minus_inputs'].values()]
        lower = min([0]+all_margins); upper_margin = max([0]+all_margins)
        padding = max(.5, (upper_margin-lower)*.18)
        for ax, pair in zip(axes[:2], a['pairs']):
            inputs = pair['inputs']; x = np.arange(len(inputs))
            for offset, split, color, hatch in ((-.18, 'development', STYLE['series']['primary'], None),
                                               (.18, 'confirmation', STYLE['series']['tertiary'], '//')):
                vals = [pair['panels'][split]['candidate_minus_inputs'][q] for q in inputs]
                bars = ax.bar(x+offset, vals, width=.32, color=color, hatch=hatch, edgecolor=STYLE['axis'], linewidth=.5, label=split)
                for bar, value in zip(bars, vals):
                    ax.annotate(f'{value:+.3f}', (bar.get_x()+bar.get_width()/2, value),
                                xytext=(0, 5 if value>=0 else -5), textcoords='offset points',
                                ha='center', va='bottom' if value>=0 else 'top', fontsize=9)
            ax.axhline(0, color=STYLE['annotation']['target'], lw=1)
            ax.set_xticks(x, [f'minus {q}' for q in inputs]); ax.set_ylim(lower-padding, upper_margin+padding)
            ax.set_ylabel('candidate − input mean registered core count')
            ax.set_title(f'{pair["candidate"]} vs both encounter inputs')
            ax.legend(loc='upper center', bbox_to_anchor=(.5, -.13), frameon=False, fontsize=8)
            verdict = 'MET' if pair['structural_advantage_both_panels'] else 'NOT MET'
            ax.text(.5, -.29, f'Frozen structural strict-advantage criterion: {verdict}', transform=ax.transAxes, ha='center', fontsize=8)
        card = axes[2]; card.set_axis_off(); passed = a['calibration']['gate_passed']
        card.add_patch(Rectangle((.02, .08), .96, .84, transform=card.transAxes, fill=False,
                                edgecolor=fg, hatch=None if passed else '///', alpha=.3))
        if passed:
            result = a['yield']; text = ('CALIBRATION PASSED\n\nFROZEN CRITERION MET\n'
                    f'main: {result["main"]["confirmed"]}/36\nheld-out: {result["heldout"]["confirmed"]}/18\n'
                    f'overall: {result["overall"]["confirmed"]}/54\n\nIndependent exposure\nconfirmation unresolved\n\n16 other candidate encounters\nremain unresolved')
        else:
            assert all(p['confirmed_benefit'] is None for p in a['pairs'])
            text = ('CALIBRATION NOT PASSED\n\nBenefit confirmation\nBLOCKED\n\nBeneficial-heritable yield\nUNKNOWN, not zero\n\nEncounter denominators:\n36 main; 18 held-out; 54 total')
        card.text(.5, .52, text, transform=card.transAxes, ha='center', va='center', fontsize=9)
        fig.suptitle(f'Paired structural score contrasts · {experiment}', fontsize=14)
        fig.text(.5, .015, 'Each panel mean pools two frozen conditions (162 samples); strict criterion requires all four displayed contrasts >0.\n'
                 +impact_note+' '+panel_note+'\n'
                 "Frozen 'confirmation' is a rotational symmetry duplicate; independent exposure confirmation remains unresolved.\n"
                 'Descriptive margins. No confidence intervals, independent-population or disturbance-resilience inference.',
                 ha='center', fontsize=8)
        fig.subplots_adjust(left=.065, right=.98, top=.85, bottom=.3, wspace=.43)
        export(fig, 'paired-margins', dark, artifacts, [experiment, m['calibration_experiment_id']], paths,
               {'candidate_pairs': m['config']['pairs'], 'gate_passed': passed,
                'metric': 'candidate minus each input mean fixed-registry core score; paired condition panels'})


def ecological_animation(frames, times, stages, path, state, condition, experiment, impact_note):
    """Literal pixels, explicit before/after stages, and no lineage overlays."""
    scale = 2; images = []; small = ImageFont.truetype(FONT_PATH, 11)
    for grid, t, stage in zip(frames, times, stages):
        raw = Image.fromarray(PALETTE[grid]).resize((grid.shape[1]*scale, grid.shape[0]*scale), Image.Resampling.NEAREST)
        width = max(640, raw.width); offset = (width-raw.width)//2
        canvas = Image.new('RGB', (width, raw.height+188), STYLE['ink']); canvas.paste(raw, (offset, 80))
        draw = ImageDraw.Draw(canvas)
        draw.text((18, 10), f'CHROMATIC FIELDS / {state} disturbance assay', font=FONT, fill=STYLE['heading'])
        draw.text((18, 38), f't = {t:,} updates | {stage}', font=SMALL, fill=STYLE['text'])
        draw.text((18, 59), f'{experiment} | {condition} | periodic world', font=SMALL, fill=STYLE['text'])
        draw.rectangle((offset-1, 79, offset+raw.width, 80+raw.height), outline=STYLE['axis'], width=1)
        y = raw.height+87
        draw.text((18, y), f'literal states | {grid.shape[1]} × {grid.shape[0]} cells | 10-cell scale', font=SMALL, fill=STYLE['text'])
        draw.line((width-50, y+9, width-50+10*scale, y+9), fill=STYLE['text'], width=2)
        for index, name in enumerate(['quiescent', 'carrier', 'sheath', 'junction', 'turn', 'messenger', 'cord', 'growth', 'dissolve']):
            xx = 12+(index%5)*(width//5); yy = raw.height+112+(index//5)*23
            draw.rectangle((xx, yy+2, xx+10, yy+12), fill=STYLE['cell_states'][index], outline=STYLE['text'], width=1)
            draw.text((xx+14, yy), f'{index} {name}', font=small, fill=STYLE['text'])
        draw.text((18, raw.height+162), impact_note+' Core counts are a structural proxy.', font=small, fill=STYLE['text'])
        images.append(canvas)
    images[0].save(path, save_all=True, append_images=images[1:], duration=150, loop=0, lossless=True, method=6)
    return scale


def evidence_figure(a, m, artifacts):
    """Shared encounter denominator; unresolved cases are never failed trials."""
    atlas_path = ROOT/'data/atlas-v2/analysis.json'
    catalogue_path = ROOT/'data/atlas-v2/confirmed/catalogue.json'
    atlas = read_json(atlas_path); catalogue = read_json(catalogue_path)
    n = sum(s['total'] for s in atlas['splits'].values())
    candidate = sum(s['candidate_runs'] for s in atlas['splits'].values())
    inherited = sum(s['confirmed_inherited_runs'] for s in atlas['splits'].values())
    catalogue_absent_origins = {origin['run_id'] for entry in catalogue['entries']
                               if entry['novel_to_input_catalogue'] for origin in entry['confirmation_origins']}
    benefit = a['yield']['overall']['confirmed']
    values = [candidate, inherited, len(catalogue_absent_origins), benefit]
    paths = [atlas_path, catalogue_path, OUT/'analysis.json', OUT/'calibration-analysis.json', OUT/'manifest.json']
    _,impact_paths,impact_note = impact_summary(m)
    paths += impact_paths
    if (OUT/'symmetry-audit.json').exists():paths.append(OUT/'symmetry-audit.json')
    for dark in THEMES:
        _,fg = theme(dark)
        fig,(ax,card) = plt.subplots(1,2,figsize=(13,6.3),gridspec_kw={'width_ratios':[4.2,2.2]})
        colors=[STYLE['status']['candidate'],STYLE['status']['confirmed'],STYLE['series']['secondary'],STYLE['series']['tertiary']]
        for index,value in enumerate(values):
            if value is None:
                ax.text(index,1,'UNKNOWN\ncalibration blocked',ha='center',fontsize=8)
                continue
            ax.bar(index,value,width=.62,color=colors[index])
            ax.text(index,value+.5,f'{value}/{n}',ha='center',fontsize=13)
        ax.set_xticks(range(4),['Pair-relative\ncandidate novelty','Pair-relative\nconfirmed inheritance','Inherited identity\nabsent from\ninput catalogue','Frozen calibrated-proxy\ncriterion met'])
        ax.tick_params(axis='x',labelsize=9)
        ax.set_ylim(0,max(candidate+3,5)); ax.set_yticks(range(0,candidate+3,2)); ax.set_ylabel('encounters meeting the stated endpoint')
        ax.set_title('Shared denominator: main + held-out encounter states',fontsize=12)
        card.set_axis_off()
        card.add_patch(Rectangle((.02,.03),.96,.92,transform=card.transAxes,fill=False,edgecolor=fg,alpha=.4))
        card.text(.5,.79,f'{a["unresolved_other_candidate_encounters"]}/{n} other candidate-producing encounters\nremain unresolved under bounded searches.\nThey are not confirmed failures.',transform=card.transAxes,ha='center',va='center',fontsize=10)
        card.text(.5,.49,'RV01: recovers known V01 identity,\npair-relative novelty; frozen proxy criterion met.\n\nRV02: absent from input catalogue;\nfrozen proxy criterion not met.',transform=card.transAxes,ha='center',va='center',fontsize=9)
        card.text(.5,.18,"'Confirmation' is a symmetry duplicate.\nIndependent exposure confirmation unresolved.\nH1/H3 and RSI remain untested/unestablished.",transform=card.transAxes,ha='center',va='center',fontsize=9)
        fig.suptitle(f'Current evidence endpoints · {atlas["experiment_id"]} + {a["experiment_id"]}',fontsize=14)
        fig.text(.5,.055,f'All {n} encounter states retained: {atlas["splits"]["main"]["total"]} main + {atlas["splits"]["heldout"]["total"]} held-out. Bars have one common denominator and no uncertainty intervals.\n'
                 'Catalogue absence and frozen score advantage are different endpoints; none assigns genetic parentage.\n'
                 'Known-identity structural proxy only. '+impact_note+' No disturbance-resilience claim.',ha='center',fontsize=8)
        fig.subplots_adjust(left=.07,right=.98,top=.85,bottom=.27,wspace=.28)
        export(fig,'evidence-stages',dark,artifacts,[atlas['experiment_id'],m['calibration_experiment_id'],a['experiment_id']],paths,
               {'denominator':n,'counts':{'pair_relative_candidate':candidate,'pair_relative_inheritance':inherited,
                'inherited_absent_input_catalogue':len(catalogue_absent_origins),'frozen_proxy_criterion':benefit},
                'unresolved_other_candidate_encounters':a['unresolved_other_candidate_encounters'],
                'independent_exposure_confirmation':'unresolved; reserved conditions are symmetry duplicates'})


def disturbance_figures(m, artifacts):
    experiment = m['benefit_experiment_id']; states = ['V01', 'RV01', 'RV02']
    selected = [next(r for r in m['runs'] if r['state']==state and r['condition']['id']=='development-0') for state in states]
    records = []; source_paths = [OUT/'manifest.json']; metadata = []
    for spec in selected:
        folder = OUT/'development'/spec['run_id']; result = read_json(folder/'result.json')
        source_paths.append(folder/'result.json'); snapshots = []
        for t in m['benefit']['disturbance_times']:
            path = folder/f'disturbance-{t}.npz'; source_paths.append(path)
            event = next(e for e in result['events'] if e['type']=='disturbance' and e['t']==t)
            with np.load(path) as arrays:
                before=arrays['before'].copy(); after=arrays['after'].copy()
            assert digest(before)==event['before_hash'] and digest(after)==event['after_hash']
            snapshots.extend([(before, t, 'before', event), (after, t, 'after', event)])
        records.append((spec, snapshots))
        metadata.append({'state': spec['state'], 'run_id': spec['run_id'], 'times': m['benefit']['disturbance_times'],
                         'block': spec['condition']['block'], 'block_size': m['benefit']['block_size']})
    for dark in THEMES:
        theme(dark); fig, axes = plt.subplots(len(states), 4, figsize=(13, 11.5), squeeze=False)
        for i, (spec, snapshots) in enumerate(records):
            for j, (grid, t, stage, event) in enumerate(snapshots):
                ax=axes[i,j]; ax.imshow(grid, cmap=CMAP, norm=NORM, interpolation='nearest')
                count=event[f'{"pre" if stage=="before" else "post"}_counts']['scored_cores']
                ax.set_title(f'{spec["state"]} · t={t} {stage} clear\nregistered cores: {count}', fontsize=9)
                y,x=spec['condition']['block'];size=m['benefit']['block_size']
                ax.add_patch(Rectangle((x-.5,y-.5),size,size,fill=False,edgecolor=STYLE['annotation']['target'],lw=1,linestyle='--'))
                ax.set_xticks([0,grid.shape[1]//2,grid.shape[1]-1]); ax.set_yticks([0,grid.shape[0]//2,grid.shape[0]-1]);ax.set_xlabel('column / cells',fontsize=9)
                if j==0:ax.set_ylabel('row / cells',fontsize=9)
            removed = [snapshots[j][3]['removed_occupied_cells'] for j in (0,2)]
            axes[i,0].text(0,-.34,f'{spec["run_id"]}: removed occupied cells {removed[0]} at t=600; {removed[1]} at t=1000.',
                           transform=axes[i,0].transAxes,ha='left',fontsize=8)
        fig.suptitle(f'Actual declared disturbance states · {experiment} · development-0', fontsize=14)
        events = [snapshots[j][3] for _,snapshots in records for j in (0,2)]
        zero = sum(e['removed_occupied_cells']==0 for e in events)
        fig.text(.5,.10,f'{zero}/{len(events)} depicted clearings removed zero occupied cells. These are predeclared cases, not disturbance-resilience demonstrations.\n'
                 'Dashed outline: prescribed 24×24 cleared block. Before and after are the same update, separated by the explicit intervention.\n'
                 'Full periodic domains; literal state colors; registered core counts are structural measurements, not assigned lineages or proved native viability.\n'
                 'Cases were declared before scoring, not selected for large disturbance responses.',ha='center',fontsize=8)
        fig.subplots_adjust(left=.07,right=.98,top=.91,bottom=.22,wspace=.28,hspace=.7);legend(fig)
        export(fig,'disturbance-states',dark,artifacts,[experiment],source_paths,{'cases':metadata,'selection':'predeclared development-0 states V01, RV01, RV02'})
    # Stream one state at a time; normal raw data are compact post-intervention samples.
    for spec in selected:
        folder=OUT/'development'/spec['run_id']; replay=folder/'replay.npz'; result=read_json(folder/'result.json')
        with np.load(replay) as arrays:
            raw_frames=arrays['frames'];raw_times=arrays['times'];display=[]
            for index,t in enumerate(raw_times):
                if index%2==0 or int(t) in m['benefit']['disturbance_times'] or index==len(raw_times)-1:
                    display.append((int(t),1,raw_frames[index].copy(),'post-intervention sample'))
        paths=[replay,folder/'result.json',OUT/'manifest.json']
        for t in m['benefit']['disturbance_times']:
            path=folder/f'disturbance-{t}.npz';paths.append(path)
            event=next(e for e in result['events'] if e['type']=='disturbance' and e['t']==t)
            with np.load(path) as arrays:display.append((t,0,arrays['before'].copy(),f'before clear · removes {event["removed_occupied_cells"]} occupied'))
        display.sort(key=lambda frame:frame[:2]);frames=[d[2] for d in display];times=[d[0] for d in display]
        events=[e for e in result['events'] if e['type']=='disturbance']
        removed={e['t']:e['removed_occupied_cells'] for e in events}
        stages=[f'after clear · removed {removed[t]} occupied' if t in removed and order==1 else stage for t,order,_,stage in display]
        impact_note=f'{sum(e["removed_occupied_cells"]==0 for e in events)}/{len(events)} clearings remove zero occupied cells.'
        path=FIG/f'{PREFIX}disturbance-{spec["state"]}.webp'
        scale=ecological_animation(frames,times,stages,path,spec['state'],'development-0',experiment,impact_note)
        artifacts.append({'file':path.name,'experiments':[experiment],'command':COMMAND,'run_id':spec['run_id'],
                          'source_sha256':sources_metadata(paths),'selection':'predeclared development-0 case',
                          'display_times':times,'display_stages':stages,'pixels_per_cell':scale,
                          'disturbance_impact':impact_note,
                          'sha256':file_hash(path),'style_sha256':file_hash(ROOT/'configs/style.json')})
        del frames,display,raw_frames
        gc.collect()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--only',choices=['calibration','benefit','evidence','disturbances','all'],default='all');args=parser.parse_args()
    FIG.mkdir(exist_ok=True);m=read_json(OUT/'manifest.json');target=FIG/'manifest.json';existing=read_json(target)
    names={'calibration':('calibration-recovery','calibration-strata'),'benefit':('score-matrix','paired-margins'),
           'evidence':('evidence-stages',),'disturbances':('disturbance-states','disturbance-V01','disturbance-RV01','disturbance-RV02')}
    selected=list(names) if args.only=='all' else [args.only]
    prefixes=tuple(PREFIX+name for group in selected for name in names[group])
    artifacts=[a for a in existing['artifacts'] if not a['file'].startswith(prefixes)]
    if 'calibration' in selected:calibration_figures(read_json(OUT/'calibration-analysis.json'),m,artifacts)
    if 'benefit' in selected:benefit_figures(read_json(OUT/'analysis.json'),m,artifacts)
    if 'evidence' in selected:evidence_figure(read_json(OUT/'analysis.json'),m,artifacts)
    if 'disturbances' in selected:disturbance_figures(m,artifacts)
    existing['artifacts']=artifacts;target.write_text(json.dumps(existing,indent=2)+'\n')
    print('Ecological exports complete; figure manifest contains',len(artifacts),'artifacts',flush=True)


if __name__=='__main__':main()
