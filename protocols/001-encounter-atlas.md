# Frozen first encounter atlas — EXP-atlas-001

Freeze date: 2026-10-10, before the main simulations. Configuration:
configs/atlas-v1.json. Freeze commands generate a SHA-256 manifest and complete
starting grids. Those grids, rather than prose coordinates, define every run.
Exploration EXP-discovery-001 and all measurement development are separate.
This is the first small prospective atlas; not a preregistered population-level test.

## Organisms and states

S13 is the pinned documented species13 seed, including its arm. N01 is the first
novel naturally generated genotype passing the declared complete-component
isolation inheritance search in the 160×160 exploratory torus. When a transient
source produces a stable descendant, the input panel uses that descendant,
not a manufactured genome. Record source time, source core, snapshot and tests.
Stop discovery after two verified genotypes; use no unpublished author seeds.

Each organism's phase state is constructed by advancing its complete snapshot
alone in a 192×192 empty periodic grid by 0, 30, or 60 updates, retaining the
entire occupied configuration cropped to its bounding rectangle. Each phase
must contain exactly one detected core, with unchanged operational genotype,
and avoid the boundary. Phase offsets are elapsed updates relative to each
snapshot; they are not asserted to be homologous biological phases.

For every ordered focal×partner pair, the focal faces the seed's original
orientation; the partner rotates by a specified multiple of 90 degrees.
In the near grid (384×384), focal top-left is (192,144); partner top-left is
(192+dy, 144+focal_width+gap). Bounding rectangles are disjoint. Main: four
geometries × phases 0/60 = eight configurations per pair (32 total). Held-out:
two new geometries × phase 30 = two per pair (8 total). Both components use
the listed phase. Ordered labels do not imply assigned genetic parentage.

Matched separated controls retain organisms, phases, relative row offsets,
and orientations, but use a 640×640 torus with focal at (320,140) and partner
at (320+dy,460), producing 40 controls. Actual absence of contact must be checked
throughout the window, not assumed. Alone controls cover each panel organism
at each used phase and orientation (24 configurations). These are explicit
separation/solo interventions; grid extent differs in the far treatment.

## Dynamics and contact

Original nine-state evoloop rules, synchronous CTRBL, periodic boundary; no
mutation injection. Observe 1,600 completed updates. Occupied input cells
receive provenance masks 1/2; every newly occupied cell inherits the bitwise
union of occupied contributors in its local neighborhood. This overapproximates
physical causal contribution and is not a genetic pedigree. Contact is the
first update with occupied exclusive-provenance adjacency (von Neumann) or
occupied provenance mixing. Test at every update and record exact grid time.
It is an operational contact diagnostic, not proof of a mutational mechanism.

Sample closed-core structures every ten updates, including transients. An
enclosed rectangular zero core with an intact 2/3 inner sheath is a structural
candidate. The operational genotype retains the complete clockwise signal-ring
word (states 0/1/4/7), circularly phase-normalized without reflection, with
rotation-normalized core dimensions. Retain carriers because spacing matters.
It differs from the published counterclockwise birth-anchored species ID.
Contaminated channels have unknown genotype. Structure detection alone is not
viability. Novelty means different from BOTH panel input genotypes in that run.

Record closure-first-observed times as interval-censored within ten updates;
do not call them exact births. Track cores by fixed spatial coordinates;
death/loss is disappearance of that recognized core, not necessarily cell death.
Record input-core structural survival, newly appearing cores (reproduction
proxy), genotype candidates, unknown genotype, boundary-touch flags, final
grid, metrics, and initial/final hashes. Boundary/spatial segmentation failures
are limitations; never interpret an absent detected core alone as extinction.

## Isolation inheritance

For novel genotypes, retain the earliest two distinct extractable component
snapshots per run/genotype. Extraction is an explicitly imposed isolation
intervention: preserve all occupied cells in the component, including arms,
remove other components, center it on an empty 192×192 torus. Reject components
touching an edge, containing multiple recognized cores, or exceeding the size
budget. Shared or ineligible components remain unresolved. Preserve source
grid, original core, extraction box, and full snapshot. The two-attempt cap is
fixed and may miss later successful phases or siblings.

Advance 1,600 updates per generation; seek the first newly positioned core
whose component detaches and has a valid genotype. Permit genotype changes
between source and first isolated descendant. Then isolate that complete
descendant and require reproduction of its genotype. If the first descendant
differs from source, require a further isolated generation of the stable
genotype (two stable transmissions). Record both closure and detachment times.
Stable genotypes produced only after isolation are labeled assay-derived.
Recheck novelty against both encounter inputs. A path failing to reproduce
within the horizon is unresolved; an empty isolation grid is assay extinction,
not proof that the original ecological structure was nonviable.

Counts distinguish candidate signal novelty, detached assay eligibility,
confirmed isolation inheritance, and confirmed ecological benefit. Keep all
40 near encounters, including lethal/nonproductive encounters, in denominators.
Report per-run any-candidate and any-confirmed-novel-stable-path indicators,
unique genotypes and all unresolved/ambiguous cases. All postcontact novel paths
have conservative parent set {focal,partner}; do not assign focal-specific yield.
Precontact paths retain single-input provenance if supported, but report both.

## Prospective benefit assay

The JSON freezes a paired disturbance assay before winners are selected:
192×192 torus, 1,600 updates, removal of a 24×24 cell block at t=600/1000.
The block coordinates and rotations are split into two development and two
independent confirmation conditions. This intervention is external and labeled.
The metric is mean intact-core population of independently isolation-confirmed
genotypes, sampled every 20 updates including t=0/1600. It captures persistence
and recolonization occupancy, not adaptive capacity by itself. Candidate and
BOTH inputs use the same condition schedule. Candidate advantage must exceed
both input means in both panels. No search across schedules is permitted.

Individual viability calibration is required before calling the structural
population proxy confirmed benefit. If this calibration or assays remain
unfinished, record pending benefit and conditional beneficial-heritable yield
as unknown, not zero. Publish completed encounters and inheritance evidence.

## Analysis and claims

Compute focal-by-partner rates, denominators, and the frozen 2×2 difference of
differences for main and held-out geometry/phase panels separately. Examine
partner-dependent focal rankings. A partner main effect alone is insufficient.
Because ancestry is unresolved, interactions are of pair-configuration outcomes,
not estimates of individual mutational capacity. Reciprocal labels can represent
related physical encounters; never treat them as independent evolutionary histories.
These are census summaries of a finite deterministic panel: no binomial CIs,
bootstrap over repeated states, p-values, or claims of independent histories.
Panel organisms are one seed and one selected descendant from one exploratory
history; organism generalization, H1, H3, beneficial evolvability, and RSI remain
unestablished. Hold-out geometry tests only geometric/phase transfer here.
