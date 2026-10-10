# Where Does Evolvability Reside? Organisms, Encounters, and Ecological History in Self-Reproducing Cellular Automata

**An encounter experiment separating the production of candidate variants from their stable transmission**

## Abstract

Encounters can generate new forms; heritable variation requires transmission of their differences. We investigate these stages in evoloops, a deterministic cellular automaton in which interacting reproductive structures can alter descendants. An initial two-organism atlas produced candidate changes in six of 40 contacting configurations, with none in 64 controls and no confirmed stable novelty. A delayed-extraction calibration likewise recovered no stable candidate novelty, while recovering known organisms in all eight positive-control states. A subsequent prospective atlas crossed three naturally generated, separately verified identities across 54 contacting configurations and 90 controls. Candidate words appeared in 14/36 main and 4/18 held-out configurations. Serial isolation confirmed pair-relative inherited novelty in two main configurations and none held out. One produced a stable word absent from all three inputs; the other recovered the third catalogue identity, absent from its input pair. Eight successful extraction roots converged on these two outcomes. Main-panel candidate rank reversals and inherited interaction contrasts did not transfer to held-out configurations. The positive and negative atlases differ in inputs, arena size, screening, and search, preventing a causal attribution of their yield difference. Ecological benefit remains unassessed. These results distinguish variation production, stable transmission, and adaptive value while bounding claims about partner-dependent evolvability.

## 1. Introduction

A system's capacity for evolutionary change depends on more than producing new forms. For adaptive evolution, differences must pass to descendants and improve performance in a relevant environment. Separating these steps is particularly important when reproduction itself depends on interactions: an encounter may create a novel structure, help it reproduce, or destroy it before its differences can persist.

Evoloops make these possibilities observable. They are self-reproducing structures embedded in a two-dimensional cellular automaton. A circulating signal sequence participates in constructing offspring, while contact between reproductive structures can change the sequence and shape of the resulting loops. All events follow fixed local rules (Sayama, 1999). The model therefore lets us intervene on encounters without inserting a separate mutation operator.

Where, then, does the capacity to generate heritable variation reside? An organism may carry a transferable bias in the variants it produces. That bias may be expressed differently against different partners. Previous ecological conditions may shape both the organisms present and the encounters they experience. These are compatible contributions, whose identification requires different comparisons. We organize them as three hypotheses: **H1**, a contribution transferable with the organism under common encounter conditions; **H2**, a contribution specific to organism–partner combinations; and **H3**, historical effects mediated by changes in organisms and encounter distributions.

The present experiments address the encounter comparison. We first cross two input organisms across a defined spatial panel, then follow candidate variants through isolation and repeated reproduction. Crossing partners asks whether the outcome associated with changing one organism depends on the other. Following descendants asks whether any such pattern concerns temporary structural changes or transmitted variation. A calibration examines whether early extraction or restricted descendant search explains failed transmission. A fresh crossed atlas then uses three naturally generated, separately verified inherited identities, new configurations, and the calibrated descendant search to examine how far the original result depends on its input panel.

The completed studies recover both negative and positive transmission outcomes. The original candidates did not yield confirmed stable novelty under either calibrated search, whereas two configurations in the fresh atlas did. One produces a word absent from the input catalogue; the other recovers a known catalogue word absent from its input pair. Neither result transfers as an inherited-yield difference to the held-out configurations. Together they establish what subsequent organism and history comparisons must measure: variation production, transmission, and ecological benefit as separate stages, with novelty defined relative to a declared comparison set.

## 2. Prior work and the experimental question

Sayama's original evoloop establishes interaction-mediated genotype change and spatial selection in deterministic, synchronous nine-state dynamics (Sayama, 1999). Later work shows that loops of the same size can differ in gene arrangement, colony morphology, persistence, and mutational bias. Salzberg and Sayama report round-robin competition among 15 size-4 genotypes and descendants inheriting variation biases (Salzberg and Sayama, 2004). These findings already connect inherited organization with evolutionary outcomes.

