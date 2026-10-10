# Independent Chromatic Fields visual review

Reviewed 2026-10-10. Scope: rendered `world-overview-{dark,light}.png`,
`inheritance-path-{dark,light}.png`, sampled decoded frames of
`world-overview.webp`, figure code, shared style, figure manifest, and raw
exploratory evidence. Atlas matrix, evidence stages, and encounter replays had
not yet been rendered at the time of this initial review. This review does not
certify artifacts generated after it.

## Geometry and traceability

The static panels retain square cells and match the recorded grid geometry;
row increases downward and numerical row/column axes make scale explicit.
Nearest-neighbor rendering preserves sheath, channel spacing, and chirality.
Dark and light exports use the same literal nine-state palette. Their changed
page background does not recolor the simulated states. No lineage overlay is
mistaken for a literal state in these outputs.

The world animation contains 30 frames from the recorded 160-by-160 exploratory
world, sampled at 100-update spacing from t=0 through t=2900. Decoded frames 0,
15, and 29 match the corresponding raw arrays pixel-for-pixel after fourfold
nearest-neighbor expansion; this includes the entire 640-by-640 grid region,
not only organism crops. The 10-cell scale bar is 40 pixels, consistent with
that expansion. The compact animation correctly declares a periodic world;
organisms intersecting world edges are visibly clipped by the displayed domain.

The overview's final displayed frame is t=2900, ten updates before the N01
source recorded at t=2910. Its title is exploratory and does not imply that the
atlas panel or discovery event itself is shown. The manifest associates each
artifact with `EXP-discovery-001` and the regeneration command
`OPENBLAS_NUM_THREADS=1 python -m scripts.figures`. The animation additionally
names its NPZ source. Static artifacts would benefit from equally explicit
source paths, although the generator currently provides the mapping.

## Readability

Ink backgrounds, cyan carriers, cobalt sheaths, generous spacing, and large
panel labels meet the requested direction. The inheritance close-up shows
individual cells clearly. Axes, core dimensions, time labels, and experimental
identifier are legible at the exported size. Both presentation and paper views
are useful; neither introduces invented lineage or quantitative information.

Required small fixes before treating the figures as final:

1. In both light figures, the state-3 legend swatch is exactly the off-white page
   color and disappears. State 8 is also faint. Add a contrasting marker edge to
   all state swatches while keeping their fill colors literal.
2. Include state 0/quiescence in the legend or a concise explicit annotation.
   The ink field is a real CA state, including the gaps inside the channel, not
   merely missing pixels or unmeasured background.
3. The inheritance caption says "times after each separate isolation," whereas
   the first t=2910 uses the exploratory world clock. Say that the source uses
   exploration time and descendant clocks restart at each isolation. The
   descendant event times are first observed at 10-update sampling resolution;
   label that resolution rather than implying exact continuous detection.
4. The animation has time, domain dimensions, and scale but no state legend.
   Provide a compact legend or an explicit accompanying legend link wherever it
   is embedded; an independently downloaded animation should retain enough
   encoding information to interpret its colors.

## Scientific interpretation

The inheritance figure's narrow claim is supported by the evidence: N01's
source has an 11-by-13 operational channel genotype, the stabilized descendant
has a 12-by-12 channel genotype, and their phase-normalized signal words match.
That word differs from the documented S13 source word. The three isolated
reproduction stages recur with the stabilized operational genotype, at first
observed detached times 380, 390, and 390. The spatial crops show the recorded
source/offspring cores rather than synthetic examples.

These images support an exploratory transient-to-stable inheritance path under
the standardized isolation intervention. They do not demonstrate ecological
benefit, H1, H3, independent ancestral histories, or recursive self-improvement.
The title "changed word survives morphological stabilization" is acceptable if
"word" remains explicitly the operational phase-normalized signal word; it must
not be presented as exact preservation of the full organism state. A close-up
of a detached offspring is structural evidence alongside recorded reproduction
assays; it is not a standalone visual proof of ancestry.

## Pending atlas review

