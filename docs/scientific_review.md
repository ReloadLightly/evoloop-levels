# Independent scientific implementation review

Reviewed 2026-10-10 against the initial `tracking.py`, `assays.py`, `engine.py`,
`verify.py`, `explore.py`, scientific contract, and primary paper texts. This is
a pre-batch scientific review, not certification of later changes. Findings
below distinguish implementation limits from conclusions the pilot can support.

## What is already sound

The contract separates organism, encounter, and historical contributions and
correctly treats history as upstream of a deterministic complete state. It keeps
H1 and H3 untested. The engine uses a compact synchronous nine-state CTRBL lookup
table with periodic boundaries. Exhaustive comparison and an independent
author-program comparison cover all 59,049 transitions. The grid oracle checks
neighborhood order and the C kernel; replay and resume check determinism.

The detector retains carrier states, gene spacing, and signal direction rather
than discarding them to classify by size or unordered genes. It does not equate
closed structures with viability. Causal provenance is explicitly conservative.
Temporary source PDFs and restricted author-program assets are not incorporated.

A focused reviewer execution from the licensed S13 seed at `(65,45)` in a
160-by-160 world, observing every step through 1200, found one unchanged channel
genotype at the original core in 1154 valid detections, and five detections with
unknown genotype during channel contamination. Seven additional observed cores
carried the same valid genotype. This is useful evidence of phase invariance;
it is not a substitute for isolated inheritance tests or event inspection.

## Critical fixes or explicit limitations before freezing the atlas

1. **Retain transient-to-stable inheritance paths.** Initial `generation` returns
   only an offspring matching the input channel genotype. This cannot confirm a
   transient candidate whose first isolated offspring has a different genotype
   and subsequently breeds true. BioSystems section 3.4 explicitly includes
   these and states that most transitions between self-replicators pass through
   transient species. Observe all new cores, isolate a declared bounded set of
   candidate descendants, and test whether a descendant genotype recurs in its
   own offspring and reproducing offspring. Keep the original candidate genotype,
   descendant genotype, and the path separate. Exhausting the search budget is
   unresolved. A narrower direct-inheritance criterion is acceptable only if
   reported as a conservative subset that does not exclude transient observations
   from the evidence or denominator.

2. **Describe cropping honestly.** The raw S13 seed is 17-by-31, whereas its
   detector snapshot is 17-by-17. The fixed crop removes an extended arm and may
   remove partner material or retain adjacent fragments. This is a standardized
   destructive isolation intervention, not transplantation of the complete
   pre-intervention organism. Store source grid, time, core, bbox, snapshot hash,
   and exact isolation placement. Require exactly one detected initial core and
   record unexpected extra structures. A failure of one cropped phase does not
   establish nonviability of the original organism. If selected input phases
   fail alone, report it and keep them as declared treatment states rather than
   replacing them after seeing encounter outcomes.

3. **Freeze candidate effort and unresolved outcomes.** A genotype may be sampled
   in many circulation/arm phases. Predeclare the number of distinct snapshot
   hashes attempted per genotype, their deterministic order, and both isolation
   horizons. Report attempts and reasons for unresolved status. Distinguish zero
   novel genotypes, no confirmed inheritance after completed attempts, and
   untested candidates. Benefit pending is not benefit zero.

4. **Do not overstate genotype equivalence.** The initial traversal is clockwise,
   while published species identification follows counterclockwise genes starting
   at an umbilical dissolver. It is a legitimate *operational phase-normalized
   channel genotype* if defined precisely, but is not automatically the published
   G/T/C species identifier. Circular minimization removes circulation phase and
   possibly information about gene position relative to the arm. Preserve the
   complete snapshot so experiments do not conflate complete states. Normalize
   rectangle dimensions under quarter-turn rotation, or explicitly retain
   oriented dimensions and treat rotations as distinct phenotype states. Never
   identify reflections as equivalent under chiral propagation rules.

5. **Separate structure tracking, birth observations, and parentage.** Closed-core
   appearance is not the literature's umbilical-dissolver birth marker. Label
   events as first observed closures, record temporal resolution, and inspect raw
   frames around representative births. Spatial continuity tracks a core at a
   location; it does not prove descent. If two input causal labels mix, report
   pair-level novelty with ambiguous ancestry. Do not silently assign every
   novelty to the focal organism. Same-genotype new cores require reproduction
   confirmation, rather than shape alone.