Salzberg, Antony, and Sayama examine genealogy, biased accessibility of larger species, pathogens, and localized or distributed disturbances (Salzberg, Antony, and Sayama, 2004). They also retain transient species that produce stable replicators in a later cycle. A failure to copy the first observed candidate immediately is therefore insufficient grounds for discarding its evolutionary potential. The recent review places these mechanisms within the broader problem of reproduction supporting inherited variation and discusses persistent questions of individuality and long-term evolution (Sayama and Nehaniv, 2025; preprint 2024).

Our experiment builds on these results by comparing the fate of variation under specified encounters. Population competition measures which types persist; here the immediate outcome is whether a particular encounter produces a new identity with a recoverable transmission path. Retaining nonproductive encounters supplies the denominator, while isolation tests and delayed extraction distinguish candidate appearance from later reproduction. The contribution is this intervention-and-measurement comparison, rather than the discovery of interaction-generated mutation or inherited mutational bias.

## 3. Methods

### 3.1 Dynamics and organisms

We use the original nine-state evoloop transition system, synchronous updates, and periodic boundaries. The neighborhood is center, top, right, bottom, left; rotations of explicit rules and the dissolution/default rules produce all 59,049 local transitions. The lookup table agrees exhaustively with the pinned CellPyLib reference and an independent expansion of the author's EvoLoopS rules (Antunes, CellPyLib; Sayama, EvoLoopS). Seed reproduction, deterministic replay, and checkpoint/resume are verified. Exact versions, hashes, licensing, and execution details are documented in [source review](../docs/source_review.md) and [reproduction instructions](../docs/reproducing-results.md).

S13 is CellPyLib's documented species13 seed, matching the author's `13.img`, rather than the alternative default `13-2.img` (Antunes, CellPyLib documentation). N01 is a stable descendant obtained from a 160×160 exploratory torus initiated with S13 at (65,45). Discovery samples every ten updates, considers up to four detached phases per candidate, and ends after two verified identities. This selected exploratory history supplies an experimental input; it is not replication across independently evolved populations.

A prospective discovery schedule (protocol 005) supplies the fresh extension with three naturally generated channel identities. It reverifies the original native N01 component, then searches three declared histories: the original 160-square S13 ecology to 12,000 updates, an S13/N01 encounter in 320-square space to 16,000, and an N01/N01 encounter in 320-square space to 16,000 or the three-identity stopping point. Sampling is every 20 updates, with at most two complete-component hashes per source composite identity and 32 verification trials per history. The first detached offspring must transmit its composite identity in two further isolated generations, and its word must equal the native source word. Selection also requires one unchanged core at elapsed offsets 20, 50, 80. Third detached descendants supply uniform input snapshots. Discovery selects on provenance and reproduction before viewing encounter outcomes; it is not independent-population replication.

### 3.2 Crossed encounters and controls

Before acquisition, protocol 001 specifies 32 main encounters, eight held-out encounters, and controls. Complete input snapshots advance alone by 0, 30, or 60 updates. Each resulting state must retain one recognized core, unchanged identity, and no boundary contact. These offsets refer to different snapshot origins; they are not necessarily homologous reproductive phases.

All four ordered S13/N01 pairings are tested against four main geometries at offsets 0 and 60, giving eight configurations per pair. Two held-out geometries at offset 30 give two further configurations per pair. Near configurations occupy 384×384 tori, with specified positions, rotations in 90-degree increments, and nonoverlapping input rectangles. Forty separated controls retain identities, offsets, orientations, and row displacement in 640×640 tori, with horizontal displacement of 320 cells. Twenty-four solitary controls cover organism, offset, and orientation. Every configuration runs for 1,600 completed updates; separated controls are checked for contact throughout.

The fresh protocol 006 defines nine ordered V01/V02/V03 pairings, four main configurations per pair at offsets 20/80, and two held-out configurations per pair at offset 50. Complete phase snapshots, relative displacements, and rotations differ from the original panel. All 144 near, separated, and solitary arenas use the same 640-square periodic domain. The 54 paired separated controls change only horizontal partner displacement; 36 solitary states cover each organism, offset, and orientation. The panel and its complete starting states were frozen before acquisition. Main and held-out configurations use different phases, orientations, and offsets; each is a specified finite panel rather than a random sample of encounters.

