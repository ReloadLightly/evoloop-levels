# Where Does Evolvability Reside? Organisms, Encounters, and Ecological History in Self-Reproducing Cellular Automata

**An encounter experiment separating the production of candidate variants from their stable transmission**

## Abstract

Encounters between self-reproducing structures can generate new forms; establishing heritable variation requires demonstrating transmission of their differences. We investigate this distinction in evoloops, a deterministic cellular automaton in which interacting reproductive arms can alter descendants. A crossed experiment pairs a documented organism with a naturally generated, inheritance-verified variant across controlled spatial configurations. Candidate signal changes occurred in six of 40 encounter configurations, compared with zero of 40 separated and 24 solitary controls. None of 11 initial isolation paths confirmed stable novel transmission. Partner-dependent candidate rankings in the main panel failed to transfer to held-out configurations. To examine whether early extraction or restricted descendant search explained the inheritance result, a subsequent calibration followed all seven candidate identities at four delays and compared two isolation searches on identical components. Fifteen of 28 candidate-delay observations were eligible for extraction; neither search recovered stable novelty. Both recovered the known input identities in all eight positive-control observations. Thus, in this panel, encounter-dependent candidate production was not accompanied by recovered stable inheritance, even after the specified extensions of maturation time and descendant search. The remaining unexamined paths and ecological dependence limit this conclusion. The study identifies a measurement problem central to locating evolvability: organism and encounter effects on producing variation must be distinguished from their effects on transmitting it.

## 1. Introduction

A system's capacity for evolutionary change depends on more than producing new forms. For adaptive evolution, differences must pass to descendants and improve performance in a relevant environment. Separating these steps is particularly important when reproduction itself depends on interactions: an encounter may create a novel structure, help it reproduce, or destroy it before its differences can persist.

Evoloops make these possibilities observable. They are self-reproducing structures embedded in a two-dimensional cellular automaton. A circulating signal sequence participates in constructing offspring, while contact between reproductive structures can change the sequence and shape of the resulting loops. All events follow fixed local rules (Sayama, 1999). The model therefore lets us intervene on encounters without inserting a separate mutation operator.

Where, then, does the capacity to generate heritable variation reside? An organism may carry a transferable bias in the variants it produces. That bias may be expressed differently against different partners. Previous ecological conditions may shape both the organisms present and the encounters they experience. These are compatible contributions, whose identification requires different comparisons. We organize them as three hypotheses: **H1**, a contribution transferable with the organism under common encounter conditions; **H2**, a contribution specific to organism–partner combinations; and **H3**, historical effects mediated by changes in organisms and encounter distributions.

The present experiment addresses the encounter comparison. We cross two input organisms across a defined spatial panel, then follow candidate variants through isolation and repeated reproduction. Crossing partners asks whether the outcome associated with changing one organism depends on the other. Following descendants asks whether any such pattern concerns temporary structural changes or transmitted variation. A second experiment examines a concrete alternative explanation for failed transmission: the initial assay may extract candidates too early or follow too few descendants.

The resulting distinction provides the current contribution. Encounters produced candidate signal changes, but the tested candidates did not yield confirmed stable novel inheritance under either isolation search. Known input organisms remained recoverable under the same calibration. This localizes the unresolved question to candidate fate and assay coverage, rather than treating every observed change as an equivalent evolutionary event. It also establishes what subsequent organism and history comparisons must measure: variation production, transmission, and ecological benefit as separate stages.

## 2. Prior work and the experimental question

Sayama's original evoloop establishes interaction-mediated genotype change and spatial selection in deterministic, synchronous nine-state dynamics (Sayama, 1999). Later work shows that loops of the same size can differ in gene arrangement, colony morphology, persistence, and mutational bias. Salzberg and Sayama report round-robin competition among 15 size-4 genotypes and descendants inheriting variation biases (Salzberg and Sayama, 2004). These findings already connect inherited organization with evolutionary outcomes.

Salzberg, Antony, and Sayama examine genealogy, biased accessibility of larger species, pathogens, and localized or distributed disturbances (Salzberg, Antony, and Sayama, 2004). They also retain transient species that produce stable replicators in a later cycle. A failure to copy the first observed candidate immediately is therefore insufficient grounds for discarding its evolutionary potential. The recent review places these mechanisms within the broader problem of reproduction supporting inherited variation and discusses persistent questions of individuality and long-term evolution (Sayama and Nehaniv, 2025; preprint 2024).

