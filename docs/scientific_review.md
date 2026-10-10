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

## Final first-checkpoint reporting assessment: EXP-atlas-001 (2026-10-10)

This historical assessment predates EXP-atlas-002 and the ecological batches;
its pending-benefit statements describe that checkpoint only.

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

## Completed candidate-fate calibration assessment: EXP-fate-calibration-001 (2026-10-10)

Reviewed `data/fate-calibration/analysis.json`, its rendered analysis, and all
36 case summaries after acquisition. Of 28 candidate identity/delay observations,
15 were eligible for paired isolation, ten had lost their fixed target, and
three remained shared components. Neither the unchanged legacy search nor the
expanded bounded search recovered a novel stable word. Both searches recovered
the original identities in all eight eligible S13/N01 control observations.
This establishes recovery of these known controls under the tested delays and
shows that the tested timing/search extensions did not rescue the eligible
candidates. It does not establish universal assay sensitivity or intrinsic
nonviability of all candidate structures.

No expanded candidate search reached the simulation or depth ceiling. The
first-three-detached-offspring limit, horizon, exact fixed-core matching, and
ineligible phases still limit what was searched. Candidate searches simulated
69 generation nodes. Delay observations remain nested in seven identities and
six originating configurations, rather than independent histories.

Native boundary flags occurred in 16 of 28 candidate windows and two of eight
control windows, so native seam-crossing populations can be underdetected.
The four positive native original-word observations all refer to the same C05
event viewed through overlapping windows. Its word appeared at one other
9-by-9 core at two consecutive ten-update samples. This is transient
structural recurrence, not four independent events, proved ancestry, stable
native inheritance, or evidence of ecological assistance rescuing reproduction.

The most informative next scientific experiment is a small fresh crossed atlas
with an expanded panel of three or four naturally generated, isolation-verified
viable identities, selected by a predeclared discovery rule before assessing
encounters. Use fresh held-out configurations and the bounded inheritance
search. This broadens viable variation sources after the measured negative
calibration; there is presently no recovered novel candidate available for a
benefit assay. Quantitative native counts require boundary-safe observation or
periodic detection. This recommendation does not authorize execution and does
not establish H2, H1/H3, beneficial evolvability, or RSI.

## Fresh crossed atlas: independent results review before ecological assays (2026-10-10)

This historical assessment records the post-atlas, pre-benefit checkpoint. The
completed ecological assessment below supersedes its pending-benefit status.

Reviewed the frozen `EXP-atlas-002` analyzer, its actual aggregate results, and
the eight reported positive isolation paths. The independent dense-source and
graph-link audit passed with zero mismatches in 123.16 seconds; its evidence is
in `data/atlas-v2/lineage-integrity.json`. It checked all 144 initial/final grid
and provenance self-hashes, replayed 24,230 original-dense updates across all
18 candidate-producing runs and 99 observation/capture times, verified every
one of 52 candidate first observations, and retained 52 compact raw frames.
It verified all 88 captured native snapshots, 1,205 isolated node inputs,
1,117 linked parent-child edges, 1,323 child arrays, and eight confirmations.
This supplements the separate individual-generation replay: it checks actual
source-to-assay and graph links, not every full terminal native trajectory or
unobserved ancestry.

The atlas contains 144 distinct configurations: 54 near encounters, 54 matched
separated controls, and 36 single-organism controls. All 54 near configurations
made contact; neither control treatment made contact or generated screened
novel words. Native candidates occurred in 14/36 main and 4/18 held-out near
configurations. Stable pair-novel descendants were recovered from 2/36 main
and 0/18 held-out configurations, hence 2/54 over the complete near panel.
Every configuration remains in these denominators, including nonproductive
encounters. Benefit was not assayed and beneficial-heritable yield is unknown.

The two positive configurations are `near-main-V01-V03-p20-a-parallel` and
`near-main-V02-V03-p20-a-parallel`. Their eight positive assay roots are two
captured phases of each of four encounter composite identities, nested within
these **two** originating configurations. They are neither eight independent
encounters nor eight independently discovered stable words. The V01/V03 path
changes morphology from 13-by-15 to stable 14-by-14 while preserving its channel
word. The V02/V03 path changes a transient 12-by-13 word into a stable 12-by-12
word; that stable word also appears in the native encounter. Each reported
positive path has two consecutive identical composite transmissions after its
last composite identity change, and the stable word differs from both local
input words.

The stable 12-by-12 word is exactly the existing V01 catalogue word. Its
recovery is therefore **novel relative to the V02/V03 input pair**, not new to
the input catalogue. The stable 14-by-14 word differs from all three input
catalogue words. These classifications describe word identity, not global
historical priority or proof of a particular genetic parent. The conservative
pair-novel endpoint correctly admits both outcomes, but a claim of two new
catalogue genotypes would be incorrect.

There were 52 run/composite candidate identities, six without any extractable
captured phase, and 88 isolation roots comprising 1,205 simulated generations.
The search records 134 simulation-budget truncations, 24 depth truncations,
and no component-size truncations; 441 nodes collected the maximum three
offspring. Nonconfirmation is unresolved under these limits, not exhaustive
evidence of nonheritability. Serial imposed isolation establishes heritable
recovery under this intervention; native channel recurrence and causal masks
do not reconstruct native genetic ancestry.

The frozen generated `data/atlas-v2/analysis.md` includes an overgeneralized
sentence saying “zero confirmed inheritance is a measured search result.”
For this batch, that qualification applies only to zero cells and
nonconfirming searches. It must not be read as the overall outcome: its own
table and machine-readable counts show **2/54 positive encounter states**.
The generated artifact and frozen analyzer are preserved; this note records
the necessary interpretation correction without silently changing them.

