# Where Does Evolvability Reside? Organisms, Encounters, and Ecological History in Self-Reproducing Cellular Automata

**Working manuscript — first scientific checkpoint, 10 October 2026.**
Target venues: ALIFE 2027 or GECCO 2027. This document reports a small prospective
deterministic encounter atlas, not a completed test of all three hypotheses.
Author list and affiliations remain to be supplied by the project owner.

## Abstract

Evolvability concerns the capacity to generate useful heritable variation.
In spatial artificial life, that capacity can depend on an organism's inherited
state, the organisms it encounters, and ecological histories that change both.
We frame these as compatible causal contributions and implement a reproducible
encounter intervention in the original nine-state evoloop cellular automaton.
An exhaustive comparison of all 59,049 local neighborhoods establishes agreement
with two reference routes. A documented seed reproduces, and deterministic
replay and checkpoint/resume agree. Natural exploratory variation supplies a
second verified input organism through a transient-to-stable inheritance path.
We prospectively freeze 32 main crossed encounters, eight held-out encounters,
40 separated controls, and 24 alone controls, with complete starting grids and
conservative pair-level ancestry. Results of the atlas and isolation checks
will populate the Results section only after completion. A paired ecological
benefit assay is frozen but remains pending viability calibration. The
organism-transfer and ecological-history hypotheses remain untested.

## 1. Introduction

Self-reproducing cellular automata make evolutionary events inspectable at the
level of individual cells. Rules can remain fixed while interacting structures
produce inherited changes. Sayama's evoloop demonstrates this possibility in a
deterministic, synchronous, nine-state lattice: reproductive arms interact,
offspring differ, and competition for space changes population composition
[@sayama1999evoloop]. The relevant evolutionary unit is nevertheless not
obvious. A circulating signal sequence controls a loop's construction behavior,
but the sequence it passes to a descendant can depend on structures encountered
during reproduction.

Our question is where the capacity for further adaptive change resides.
Three compatible hypotheses organize the problem. H1 concerns transferable
organism properties: organisms sampled from evolved populations should retain
higher beneficial-heritable-variant yield than matched ancestors under the same
held-out partners, geometries, and phases. H2 concerns encounters: crossing
focal and partner identities should reveal organism-by-partner interactions,
possibly including partner-dependent rankings. H3 concerns ecological history:
history can change inherited organisms and the distribution of encounters they
subsequently experience. The hypotheses need not compete for an exclusive
explanation; an organism can carry a variation bias that is expressed differently
against different partners, with both shaped by its prior ecology.

History is upstream of the present state. Under deterministic CA dynamics,
identical complete starting states and intervention schedules imply identical
futures. A history transplant can identify paths mediated by organism state or
encounter distribution; it cannot establish an additional historical force after
holding the entire state fixed. This constraint is useful because it specifies
which comparisons can distinguish levels of causation.

The project has a limited potential connection to recursive self-improvement:
an evolving system might acquire greater capacity to generate further adaptive
change. Neither ordinary adaptation nor greater population size demonstrates
that claim. We first measure the production and inheritance of variation under
a declared encounter panel. Ecological benefit requires a separate comparison;
increased evolvability would then require a comparison of such beneficial
variation yields between transferred organism states or histories.

This checkpoint therefore targets the smallest reliable intervention addressing
H2. It establishes verified dynamics, freezes a small crossed atlas, and follows
candidate novelty through explicit isolation assays. It retains lethal and
nonproductive encounters and marks unresolved cases. It does not infer
organism-level mutation rates from ambiguous pedigrees, or generalize from one
selected descendant to independently evolved populations.

## 2. Related work and contribution

The original evoloop study introduces structural dissolution, interaction-
mediated genotype change, and spatial selection within a deterministic rule
system [@sayama1999evoloop]. Its configurations include arm takeover, smaller
descendants, and transient or rectangular structures. The recent review situates
these models among self-reproducing CA and distinguishes reproduction supporting
inherited variation from exact replication [@sayama2025review;
@sayama2024reviewpreprint]. Our study uses the original synchronous rules; it
does not combine self-protecting, asynchronous, pathogen, or sexually reproducing
variants with that baseline.

Subsequent work established a much richer genotype space than size alone
captures. Salzberg and Sayama report genotype-dependent colony morphology,
mutation bias, persistence, and population density, including a round-robin
competition among all 15 size-4 genotypes [@salzberg2004complex]. They also
describe inherited mutational biases. Thus neither crossed competitors nor
inheritance of a variation bias is by itself our proposed novelty. Their
population competition endpoint addresses which types persist; our immediate
endpoint is whether specified encounters produce new genotypes that reproduce
after separation from the encounter.