Our experiment builds on these results by comparing the fate of variation under specified encounters. Population competition measures which types persist; here the immediate outcome is whether a particular encounter produces a new identity with a recoverable transmission path. Retaining nonproductive encounters supplies the denominator, while isolation tests and delayed extraction distinguish candidate appearance from later reproduction. The contribution is this intervention-and-measurement comparison, rather than the discovery of interaction-generated mutation or inherited mutational bias.

## 3. Methods

### 3.1 Dynamics and organisms

We use the original nine-state evoloop transition system, synchronous updates, and periodic boundaries. The neighborhood is center, top, right, bottom, left; rotations of explicit rules and the dissolution/default rules produce all 59,049 local transitions. The lookup table agrees exhaustively with the pinned CellPyLib reference and an independent expansion of the author's EvoLoopS rules (Antunes, CellPyLib; Sayama, EvoLoopS). Seed reproduction, deterministic replay, and checkpoint/resume are verified. Exact versions, hashes, licensing, and execution details are documented in [source review](../docs/source_review.md) and [reproduction instructions](../docs/reproducing-results.md).

S13 is CellPyLib's documented species13 seed, matching the author's `13.img`, rather than the alternative default `13-2.img` (Antunes, CellPyLib documentation). N01 is a stable descendant obtained from a 160×160 exploratory torus initiated with S13 at (65,45). Discovery samples every ten updates, considers up to four detached phases per candidate, and ends after two verified identities. This selected exploratory history supplies an experimental input; it is not replication across independently evolved populations.

### 3.2 Crossed encounters and controls

Before acquisition, protocol 001 specifies 32 main encounters, eight held-out encounters, and controls. Complete input snapshots advance alone by 0, 30, or 60 updates. Each resulting state must retain one recognized core, unchanged identity, and no boundary contact. These offsets refer to different snapshot origins; they are not necessarily homologous reproductive phases.

All four ordered S13/N01 pairings are tested against four main geometries at offsets 0 and 60, giving eight configurations per pair. Two held-out geometries at offset 30 give two further configurations per pair. Near configurations occupy 384×384 tori, with specified positions, rotations in 90-degree increments, and nonoverlapping input rectangles. Forty separated controls retain identities, offsets, orientations, and row displacement in 640×640 tori, with horizontal displacement of 320 cells. Twenty-four solitary controls cover organism, offset, and orientation. Every configuration runs for 1,600 completed updates; separated controls are checked for contact throughout.

### 3.3 What counts as a variant?

A structural detector samples rectangular zero-valued cores with intact inner sheaths in states 2/3 every ten updates. For channels containing only states 0/1/4/7, we read a clockwise signal word, preserving carrier spacing and normalizing by cyclic shift without reflection. Pairing this word with sorted core dimensions defines the operational composite identity. It preserves chirality but differs from the published counterclockwise, birth-anchored species identifier (Salzberg, Antony, and Sayama, 2004). Contaminated channels have unknown identity; recognized cores alone do not establish viability.

A candidate composite identity must differ from both encounter inputs. A reporting audit introduced during acquisition, before inheritance analysis, additionally distinguishes signal-word novelty from shape-only differences. The composite endpoint remains the frozen primary definition. Word-only novelty is a separately labeled, post-hoc sensitivity endpoint; it was not prospectively specified. Protocol 002 records this distinction without changing raw outcomes or search budgets.

Occupied input cells receive provenance masks 1 and 2; newly occupied cells inherit the union of occupied contributors in their neighborhood. Contact is the first update containing exclusive-provenance adjacency or mixed occupied provenance. These masks overapproximate causal contribution and do not identify genetic parents. After contact, novelty is consequently a pair-level outcome.

Core coordinates track structures. Appearances and losses are interval-censored within ten updates. Boundary contact is flagged because the detector does not join structures across the torus seam. Nonrectangular structures can also escape recognition. Structure persistence, lineage survival, candidate novelty, inheritance, and benefit remain distinct measurements.

### 3.4 Testing transmission after isolation

The initial assay extracts the entire occupied connected component, including reproductive arms, if it contains exactly one recognized core and avoids the boundary. It places the component in an empty 192×192 torus. Shared, boundary-spanning, and oversized components are ineligible. The earliest two distinct extractable snapshots per run/identity define the search budget; size checks occur after capture, so oversized attempts consume that budget and remain unresolved.

