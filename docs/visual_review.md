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