### 3.3 What counts as a variant?

A structural detector samples rectangular zero-valued cores with intact inner sheaths in states 2/3 every ten updates. For channels containing only states 0/1/4/7, we read a clockwise signal word, preserving carrier spacing and normalizing by cyclic shift without reflection. Pairing this word with sorted core dimensions defines the operational composite identity. It preserves chirality but differs from the published counterclockwise, birth-anchored species identifier (Salzberg, Antony, and Sayama, 2004). Contaminated channels have unknown identity; recognized cores alone do not establish viability.

In the original atlas, a candidate composite identity must differ from both encounter inputs. A reporting audit introduced during acquisition, before inheritance analysis, additionally distinguishes signal-word novelty from shape-only differences. That composite endpoint remains the frozen primary definition; word-only novelty is a separately labeled, post-hoc sensitivity endpoint (protocol 002). The fresh atlas prospectively screens for a native signal word different from both inputs and records morphology-only changes separately. A candidate may match the third catalogue identity: novelty here is relative to the input pair, not global sequence novelty. This narrower screen leaves morphology-only routes to later word changes outside the inheritance endpoint.

Occupied input cells receive provenance masks 1 and 2; newly occupied cells inherit the union of occupied contributors in their neighborhood. Contact is the first update containing exclusive-provenance adjacency or mixed occupied provenance. These masks overapproximate causal contribution and do not identify genetic parents. After contact, novelty is consequently a pair-level outcome.

Core coordinates track structures. Appearances and losses are interval-censored within ten updates; reported candidate times are first sampled observations, not exact mutation or birth times. A changed word at an existing core can be registered without a new-core appearance event. The legacy detector does not join structures across the torus seam, so boundary contact limits the earlier native counts. The fresh atlas uses independently validated periodic recognition: four cuts cover cores whose six-cell padded bounding dimensions are smaller than half each domain dimension, occupied components are joined across seams, and a single-core component is unwrapped only when an empty row and column allow its complete extent to be retained. Winding and multicore components remain ineligible. Nonrectangular structures can escape either detector. Structure persistence, lineage survival, candidate novelty, inheritance, and benefit remain distinct measurements.

### 3.4 Testing transmission after isolation

The initial assay extracts the entire occupied connected component, including reproductive arms, if it contains exactly one recognized core and avoids the boundary. It places the component in an empty 192×192 torus. Shared, boundary-spanning, and oversized components are ineligible. The earliest two distinct extractable snapshots per run/identity define the search budget; size checks occur after capture, so oversized attempts consume that budget and remain unresolved.

Each generation runs for up to 1,600 updates. In the first legacy stage, the first newly positioned, valid closed core with a detached component supplies the next isolated generation. Later legacy stages select the first detached core matching the proposed stable composite identity, skipping other identities; the expanded search instead retains alternate valid descendants. A candidate may first produce a different stable descendant. That descendant must transmit the same identity twice consecutively, requiring an additional generation when the original candidate was transient. Closure and detachment are recorded separately. Stable identities first arising after extraction are labeled assay-derived and checked again against both inputs.

A path without qualifying reproduction by the horizon is unresolved; an empty grid is extinction under isolation. Either outcome can coexist with an unexamined successful path or ecological dependence. Complete-component extraction preserves active arms, avoiding the disruption caused by cropping only the central body.

### 3.5 Delayed extraction and expanded descendant search

Protocol 004 tests whether maturation or a broader search recovers inheritance missed by the initial assay. It follows all seven candidate identities, nested within six originating configurations. At first observation, the lexicographically first matching core tuple fixes the target. No later successful structure may replace a lost target. Verified S13 and N01 snapshots in empty 384×384 worlds provide positive controls.

