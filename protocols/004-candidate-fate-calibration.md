# EXP-fate-calibration-001 — prospective measurement calibration

Specified after EXP-atlas-001, before this batch. This is a calibration selected
because the atlas had six novelty-producing configurations, seven composite
identities, and no confirmed stable novel paths. It is not independent H2
confirmation. Preserve protocols 001–003 and their outcomes unchanged.

## Panel and fixed targets

Include all seven candidate identities from the six originating atlas states,
including the previously inseparable candidate. Replay each complete original
initial grid to the candidate's recorded first-observed time. Among recognized
cores with that composite identity, choose the lexicographically first core
(row, column, height, width). Save this complete source grid, its hash, original
core tuple, word, and originating run. First-observed times have ten-update
resolution. A changed genotype at a pre-existing core is allowed as a candidate.
This source construction does not inspect delayed outcomes.

Two positive controls use the verified S13/N01 catalogue snapshots, placed
unchanged at (192,144) in empty 384×384 periodic worlds. Their t=0 sole core is
the fixed target. Both control words are already verified heritable.

For every target use delays 0, 60, 120, 240 updates after its source time: 28
candidate delay observations and eight control delay observations. Advance the
**complete native source world**, retaining ecological surroundings, to each
delay. Match only the exact original core tuple. Do not replace a lost core,
resize its anchor, select a later offspring, or search for a successful phase.
Record the current identity even if it changed. Loss, unknown genotype, shared
component, boundary component, and excessive size are distinct ineligible
observations. Retain them in the 28/8 denominators. Track the fixed core every
ten updates from source to delay. Any observed loss followed by same-tuple
recurrence is separately ineligible (`target_recurrence_after_loss`), not
continuous individual survival. Continuity between sampled times is unresolved.

## Paired interventions and outcomes

Native continuation retains the full delayed world and runs another 1,600
updates. Record the original target's presence/identity, numbers and locations
of recognized original-word cores anywhere, other/unknown-word counts, new core
appearances, disappearance intervals, occupied cells, and boundary flags every
ten updates (summary every 100). Keep the complete start/final worlds. Native
appearance of the target word at another core is **not confirmed offspring or
inheritance**; ancestry remains ambiguous. Overlapping native windows are
paired deterministic views of the same trajectory, not replicates.

Isolation preserves the entire occupied connected component only when it has
one recognized core, no edge contact, a valid word, and max dimension +20 ≤192.
Center it in an empty 192×192 torus. This is an external intervention changing
surroundings and translation/domain size; it does not change rules or genes.

Run two inheritance searches on each **identical eligible snapshot**:

1. The unchanged frozen `evoloop.assays.inheritance` assay (legacy comparator).
2. A bounded expanded search: each generation seeks up to the first three newly
   positioned cores with valid identities and complete detached components.
   Each core coordinate is admitted once, at its first eligible sampled time;
   do not admit alternative phases of that same core. Exclude all t=0 core
   tuples. Sort children by detached time, core tuple, snapshot hash. Each
   generation stops upon collecting three children or at 1,600 updates.
   Traverse depth-first, maximum six transmissions and **24 generation
   simulations per root**. Explore different identities, resetting the streak
   when identity changes. Two consecutive identical composite-identity
   transmissions confirm a stable path. Children with excessive component size
   are recorded but cannot be isolated. Budget, depth, or horizon exhaustion
   leaves unexamined paths unresolved. Empty terminal grids are assay extinction.

For candidates, a recovered stable word must differ from **both original atlas
input words**. Report stable nonnovel paths separately and continue searching
within the cap; stop on the first confirmed novel path. For positive controls,
success requires the original composite identity (and hence original word),
not an arbitrary stable descendant. Stop on that success. Every eligible
positive-control extraction should succeed; report any nonconfirmation as a
measurement limitation. Ineligible control phases remain ineligible.

Persist each generation's complete isolated initial/final grid, sampled core
events, hashes, extracted children, parent stage, transmission streak, and
selection order. This imposed serial isolation search does not demonstrate
unassisted inheritance in the native ecology. A confirmed path can arise only
after isolation and must be labeled assay-derived.

## Analysis and limits

Primary calibration outcomes: eligible fraction per delay; legacy/expanded
confirmed original-identity control recovery; legacy/expanded confirmed novel
candidate recovery; unresolved search and target statuses. Cross-tabulate
paired legacy/expanded results on identical snapshots. Compare delay outcomes
within each source and summarize candidate results at the six originating
configuration units (seven identities are nested). No confidence intervals or
p-values; deterministic delays and branches are not independent samples.

Native original-word appearance at other cores and occupancy are parallel
structural diagnostics, not an equivalent inherited-variant endpoint. A native
appearance/isolation nonconfirmation contrast alone does not prove ecological
dependence. Delay effects combine maturation with continued ecological
exposure; matched search effects condition on a fixed extracted snapshot.
Hold full source state and physics fixed; no residual historical causal effect.

No benefit assay or atlas enlargement occurs here. Benefit yield remains
unknown; H1/H3 and RSI remain unestablished. Preserve all missing, ineligible,
negative, lethal, and unresolved outcomes. Freeze configuration, code hashes,
source-state hashes, and this protocol before running delayed branches. One
worker, measured memory headroom ≥200 MiB, streamed metrics, selective raw
snapshots, no exhaustive frame dump. The absolute expanded-search ceiling is
36×24=864 generation simulations; actual count may be lower through eligibility
and stopping. Main commands are in scripts/fate_calibration.py.
