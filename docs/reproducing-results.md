# Reproducing the experiments and figures

The [README](../README.md) explains the research and results. This guide contains installation, integrity checks, and execution details. Existing experiment definitions and evidence remain in `protocols/`, `configs/`, and `data/`.

## Installation

Use Python 3.10+, GCC, and the pinned packages. Commands below assume a shell in the repository root and an activated environment.

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
export OPENBLAS_NUM_THREADS=1
```

## Inspect the committed evidence

```sh
sha256sum -c data/SHA256SUMS
```

Read [atlas analysis](../data/atlas/analysis.md), [inheritance follow-up analysis](../data/fate-calibration/analysis.md), and the [paper](../paper/manuscript.md). Figures are already committed and indexed in [figures/manifest.json](../figures/manifest.json).

The checksum file covers committed data. Regenerated timing and export metadata may differ even when physical results agree. Compare physical grid hashes and scientific endpoint tables when reproducing an experiment; refresh checksums with `python -m scripts.checksums write` only after inspecting intentional changes.

## Rebuild analyses and exports

These commands read completed experiment evidence; they do not launch a new encounter campaign.

```sh
python -m scripts.analyze
python -m scripts.analyze_fate
python -m scripts.figures
python -m scripts.figures_fate
python -m scripts.render_manuscript
```

The Markdown manuscript is authoritative; the final command regenerates its PDF. The style configuration is `configs/style.json`. Each scientific figure records its experiment, source state, and regeneration command in the figure manifest.

## Verify or resume the recorded experiments

```sh
python -m scripts.verify
python -m scripts.atlas run
python -m scripts.atlas inherit
python -m scripts.check_evidence
python -m scripts.fate_calibration run
python -m scripts.fate_calibration verify
```

The runners skip completed cases. Verification includes exact physical replay, and `scripts.check_evidence` writes integrity reports and extracted-state records; use a separate checkout if you need to preserve every committed artifact byte. These commands reproduce existing work rather than define independent evolutionary replicates.

The atlas contains 32 main and eight held-out contacting states, 40 separated controls, and 24 alone controls. Its design is in [protocol 001](../protocols/001-encounter-atlas.md); the identity-definition audit is in [protocol 002](../protocols/002-identity-audit.md). The inheritance follow-up design is in [protocol 004](../protocols/004-candidate-fate-calibration.md).

## Run from fresh states

Work in a separate checkout so the original evidence stays available for comparison. Remove that copy's `data/atlas/runs/` directory to rerun the atlas, or its `data/fate-calibration/runs/` directory to rerun the calibration. Then execute the corresponding run, inheritance, and analysis commands above.

For reconstruction of the atlas starting states, first run `python -m scripts.explore`, remove the separate copy's `data/atlas/manifest.json`, and run `python -m scripts.atlas freeze`. Compare complete starting-grid hashes against the original manifest. For calibration reconstruction, remove the copy's calibration manifest and run `python -m scripts.fate_calibration freeze`; compare source hashes and the frozen code/configuration versions. The versioned protocols identify the original acquisition conditions.

## Implementation and provenance

The compiled C kernel implements synchronous periodic updates with compact uint8 arrays. All 59,049 local neighborhoods agree with the pinned CellPyLib reference and an independent expansion of the original author rules. Exact seed, rule, and source details are in [source_review.md](source_review.md), `data/verification.json`, and `data/author_comparison.json`. Third-party license and attribution notices are retained in `evoloop/vendor/`.

An independent author-file comparison is available as `python -m scripts.compare_author /path/to/temporary/EvoLoopS-1.0` after retrieving the archive linked in the source review. The author archive is inspected separately rather than bundled with this project.

`python -m scripts.accelerated_atlas` uses the independently checked compiled contact diagnostic. The original route and its equivalence checks are recorded in `data/atlas/execution.json` and [execution-optimization.md](execution-optimization.md). Recorded runner times were 19.6 minutes for the atlas and 8.5 minutes for calibration, with peak runner memory of 61.9 and 63.6 MiB respectively; these exclude separate rendering processes and describe the acquisition machine.

Operational continuity is recorded in [RESEARCH_STATE.md](../RESEARCH_STATE.md). The [next experiment](next-experiment.md) describes the scientific extension beyond the committed data.

## Three-identity discovery and fresh atlas

Protocol 005 reached three viable native-word identities in 79 selected trials,
with complete source and serial-isolation evidence in `data/panel-v2/`.
Runtime was 13.1 minutes and peak RSS 64.7 MiB with one worker. All three histories,
79 source extractions, and 149 generation states replayed exactly. The periodic
measurement module is separate from the frozen legacy detector; its tests cover
seam translation, full-component extraction, shared cores, and winding rejection.

```sh
OPENBLAS_NUM_THREADS=1 python -m unittest tests.test_periodic_tracking -v
OPENBLAS_NUM_THREADS=1 python -m scripts.verify_fresh panel
OPENBLAS_NUM_THREADS=1 python -m scripts.cropped_fresh_atlas run
OPENBLAS_NUM_THREADS=1 python -m scripts.cropped_fresh_atlas inherit
OPENBLAS_NUM_THREADS=1 python -m scripts.analyze_fresh_atlas
OPENBLAS_NUM_THREADS=1 python -m scripts.audit_fresh_atlas
OPENBLAS_NUM_THREADS=1 python -m scripts.verify_fresh atlas
OPENBLAS_NUM_THREADS=1 python -m scripts.audit_fresh_lineages
OPENBLAS_NUM_THREADS=1 python -m scripts.catalogue_fresh_variants
OPENBLAS_NUM_THREADS=1 python -m scripts.figures_panel
OPENBLAS_NUM_THREADS=1 python -m scripts.figures_fresh_atlas
OPENBLAS_NUM_THREADS=1 python -m scripts.render_manuscript
```

The 144 complete starting grids are frozen in `data/atlas-v2/manifest.json`:
36 main near, 18 held-out near, 54 matched separated, 36 solitary. This uses the same
640-square world extent for every treatment. The inheritance search follows
three offspring per generation, depth six, and at most 24 simulations per root.
Benefit remains a separate, unfinished comparison. The optimized route requires
the committed implementation-equivalence report. It preserves the frozen rule,
starting states, detector outcomes, and search budgets; [tiled execution](tiled-execution.md)
and [cropped detection](cropped-execution.md) document equivalence checks and
the original dense alternative.

For full reconstruction, preserve the committed evidence in another checkout,
then remove that copy's `data/panel-v2/` and `data/atlas-v2/` directories. Run
`python -m scripts.panel_discovery freeze`, `python -m scripts.panel_discovery run`,
and `python -m scripts.fresh_atlas freeze`, then use the unoptimized
`python -m scripts.fresh_atlas run` and `python -m scripts.fresh_atlas inherit`
followed by the analysis/export commands above. Optimization proofs are bound
to the committed manifest; reconstruct and reverify them before using optimized
execution with a renewed manifest. Compare physical grid and snapshot hashes, endpoint counts, and plots.
Runtime fields change; frozen manifest hashes are renewed for the new execution.
Do not rerun discovery over an existing frozen atlas: its source-report hash is
enforced. Check committed `data/SHA256SUMS` before regenerating timing metadata.

The completed acquisition took 35.8 minutes summed across the recorded runs;
the last acquisition process used 69.9 MiB peak RSS. The serial-isolation search
took 344.9 seconds for 88 captured roots and 1,205 generation simulations.
These times describe this machine and the mixed, explicitly recorded execution
routes; the short kernel benchmark is not a full-campaign speedup estimate.

`outcomes.csv` joins acquisition records with the final inheritance searches.
Acquisition `result.json` files preserve their original, pre-search pending
statuses; consult the joined table and `inheritance.json` for completed search
outcomes. Structural core appearances and disappearance are recorded separately
from verified serial reproduction. The independent lineage audit checks every
candidate's first observation and every linked search state, while the dense
verification replays four full encounter/control trajectories and every isolated
generation. Its scope is recorded in the corresponding JSON reports; it does
not imply dense replay of all 144 complete trajectories.

The frozen analyzer's generic sentence about zero confirmed inheritance applies
to zero cells and nonconfirming searches, not the complete fresh atlas, whose
observed count is 2/54. Its source and generated report are preserved; the
[independent interpretation audit](scientific_review.md) records this wording
clarification and verifies the positive denominators and paths.

`confirmed/catalogue.json` retains both recovered stable identities and all
eight confirmation origins. One matches V01 in the input catalogue and is novel
relative to its V02/V03 encounter inputs; the other differs from all three input
words. Repeated roots in one encounter are not independent variant-generating
events. Export labels and the earliest-capture representative rule are fixed in
`scripts.catalogue_fresh_variants`; benefit is unknown for both identities.