Revisit the matrix and evidence stages after the full batch and inheritance
checks finish. Check explicit denominators, unknown/pending benefit, composite
versus signal-word novelty, held-out labels, interaction contrasts, and any
protocol amendments. For replays, verify the saved final-state hash, full-grid
replay versus recorded initial state, fixed crop, non-overlapping inputs,
operational contact definition, ancestry caveats, and visually unobstructed
input/contact/result annotations.

## Completed atlas review

The full atlas outputs were reviewed after acquisition and inheritance checks:
`outcome-matrix-{light,dark}.png`, `evidence-stages-dark.png`, three static
encounter examples across the two themes, and decoded frames from all three
encounter WebPs. Matrix numerators, denominators, proportions, and interaction
contrasts match `data/atlas/analysis.json`. Main candidate proportions are
3/8, 0/8, 1/8, and 1/8; held-out proportions are 0/2, 0/2, 1/2, and 0/2 in
row-major order S13 then N01. Candidate difference-of-differences is +0.375
main and −0.500 held-out. No atlas configuration has confirmed inheritance,
and the figure does not turn candidate novelty into an inherited or beneficial
outcome. The held-out result does not reproduce the main strict rank reversal.
The shared fixed 0-to-1 viridis scale is appropriate, and counts prevent the
small held-out denominators from being hidden by percentages.

The evidence stages correctly use complete near configurations as their unit:
6/40 have candidate novelty, 5/40 have an eligible complete component, and 0/40
have confirmed inheritance. Seven unresolved **run/genotype candidates** are a
different unit from the six novelty-producing runs; the caption preserves that
distinction. The zero confirmed count is observed nonconfirmation under the
bounded search and must not be read as seven completed proofs of nonheritability.
Benefit is unmeasured. An initially rendered hatched bar at height 40 still
carried a quantitative visual suggestion despite its PENDING label; the project
lead is replacing it with a separate nonquantitative status card.

The matrix visibly labels the signal-word audit as added during acquisition and
notes agreement of the frozen composite endpoint here. That prevents the
sensitivity analysis from being presented as wholly preregistered. It also
states finite-panel status, ambiguous ancestry, absence of inferential intervals,
and pending benefit. A concise indication of unresolved inheritance beside the
matrix would further prevent readers from treating confirmed zero as a fully
resolved inheritance rate.

### Independent encounter replay checks

For each selected encounter, the reviewer replayed the complete saved initial
grid with causal labels through all 1600 updates, scanning the operational
contact diagnostic every step. First contacts matched stored results exactly:

| Figure | Run ID | First operational contact |
| --- | --- | ---: |
| encounter-1 | near-main-N01-N01-p0-offset | 1008 |
| encounter-2 | near-heldout-N01-N01-p30-held-parallel | 64 |
| encounter-3 | near-heldout-N01-N01-p30-held-opposed | 910 |

The NumPy contact reference agreed at each contact state. All three final grid
hashes matched their stored results. For all three WebPs, decoded grid pixels
at t=0, 800, and 1600 matched the replay arrays exactly under threefold
nearest-neighbor expansion and the manifest's fixed crop. Thus annotations and
state palette do not distort grid geometry. Full raw grids at the reported
contact times were visually inspected as well. These checks validate a declared
potential-influence/occupied-adjacency diagnostic, not genetic exchange or a
more exact biological contact concept.

Static examples label input slots, operational contact, observed candidate or
horizon, unresolved inheritance, and pending benefit. The second example leaves
visible debris and correctly claims no observed channel novelty rather than
extinction. The third shows many closed structures without upgrading them to
individually established viable organisms. Its outlines remain detector labels,
not lineage or ancestry assignments. The selected examples are post-analysis
illustrations, explicitly recorded as such in the manifest.

### Final rendering issues and fixes

The previously requested state-0 legend, contrasting swatch edges, and animation
state legend are present in this batch. The state-3 swatch is now visible on the
paper background. Two final layout problems were identified:

- Static encounter-2's original arrow tags overlapped its input title and x-axis
  ticks. The lead is moving slot tags inside the axis, keyed to dashed boxes.