Each generation runs for up to 1,600 updates. The first newly positioned, valid closed core with a detached component supplies the next isolated generation. A candidate may first produce a different stable descendant. That descendant must transmit the same identity twice consecutively, requiring an additional generation when the original candidate was transient. Closure and detachment are recorded separately. Stable identities first arising after extraction are labeled assay-derived and checked again against both inputs.

A path without qualifying reproduction by the horizon is unresolved; an empty grid is extinction under isolation. Either outcome can coexist with an unexamined successful path or ecological dependence. Complete-component extraction preserves active arms, avoiding the disruption caused by cropping only the central body.

### 3.5 Delayed extraction and expanded descendant search

Protocol 004 tests whether maturation or a broader search recovers inheritance missed by the initial assay. It follows all seven candidate identities, nested within six originating configurations. At first observation, the lexicographically first matching core tuple fixes the target. No later successful structure may replace a lost target. Verified S13 and N01 snapshots in empty 384×384 worlds provide positive controls.

Extraction occurs after 0, 60, 120, or 240 updates: 28 candidate-delay and eight control observations. Ten-update tracking distinguishes target loss and subsequent same-tuple recurrence. Lost, recurrent, unknown, shared, boundary, and oversized targets are ineligible. Each delayed world also continues natively for 1,600 updates. Matching words elsewhere are structural observations; they do not establish offspring ancestry. These continuation windows overlap and are not independent observations.

Every eligible component enters both the unchanged legacy assay and an expanded search. The expanded search collects the first three detached, newly positioned valid cores per generation, once per core tuple, ordered by time, coordinates, and snapshot hash. Depth-first traversal permits six transmissions and at most 24 generation simulations per root, each lasting at most 1,600 updates. Identity changes reset the transmission streak. Two identical consecutive transmissions confirm stability. Candidate recovery requires a stable signal word different from both inputs; control recovery requires the original composite identity.

Comparing searches on the same snapshot isolates search sensitivity. Comparing delays combines maturation with continued ecological interaction. Ineligible extractions and unexamined branches remain explicit.

### 3.6 Analysis and ecological benefit

The completed primary endpoint is any confirmed novel stable transmission path per near configuration, retaining all 40 near states in the denominator. Candidate and unresolved outcomes are reported separately. For each main or held-out panel, the candidate interaction contrast is the difference of differences:

`[rate(S13,S13) − rate(N01,S13)] − [rate(S13,N01) − rate(N01,N01)]`.

This measures pair-configuration interaction under ambiguous parentage, rather than an identified focal mutation capacity. The configurations form a specified finite panel, not a random sample from a natural encounter distribution. Deterministic reruns verify reproducibility. Accordingly, we report descriptive contrasts without binomial intervals or inferential p-values. Held-out geometries assess configuration transfer; they do not supply independent organisms or evolutionary histories.

A prospectively specified benefit assay would compare an inheritance-confirmed candidate with both inputs in 192×192 tori over 1,600 updates, removing a 24×24 block at updates 600 and 1,000. The proposed score is mean intact-core population of isolation-confirmed identities, sampled every 20 updates, under two development and two independent confirmation schedules. Success requires exceeding both inputs' means in both panels. Viability calibration is necessary because intact cores can be doomed. These comparisons have not been completed; beneficial-heritable yield is therefore unknown. The present results concern production and transmission.

## 4. Results

### 4.1 A transient structure supplies an inherited input variant

In discovery, a candidate appearing at update 2,910 had an 11×13 core and a signal word different from S13. Isolation yielded a 12×12-core descendant, followed by two generations transmitting that stable identity. Detachment was first observed after 380, 390, and 390 updates in the successive assays, at ten-update resolution. N01 denotes the stable descendant. The transient and stable forms share the changed word, distinguishing morphological stabilization from signal change. This observed route motivates allowing transient-to-stable paths in encounter assays.

### 4.2 Encounters produce candidate changes without confirmed stable transmission

All 40 near configurations contacted within the observation window. Five of 32 main configurations and one of eight held-out configurations produced candidate composite changes. All seven candidate identities also differed in signal word from both inputs, so the post-hoc word-only classification agrees here. Separated controls produced 0/40 candidates and solitary controls 0/24. No atlas state received a boundary-touch flag. The matched near-minus-separated candidate contrast is 6/40, or 0.150, for this panel.