Extraction occurs after 0, 60, 120, or 240 updates: 28 candidate-delay and eight control observations. Ten-update tracking distinguishes target loss and subsequent same-tuple recurrence. Lost, recurrent, unknown, shared, boundary, and oversized targets are ineligible. Each delayed world also continues natively for 1,600 updates. Matching words elsewhere are structural observations; they do not establish offspring ancestry. These continuation windows overlap and are not independent observations.

Every eligible component enters both the unchanged legacy assay and an expanded search. The expanded search collects the first three detached, newly positioned valid cores per generation, once per core tuple, ordered by time, coordinates, and snapshot hash. This is the operational offspring criterion; a core appearance event alone is not sufficient. Depth-first traversal permits at most six simulated generations along a path and 24 generation simulations per root, each lasting at most 1,600 updates. Identity changes reset the transmission streak. Two identical consecutive transmissions confirm stability. Candidate recovery requires a stable signal word different from both inputs; control recovery requires the original composite identity.

Comparing searches on the same snapshot isolates search sensitivity. Comparing delays combines maturation with continued ecological interaction. Ineligible extractions and unexamined branches remain explicit.

The fresh atlas applies the same expanded search budgets with periodic recognition to the earliest two distinct complete-component snapshots per run/composite candidate identity. Stable transmission requires two consecutive identical composite identities and a stable word different from both inputs. Transients may produce another stable identity. Size-ineligible snapshots consume an attempt; missing components and capped paths remain unresolved. Native appearance, isolated transmission, and ecological dependence are separate outcomes.

### 3.6 Analysis and ecological benefit

The original primary endpoint is any confirmed novel stable composite identity per near configuration; the fresh primary endpoint is any confirmed stable word different from both inputs, conditional on its prospective native-word screen. Each retains all declared near states in its denominator: 40 in the original atlas and 54 in the fresh atlas. Rates are reported separately because the panels and candidate screens differ. Catalogue-relative novelty is a supplementary description, not a replacement for the pair-relative endpoint. Candidate and unresolved outcomes are reported separately. For each main or held-out panel, an interaction contrast is a difference of differences; the original two-input comparison is:

`[rate(S13,S13) − rate(N01,S13)] − [rate(S13,N01) − rate(N01,N01)]`.

This measures pair-configuration interaction under ambiguous parentage, rather than an identified focal mutation capacity. The configurations form a specified finite panel, not a random sample from a natural encounter distribution. Deterministic reruns verify reproducibility. Accordingly, we report descriptive contrasts without binomial intervals or inferential p-values. Held-out geometries assess configuration transfer; they do not supply independent organisms or evolutionary histories. For the three-input atlas we report focal and partner marginal means, residuals from their additive decomposition, and all nine contrasts obtained by choosing two focal identities and two partner identities. A strict rank reversal requires opposing, nonzero focal contrasts across partners; persistence requires the same two signs in the held-out panel. These analyses concern pair-level outcomes because provenance does not resolve genetic parentage.

A prospectively specified benefit assay would compare an inheritance-confirmed candidate with both inputs in 192×192 tori over 1,600 updates, removing a 24×24 block at updates 600 and 1,000. The proposed score is mean intact-core population of isolation-confirmed identities, sampled every 20 updates, under two development and two independent confirmation schedules. Success requires exceeding both inputs' means in both panels. Viability calibration is necessary because intact cores can be doomed. These comparisons have not been completed; beneficial-heritable yield is therefore unknown. The present results concern production and transmission.

## 4. Results

### 4.1 A transient structure supplies an inherited input variant

In discovery, a candidate first observed at update 2,910 had an 11×13 core and a signal word different from S13. Isolation yielded a 12×12-core descendant, followed by two generations transmitting that stable identity. Detachment was first observed after 380, 390, and 390 updates in the successive assays, at ten-update resolution. N01 denotes the stable descendant. The transient and stable forms share the changed word, distinguishing morphological stabilization from signal change. This observed route motivates allowing transient-to-stable paths in encounter assays.