- Encounter-2's 88-by-42 crop gave a 264-pixel-wide animation canvas. Its subtitle
  and scale annotation clipped, and its five-column state legend overlapped.
  Canvas width must accommodate labels independently of the threefold grid
  scale; centering the unchanged grid in a wider canvas preserves geometry.

A small arrow or ring identifying the first diagnostic contact location would
help readers locate contact in the crowded larger scenes. This is a readability
improvement rather than a prerequisite for the reported contact checks.

### Final rerender acceptance

The revised outputs were inspected again. Encounter-2 now uses a 640-pixel-wide
canvas with its unchanged 264-by-126 grid centered inside a thin domain border.
Its final-frame contact annotation, subtitle, scale, and all nine state legend
entries are fully visible without overlaps. The static input slot tags sit
inside the axes and no longer cross titles or tick labels. The evidence-stage
benefit card occupies a separate axis-free panel; its "NOT ASSAYED / Yield
unknown" wording and spatial separation make pending status nonquantitative.
The matrix caption now explicitly says that zero confirmations leave seven
run/identity candidates unresolved. These fix the critical identified issues.

After centering, the t=800 grid pixels of all three animations were independently
checked again and remain exact matches to the original-state replay arrays at
threefold scale. Every artifact checksum in the final figure manifest matches
its current file. No critical rendering issue remains in the reviewed outputs;
more precise contact-location marking is a possible later refinement.

### Working PDF inspection

The project lead rasterized the generated manuscript with the available
Ghostscript toolchain and inspected the title, narrative, limitations, next
experiment, and reference pages. A clipped title was corrected by narrower
wrapping; nested BibTeX capitalization braces now retain software reference
titles. The final title and bibliography pages were inspected again after
regeneration. The 16-page PDF is a readable working export with seven appended
recorded-data figures; Markdown and BibTeX remain the authoritative sources.

## Candidate-fate calibration review

Reviewed the completed `EXP-fate-calibration-001` batch on 2026-10-10 against
protocol 004, `scripts/figures_fate.py`, completed analysis and per-case
outcomes, all six dark/light calibration PNG renders, compact saved grids,
and the 64-artifact figure manifest. No scientific code or data was edited.

The calibration matrix accurately distinguishes three observed extraction
states: eligible, fixed target lost, and shared occupied component. Fifteen of
28 candidate delay observations are eligible; ten are lost and three shared.
All 15 eligible candidate observations have zero endpoint confirmation in both
legacy and expanded searches. The eight parent-control delay observations are
eligible and confirmed in both searches. Ineligible observations have a neutral
hatched fill and em dash, so they cannot be read as tested zeroes. The caption
states the different candidate and control endpoints, the seven identities
nested in six originating configurations, and the finite deterministic panel.
The matched searches use identical extracted snapshots; the four delays are
not falsely labeled independent replicates. All text and row boundaries are
legible in both themes.

The native trajectory panels keep original-word structural counts separate
from fixed-target presence. Count ticks are integers. The added per-sample
terracotta ticks ensure that even isolated observed target absences are shown;
the filled strip provides context without silently dropping those samples.
Extraction-delay lines and boundary-flag shading are visibly distinct. The
caption gives the actual boundary-flag denominators, 16/28 candidate and 2/8
control windows, and states that seam-crossing cores may be missed. The source
trajectories merge overlapping deterministic windows rather than counting them
as new replication. Their 0–1840 update extent therefore describes the union of
observation windows, not one common native horizon after every extraction.

The native curves support structural presence and disappearance only. The
explicit ancestry/inheritance caveat is necessary: controls increase their
matching core counts, whereas candidate traces become absent or recur briefly,
without the figure treating either pattern as adaptive benefit or autonomous
confirmed inheritance. H1, H3, and RSI remain unsupported by this calibration.

### Independent C05 recurrence check

The reviewer loaded only the frozen C05 source grid, verified its recorded hash,
and advanced it to a bounded set of times without retaining exhaustive history.
Matching-word detection reproduced these observations:

