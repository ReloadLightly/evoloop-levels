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
