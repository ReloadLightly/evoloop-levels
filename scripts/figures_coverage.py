"""Recorded protocol 010 coverage outcomes under the shared Chromatic Fields theme."""
import argparse
import hashlib
import json

import numpy as np
from evoloop.engine import ROOT
from scripts.figures import (FIG, STYLE, THEMES, CMAP, NORM, theme, save, legend,
                             quantitative_cmap, annotation_color)
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

OUT = ROOT / "data/coverage-v1"
COMMAND = "OPENBLAS_NUM_THREADS=1 python -m scripts.figures_coverage"


def read(path):
    return json.loads(path.read_text())


def export(fig, name, dark, artifacts, paths, extra=None):
    sources = [OUT / n for n in ("manifest.json", "readiness.json", "analysis.json", "integrity.json")]
    sources += paths
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(sources))}
    save(fig, "coverage1-" + name, dark, artifacts, ["EXP-score-coverage-001"],
         {"command": COMMAND, "source_sha256": hashes, **(extra or {})})


def recovery(analysis, artifacts):
    labels = ["scored", "valid_unregistered", "unknown_identity"]
    cols = [0, 100, 400]
    lookup = {(r["source_class"], r["delay"]): r for r in analysis["by_delay"]}
    values = np.full((3, 3), np.nan)
    for i, label in enumerate(labels):
        for j, delay in enumerate(cols):
            row = lookup[label, delay]
            if row["planned"]:
                values[i, j] = row["confirmed"] / row["planned"]
    for dark in THEMES:
        theme(dark); fig, ax = plt.subplots(figsize=(10.8, 5.5))
        cmap = quantitative_cmap().copy(); cmap.set_bad(STYLE["status"]["missing"])
        im = ax.imshow(values, vmin=0, vmax=1, cmap=cmap, aspect="auto", interpolation="nearest")
        for i, label in enumerate(labels):
            for j, delay in enumerate(cols):
                row = lookup[label, delay]
                fill = cmap(values[i, j]) if row["planned"] else STYLE["status"]["missing"]
                text = (f'{row["confirmed"]}/{row["planned"]} confirmed\n{row["eligible"]}/{row["planned"]} extractable'
                        if row["planned"] else "EMPTY\n0 selected")
                ax.text(j, i, text, ha="center", va="center", color=annotation_color(fill), fontsize=11)
                if not row["planned"]:
                    ax.add_patch(Rectangle((j-.5, i-.5), 1, 1, fill=False, hatch="///", edgecolor=STYLE["text"]))
        ax.set_xticks(range(3), [f"delay {d} updates" for d in cols])
        ax.set_yticks(range(3), ["registry-scored source", "valid unregistered source", "unknown source identity"])
        ax.set_xlabel("Isolation after native maturation; source times 400, 800, 1200 updates")
        ax.set_title("Stable descendant recovery / all selected roots · EXP-score-coverage-001", pad=14)
        fig.colorbar(im, ax=ax, fraction=.04, pad=.035, label="confirmed / planned delay selections")
        fig.subplots_adjust(left=.25, right=.89, bottom=.27, top=.84)
        controls = analysis["phase_controls"]; score = analysis["scored_delay0"]
        fig.text(.5, .07, f'40 finite D/U worlds; 360 declared class strata. Coverage gate: {analysis["gate_status"].upper()}.\n'
                 f'Original-identity phase controls {controls["confirmed"]}/{controls["selected"]}; scored delay-zero {score["confirmed"]}/{score["selected"]}; RV02 {score["per_state"][-1]["confirmed_delay0"]}/{score["per_state"][-1]["selected"]} below 80%.\n'
                 'All selected observations remain in denominators, including lost and shared targets. Stable transmission requires two unchanged edges.\n'
                 'Missing strata are hatched; measured zero is numeric. Recovery after isolation does not establish benefit or total viable population.',
                 ha="center", fontsize=8.5)
        export(fig, "recovery", dark, artifacts, [], {"encoding": "exact confirmed/planned and eligible/planned integer counts", "status": "completed diagnostic panel"})


