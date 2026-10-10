# Ecological-score calibration and paired benefit assay

EXP-ecological-calibration-001 and EXP-benefit-001 extend the completed
EXP-atlas-002. Freeze this protocol, configs/ecological-v1.json, code, source
snapshots, identity registry, and all initial grids before any acquisition.
The ecological schedules and strict comparison criterion were already frozen
in configs/atlas-v2.json before atlas winners were known. This protocol resolves
preparation, registry, intervention order, and score averaging prospectively;
it does not change those schedules or select variants by ecological performance.

## Prepared states and frozen score

Retain both confirmed stable outcomes. RV01 is recovered V01 from the V02/V03
encounter; RV02 is the 14x14 identity absent from the input catalogue, from
V01/V03. Use their existing catalogue representatives (earliest native capture,
then run/root ordering), complete final detached descendant snapshots. Use the
third detached input snapshots V01/V02/V03 from discovery. Do not strip arms or
advance preparation phase. RV01 and V01 share a composite identity but have
different complete snapshots; compare declared states, not words alone.

Rotate each whole snapshot, then center its rotated bounding rectangle in an
empty 192-square torus by floor division. Save all grids and hashes. All five
states are retained; the four unique exact composite identities form one fixed
score registry, deduplicating RV01/V01. Count every recognized closed core whose
composite identity is in that registry, regardless of the starting organism.
Record unregistered valid and unknown-identity cores separately. Do not expand
the registry in response to assay performance. The score concerns known-identity
population and can miss viable unregistered descendants.

At each sample t=0,20,...,1600, advance the original synchronous nine-state CA
to t, remove the declared 24x24 block if t=600 or 1000, then detect. Clear cells
to state zero as an explicitly imposed disturbance, leaving the update law
unchanged. Coordinates are block top-left (row,column); blocks do not wrap.
Save pre/post grids and actual removed cells and detected cores. Retain zero-
impact removals. Arithmetic mean of all 81 equally weighted counts is the
frozen condition score, including zeros and the starting sample.

## Prospective calibration

Use ten new preparation ecologies: all five states crossed with two conditions
(rotation0, block80/80) and (rotation1, block80/112). These are separate from all
four benefit conditions. At t=400,620,1020,1400, classify recognized cores as
scored or unscored using the fixed registry. Select the first and last distinct
lexicographic (row,column,height,width) tuples within each class. If one exists,
select it once; if none exists, record an empty stratum. Selection is made before
inspecting any descendant fate. At most80 scored and80 unscored observations.
Save complete source grids and selected core metadata, including ineligible
components. Earlier and later observations can refer to the same organism or
ecology; they are nested deterministic observations, not independent samples.

Extract only a complete single-core occupied component, retaining arms and
using the existing validated periodic unwrapping. Shared, winding, and oversized
components remain ineligible. Missing and unresolved attempts remain in the
selected-observation denominator. Each eligible snapshot uses the existing
bounded serial-isolation search: first3 detached new-core candidates per
generation, depth6 generation states, maximum24 simulations, horizon1600,
detect10. Scored observations must reach two consecutive transmissions of the
ORIGINAL counted composite identity, allowing transient intermediates. For
unscored observations, any two consecutive stable composite transmissions are
a descriptive recovery endpoint. Neither nonconfirmation nor ineligibility
demonstrates that the native organism was nonviable.

Five baseline controls apply the same search to each verified starting snapshot
and require original-identity recovery. The calibration gate requires all5
baselines, at least90% confirmed original-identity recovery over ALL selected
scored observations, at least80% for EACH starting-state group, and at least1
confirmed recovery in EVERY nonempty state x condition x source-time scored
stratum. A zero pooled denominator fails the gate. Empty strata do not invent
zero-valued organisms; each is explicitly retained. These conservative finite-
panel thresholds are practical validation criteria, not inferential intervals.
Unscored recovery quantifies excluded viable structures but does not change the
known-identity score or its gate.

Each selected native source also has a1600-update continuation, retaining the
remaining absolute interventions at600/1000 and none thereafter. Reuse the same
deterministic trajectory extended to3000 for these overlapping windows. Record
fixed-core loss/recurrence, endpoint identity, and matching words elsewhere.
These are structural observations, not offspring/genetic-parent assignments.
Isolation recovery validates sampled recoverability under an imposed standard
environment; it does not establish reproduction in the original crowded ecology.
Even a passing gate supports a calibrated known-identity structural proxy,
never an exact census of total viable native population.

## Frozen paired assay and confirmation

After calibration, run every development condition for every state, then every
reserved confirmation condition; no winner or condition is removed. Development:
rotation0/block40,40 and rotation1/block128,128. Confirmation: rotation2/block40,128
and rotation3/block128,40. Schedules,192-square extent,1600 horizon and24-square
removals at600/1000 are copied exactly from the pre-atlas benefit definition.
Five states x four conditions gives20 unique simulations; reuse common input
scores across pairs rather than call identical controls independent replicates.
Within each condition, candidate and both originating inputs receive the same
schedule. The two-condition arithmetic mean gives each panel score. Strictly
exceed EACH input in BOTH panels; ties fail. No p-values, pseudo-replicated
confidence intervals, or post-hoc selection of favorable contrasts.
Compare integer sums over the162 samples in each panel, rather than rounded
floating-point means, so an exact tie cannot become an apparent advantage.

If calibration passes, report whether each candidate meets this conditional
benefit criterion. Advantage concerns the calibrated persistence/recolonization
proxy under the specified schedules; report actual disturbance impact, and do
not infer recolonization when a block removes nothing. If calibration fails,
still execute the20 states as structural diagnostics, but block benefit
confirmation and keep beneficial-heritable yield UNKNOWN rather than zero.
Any revised metric or gate requires a separate prospective protocol.

Link assay outcomes to the two originating encounter states conservatively;
parentage is ambiguous. Denominators remain36 main,18 held-out and54 overall
encounter configurations. Eight confirming roots are not eight independent
variants. Preserve all other bounded-search and undetected outcomes as
unresolved; assay failure is conditional, not a proof of general disadvantage.
No advantage in population score alone establishes increased evolvability,
H1/H3, or recursive self-improvement.

## Evidence, verification, and publication

Use one original-dense worker and measure runtime/RSS with200MiB headroom.
Stream core records and counts; retain source, disturbance, terminal, and
isolation-selection grids, not exhaustive histories. Verify every native and
paired trajectory, source selection/extraction, score, schedule, and linked
isolation generation. Independent review checks the gate and paired arithmetic.
Record all hashes and run IDs. Update analyses, Chromatic Fields figures,
manuscript, README, and research state after each scientific batch; publish
verified commits. Preserve earlier frozen files and pending acquisition labels.