Salzberg, Antony, and Sayama analyze genealogy, biased accessibility of larger
species, pathogens, and periodic localized or distributed block removal
[@salzberg2004hostile]. Their treatment of transient species is particularly
important: structures that do not directly reproduce their own genotype may
produce stable descendants. Discarding them at first observation would exclude
an established route to inherited variation. The present isolation search
therefore allows a candidate to produce a different stable descendant before
checking repeated transmission. Ecological disturbance and limited complexity
growth are prior results, not outcomes to be rediscovered here under a new name.

The intended addition is a controlled, prospectively specified comparison of
variation-generating outcomes: candidate production, isolated inheritance,
and ultimately paired ecological advantage over both encounter inputs. Exact
starting states, negative encounters, horizon censoring, and ambiguous ancestry
make the denominator reviewable. Held-out configurations test whether an
interaction contrast transfers across geometry and phase, while future organism
and encounter-distribution transplants address its causal location. At this
checkpoint, novelty is an intervention-and-measurement comparison rather than
a claim of a new physical mechanism.

## 3. Methods

### 3.1 Rule system, reference agreement, and licensing

Each cell has one of nine states. The local neighborhood is ordered center,
top, right, bottom, left (CTRBL); updates are synchronous and boundaries are
periodic. Explicit rules are completed under rotations of the four neighbors,
then dissolution and undefined-neighborhood defaults supply a full lookup table.
We select the original evoloop transition system implemented by CellPyLib at
commit `743e936d48f8520f6f4ac652570ac7bb46414189` [@antunesCellPyLib].
The expanded uint8 lookup-table SHA-256 is
`9d0652aaceb55dd3c7ff9814b45ae56c7782c8a20cab0fc88e11fc6d1cae37f3`.

An independent expansion of the author's EvoLoopS 1.0 rule file agrees on all
59,049 neighborhoods. The documented CellPyLib species13 seed matches the
author's `13.img`; it differs from the author's default `13-2.img` seed. Seed
variants do not imply different transition rules. We do not claim to reproduce
the original default evolutionary demonstration. The reference modules are
redistributed under Apache License 2.0 with their license and attribution;
the author software, seed catalogue, artwork, and PDFs are not redistributed.
Source hashes, publication-year caveats, and reuse decisions appear in
`docs/source_review.md` [@cellpylibEvoloopDocumentation; @sayamaEvoLoopS].

### 3.2 Engine and focused verification

A headless C kernel accessed from Python uses compact uint8 arrays and a
59,049-entry lookup table. Two arrays implement synchronous updates. No mutation
injection occurs in the atlas. A separate occupied-cell provenance layer records
potential input contribution without modifying the CA state. Complete initial
grids, rule/configuration hashes, event times, snapshots, and final hashes are
saved. Normal runs stream structural metrics and retain selective candidate
evidence rather than exhaustive frame histories.

Verification exhaustively compares local transitions with the callable reference,
checks a random periodic grid against a cellwise oracle, observes documented
seed reproduction, and compares exact deterministic replay and checkpoint/resume.
Rotation tests cover square and naturally generated rectangular genotypes.
Measurement development found that body-only crops can destroy active arms;
we rejected that extraction method before freezing the main atlas. The final
assay preserves complete detached components. The runtime benchmark and peak
resident memory are recorded in `data/verification.json`; one worker is used
because available system memory, rather than CPU count, limits concurrency.

### 3.3 Exploratory panel and prospective encounter configurations

The panel has two organisms: S13, the documented seed, and N01, the first new
stable genotype confirmed in a 160×160 exploratory torus (EXP-discovery-001).
Exploration starts with one S13 seed at (65,45), samples every ten updates,
and stops after two verified genotypes. Up to four naturally observed detached
phases per candidate are available for discovery testing. N01 is obtained through
a transient-to-stable path; the catalogue stores its confirmed descendant state.
This is one selected exploratory history, not independent evolutionary replication.

Protocol 001 and `configs/atlas-v1.json` are frozen before the main batch.
Each input snapshot is advanced alone by 0, 30, or 60 updates, retaining its
entire occupied configuration. The resulting phase states must each contain one
recognized core with unchanged genotype and no boundary contact. The offsets
are elapsed updates relative to different snapshot origins, not homologous
reproduction phases. Complete grids make this distinction reproducible.

