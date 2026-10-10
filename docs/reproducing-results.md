# Reproducing the experiments and figures

The [README](../README.md) explains the research and results. This guide contains installation, integrity checks, and execution details. Existing experiment definitions and evidence remain in `protocols/`, `configs/`, and `data/`.

## Installation

Use Python 3.10+, GCC, and the pinned packages. Commands below assume a shell in the repository root and an activated environment.

PDF assembly also requires Ghostscript (`gs`). The renderer builds the text
pages with Matplotlib, appends the verified vector figure PDFs at their native
page sizes, and replaces the working PDF only after successful assembly.

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

## Verify the prospective score-coverage freeze

[Protocol 010](../protocols/010-paired-world-score-coverage.md) and
[coverage-v1.json](../configs/coverage-v1.json) define EXP-score-coverage-001.
Its [design receipt](../data/coverage-v1/manifest.json) references all 40 existing
paired-world initial grids and all 30 complete phase controls, with file and
original physical hashes. It also binds the unchanged registry, source physics,
extraction/search implementation and earlier numerical outcomes.

```sh
python3 -m scripts.coverage_protocol verify
python3 -m unittest tests.test_coverage_protocol -v
```

These checks use only the Python standard library; they perform no simulation,
root selection, or recovery acquisition. `freeze` creates a new receipt only
when none exists and refuses to replace one. Do not remove the committed receipt
to change the design: a revised scientific design requires a new version.

The implementation-readiness receipt is `data/coverage-v1/readiness.json`,
committed and remotely verified at `3aa73b85892e3d06115e738978ccef1bc54bf53d`
before acquisition. It binds the runner, independent auditor, fixtures, reused
verifiers, memory guard and all 40 original sample-record files. Thirty tests
passed before readiness, including an unknown source becoming identifiable at
a later delay. Search input identity is measured from the delayed snapshot;
source class remains immutable. The timing benchmark uses V01-age0 and does
not add an independent scientific sample.

```sh
OPENBLAS_NUM_THREADS=1 python -m scripts.memory_guard --retry --reserve 140 --log data/coverage-v1/execution.jsonl python -m scripts.coverage_assay run --readiness-commit 3aa73b85892e3d06115e738978ccef1bc54bf53d
OPENBLAS_NUM_THREADS=1 python -m scripts.memory_guard --retry --reserve 180 --log data/coverage-v1/execution.jsonl python -m scripts.verify_coverage
OPENBLAS_NUM_THREADS=1 python -m scripts.memory_guard --retry --reserve 140 --log data/coverage-v1/execution.jsonl python -m scripts.coverage_equivalence
OPENBLAS_NUM_THREADS=1 python -m scripts.memory_guard --retry --reserve 220 --log data/coverage-v1/execution.jsonl python -m scripts.figures_coverage
OPENBLAS_NUM_THREADS=1 python -m scripts.memory_guard --retry --reserve 180 --log data/coverage-v1/execution.jsonl python -m scripts.verify_coverage_figures
```

Run acquisition, audits, rendering and Git packing sequentially. Commands use
one worker with at least 200 MiB available memory. Completed native/search cases
are reused only after their bindings and complete artifact hashes pass. Interrupted
invocations remain in `execution.jsonl`; independent proofs permit audit resumption.
The hard design ceiling is 1080 delayed roots plus 30 controls, at most 26,640
generation simulations; empty strata reduce actual work. The design receipt
remains an immutable pre-acquisition record, while recovery results, analyses
and integrity proofs are separate artifacts. `--fresh` on the verifier requests
full replay instead of reusing passed proofs.

The completed coverage batch contains 40 native worlds, 137 selected sources,
411 planned delays, 362 eligible searches and 30 phase controls. Independent
replay passes with zero mismatches. Analysis and per-unit proof receipts are in
`data/coverage-v1`; the immutable input and readiness receipts remain separate.
The supplementary equivalence check groups 362 delayed inputs into 188 complete
states, without changing frozen source counts. Publication validation is in
`docs/coverage_figure_validation.json` and `docs/coverage_manuscript_validation.json`.
The one-control benchmark took 0.614 s (65.4 MiB peak RSS); main runner work took
580.713 s (78.8 MiB peak RSS), and independent audit work 849.307 s (134.0 MiB).
Guarded invocation durations include startup and other overhead and are retained
separately in `execution.jsonl`. These are verification timings, not replicates.

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
Benefit is a separate comparison, completed in ecological-v1 below. The optimized route requires
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
`scripts.catalogue_fresh_variants`; the later ecological-v1 analysis supplies
the completed paired proxy-benefit status for both identities.