| Updates since source | Original-word core count | Core location | Fixed source core present |
| ---: | ---: | --- | --- |
| 0 | 1 | (183, 188, 9, 9) | yes |
| 370 | 0 | none | no |
| 380 | 1 | (206, 165, 9, 9) | no |
| 390 | 1 | (206, 165, 9, 9) | no |
| 400 | 0 | none | no |

Raw close-ups at source, 380, and 390 were inspected. The recurrent core is at
a different location and carries the same operational signal word in two
sampled phases. This validates the plotted brief structural recurrence. It
does not establish its parentage or heritability, and the continued absence of
the fixed source core is correctly retained in the terracotta trace.

### Raw comparison and acceptance

The illustrated case is C02-d000, selected after analysis by the declared
maximum expanded search count and lexicographic tie-break. Native panels show
384-by-384 worlds at extraction and 1600 subsequent updates; isolated panels
show 192-by-192 worlds at extraction and the actual first-generation stopping
time, 510 updates. Axes and caption explicitly preserve the differing domains
and clocks rather than implying equal cell scale or horizon. Square pixels,
literal nine-state fills, and separate magenta source-location outline preserve
geometry and distinguish annotation from lineage.

The reviewer checked both displayed final-state hashes against per-case results
and verified that cropping the isolated initial grid recovers the exact complete
component extracted from the native initial grid. Isolation removes surrounding
native structures and translates the component; the image correctly depicts
this declared external intervention. The isolated panel's new cores are not
labeled confirmed novel inheritable descendants merely because they appear.

All current figure-manifest checksums match all 64 artifact files, including
the 18 calibration exports. The new exports include experiment IDs,
regeneration command, data sources, illustrated case, exact panel times, and
selection rule. No critical scientific or layout issue remains in these
renders. For later publication refinement, the light-paper cyan trajectories
could have stronger contrast, and the tiny fixed-source outline in the full
raw-world view could be accompanied by a zoom or callout. Neither changes the
underlying observations or the present conservative interpretation.

### Final calibration publication refinements

The project lead added a darker teal quantitative curve for light paper output
in the shared style configuration, leaving the literal cell-state palette
unchanged. Magenta callouts now locate the fixed target in both native raw
panels. The rerendered curves and raw panels were inspected and all 64 figure
checksums pass. The working PDF's calibration results and limitations pages
were rasterized and inspected with Ghostscript; Markdown tables are aligned
in their monospaced export. These refinements change presentation, not data.

## Fresh atlas and recovered-path acceptance

Reviewed completed `EXP-atlas-002` Midnight Blue exports: outcome matrix,
evidence stages, verified inputs, all three annotated static encounters,
representative decoded frames of all three encounter WebPs, and the recovered
inheritance paths. The current shared style intentionally uses canonical dark
exports; the fixed literal nine-state palette remains unchanged. Quantitative
blue scales, annotation roles, and solid/dashed input-placement outlines are
separate from literal cell-state encodings.

Matrix and stage counts match completed analysis: 14/36 main and 4/18 held-out
near configurations have native candidate words; 2/36 main and 0/18 held-out
have confirmed isolated inheritance. Each main pair cell retains four declared
configurations, each held-out cell two. The colorbar has clear separation from
axes and text. The independent benefit status card is visibly unquantified and
says NOT ASSAYED, rather than depicting missing benefit as a measured zero.
The caption preserves unsearched candidate fates as unresolved and limits the
result to serial isolation and finite-panel pair-level novelty.

All three static encounter panels now share a focused crop over their annotated
states. Inputs, first operational contact, first observed candidate, and later
state remain visible at readable cell scale. The animation crop covers the union
of all recorded replay frames, so this static focus does not omit later cells
from the animations. Candidate core outlines, placement outlines, and literal
state pixels remain distinct. Experimental IDs, periodic domain labels,
10-update candidate sampling, ancestry caveats, axes, titles, and nine-state
legends are readable without clipping.