All four ordered pairs are crossed against four main relative geometries at
phases 0 and 60 (eight states per pair), and two held-out geometries at phase 30
(two per pair). The main torus is 384×384. Rotations are exact multiples of
90 degrees, bounding rectangles do not overlap, and the protocol records
coordinates. Forty matched separated controls retain identities, phases,
orientations, and row offsets in a 640×640 torus with horizontal displacement
320 cells. Their lack of contact is verified throughout the window. Twenty-four
alone controls cover each organism, phase, and orientation. Every state is
observed for 1,600 completed updates.

### 3.4 Contact, structures, genotypes, and ancestry

Input occupied cells receive provenance masks 1 and 2. A newly occupied cell
inherits the union of occupied contributors in its CTRBL neighborhood. This is
a causal overapproximation, not a genetic pedigree. Operational contact is the
first update with occupied exclusive-provenance von Neumann adjacency or mixed
occupied provenance. Contact is checked every update and records grid time.
It does not by itself prove a mutational mechanism.

The detector samples enclosed rectangular zero cores with intact inner sheaths
in states 2/3 every ten updates. This is a structural observation, not a viability
claim. For channels containing only 0/1/4/7, the operational genotype is the
clockwise signal-ring word, including carrier spacing, normalized by cyclic
shift without reflection and paired with sorted core dimensions. It preserves
chirality and distinguishes gene spacing. It is not the published counterclockwise,
birth-anchored species identifier [@salzberg2004hostile]. Contaminated channels
have unknown genotype.

Structures are tracked by core coordinates. First appearance and loss times are
sampled proxies, interval-censored within ten updates. Input-core persistence
is reported as structural survival; it does not establish continued viability
or lineage survival. Boundary touch is flagged because the rectangular detector
does not join structures crossing the torus seam. Nonrectangular and inseparable
structures remain possible sources of missed candidates.

Novelty requires a genotype different from both encounter inputs. Snapshots retain
the source grid, extraction box, and provenance. After contact, genetic parentage
is conservatively ambiguous, so the primary unit is pair-level novelty. A changed
structure, a changed signal genotype, a detached organism, a heritable variant,
and a beneficial variant are separate outcomes.

A reporting audit added during acquisition, before inheritance analysis,
clarifies that the code field `genotype` is a composite signal-word/core-shape
identity. The frozen primary endpoint retains this definition and is reported
as **composite organism-identity novelty**. A separately labeled sensitivity
endpoint requires the channel word alone to differ from both inputs. Shape-only
differences are morphological candidates, not genetic changes. No raw outcomes
or search budgets change; protocol 002 records the timing and reason for this
audit. The signal-word result must not be described as prospectively frozen.

### 3.5 Isolation and transient-to-stable inheritance

Isolation is an explicitly imposed intervention. We extract the full occupied
connected component, including arms, only when it contains exactly one recognized
core and avoids the grid edge. We remove other components and center the snapshot
in an empty 192×192 torus. Oversized, shared, or boundary-spanning components are
ineligible. The earliest two distinct eligible phases per run/genotype constitute
the frozen search budget; later phases and siblings may be missed.

Each isolation generation runs for up to 1,600 updates. We seek the first
newly positioned closed core with a valid genotype and a complete detached
component. The first descendant may differ from the encounter candidate. It
is then isolated and must reproduce its own genotype. If the initial candidate
was transient, a further generation must transmit the stable genotype, providing
two stable transmissions. Closure-first-observed and detachment-first-observed
times are separate. Stable genotypes arising only after isolation are explicitly
assay-derived, and novelty is checked again against both encounter inputs.

A path that fails to reproduce by the horizon is unresolved. An empty isolation
grid is assay extinction, not proof of ecological nonviability of the original
structure. The first-descendant search is conservative: later offspring might
reproduce successfully. Stable isolated inheritance establishes a reproducible
transmission path through the stated intervention, not ecological independence
of every structure with the same observed genotype.

### 3.6 Benefit assay and finite-panel analysis

Before selecting any atlas winner, we freeze a paired disturbance assay in
192×192 tori over 1,600 updates. At updates 600 and 1,000, a specified 24×24
block is removed; this is an external ecological intervention. The metric is
mean intact-core population of isolation-confirmed genotypes, sampled every
20 updates. Two development and two independent confirmation schedules specify
block positions and initial orientations. A candidate must exceed both input
means in both panels. The measure targets persistence and recolonization
occupancy, not evolvability by itself. Because recognized cores can include doomed
individuals, viability calibration is required before confirmed-benefit claims.
Benefit remains pending if those assays or calibration are unfinished.

