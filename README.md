# Evoloop Levels

## Where Does Evolvability Reside? Organisms, Encounters, and Ecological History in Self-Reproducing Cellular Automata

### Abstract

Evolution depends on variation that survives reproduction. In evoloops, digital organisms reproduce within a cellular grid, and their encounters can change the structures they produce. We investigate how organisms, their partners, and ecological history contribute to useful heritable variation. An initial two-organism experiment produced candidate changes in six of 40 contacting configurations but no confirmed stable novelty, including after a delayed-extraction calibration. A fresh three-organism atlas now confirms pair-relative inherited novelty in **2/36 main configurations and 0/18 held-out configurations**, with no candidates in 90 controls. One successful configuration produces a word absent from all three inputs; the other recovers the third catalogue identity. Candidate rank reversals and inherited interaction contrasts do not transfer to held-out states. Ecological benefit remains unassessed.

![Recorded evoloop world, with cell states shown in the project's Chromatic Fields palette](figures/world-overview-dark.png)

*A recorded world from the exploratory simulation. Loops grow, reproduce, and encounter other structures under the same local rules. [Watch the simulation](figures/world-overview.webp). This overview illustrates the experimental system; the controlled comparisons are reported below.*

[Working paper](paper/manuscript.md) · [Paper PDF](paper/manuscript.pdf) · [Reproduce the results](docs/reproducing-results.md)

## Why study encounters?

An evoloop contains circulating signals that guide the construction of another loop. Reproduction takes place in the same space as other organisms, so a growing structure can meet a neighbour and produce a different outcome. The local update rules remain fixed while the organisms and their relationships change.

Sayama's original work established that this system supports heritable variation and natural selection [1]. Subsequent studies showed that genetic arrangements influence colony form and mutational biases, and that ecological conditions affect evolutionary dynamics [2, 3]. These findings raise a further experimental question: **when one organism produces more heritable variation than another, how much of that difference travels with the organism, and how much depends on whom it meets?**

We approach evolvability as the capacity to generate useful heritable variation under specified conditions. Measuring it requires connecting three observations: the appearance of a changed structure, the transmission of a changed identity through reproduction, and an advantage in a stated ecological task. The completed experiments examine the first two stages. A separate ecological comparison will assess whether confirmed variants improve persistence and recolonization. The distinction between replication and reproduction with inherited variation is developed in the recent review [4].

## Three linked research questions

The research programme separates contributions by changing one part of an encounter while holding another fixed. These contributions can coexist: an inherited property may be expressed only with certain partners, and ecological history may change both the property and the partners available.

| Question | Comparison | What the comparison would establish |
|---|---|---|
| **Organisms (H1): do evolved organisms retain an increased capacity under shared conditions?** | Compare organisms sampled from independently evolved populations with their ancestors in the same held-out encounter panel. | Whether evolved organisms retain higher beneficial-heritable-variant yield than their ancestors when partners and encounter conditions are shared. |
| **Encounters (H2): does a particular pairing matter?** | Exchange partners in a crossed design and compare outcomes across additional positions and reproduction phases. | Whether the effect of changing an organism depends on its partner, and whether that pattern transfers to new encounters. |
| **Ecological history (H3): how does the past shape future variation?** | Put history-derived organisms into common encounters, and common organisms into history-derived encounter distributions. | How historical effects are carried through inherited organism states, encounter opportunities, or their interaction. |

The present empirical study develops the encounter comparison and tests the inheritance of its candidate variants. The organism and history transplants extend this design to the other two questions. In this deterministic system, history acts through the states and conditions it produces; identical complete states with identical future interventions have identical futures.

## Experimental approach

We use the original synchronous, nine-state evoloop rules. The input organisms are **S13**, a documented seed, and **N01**, a stable descendant recovered through an exploratory sequence of isolation and reproduction. N01 gives us a second verified organism with which to exchange partners.

The encounter panel contains all four ordered S13/N01 pairings. Each pairing is tested in eight main configurations and two held-out configurations, varying relative geometry, orientation, and elapsed development time. All 40 nearby configurations make contact during the 1,600-update observation window. Another 40 configurations place the same inputs farther apart, and 24 grow the organisms alone. The separated controls use a larger grid; they test the declared no-contact conditions, rather than changing distance alone.

A candidate is a newly detected loop whose operational identity differs from both inputs. The recorded identity combines its circulating signal sequence and core dimensions. A subsequent reporting audit established that all seven candidate identities also differ in signal sequence; this stricter reading was added after the original definition was fixed.

To test inheritance, we move a complete separable structure, including its growing arms, into an empty world. We then follow detached descendants and require repeated transmission of a stable identity. A transient candidate can qualify by first producing a different, stable descendant. This intervention tests reproduction after separation from the encounter; it can also change the conditions a candidate needs to reproduce.

After the initial tests recovered no stable novel identity, a follow-up examined two explanations: candidates might need more time before extraction, or the initial search might miss a successful descendant. It therefore tested delays of 0, 60, 120, and 240 updates and compared the original search with a broader descendant search on identical eligible snapshots. Known S13 and N01 states served as positive controls.

The fresh comparison uses three distinct naturally generated channel identities, selected before their encounter outcomes were observed. Each input word survived stabilization and two further isolated transmissions. Nine ordered pairings are assessed in four main and two held-out configurations each, alongside matched separated and solitary controls. All 144 arenas share a 640×640 periodic domain; paired controls change only partner distance. Unlike the original atlas, this comparison prospectively screens for words different from both inputs and applies the broader descendant search with validated periodic recognition. The two atlases therefore have separate conditional endpoints.

## Results

### Encounters produced candidate variation

| Configuration group | Configurations observed | Configurations producing candidates |
|---|---:|---:|
| Contacting pairs | 40 | 6 |
| Separated pairs | 40 | 0 |
| Organisms alone | 24 | 0 |

The six contacting configurations produced seven candidate identities. Five configurations supplied 11 isolatable snapshots; the sixth supplied no separable candidate within the observation window. None of the 11 tested paths met the stable-inheritance criterion.

Candidate production also depended on which inputs were paired. However, the partner-dependent ranking in the main configurations changed in the held-out configurations:

| Focal organism × partner | Main configurations producing candidates | Held-out configurations producing candidates |
|---|---:|---:|
| S13 × S13 | 3/8 | 0/2 |
| S13 × N01 | 0/8 | 0/2 |
| N01 × S13 | 1/8 | 1/2 |
| N01 × N01 | 1/8 | 0/2 |

In the main panel, S13×S13 configurations produced candidates more often than N01×S13, whereas S13×N01 produced fewer than N01×N01. That reversal did not persist in the held-out panel, and neither panel yielded confirmed stable novel inheritance. The observed ranking therefore concerns candidate production in the main configurations, rather than a transferable ranking of evolvability.

![Crossed encounter outcomes](figures/outcome-matrix-dark.svg)

*Candidate production and confirmed inheritance are shown separately. Counts refer to the specified configurations, not independent evolutionary populations. [Complete encounter analysis](data/atlas/analysis.md).*

### More time and a broader search did not recover the tested candidates

The follow-up revisited all seven candidate identities at four delays, yielding 28 observations. Fifteen contained an eligible separable structure, ten had lost the tracked core, and three remained joined to other structures. The latter 13 observations could not enter the paired isolation comparison.

| Structures assessed | Eligible observations | Stable novel identity: original search | Stable novel identity: broader search |
|---|---:|---:|---:|
| Encounter candidates | 15 of 28 | 0/15 | 0/15 |

For the positive controls, the endpoint was recovery of the **original** identity. Both searches recovered it in **8/8 states**: two known organisms assessed at four delays each.

![Paired inheritance tests for candidate and known-organism states](figures/fate-calibration-matrix-dark.svg)

*The two searches assess the same extracted structures. Delay observations revisit candidates from six originating configurations; they are not independent populations. [Complete follow-up analysis](data/fate-calibration/analysis.md).*

### Fresh encounters recover two stable pair-relative outcomes

A frozen discovery schedule has now verified three distinct naturally generated channel identities. V01 is the reverified N01 word. The native sources of V02 and V03 were first observed in an N01×N01 history at sampled updates 3,440 and 5,040, then each stabilized from a 12×14 to a 13×13 core while transmitting its changed word through two further isolated generations. The two new identities share core dimensions but carry different channel words.

All 79 verification trials are retained: three identities passed, 74 remained unresolved or changed identity during the transmission chain, and two reproduced a word different from their native source. These selected trials assemble inputs; they do not estimate encounter yield or provide independent population histories. The completed fresh atlas has 144 distinct starting states: 54 near configurations, 54 separated controls, and 36 solitary controls. All near configurations contact; none of the separated controls do.

![Native discovery histories](figures/panel2-native-worlds-dark.svg)

*Recorded cell states under the unchanged rule; isolation verification supplies the viable input identities. [Discovery protocol](protocols/005-natural-panel-discovery.md) and [complete evidence](data/panel-v2/discovery.json).*

| Fresh panel | Candidate-producing configurations | Confirmed pair-relative inheritance |
|---|---:|---:|
| Main encounters | 14/36 | 2/36 |
| Held-out encounters | 4/18 | 0/18 |
| Separated controls | 0/54 | 0/54 |
| Solitary controls | 0/36 | 0/36 |

The successful states are V01×V03 and V02×V03 in the parallel geometry at offset 20. V01×V03 yields a 14×14 stable identity whose word differs from all three catalogue inputs. V02×V03 recovers V01's known 12×12 identity, which differs from its two inputs and qualifies under the frozen pair-relative definition. Thus supplementary catalogue-relative yield is 1/36 main and 0/18 held out. Both stable words are observed natively and transmit repeatedly after isolation; parentage within the original pair remains ambiguous.

![Recorded transmission paths from successful encounters](figures/atlas2-inheritance-path-dark.svg)

*Transient candidates, complete extracted components, and stable isolated descendants from actual recorded states. Eight successful roots converge on two identities from two configurations; they are not eight independent events. [Fresh encounter analysis](data/atlas-v2/analysis.md), [joined outcomes](data/atlas-v2/outcomes.csv), and [independent interpretation audit](docs/scientific_review.md).*

![Fresh focal-by-partner outcome matrix](figures/atlas2-outcome-matrix-dark.svg)

*Candidate and inherited outcomes retain every declared configuration in their denominators. Main candidate rank reversals do not persist held out; inherited main differences also disappear held out. [Candidate, inheritance, and pending-benefit stages](figures/atlas2-evidence-stages-dark.svg) and [annotated replay](figures/atlas2-encounter-1.webp).*

The isolation search evaluates 88 roots from 52 run/composite candidate identities, executing 1,205 generation simulations. Six identities have no extractable phase. Simulation-budget and depth limits leave 158 recorded truncations, and 441 nodes reach the three-offspring collection cap. Unrecovered candidates and later branches remain unresolved. No benefit comparison has been run; beneficial-heritable-variant yield is unknown.

## What these findings mean

The completed comparisons separate candidate production from stable transmission. The original negative result persists under its specified maturation and search extensions; the fresh atlas supplies two positive configurations, including a transient-to-stable route carrying a word absent from the catalogue. Success after isolation demonstrates heritable variation under that imposed assay. It does not establish native ancestry or ecological advantage.

The atlases differ in organism inputs, arena extent, candidate screening, periodic measurement, and descendant search. Their different yields therefore cannot be attributed to enrichment of the organism panel alone. The same-size V02/V03 comparison holds core dimensions fixed, while words, arms, complete states, and developmental timing still vary. All three fresh identities are related selected descendants, not independent population histories.

The next experiment will calibrate the ecological population score and execute the frozen paired disturbance assay for both confirmed identities against both originating inputs. It measures persistence and recolonization; increasing that score alone would not demonstrate recursive self-improvement. The [experimental extension](docs/next-experiment.md) retains independent organism and ecological-history transplants for H1 and H3, which remain untested.

The longer-term question is whether evolutionary change alters the capacity for further adaptive change. The route to answering it is to measure the production, transmission, and ecological consequences of variation together, then determine which differences transfer with organisms and which depend on their encounters.

## Reproduce and explore

The repository includes complete starting states, compact outcome data, experiment protocols, analysis scripts, and figure sources. [Reproduction instructions](docs/reproducing-results.md) cover installation, analysis, replay, and fresh runs. The [working paper](paper/manuscript.md) gives the full methods and interpretation; [source notes](docs/source_review.md) document the model and literature.

Visualizations use one shared [Chromatic Fields / Midnight Blue configuration](configs/style.json): dark navy, blue typography, and blue quantitative scales. The nine literal cell states retain a fixed, labelled categorical palette; missing measurements use neutral hatching. [Fresh encounter replays](figures/atlas2-encounter-1.webp), [confirmed inheritance paths](figures/atlas2-inheritance-path-dark.svg), [the original exploratory path](figures/inheritance-path-dark.svg), and [raw-state comparisons](figures/fate-raw-comparison-dark.svg) make individual events inspectable. The [figure manifest](figures/manifest.json) links each image to its evidence and regeneration command.

## References

1. Sayama, H. (1999). *A New Structurally Dissolvable Self-Reproducing Loop Evolving in a Simple Cellular Automata Space*. Artificial Life, 5(4), 343–365. [Paper](https://bingdev.binghamton.edu/sayama/papers/ALIFE5-4-343.pdf).
2. Salzberg, C., & Sayama, H. (2004). *Complex Genetic Evolution of Artificial Self-Replicators in Cellular Automata*. Complexity, 10(2), 33–39. [Paper](https://bingdev.binghamton.edu/sayama/papers/Complexity-preprint.pdf).
3. Salzberg, C., Antony, A., & Sayama, H. (2004). *Evolutionary Dynamics of Cellular Automata-Based Self-Replicators in Hostile Environments*. BioSystems, 78(1–3), 119–134. [Paper](https://bingdev.binghamton.edu/sayama/papers/BioSystems-preprint.pdf).
4. Sayama, H., & Nehaniv, C. L. (2025). *Self-Reproduction and Evolution in Cellular Automata: 25 Years After Evoloops*. Artificial Life, 31(1), 81–95. [Preprint](https://arxiv.org/abs/2402.03961v2).