The prospective discovery reached three eligible identities in 79 selected native-component trials: the original N01 source and 78 new trials. V01 is the reverified N01 word; The native sources of V02 and V03 were first observed in the N01/N01 history at updates 3,440 and 5,040, sampled every 20 updates. Each retains its native word while stabilizing from a 12×14 to a 13×13 core under isolation. Their stable words differ from one another and from V01. Seventy-four trials were unresolved or changed identity before completing the declared transmission chain; two recovered stable words different from their native source and were therefore rejected. These counts describe input selection, not encounter yields.

| Input | Native history, time | Native → stable core | Detachment times |
|---|---|---|---|
| V01 | Original discovery,2910 | 11×13 →12×12 | 380,390,390 |
| V02 | N01/N01,3440 | 12×14 →13×13 | 430,410,420 |
| V03 | N01/N01,5040 | 12×14 →13×13 | 410,420,410 |

Times are updates from each isolated generation's start, sampled every 10. Both new identities come from the same history and are separately verified, not independently evolved population replicates. These positive transmission paths broaden the input panel and show that the earlier negative encounter result does not amount to a general inability of transients to stabilize.

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

### 4.4 A fresh panel recovers two pair-relative inherited outcomes

EXP-atlas-002 completed all 144 frozen states. Contact occurred in all 36 main and 18 held-out near configurations, at updates 151–990 and 251–1,090 respectively. None of the 54 separated controls contacted. Native candidate words occurred in 14/36 main and 4/18 held-out states, compared with 0/54 separated and 0/36 solitary states. No morphology-only changed identities were observed in near states. The paired near-minus-separated candidate contrast is 18/54, or 0.333.

| Pair | Candidates: main | Candidates: held-out | Inherited: main | Inherited: held-out |
|---|---:|---:|---:|---:|
| V01 × V01 | 1/4 | 0/2 | 0/4 | 0/2 |
| V01 × V02 | 2/4 | 0/2 | 0/4 | 0/2 |
| V01 × V03 | 2/4 | 0/2 | 1/4 | 0/2 |
| V02 × V01 | 2/4 | 1/2 | 0/4 | 0/2 |
| V02 × V02 | 0/4 | 0/2 | 0/4 | 0/2 |
| V02 × V03 | 2/4 | 1/2 | 1/4 | 0/2 |
| V03 × V01 | 1/4 | 1/2 | 0/4 | 0/2 |
| V03 × V02 | 2/4 | 0/2 | 0/4 | 0/2 |
| V03 × V03 | 2/4 | 1/2 | 0/4 | 0/2 |

Bounded serial isolation confirms pair-relative inherited novelty in **2/36 main configurations and 0/18 held-out configurations**. Combined yield is 2/54, or 0.037, conditional on this panel, horizon, screen, and search. Fourteen main and four held-out candidate-producing states supply 52 run/composite identities and 88 extraction roots. Eight roots confirm the endpoint, but they converge on two stable identities from two configurations; they are not eight independent inherited events. Six candidate identities lack an extractable phase. The other 16 candidate-producing configurations remain unresolved for stable novel inheritance under the bounded search.

Both successful configurations use the parallel geometry at elapsed offset 20. In `near-main-V01-V03-p20-a-parallel`, contact begins at update 224. A 13×15-core candidate observed at 1,110 produces a 14×14-core isolated descendant, followed by two transmissions first observed after 440 updates each. Its stable word equals the native candidate word and differs from all three catalogue words. A matching 14×14 composite identity appears natively at 1,550 and also reproduces twice after extraction. Roots captured ten updates apart converge on identical later snapshots. This is one configuration with a stable word absent from the catalogue, giving supplementary catalogue-relative yield 1/36 main and 0/18 held out.