Candidate ranks reverse for V01 versus V02 and V02 versus V03 between the
V01/V02 partner columns in the main panel, but neither reversal persists in
held-out configurations. Confirmed inheritance has no strict rank reversal.
Four inherited interaction contrasts are -0.25 in the main panel and zero
held-out; the remaining five are zero in both. These are descriptive contrasts
over the specified configurations. They show conditional encounter-dependent
recovery and candidate nonadditivity; they do not establish a stable,
generalizable H2 effect on useful variation. H1, H3, beneficial evolvability,
and RSI remain untested or unestablished.

The most informative next experiment is prospective viability calibration of
the declared disturbance assay, followed by paired benefit comparisons of the
two recovered stable words against both corresponding inputs under frozen
development and independent confirmation conditions. Its first task is to
test whether recognized closed-core counts track reproductively viable
organisms in the assay, so a change in structural counts is not misreported as
benefit. Recovered V01 must retain its known-catalogue label throughout.

## Ecological calibration and benefit: independent assessment (2026-10-10)

The independent original-dense audit passed with zero mismatches in 306.45
seconds, peak RSS 63,960 KiB (62.46 MiB). It replayed all 30 ecological worlds,
62,000 updates, 3,130 sampled records, 60 explicit block removals, and 123
animation frames. It verified all 40 calibration source frames, 68 extracted
components and native continuation windows, 73 isolation-search roots, 141
isolated generation states, 408 child-selection states, 68 graph edges, and 68
confirmations (five baselines and 63 selected sources). Gate and paired
comparison arithmetic were independently reconstructed using exact integer
sample totals. Evidence is `data/ecological-v1/integrity.json`; rerun with
`OPENBLAS_NUM_THREADS=1 python -m scripts.verify_ecological`.

The frozen calibration gate passes: all five baseline states recover, and
63/68 selected scored cores recover their original composite identity. Each
starting-state and nonempty-stratum requirement also passes. All 68 selected
cores were extractable; there were no selected unscored cores. Thus the
unscored class supplies no recovery evidence (0/0, not a zero recovery rate).
Three scored components dissolve under isolation and two produce no detached
offspring by the horizon. These five unresolved native fates are allowed by
the prospective gate and must remain visible. No depth or simulation cap was
reached, while 136 productive nodes reached the three-offspring collection cap.
Passing this finite sampled gate does not make every counted core viable in
its native ecology or turn the score into total viable population.

RV01, the recovered known V01 identity from V02/V03, **meets the frozen numerical
proxy-advantage criterion** in both named panels. Its panel score is
580/162 = 3.58025, against V02's 546/162 = 3.37037 and V03's 538/162 = 3.32099.
RV02, the catalogue-new 14-by-14 identity, does not meet it: 508/162 = 3.13580,
below V01's 577/162 = 3.56173 and V03's 538/162. The frozen analyzer's resulting
formal confirmed-proxy yield is 1/36 main, 0/18 held-out, or **1/54 overall**.
Its label is preserved as the result of the declared rule, not silently changed
after the experiment. The other 16 candidate-producing encounter states remain
unresolved under the earlier bounded inheritance search. No new catalogue word
has demonstrated advantage in this assay.

The supplementary symmetry audit identifies a material limitation of that
formal result. For every starting state, development-1 and confirmation-0
initial and final grids are related by a 90-degree counterclockwise rotation;
the odd 19-by-19 V02/V03 snapshots additionally require a one-row translation
because of centering. Development-0 and confirmation-1 are related by a
270-degree rotation, with a one-column translation for those odd snapshots.
All 81 samples match for scored, unscored, unknown, total-core, and occupied-cell
counts. The proof includes byte hashes, raw array locations, actual clearing
operations, and transformations in `data/ecological-v1/symmetry-audit.json`;
rerun with `OPENBLAS_NUM_THREADS=1 python -m scripts.audit_ecological_symmetry`.

Development-1's block at (128,128) rotates to confirmation-0's (40,128) for the
only impacted states, V01/RV01. Other differing block footprints do nothing to
occupied cells in both corresponding histories. Exactly 36/40 benefit clears
remove zero occupied cells. The remaining four each remove 18 occupied cells
at t=1000 in V01/RV01 development-1/confirmation-0. None of the 40 clears changes
the registered-core count immediately. The update law's rotation/translation
symmetry, transformed initial arrays, and identical effective removals explain
the identical panel scores. Nominally reserved confirmation schedules therefore
repeat the development challenges; they do not provide a distinct effective
ecological confirmation.

Consequently, **the frozen criterion is met, but independent challenge
confirmation remains unresolved**. The evidence supports a finite-panel
advantage in the known-identity structural population proxy for RV01. It does
not establish recovery of a depleted viable population, robustness to effective
disturbance, generally superior ecological performance, an increased capacity
for further adaptive variation, or RSI. The known identity's recovered snapshot
differs from the catalogue preparation, so score differences must be attributed
to declared complete states rather than signal words alone. Native continuation
and causal provenance do not identify genetic parentage. H1/H3 remain untested,
and the original held-out encounter inheritance result remains zero.

The single most informative next experiment is a prospectively frozen,
nonsymmetric, **impact-matched disturbance comparison with paired undisturbed
controls**. Retain both outcomes and the relevant inputs, declare preparation
phases, and specify a minimum nonzero population-impact target and a deterministic
selection rule before seeing performance. Record the actual lost registered
cores and occupied cells; preserve unmet-target cases explicitly. Use reserved
conditions that cannot be obtained from development conditions by CA symmetries,
and compare the disturbance effect with each state's exact no-clear control.
This separates ordinary growth and preparation-phase effects from recovery
under real damage without revising the completed assay's metric or criterion.