def strata(analysis, artifacts):
    states = read(OUT / "manifest.json")["config"]["states"]
    labels = ["scored", "valid_unregistered", "unknown_identity"]
    selected = []; confirmed = []
    for state in states:
        ss = []; cc = []
        for label in labels:
            row = next(r for r in analysis["breakdown"] if r["dimension"] == "state" and r["value"] == state and r["source_class"] == label)
            ss.append(row["selected"]); cc.append(row["confirmed"])
        selected.append(ss); confirmed.append(cc)
    selected = np.asarray(selected); confirmed = np.asarray(confirmed)
    ratios = np.divide(confirmed, selected, out=np.full(selected.shape, np.nan), where=selected > 0)
    for dark in THEMES:
        theme(dark); fig, ax = plt.subplots(figsize=(10.3, 6.0))
        cmap = quantitative_cmap().copy(); cmap.set_bad(STYLE["status"]["missing"])
        im = ax.imshow(ratios, vmin=0, vmax=1, cmap=cmap, aspect="auto", interpolation="nearest")
        for i in range(len(states)):
            for j in range(3):
                n = selected[i, j]; yes = confirmed[i, j]
                fill = cmap(ratios[i, j]) if n else STYLE["status"]["missing"]
                ax.text(j, i, f"{yes}/{n}" if n else "EMPTY\n0 selected", ha="center", va="center", color=annotation_color(fill), fontsize=12)
                if not n:
                    ax.add_patch(Rectangle((j-.5, i-.5), 1, 1, fill=False, hatch="///", edgecolor=STYLE["text"]))
        ax.set_xticks(range(3), ["scored", "valid unregistered", "unknown identity"])
        ax.set_yticks(range(len(states)), states); ax.set_ylabel("complete starting representative")
        ax.set_xlabel("Source classification stays fixed if descendants change identity")
        ax.set_title("Recovery at any declared delay / selected observations · EXP-score-coverage-001", pad=14)
        fig.colorbar(im, ax=ax, fraction=.04, pad=.035, label="union recoveries / selected observations")
        fig.subplots_adjust(left=.10, right=.88, bottom=.23, top=.86)
        fig.text(.5, .065, 'One recovery per source observation across delays 0/100/400; eight D/U condition worlds per state.\n'
                 'Repeated roots and convergent paths are not independent organisms or histories. Unknown and ineligible selections remain explicit.\n'
                 'Coordinate-selected diagnostic sample; D/U composition contrasts do not identify a disturbance effect.', ha="center", fontsize=9)
        export(fig, "state-unions", dark, artifacts, [], {"encoding": "exact union-confirmed/selected source observations", "status": "completed diagnostic panel"})


def raw(recovery, artifacts):
    examples = [next((o for o in recovery["observations"] if o["source_class"] == label), None)
                for label in ("valid_unregistered", "unknown_identity")]
    examples = [o for o in examples if o is not None]
    if not examples:
        return
    paths = []
    for dark in THEMES:
        theme(dark); fig, axes = plt.subplots(len(examples), 3, figsize=(12, 4.5*len(examples)+1), squeeze=False)
        for i, o in enumerate(examples):
            for j, delayed in enumerate(o["delays"]):
                ax = axes[i, j]
                path = OUT / "worlds" / o["run_id"] / f'grid-{delayed["t"]}.npz'
                paths.append(path)
                with np.load(path, allow_pickle=False) as data:
                    grid = data["grid"]
                ax.imshow(grid, cmap=CMAP, norm=NORM, interpolation="nearest", extent=(-.5, 191.5, 191.5, -.5))
                y, x, h, w = o["core"]
                # Split torus-wrapped target outlines into exact visible rectangles.
                for xx, ww in ((x, min(w, 192-x)), (0, max(0, x+w-192))):
                    for yy, hh in ((y, min(h, 192-y)), (0, max(0, y+h-192))):
                        if ww and hh:
                            ax.add_patch(Rectangle((xx-.5, yy-.5), ww, hh, fill=False, edgecolor=STYLE["annotation"]["target"], linewidth=1))
                ax.plot([8, 18], [182, 182], color=STYLE["text"], lw=2)
                ax.text(8, 176, "10 cells", color=STYLE["text"], fontsize=7)
                ax.set_xticks([0, 191]); ax.set_yticks([0, 191]); ax.set_aspect("equal")
                ax.set_title(f'native t={delayed["t"]}; delay {delayed["delay"]}\nisolation outcome:\n{delayed["status"].replace("_", " ")}', fontsize=9)
                if j == 0:
                    ax.set_ylabel(o["source_class"].replace("_", " ") + "\n" + o["run_id"], fontsize=8)
        fig.suptitle("Native source targets through maturation · EXP-score-coverage-001", fontsize=15)
        fig.subplots_adjust(left=.08, right=.98, bottom=.17, top=.91, hspace=.27)
        legend(fig)
        fig.text(.5, .10, 'Full 192×192 periodic grids, literal nine-state colors, nearest-cell rendering; outlines retain original source core geometry.\n'
                 'First selected source in each omitted class, selected for illustration after acquisition; no outcome-based replacement.\n'
                 'Shared components and sampled core loss remain ineligible. Native structure does not identify genetic ancestry.', ha="center", fontsize=8.5)
        export(fig, "native-targets", dark, artifacts, [OUT / "recovery.json", *paths],
               {"examples": [o["observation_id"] for o in examples], "encoding": "literal cell-state mapping; original source core outline", "selection": "first selected observation per omitted source class"})