The reviewer independently reconstructed every retained raw replay frame from
its full original initial grid: 43, 43, and 44 frames, respectively. All 130
cropped frame arrays match exactly, and all three complete final-state hashes
match stored outcomes. Representative initial, middle, and final decoded WebP
frames match those NPZ arrays pixel-for-pixel at the declared one pixel per
cell. WebP frame counts match `display_times`; reduced display cadence is
explicit metadata, while the finer retained raw evidence remains available.
The animations' centered domain border, labels, scale, and legend remain clear;
the static panels supply enlarged cell-level detail.

Recovered paths select one actual root per stable composite identity, sorted by
identity and then earliest native capture/run/genotype/source file. All eight
source/selected-child component hashes match their manifest paths and saved
arrays. RV01 starts at native t=460, changes its word after isolation, and
recovers known panel V01 through 12×13 → 12×12 → 12×12 → 12×12, with detached
observations +400, +390, +390. RV02 starts at native t=1110, retains its word
through 13×15 → 14×14 → 14×14 → 14×14, with +440, +440, +440. Its final identity
is labeled "absent from input catalogue," avoiding a claim of global novelty.
Complete saved components retain their arms; a common padded canvas gives every
panel the same cell scale and component-relative coordinates. The caption
separates native and restarted isolation clocks and explicitly limits the
images to assay-derived paths with ambiguous native ancestry and no benefit
claim. Both final rows and footer are readable.

The initial verified-input render overlapped provenance and x-axis labels. Its
selective rerender moves provenance below the labels and uses integer ticks;
that issue is resolved. The final recovered-path wording was also rerendered
and inspected. All 66 current figure-manifest artifact checksums match their
files after those changes. No critical scientific or rendering issue remains
in the reviewed fresh-atlas outputs.

The final 31-page working PDF passes Ghostscript decoding. Rendered checks of
the opening page, fresh-results page, outcome matrix, and inheritance-path page
show readable text and figures. The renderer keeps short results tables intact
with their headers; the calibration and fresh-atlas tables fit the page width.

## Ecological calibration and frozen proxy criterion

Reviewed all six `eco1-` static PNG exports and representative decoded frames
of all three WebPs for `EXP-ecological-calibration-001` and `EXP-benefit-001`.
The 21 new exports preserve the earlier 66 manifest entries. SVG/PDF/PNG use
canonical Midnight Blue, the shared quantitative scale, and the fixed literal
nine-state palette. Wrapped gate-card and evidence-category labels resolve
the initially crowded text; score annotations now separate prominent means
from smaller occupied-cell removal counts. Final titles, axes, colorbars,
footers, legends, and status cards are readable without clipping or overlap.

Calibration plots match all 68 selected scored observations, including the five
unresolved recoveries: 68/68 extractable, 63/68 original-identity recoveries,
and 5/5 baseline recoveries. State-specific fractions and all 40 scored strata
retain their declared denominators. Thresholds are shown explicitly: 90%
overall, 80% per prepared state, all five baselines, and at least one recovery
per nonempty scored stratum. The legend and captions distinguish extraction
eligibility from bounded serial-isolation recovery and native viability.
Empty strata have an explicit missing/empty encoding in the script; none occurred
in this completed batch. No confidence intervals suggest independent sampled
populations.

The 5×4 score matrix and paired margins agree with completed analysis. RV01
exceeds V02 and V03 by 0.210 and 0.259 registered cores in each pooled panel;
RV02 falls below V01 and V03 by 0.426 and 0.185. These are means of fixed-
registry recognized closed-core counts, not a total viable-population census.
V01 and RV01 share one identity while retaining distinct prepared snapshots.
All 20 score cells display actual removals at t=600 and 1000. Across 40 clearings,
36 remove zero occupied cells; four remove 18 cells, and zero immediately change
registered core counts. The plots explicitly reject a disturbance-resilience
interpretation.