In `near-main-V02-V03-p20-a-parallel`, contact begins at update 233. A 12×13 candidate at 460 produces a different word in a 12×12 isolated descendant, which transmits twice, first observed after 390 updates in each generation. The stable identity exactly matches **V01**. That word is absent from V02 and V03 and therefore satisfies the frozen pair-relative endpoint; it is a recovery of an existing catalogue identity. V01's word also appears natively at 860 in a 12×12 core and reproduces after extraction. Its native appearance does not assign ancestry to the earlier candidate. The changed-word transition along the 460 extraction path occurs in the imposed isolation assay; the stable-word native observations and their own isolation tests provide separate evidence.

![Two recorded routes to stable transmission](../figures/atlas2-inheritance-path-dark.svg)

*Each row shows one complete captured component and its recorded isolated descendants from a successful configuration. Multiple extraction roots within each encounter converge on the same stable identity; they are not independent encounter outcomes. Sources and regeneration commands are in the figure manifest.*

The expanded search executes 1,205 generation simulations. It records 134 simulation-budget and 24 depth-limit truncations; 441 nodes reach the three-offspring collection cap. Later branches, unsampled phases, and ecological dependence remain unexamined. Edge activity occurs in 73/144 native arenas; the fresh periodic detector handles validated small rectangular bodies and contractible single-core components, while large, nonrectangular, winding, and shared structures remain outside the confirmed extraction scope.

Main-panel candidate contrasts show two strict focal rank reversals. For V01 minus V02, the contrasts are −0.250 against V01 and +0.500 against V02, producing a difference of differences of −0.750. For the same-size V02 minus V03 comparison, the contrasts are +0.250 and −0.500, producing +0.750. Neither strict reversal persists held out. Inherited main contrasts compare V01 or V02 against V03: changing from a V01 or V02 partner to V03 changes the focal contrast from zero to +0.250, giving a difference of differences of −0.250. All held-out inherited contrasts are zero, and neither split contains an inherited strict rank reversal. These are descriptive pair-configuration interactions; the concentration of successes in the V03 partner column alone would not establish H2. Benefit assays remain pending.

## 5. Discussion

### 5.1 Production and transmission require separate explanations

The encounter comparison identifies configurations that produce changed signal words; the inheritance comparison asks whether those changes persist through repeated reproduction. The original atlas and calibration show divergence between these measurements; the fresh atlas recovers stable transmission in two configurations. Treating candidate counts as evolvability would nevertheless give the main-panel reversals a generality that neither atlas supports on held-out configurations. Confirmed transmission also distinguishes a word absent from the catalogue from recovery of a known third identity. Neither is yet shown to be beneficial.

The calibration addresses two specific explanations for the negative inheritance result. Allowing the prescribed maturation delays and following additional detached descendants did not recover a stable novel path. Successful recovery of S13 and N01 shows that both searches can extract and transmit those tested identities at those delays. It makes a blanket explanation that the assay never recovers reproducing loops incompatible with the controls. It does not establish sensitivity for every altered phenotype. Candidate-specific extraction damage, ecological assistance, later offspring, and longer transient sequences remain possible.

The discovery path supplies a useful contrast: a transient structure did produce stable novelty under complete-component isolation. It demonstrates a route accommodated by the method, while its exploratory selection prevents using it to estimate encounter-wide success. The fresh positive paths further demonstrate that transient candidates can lead to stably transmitting organisms. The current evidence supports conditional variation in production and recovered inheritance, while leaving ecological value unmeasured.

### 5.2 Scope of the causal comparison

The original two-organism panel contains one selected descendant from one history. Signal word, shape, arms, and reproductive phase can covary; a pair effect cannot be assigned solely to a gene sequence. Equal observation horizons also permit unequal time after contact. Separated controls change world extent as well as distance, limiting interpretation to the declared configurations. The fresh controls hold arena extent fixed. V02 and V03 have the same 13×13 core dimensions, giving a comparison at common core size, but arms, signal words, complete states, and developmental timing still vary. All three fresh inputs are related, selected descendants; two derive from the same discovery history.