## Ecological-score calibration and paired benefit conditions

[Protocol 007](../protocols/007-ecological-calibration-and-benefit.md) and
`configs/ecological-v1.json` extend the assay already frozen in atlas-v2.
`data/ecological-v1/manifest.json` pins all source snapshots, the four-identity
score registry, code hashes, and 30 condition configurations: ten new calibration
ecologies and twenty frozen paired conditions. Some calibration/benefit initial
grids coincide, but their future disturbance schedules differ. These conditions
are not independent evolutionary histories.

```sh
OPENBLAS_NUM_THREADS=1 python -m unittest tests.test_ecology -v
OPENBLAS_NUM_THREADS=1 python -m scripts.ecological_assay calibrate
OPENBLAS_NUM_THREADS=1 python -m scripts.analyze_ecological calibration
OPENBLAS_NUM_THREADS=1 python -m scripts.ecological_assay benefit
OPENBLAS_NUM_THREADS=1 python -m scripts.analyze_ecological benefit
OPENBLAS_NUM_THREADS=1 python -m scripts.verify_ecological
OPENBLAS_NUM_THREADS=1 python -m scripts.audit_ecological_symmetry
OPENBLAS_NUM_THREADS=1 python -m scripts.figures_ecological
OPENBLAS_NUM_THREADS=1 python -m scripts.render_manuscript
```

The runner skips completed acquisition cases; the analyzer regenerates summaries
from their physical records. Frozen source/protocol/configuration hashes are
enforced. Each declared 24-square block is cleared after advancing to update
600/1000, before the corresponding sample. Every condition uses 81 samples and
comparisons use integer sums over 162 samples per panel, so exact ties fail.
Complete source, removal, and isolation-selection grids make each intervention
reviewable.

The independent verifier replays all 30 complete native trajectories, all sampled
scores and removals, each selected source component, native continuation labels,
and every linked isolated-generation state. It recomputes the calibration gate
and paired comparisons without importing the production ecological analyzer.
Read its scope and counts in `data/ecological-v1/integrity.json`. Figure sources,
style hashes, run identifiers, and regeneration commands are indexed under
`eco1-` in `figures/manifest.json`.

The supplementary symmetry audit retains the frozen outcome flags and tests
whether nominal confirmation conditions supply distinct effective challenges.
Read `data/ecological-v1/symmetry-audit.json`: rotated/translated initial and
final grids, all score samples, and actual clearing deltas expose repeated
conditions. An operational criterion pass does not supply independent ecological
confirmation when those challenges are symmetry duplicates.

Calibration tests the recoverability of known-identity cores under standardized
isolation. Shared, oversized, and nonconfirming states remain unresolved and in
the gate denominator. A failed gate still permits the prescribed twenty
structural diagnostics; benefit confirmation and beneficial-heritable yield
remain unknown. The registry is never expanded from observed assay performance.

To reconstruct in a separate checkout, remove only that copy's
`data/ecological-v1/`, then run `python -m scripts.ecological_assay benchmark`
and `python -m scripts.ecological_assay freeze` before the commands above.
The frozen benefit source and atlas/discovery evidence must remain intact.

The completed calibration took 297.5 seconds at 65.9 MiB peak RSS; the twenty
paired conditions took 85.7 seconds at 66.3 MiB peak RSS with one worker. These
are acquisition-process measurements, excluding independent verification,
analysis, and rendering. The calibration passed its declared recovery gate;
read `analysis.md` for the paired result and the mostly zero-impact clearings.

The independent full replay took 306.4 seconds at 62.5 MiB peak RSS, verifying
all 30 native trajectories, 141 isolated generations, and 408 child-selection
states with zero mismatches. This is a separate verification process.