The primary completed endpoint is any confirmed novel stable inheritance path
per near configuration, with all 32 main and eight held-out states in the
denominator. Candidate-only and unresolved outcomes remain explicit. A 2×2
focal-by-partner rate matrix and difference of differences summarize interaction:
`(S13,S13 − N01,S13) − (S13,N01 − N01,N01)`. Main and held-out panels are
analyzed separately, along with signs of the partner-specific focal contrasts.
These are pair-configuration interactions under ambiguous ancestry, not
identified focal mutation capacities. A partner main effect is insufficient
for H2.

Distinct complete deterministic configurations are finite-panel census units.
Repeated states are reproducibility checks. We report no binomial confidence
intervals, p-values, or resampling of repeated deterministic trajectories.
Held-out geometries test configuration transfer, not transfer across independent
organisms or ecological histories. Conditional beneficial-heritable yield is
unknown until benefit confirmation is completed; it must not be plotted as zero.

## 4. Results

### 4.1 Verified foundations and exploratory inheritance

All 59,049 local transitions agree with the selected callable reference and the
independent author-rule expansion. The seed agrees byte for byte with the
documented author seed, reproduces into multiple closed cores, and passes exact
replay and resume checks. The exploratory candidate observed at update 2,910
has an 11×13 inner core and a changed signal word. In complete-component
isolation it produces a stable 12×12-core descendant; two subsequent isolated
generations reproduce that stable genotype. Detachment is first observed at
380, 390, and 390 updates in the three assays, sampled every ten updates.
N01 denotes the stable descendant, not the transient source configuration.
The transient and stable structures share the changed signal word: their
11×13-to-12×12 difference is morphological stabilization, while their shared
signal word differs from S13's. This separates phenotype change from signal
genotype change in the exploratory path.

### 4.2 Encounter atlas

Main atlas simulations and their inheritance checks have not yet completed in
this draft. No outcome rates, interaction findings, benefit results, or H2
support are asserted here. This paragraph will be replaced from completed
machine-readable results.

## 5. Limitations and alternative explanations

The panel contains one documented organism and one selected descendant from
one exploratory history. Selection for isolation eligibility can favor certain
structures or phases; genotype is less than the complete transferred organism
state. Phase, arm state, phenotype, and genotype effects are entangled in this
first atlas. A measured pair interaction need not be a gene-sequence interaction.
The operational genotype may miss junction-state distinctions or identify
states with different future behavior as the same circulating signal word.

Contact provenance overapproximates causality. Structure detection does not
provide universal individuality, precise biological births, or genetic pedigree.
Isolation removes ecological assistance and can stabilize or disrupt a structure.
Its limited first-descendant and phase search can miss viable paths. Boundary
and nonrectangular structures can be missed. Surviving closed cores are therefore
distinct from independently verified viable individuals.

Separated controls change grid extent as well as displacement, so they support
contact-window diagnostics rather than an unrestricted causal estimate of
contact alone. Relative geometry, orientation, and phase are interventions, not
random samples from a natural encounter distribution. Descriptive contrasts
cannot establish population-general effects. Beneficial variation, increased
evolvability, H1, H3, and recursive self-improvement remain unestablished.

## 6. Subsequent experiment plan

For H1, evolve independent population histories, retain matched ancestors, and
sample transferable complete organisms using a fixed sampling rule. Cross each
with the same held-out partner/geometry/phase panel. This transplant holds the
assessment encounter distribution fixed and changes inherited organism state.
Population history, not each encounter or repeated deterministic run, is the
replication unit. Compare conditional beneficial-heritable yields only after
calibrated inheritance and benefit assays.

For H3, compare undisturbed histories, structured disturbances, and shuffled
controls matched on disturbance amount and an explicitly declared shuffle unit.
One transplant puts history-derived organisms into a shared encounter panel,
holding encounter distribution fixed. A second puts shared organisms into
history-specific encounter distributions, holding organism state fixed.
Crossing the two separates inherited-state and encounter-distribution pathways
and their interaction. Preserve independent histories as replication units.
All histories still act through present state and future scheduled interventions;
no residual history effect is expected for identical complete states.

## Reproducibility and data availability

Repository: https://github.com/ReloadLightly/evoloop-levels. Protocols,
configurations, source, compact raw grids, analysis, and figures are versioned.
Each figure must reference experiment IDs and a regeneration command.
The manuscript and bibliography are working artifacts, not a submitted paper.

## References

Verified BibTeX is in `paper/references.bib`. Primary papers are linked in
`docs/source_review.md`; bibliographic caveats and exact inspected hashes are
recorded there. The review's final journal issue is 2025, while its preprint is
2024. No third-party PDFs are included in this repository.