Five candidate-producing configurations supplied 11 isolation snapshots; the remaining candidate could not be separated. None confirmed stable novel transmission. Six paths produced changed detached descendants in their first stage: four subsequently dissolved, and two failed to reproduce the same identity by the next horizon. Two initial snapshots dissolved, and three produced no qualifying detached descendant. These observations separate candidate appearance from transmission under the stated assay.

| Pair | Candidates: main | Candidates: held-out | Inherited: main; held-out |
|---|---:|---:|---:|
| S13 × S13 | 3/8 | 0/2 | 0/8; 0/2 |
| S13 × N01 | 0/8 | 0/2 | 0/8; 0/2 |
| N01 × S13 | 1/8 | 1/2 | 0/8; 0/2 |
| N01 × N01 | 1/8 | 0/2 | 0/8; 0/2 |

Changing the focal organism in the main panel gives candidate contrasts of +0.250 with S13 as partner and −0.125 with N01 as partner: a rank reversal and interaction contrast of +0.375. Held-out contrasts are −0.500 and 0.000, giving −0.500 without a strict rank reversal. The candidate pattern does not transfer to the held-out configurations. All confirmed-inheritance contrasts are zero because no tested path satisfies the criterion; the candidate pattern therefore does not establish an interaction in useful heritable variation.

Thirty near states lost both initial recognized cores, although many retained input-type descendants. Five ended without a recognized core: one empty and four retaining debris. Initial cores also disappeared in all separated and solitary controls while colonies continued. Individual-core loss is therefore an unsuitable substitute for lineage extinction.

### 4.3 Neither delayed extraction nor broader search recovers candidate inheritance

An exploratory extension first followed the earliest N01×N01 offset candidate, observed at encounter update 1,550. Its 3×12-core source produced a 6×6 descendant, then a 4×4 descendant that dissolved at the third isolation stage. This selected diagnostic motivates examining more paths, but adds no independent confirmation.

The subsequent prospective calibration completed all 36 observations. Of 28 candidate-delay observations, 15 were eligible, ten had lost the fixed source core, and three remained shared. No extraction was excluded for recurrence, unknown identity, boundary contact, or size. All eight controls were eligible. Both searches confirmed 0/15 novel candidate paths and recovered 8/8 known control identities. None of the six originating configurations supplied a confirmed novel path. The 13 ineligible observations remain in the denominator for extraction eligibility; their inheritance outcomes are missing.

| Delay | Eligible / observed | Novel: legacy; expanded | Parents: legacy; expanded |
|---|---:|---:|---:|
| 0 | 4/7 | 0/4; 0/4 | 2/2; 2/2 |
| 60 | 4/7 | 0/4; 0/4 | 2/2; 2/2 |
| 120 | 4/7 | 0/4; 0/4 | 2/2; 2/2 |
| 240 | 3/7 | 0/3; 0/3 | 2/2; 2/2 |

Expanded search examined 69 candidate and 16 control generation states. No root reached the 24-simulation or six-transmission limit. Eighteen candidate generation states reached the three-offspring collection limit, leaving later offspring unexamined. Each delay of the 3×12 source generated ten searched states without stable recovery. Other eligible roots produced descendants that dissolved under further isolation or remained unresolved at the horizon.

In native continuation, the 9×9 candidate word appeared at another core at original encounter times 1,150 and 1,160. Its appearance in all four overlapping windows is one structural recurrence, not four independent reproduction events. No candidate original word was recognized at the endpoint of its continuation windows. However, boundary flags occurred in 16/28 candidate and 2/8 control windows, limiting these counts. Control words appeared at new locations and persisted at all eight endpoints. Native endpoint absence consequently cannot establish candidate extinction.

## 5. Discussion

### 5.1 Production and transmission require separate explanations

The encounter comparison identifies configurations that produce changed signal words; the inheritance comparison asks whether those changes persist through repeated reproduction. The two measurements diverge in this panel. Treating candidate counts as evolvability would attribute significance to the main-panel partner reversal despite its failure to transfer and the absence of recovered stable novelty. Transmission changes the interpretation of that apparent interaction.