6. **Declare contact as an operational quantity.** The optional kernel provenance
   ORs every occupied neighboring provenance regardless of whether the transition
   actually depends on that neighbor. It overapproximates causal influence. The
   contact function also detects occupied adjacency. Call its result occupied
   adjacency or potential inter-input influence, not proven genetic exchange.
   Check every step if reporting an exact first-contact time; sampling every ten
   steps gives a bracket. Contact-negative configurations are still retained in
   the crossed denominator. A control that unexpectedly contacts remains a
   recorded control violation rather than disappearing from the dataset.

7. **Address periodic seams.** Physics wraps periodically, while closed-core
   detection uses ordinary connected components and discards cores within three
   cells of a boundary. This can undercount reproduction and population after
   spreading. Use sufficient spatial headroom, implement periodic detection, or
   flag seam censoring and report the resulting quantitative limit. Record both
   boundary occupancy and detection uncertainty; absence of detected cores at a
   seam does not establish extinction.

8. **Make isolation lineage inference conservative.** Confirmed recurrence at a
   new location is stronger when initial isolation contains exactly one core,
   raw grid frames show construction of a separate offspring, and that isolated
   offspring produces another. Unexpected pre-existing cores or retained
   fragments should make ancestry ambiguous. Preserve full assay starting arrays
   and representative offspring frames. Extinction means all cells disappear;
   persistent debris with no reproduction by the horizon is unresolved.

## A small defensible frozen atlas

Use S13 and the first two naturally generated distinct genotypes that pass the
declared two-generation isolation criterion. Record panel selection order and
source-run provenance. They share one founding history, so these are three fixed
organism types, not three independent evolutionary histories. If only two become
available, a two-by-two crossing is preferable to indefinite discovery work.

Use ordered physical slots: focal on the left with fixed orientation and partner
on the right. Construct placements from occupied bounding boxes with positive
empty-cell gap; save every complete initial array. Cross all focal types with
all partner types and a small common geometry/phase panel, such as two gaps,
two partner rotations, and two predeclared reproduction-phase offsets. Choose
phase offsets from raw autonomous growth before any offspring closure, so each
input actually contains one organism. Store exact arrays instead of assuming
that a number called phase captures all its state.

Freeze a common observation horizon using autonomous reproduction times and
measured runtime. Reserve a complete geometry/phase subset as held-out before
running main outcomes. It tests transfer across configurations, not independent
biological replication. Include each organism/phase alone at both physical slots
and the same pair states placed far enough apart to remain contact-negative over
the horizon. Confirm the latter from raw runs and log deviations. Do not impose
blocking walls without labeling that changed treatment.

Define per-run outcomes separately: occupied contact/potential influence and its
time, persistence of each input core, closure counts, reproduction evidence,
distinct candidate novelty relative to **both** inputs, confirmed isolated
inheritance, confirmed ecological benefit, untested candidates, exhausted
inheritance searches, ancestry ambiguity, and boundary censoring. A genotype
first seen without contact can arise through autonomous self-encounters; compare
it with alone and contact-negative controls rather than attributing it to the
inter-input encounter. Keep all crossed initial configurations in denominators.

Freeze a benefit assay before selecting candidates: standardized isolated
candidate and both inputs in the same recolonization world, common placement,
common bounded horizon, and paired disturbance schedules. Mean detected closed
cores is a *structural population proxy* unless each genotype counted is
independently verified viable. Report what the chosen count includes. Hold out
independent schedules or spatial placements for confirmation. A conservative
pair-level beneficial variant must outperform both inputs on the predeclared
discovery criterion and its independent confirmation criterion. If assay
confirmation is deferred, publish pending counts explicitly and avoid claiming
beneficial-heritable yield or useful evolvability was established.

For analysis, report finite-panel counts and fractions with explicit denominators,
missingness, and unresolved categories. For each outcome compute focal means,
partner means, and residual interaction
`r_ij = y_ij - row_mean_i - col_mean_j + grand_mean`; inspect matched
configuration differences of differences and focal ranking reversals. Repeat
those descriptive contrasts on the reserved subset. A partner main effect alone
is insufficient. Deterministic duplicate states and reciprocal focal labels of
the same physical state are not independent replicates. For this small fixed
atlas, exact descriptive contrasts are more defensible than population p-values
or confidence intervals implying independently sampled organism histories.

## Permissible first-checkpoint conclusions