The independently recorded symmetry audit is included among hashed sources.
Development and nominal confirmation means are identical because the complete
states and effective interventions repeat under rotational symmetry (with
centering translations where needed). Cards therefore say FROZEN CRITERION MET,
not independently confirmed benefit. Independent exposure confirmation remains
unresolved. The current evidence figure shares one 54-encounter denominator:
18 candidate-producing encounters, two confirmed isolated inheritance
encounters, one inherited identity absent from the input catalogue, and one
meeting the frozen calibrated-proxy criterion. It separates these last two
endpoints: RV01 recovers known V01 and meets the frozen criterion; RV02 is absent
from the input catalogue and does not meet it. The 16 other candidate encounters
remain visibly unresolved, rather than appearing as confirmed failures in a
funnel. Earlier atlas figures record the earlier benefit-pending checkpoint.
H1/H3 and RSI remain untested or unestablished.

The full-domain disturbance figure uses the prospectively declared development-0
V01/RV01/RV02 cases. All six depicted clearings remove zero occupied cells; this
fact is explicit in its caption and each row's annotation. Before and after
have the same update time, separated only by the imposed clearing. The dashed
24×24 block is an intervention overlay, distinct from literal cells and any
lineage encoding. World extents are 192×192 with row/column cell coordinates.
All 75 displayed WebP frames (25 per case) match their raw NPZ frames or declared
pre-clear snapshots pixel-for-pixel at exactly two nearest-neighbor pixels per
cell. Before/after ordering and duplicate clock times match manifest stages.
The animations retain full worlds, labeled update times, periodic geometry,
10-cell scales, state legends, and zero-impact annotations.

All 87 artifact checksums and every declared figure source checksum match.
Sources include final calibration/benefit analysis, the frozen manifest, all
20 result files for disturbance summaries, actual disturbance/replay arrays,
input catalogue evidence, and the symmetry audit as appropriate. Every new
artifact records experiment IDs and `python -m scripts.figures_ecological`
regeneration instructions. Normal evidence remains compact sampled grids.

Sequential rendering used one process per group, approximately 35 seconds in
total, with maximum observed RSS 202.6 MiB and minimum sampled available memory
300.6 MiB on the successful batch. An earlier guard stopped an evidence attempt
when concurrent repository packing reduced available memory to 184.9 MiB;
that aborted attempt changed no scientific data and was superseded by complete
exports after packing ended. No critical scientific or presentation issue
remains in the reviewed final ecological exports. The independent-challenge
limitation is a finding, not a rendering defect.

## Impact-matched paired population assay

Reviewed the six static `impact1-` Midnight Blue figure groups and decoded
initial, middle, and final frames from all three paired WebPs for
`EXP-impact-calibration-001` and `EXP-impact-paired-001`. Final exports comprise
six SVG/PDF/PNG groups and three animations. The figure manifest now has 108
entries; the earlier 87 entries retain their metadata exactly. Titles, cell
axes, update/age labels, legends, quantitative scales, annotations, and
footers are legible. Initial calibration/score colorbar labels overlapped
footers; the final selective rerenders resolve this. Raw removal outlines now
appear only in pre-removal panels, so a ghost outline cannot resemble a
surviving organism after clearing.

Exposure evidence matches all 30 frozen preparations: each constructed colony
has three copies of one complete component; removal leaves two registered
cores and removes exactly one third of occupied cells, including arms. Absolute
removed-cell counts are shown for every condition/state. The other two complete
components remain unchanged. All 20 within-state development/confirmation
comparisons are nonequivalent in both full control and disturbed states under
the declared rotations/translations; zero cross-state aliases are recorded.
The captions distinguish matching structural impact from matching future
reproductive value. Age labels are elapsed updates since the detached
representative, not homologous reproductive phases; constructed microcolonies
are not native population histories.

The calibration matrix retains all 80 selected scored observations: 80/80
extractable, 77/80 original identities recovered, and 30/30 phase controls
recovered. The three remaining selected fates are unresolved under bounded
searches, not proved nonviable. All state groups and nonempty strata pass the
frozen thresholds shown on the card. There are zero unscored selections, so
coverage of viable unregistered identities remains untested. The caption
separates isolation recovery from certified native viability and identifies
nested deterministic observations rather than independent populations.