def inheritance(recovery, artifacts):
    manifest = read(OUT / "manifest.json")
    examples = []; seen = set()
    for o in recovery["observations"]:
        if o["source_class"] == "scored":
            continue
        d = o["delays"][0]
        if d["transmission_confirmed"] and d["confirmed_identity"] not in seen:
            examples.append((o, d)); seen.add(d["confirmed_identity"])
    if not examples:
        return
    paths = [OUT / "recovery.json"]; rows = []
    for o, d in examples:
        snapshot_path = OUT / d["snapshot_file"]; paths.append(snapshot_path)
        with np.load(snapshot_path, allow_pickle=False) as saved:
            snapshots = [saved["snapshot"].copy()]
        labels = ["unknown isolated source" if d["delayed_identity"] is None else "omitted isolated source"]
        reports = d["outcome"]; branch = reports["confirmation"]["path"]
        for depth, child_index in enumerate(branch):
            node = next(n for n in reports["nodes"] if n["path"] == branch[:depth])
            child = node["outcome"]["children"][child_index]
            path = OUT / d["search_dir"] / f'node-{node["node"]:02d}.npz'; paths.append(path)
            with np.load(path, allow_pickle=False) as saved:
                snapshots.append(saved[f"child{child_index}"].copy())
            states = "/".join(s for s, spec in manifest["states"].items() if spec["identity"] == child["identity"]) or "outside registry"
            labels.append(f'child {depth+1}: {states}\ndetached +{child["detached_t"]} updates')
        rows.append((o, snapshots, labels))
    columns = max(len(snapshots) for _, snapshots, _ in rows)
    for dark in THEMES:
        theme(dark); fig, axes = plt.subplots(len(rows), columns, figsize=(3.1*columns, 3.2*len(rows)+1.3), squeeze=False)
        span = max(max(a.shape) for _, snapshots, _ in rows for a in snapshots) + 6
        for i, (o, snapshots, labels) in enumerate(rows):
            for j in range(columns):
                ax = axes[i, j]
                if j >= len(snapshots):
                    ax.set_axis_off(); continue
                a = snapshots[j]; h, w = a.shape
                ax.imshow(a, cmap=CMAP, norm=NORM, interpolation="nearest", extent=(-w/2, w/2, h/2, -h/2))
                ax.set_xlim(-span/2, span/2); ax.set_ylim(span/2, -span/2); ax.set_aspect("equal")
                ax.set_xticks([]); ax.set_yticks([])
                ax.set_title(labels[j], fontsize=9)
                ax.set_xlabel(f"complete component {w}×{h} cells", fontsize=8)
                ax.plot([-span/2+2, -span/2+7], [span/2-1.5, span/2-1.5], color=STYLE["text"], lw=2)
                ax.text(-span/2+8, span/2-1.5, "5 cells", fontsize=7, va="center")
                if j == 0:
                    ax.set_ylabel(o["run_id"] + f'\nsource t={o["source_time"]}; isolation delay 0', fontsize=8)
        fig.suptitle("Omitted sources produce stable registered descendants · EXP-score-coverage-001", fontsize=14)
        fig.subplots_adjust(left=.08, right=.98, bottom=.22, top=.87, hspace=.30)
        legend(fig)
        fig.text(.5, .145, 'Recorded complete components retain arms, spacing and chirality; literal cell-state colors; equal cell geometry in every panel.\n'
                 'Each child is detached under declared serial isolation; the final two edges preserve the registered descendant identity.\n'
                 'First delay-zero positive per recovered identity, illustrated after acquisition. Source genotype remains unknown; no native parentage or benefit assigned.',
                 ha="center", fontsize=8.5)
        export(fig, "inheritance", dark, artifacts, paths,
               {"examples": [o["observation_id"] for o, _ in examples], "encoding": "literal cell states, full complete components, shared cell geometry", "selection": "first delay-zero positive omitted observation per recovered identity"})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", choices=("recovery", "strata", "raw", "inheritance"))
    args = parser.parse_args()
    integrity = read(OUT / "integrity.json")
    assert integrity["status"] == "passed" and integrity["mismatches"] == 0
    analysis = read(OUT / "analysis.json"); artifacts = []
    for name, operation in (("recovery", lambda: recovery(analysis, artifacts)),
                            ("strata", lambda: strata(analysis, artifacts)),
                            ("raw", lambda: raw(read(OUT / "recovery.json"), artifacts)),
                            ("inheritance", lambda: inheritance(read(OUT / "recovery.json"), artifacts))):
        if args.only in (None, name):
            operation()
    path = FIG / "manifest.json"; prior = read(path)
    replaced = {r["file"] for r in artifacts}
    prior["artifacts"] = [r for r in prior["artifacts"] if r["file"] not in replaced] + artifacts
    temp = path.with_suffix(".json.tmp")
    temp.write_text(json.dumps(prior, indent=2) + "\n"); temp.replace(path)
    print("Rendered", len(artifacts), "coverage artifacts", flush=True)


if __name__ == "__main__":
    main()