The checkpoint can establish a verified simulator, a reproducible finite
encounter panel, naturally generated candidate novelty, and confirmed inheritance
under the declared isolation intervention. Nonzero matched interaction contrasts
can demonstrate partner dependence of the measured outcome **within that panel**.
They do not yet establish inherited organism evolvability, beneficial variation,
independent historical effects, general rank reversals, or recursive
self-improvement. Null, lethal, and unresolved encounters remain useful evidence.

Primary basis: [Salzberg and Sayama, Complexity preprint](https://bingdev.binghamton.edu/sayama/papers/Complexity-preprint.pdf),
methods and Figure 2; [Salzberg, Antony, and Sayama, BioSystems preprint](https://bingdev.binghamton.edu/sayama/papers/BioSystems-preprint.pdf),
sections 2.1.1 and 3.4; [Sayama, original evoloop paper](https://bingdev.binghamton.edu/sayama/papers/ALIFE5-4-343.pdf),
reproduction mechanism and species definitions. Bibliographic verification and
license decisions are recorded separately in `docs/source_review.md`.

## Review of the extraction and inheritance revision

During the review, the implementation was revised to preserve the entire
four-connected occupied component, extract only components with exactly one
recognized core, and reject components touching a boundary. The project lead
observed that body-only S13 crops fail isolation, which strengthens the reason
for this fix. The complete component is appropriate material for the declared
isolation assay; the short body crop remains useful structural evidence only.

Revised isolation waits for a new core in a detached single-core component,
allows its genotype to differ from the candidate, and requires recurrence of a
stable genotype after subsequent isolation. When the first descendant differs,
an additional stable reproduction round is required. This resolves the main
transient-path omission for the chosen first-descendant path. It still selects
the first eligible descendant in deterministic scan order; later eligible
descendants are not exhaustively searched. A failed chosen path must remain
unresolved, with that declared conservative search limitation.

Record first closure and detachment separately. A return time sampled every ten
steps is first observed *detached reproduction*, rather than exact birth time.
Exactly one recognized core does not prove that no damaged or unrecognized
structure is attached; source frames and a statement of the recognition limit
are therefore still needed. Check snapshot dimensions before placement: an
oversized extracted component is an explicit assay-ineligible/unresolved case,
not an assertion crash or evidence of extinction.

An assay-derived stable genotype must remain novel relative to both original
encounter inputs before contributing to novel-heritable yield. Keep the
encounter-observed genotype and stable descendant genotype in separate columns.
The stable genotype may arise for the first time after isolation; describe it as
an inherited stabilized descendant of encounter novelty under the standardized
isolation intervention, not automatically as a stable variant observed in the
unintervened encounter world.

## Final first-checkpoint reporting assessment

Reviewed final README, research state, manuscript, and machine-generated atlas
analysis after all 104 configurations and 11 frozen isolation paths completed.
No material scientific inconsistency or unsupported H2 claim was found in these
reports. The reported counts distinguish six candidate-producing near states,
seven run/identity candidates, five states with extractable snapshots, and
eleven attempted paths. All seven candidate identities are unresolved with
respect to stable novel inheritance under the declared search. Zero confirmed
paths is a measured endpoint, not proof that ecological inheritance is absent.

The reporting audit correctly retains the frozen composite identity endpoint
while separately reporting signal-word novelty and identifying the latter as
added after freeze. All observed candidates pass both definitions. The natural
discovery path provides an actual inherited signal change, whereas its
11-by-13 to 12-by-12 stabilization is explicitly morphological. That exploratory
success is separate from the atlas's zero confirmed novel paths.

Candidate-only difference of differences is +0.375 in the main panel and -0.500
held-out; the main partner-dependent ranking does not transfer. Confirmed
inheritance contrasts are zero in both panels. These finite-panel descriptive
results support neither useful-heritable H2 nor a general rejection of encounter
dependence. Pending benefit remains unknown, and H1/H3/RSI remain unestablished.
The separate multi-transient follow-up is appropriately exploratory and does
not revise the frozen endpoint.

The recommended next experiment is the declared paired candidate-fate
calibration: native continuation versus isolation at fixed maturation delays,
a prospectively bounded transient-offspring search, and known S13/N01 positive
controls. This addresses the immediate uncertainty about candidate fate and
assay sensitivity before expanding the causal comparisons. The review does not
certify every raw array or figure; those are covered by the repository's
separate integrity and visualization checks.