Render export groups sequentially if memory is tight: append `--only calibration`,
`--only benefit`, `--only evidence`, or `--only disturbances` to the ecological
figure command. Successful measured peak export RSS was 202.6 MiB. Allow at least
200 MiB additional available memory and avoid overlapping rendering with Git
packing or other heavy jobs. The 41-page manuscript PDF used 201.3 MiB peak RSS;
its full decoding and sampled results-table/figure pages were inspected. Renderer
image references point to the appended figure pages; Markdown retains live links.

## Nonsymmetric, impact-matched paired assay

[Protocol 009](../protocols/009-impact-matched-paired-assay.md) and
[configuration](../configs/impact-v1.json) were frozen with every starting grid
before acquiring disturbed responses. The exposure-only pilot and rejected
preparation remain in `data/impact-exposure-v1/`; no disturbed continuation was
used to select preparation ages or placements. The treatment constructs three
identical complete components at declared ages and sites, then removes one.
It does not reconstruct a native ecological history.

Read `data/impact-v1/analysis.md` and the exact rational values in `analysis.json`.
Commands use one worker. The default memory guard requires 300 MiB available
before launch; figure rendering below requires 420 MiB and vector manuscript
assembly requires 360 MiB.
The guard terminates a child if available memory drops below 200 MiB. The
`--retry` option waits for headroom and resumes completed cases
without counting them again. Timing and invocation logs are not scientific
replicates. Run heavy verification, rendering, and Git packing sequentially.

```sh
export OPENBLAS_NUM_THREADS=1
python -m scripts.memory_guard --retry --log data/impact-v1/execution.jsonl python -m scripts.impact_assay calibrate
python -m scripts.analyze_impact calibration
python -m scripts.memory_guard --retry --log data/impact-v1/execution.jsonl python -m scripts.impact_assay benefit
python -m scripts.analyze_impact benefit
python -m scripts.impact_contrasts
python -m scripts.memory_guard --retry --log data/impact-v1/execution.jsonl python -m scripts.verify_impact
python -m scripts.memory_guard --retry --reserve 220 --log data/impact-v1/execution.jsonl python -m scripts.figures_impact
python -m scripts.memory_guard --retry --reserve 160 --log data/impact-v1/execution.jsonl python -m scripts.render_manuscript
```

For a full fresh acquisition, use a separate checkout and remove only that
copy's `data/impact-v1`, run `python -m scripts.impact_assay freeze`, compare the
initial/phase/prepared grid hashes with the committed manifest, then execute the
commands above. Exposure-pilot source files remain required. Runners verify
frozen code, rule, protocol, configuration and source hashes. Prepared source
states and isolated search nodes are retained as compact NPZ; normal runs stream
sampled measurements rather than retaining exhaustive frame histories. Only
three pairs retain declared replay frames. The independent verifier reconstructs
all phase preparation, exact clone removal, native sampled worlds, selected
components, and isolated search generations, plus exact paired arithmetic and
complete-state rotation/translation checks. Figure provenance records source
hashes, run IDs and regeneration commands.

The endpoint averages two exact within-condition disturbed/control ratios per
panel. It never substitutes a pooled ratio of totals. Absolute disturbed score
advantage is an additional requirement, not a consequence of relative retention.
Failed calibration or repeated effective challenges leave ecological confirmation
unknown, even when numerical score inequalities pass. All counted populations
remain fixed-registry structural proxies, not total native viable populations.

The independent audit writes small per-world/per-search proof receipts under
`data/impact-v1/integrity-proofs/`. Each records the verifier version, complete
physical evidence inventory and hashes, initial-state hash and verified count
deltas. A resumed audit rehashes every source before reusing its completed proof;
prepared states and exact analyses are rechecked on every invocation. This avoids
restarting all completed physical replays after a memory interruption. To force
an entirely new replay, add `--fresh` to `python -m scripts.verify_impact` (use a
separate checkout to preserve the recorded audit). These receipts are scientific
verification evidence, not simulation frames or independent replications.

Supplementary per-condition contrasts and rejected-preparation proof regenerate
with `python -m scripts.impact_contrasts` and
`python -m scripts.verify_preparation_rejection`. They do not alter frozen
classification; the contrast command also formats analysis.md from unchanged
analysis.json. The latter replays the documented pre-response eligibility scan
and retains both disconnected-cell V03 grids; it never continues a disturbed
state or chooses configurations from response outcomes.