Isolation deliberately changes the environment and can disrupt or stabilize reproduction. Fixed-core tracking excludes lost or reshaped targets and their possible descendants. The three-offspring cap, ineligible phases, finite horizons, rectangular detector, and seam-crossing failures bound the searched paths. Negative outcomes identify what was not recovered under specified interventions, while positive outcomes identify the particular paths those interventions recover. Successful roots stop at their first accepted identity, so the search does not exhaust the number or diversity of viable variants within a productive encounter.

### 5.3 Connecting encounters, organisms, and history

The fresh atlas broadens the verified input panel and recovers positive paths under its declared endpoint. Its higher observed yield cannot be attributed to panel enrichment alone: inputs, domain size, native screening, periodic measurement, and descendant search differ from the original atlas. It is a new conditional comparison, not a controlled estimate of the effect of changing any one of those factors. No stable-yield contrast transfers to the fresh held-out states.

The next informative experiment calibrates the ecological population score, then executes the already frozen paired benefit conditions for both confirmed identities against both originating inputs. The word absent from the catalogue is compared with V01/V03; the recovered V01 identity with V02/V03. This asks whether stable pair-relative changes improve persistence and recolonization under specified disturbances. An advantage under the calibrated assay would establish improved persistence and recolonization, not by itself evolution of the capacity for further adaptive change or recursive self-improvement. The detailed plan is in [the next-experiment plan](../docs/next-experiment.md).

H1 extends this comparison by sampling organisms from independently evolved populations and testing them, alongside matched ancestors, against a common held-out encounter panel. Higher beneficial-heritable-variant yield than matched ancestors under these shared conditions would locate an increase in transferable organism state. Population history supplies replication.

H3 crosses organisms and encounter distributions derived from undisturbed, structured-disturbance, and appropriately shuffled histories. Transplanting history-derived organisms into common encounters isolates the organism pathway; exposing shared organisms to history-specific encounters isolates the exposure pathway. Their cross identifies dependence between these contributions. In deterministic dynamics, history acts through present state and scheduled interventions: identical complete states and schedules have identical futures.

Together these experiments turn the title's question into comparisons with interpretable outcomes. Their common requirement is to follow variation from its production through transmission to ecological consequence. The present study executes the encounter and transmission comparisons, recovers two pair-relative inherited outcomes, and shows why production, transmission, and benefit cannot be collapsed into a single novelty count. H1 and H3 remain untested; no evidence of recursive self-improvement is claimed.

## Reproducibility and references

Protocols, configurations, complete starting grids, compact evidence, analyses, and figure-generation scripts are available at https://github.com/ReloadLightly/evoloop-levels. [Reproduction instructions](../docs/reproducing-results.md) link commands and evidence locations. Figures and their data provenance are indexed in [the figure manifest](../figures/manifest.json). Exact reference versions, licensing, and bibliographic caveats are documented in [the source review](../docs/source_review.md); verified bibliographic entries are in [references.bib](references.bib).


Sayama, H. (1999). A New Structurally Dissolvable Self-Reproducing Loop Evolving in a Simple Cellular Automata Space. *Artificial Life*, 5(4), 343–365. DOI: 10.1162/106454699568818.

Salzberg, C., and Sayama, H. (2004). Complex Genetic Evolution of Artificial Self-Replicators in Cellular Automata. *Complexity*, 10(2), 33–39. DOI: 10.1002/cplx.20060.

Salzberg, C., Antony, A., and Sayama, H. (2004). Evolutionary Dynamics of Cellular Automata-Based Self-Replicators in Hostile Environments. *BioSystems*, 78(1–3), 119–134. DOI: 10.1016/j.biosystems.2004.07.004.

Sayama, H., and Nehaniv, C. L. (2025). Self-Reproduction and Evolution in Cellular Automata: 25 Years After Evoloops. *Artificial Life*, 31(1), 81–95. DOI: 10.1162/artl_a_00451. Earlier version: arXiv:2402.03961v2 (2024).

Software sources: Luis M. Antunes, *CellPyLib* and its evoloop documentation (inspected 2026); Hiroki Sayama, *EvoLoopS*, version 1.0 (1999). Exact versions and source links are recorded in the bibliography and source review.