The calibration addresses two specific explanations for the negative inheritance result. Allowing the prescribed maturation delays and following additional detached descendants did not recover a stable novel path. Successful recovery of S13 and N01 shows that both searches can extract and transmit those tested identities at those delays. It makes a blanket explanation that the assay never recovers reproducing loops incompatible with the controls. It does not establish sensitivity for every altered phenotype. Candidate-specific extraction damage, ecological assistance, later offspring, and longer transient sequences remain possible.

The discovery path supplies a useful contrast: a transient structure did produce stable novelty under complete-component isolation. It demonstrates a route accommodated by the method, while its exploratory selection prevents using it to estimate encounter-wide success. The current evidence supports a conditional separation between candidate production and recovered inheritance, rather than a universal barrier to heritable variation.

### 5.2 Scope of the causal comparison

The two-organism panel contains one selected descendant from one history. Signal word, shape, arms, and reproductive phase can covary; a pair effect cannot be assigned solely to a gene sequence. Equal observation horizons also permit unequal time after contact. Separated controls change world extent as well as distance, limiting interpretation to the declared configurations.

Isolation deliberately changes the environment and can disrupt or stabilize reproduction. Fixed-core tracking excludes lost or reshaped targets and their possible descendants. The three-offspring cap, ineligible phases, finite horizons, rectangular detector, and seam-crossing failures bound the searched paths. The negative result therefore identifies what was not recovered under specified interventions, while the controls identify what those interventions demonstrably recover.

### 5.3 Connecting encounters, organisms, and history

The next informative comparison broadens the verified organism panel under a predeclared discovery and selection rule, then tests fresh crossed configurations. This asks whether the present separation persists beyond the initial pair. Native observation must handle periodic boundaries before supporting quantitative population claims. A stable novel organism and a calibrated ecological score would then permit benefit assessment; the detailed design is in [the next-experiment plan](../docs/next-experiment.md).

H1 extends this comparison by sampling organisms from independently evolved populations and testing them, alongside matched ancestors, against a common held-out encounter panel. Higher beneficial-heritable-variant yield than matched ancestors under these shared conditions would locate an increase in transferable organism state. Population history supplies replication.

H3 crosses organisms and encounter distributions derived from undisturbed, structured-disturbance, and appropriately shuffled histories. Transplanting history-derived organisms into common encounters isolates the organism pathway; exposing shared organisms to history-specific encounters isolates the exposure pathway. Their cross identifies dependence between these contributions. In deterministic dynamics, history acts through present state and scheduled interventions: identical complete states and schedules have identical futures.

Together these experiments turn the title's question into comparisons with interpretable outcomes. Their common requirement is to follow variation from its production through transmission to ecological consequence. The present study establishes the first of those comparisons and shows why its stages cannot be collapsed into a single novelty count.

## Reproducibility and references

Protocols, configurations, complete starting grids, compact evidence, analyses, and figure-generation scripts are available at https://github.com/ReloadLightly/evoloop-levels. [Reproduction instructions](../docs/reproducing-results.md) link commands and evidence locations. Figures and their data provenance are indexed in [the figure manifest](../figures/manifest.json). Exact reference versions, licensing, and bibliographic caveats are documented in [the source review](../docs/source_review.md); verified bibliographic entries are in [references.bib](references.bib).


Sayama, H. (1999). A New Structurally Dissolvable Self-Reproducing Loop Evolving in a Simple Cellular Automata Space. *Artificial Life*, 5(4), 343–365. DOI: 10.1162/106454699568818.

Salzberg, C., and Sayama, H. (2004). Complex Genetic Evolution of Artificial Self-Replicators in Cellular Automata. *Complexity*, 10(2), 33–39. DOI: 10.1002/cplx.20060.

Salzberg, C., Antony, A., and Sayama, H. (2004). Evolutionary Dynamics of Cellular Automata-Based Self-Replicators in Hostile Environments. *BioSystems*, 78(1–3), 119–134. DOI: 10.1016/j.biosystems.2004.07.004.

Sayama, H., and Nehaniv, C. L. (2025). Self-Reproduction and Evolution in Cellular Automata: 25 Years After Evoloops. *Artificial Life*, 31(1), 81–95. DOI: 10.1162/artl_a_00451. Earlier version: arXiv:2402.03961v2 (2024).

Software sources: Luis M. Antunes, *CellPyLib* and its evoloop documentation (inspected 2026); Hiroki Sayama, *EvoLoopS*, version 1.0 (1999). Exact versions and source links are recorded in the bibliography and source review.