The score matrices show all 20 disturbed/control comparisons using 81 equally
weighted observations each. Per-condition D/U ratios display exact reduced
fractions; all control sums are positive here. Missing ratios have an explicit
undefined encoding in the renderer. Absolute disturbed means and both integer
score sums remain visible beside ratios. The contrast plot shows PANEL
comparisons: an arithmetic mean of two exact per-condition ratios, not a ratio
of pooled totals. Absolute panel means use 162 samples. Both recovered states
fail the strict relative and absolute criteria against both inputs across both
panels; neither meets the joint calibrated population criterion. This is
conditional on this assay and does not convert the other 16 unresolved
candidate-producing encounters into confirmed failures. The earlier frozen
proxy result remains a separate checkpoint.

RV01's relative comparison with V02 changes sign between development
configurations, visible in the per-condition matrix. Age and geometry change
together, so the figures do not identify which causes that sensitivity. A full
age-by-geometry cross is needed for that separation. The result concerns
conditional fixed-registry structural population performance, not evolvability,
H1/H3, or recursive self-improvement. V01/RV01 share an operational identity
while retaining different representative complete states; no figure assigns
native genetic parentage.

The trajectory overview plots all 40 completed continuations on common integer
count scales: D solid, U dashed, sampled every 20 updates. Step segments position
sampled observations without claiming exact event times. These are faithful CA
continuations after external preparation/removal, with no later interventions.
The raw figure uses only the three configuration-declared cases, preserving
full 192-square periodic geometry, exact pre-state masks, disturbed t=0, and
both recorded endpoints. The paired animations use 21 retained times each,
0 through 1600 every 80 updates, and no cell overlays. All 126 displayed world
rectangles (three animations × 21 times × D/U) match raw uint8 NPZ arrays
pixel-for-pixel under the fixed literal palette and exact two-pixel nearest
scaling. Times, source rectangles, legends, and scales agree with manifest
metadata. No cases were selected by future performance.

All 108 final artifact checksums and declared source checksums pass; every new
artifact includes the frozen configuration/protocol/manifest and independent
integrity evidence. All six SVG documents parse, and all six figure PDFs pass
Ghostscript decoding. Detailed frame proof, source validation, rendering
metrics, and guard outcomes are in `docs/impact_figure_validation.json`.
Commands are recorded per artifact and use `python -m scripts.figures_impact`;
`--only` groups and individual `--only animations --case N` allow bounded
single-process reproduction.

Initial active rendering took 64.33 seconds across nine serial processes, with
maximum measured RSS 186.95 MiB. The final three refinements took 24.06 active
seconds. Host memory fluctuations caused 31 denied launches and one calibration
attempt stopped at the first sampled headroom below 200 MiB (171.84 MiB).
An idle reserve-change interruption raced a completed calibration and caused
one redundant retry; its interrupted SVG/PDF writes were superseded by a full
successful rerender. Failed/denied attempts remain in the execution log. Final
successful jobs retained at least 214.21 MiB sampled available memory. All
render queues are closed; frozen physics and scientific data were unchanged.
No critical scientific or presentation issue remains in the final exports.


## Matched-depletion working PDF — final root review

The updated 51-page PDF passes full Ghostscript decoding with PDFSTOPONERROR.
Rendered page 15 retains the five-state results table with its header, calibrated
recovery counts, negative joint criterion, and qualifications. Pages 48 and 51
retain the exact ratio/integer-score annotations, elapsed ages, paired worlds,
raw removal geometry, and literal state legend without clipping or label overlap.
The six new standalone PNG layouts were also inspected by root.

The renderer now appends the verified vector figure PDFs at native page sizes,
using the existing Ghostscript toolchain. This avoids accumulating raster figures
and preserves sharp geometry and labels. Successful assembly takes 17.05 seconds;
Python and Ghostscript each record a 79.5 MiB per-process peak, with minimum
monitored available memory 266.82 MiB. These peaks are separate measurements,
not a simultaneous process-total estimate. Output replacement is atomic on the
repository filesystem; the first cross-filesystem move was corrected before
publication. Earlier waiting-session exits and failed/denied invocations remain
in execution.jsonl. Source and PDF hashes, inspected pages, regeneration command,
and measurements are recorded in docs/impact_manuscript_validation.json.
