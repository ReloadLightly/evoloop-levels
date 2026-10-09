# Primary-source verification and contribution limits

Verified 2026-10-10. Papers were inspected from primary author-hosted PDFs in a temporary directory; this repository links them and does not redistribute them. The review was also checked against its arXiv version record and the final publisher record. This is a targeted foundation review, not a claim of an exhaustive literature search.

## Bibliographic checks

| Source | Verified citation and version | Metadata caveat |
|---|---|---|
| [Original evoloop paper](https://bingdev.binghamton.edu/sayama/papers/ALIFE5-4-343.pdf) | Hiroki Sayama (1999), *Artificial Life* 5(4):343–365, [DOI 10.1162/106454699568818](https://doi.org/10.1162/106454699568818); 23-page journal PDF | Copyright line says 2000; bibliographic issue is 1999. |
| [Complexity preprint](https://bingdev.binghamton.edu/sayama/papers/Complexity-preprint.pdf) | Chris Salzberg and Hiroki Sayama (2004), *Complexity* 10(2):33–39, [DOI 10.1002/cplx.20060](https://onlinelibrary.wiley.com/doi/abs/10.1002/cplx.20060); 12-page author preprint | Publisher first-publication date 21 December 2004. |
| [BioSystems preprint](https://bingdev.binghamton.edu/sayama/papers/BioSystems-preprint.pdf) | Chris Salzberg, Antony Antony, and Hiroki Sayama (2004), *BioSystems* 78(1–3):119–134, [DOI 10.1016/j.biosystems.2004.07.004](https://www.sciencedirect.com/science/article/abs/pii/S0303264704001388); 29-page author preprint | PDF title page dated 8 January 2005; published issue December 2004. Do not change citation year to 2005. |
| [Review requested by the protocol](https://arxiv.org/abs/2402.03961v2) | Hiroki Sayama and Chrystopher L. Nehaniv, arXiv:2402.03961, v1 6 February 2024, v2 8 June 2024; 21 pages | v2 PDF internal date 11 June 2024. Experimental HTML displays a later generated date; use arXiv submission history for version provenance. |
| [Final review publication](https://direct.mit.edu/artl/article/31/1/81/124368/Self-Reproduction-and-Evolution-in-Cellular) | *Artificial Life* **31(1):81–95 (2025)**, DOI 10.1162/artl_a_00451 | Publisher says 25 February 2025 and copyright 2024. Crossref's print date is inconsistent (2024), while online date and issue year are 2025. Use publisher issue year. |

## What is already known

The original paper demonstrates collision-mediated genotype changes and selection for smaller, faster loops under deterministic synchronous nine-state rules. Its plate 2 shows arm takeover; plate 5 illustrates a collision producing a smaller organism. Sections 3.8–3.9 distinguish seed genotypes and include rectangular or transient structures. The paper's appendix gives the principal CTRBL rules, rotation completion, dissolution rules, and defaults; the full-scale experiments use periodic boundaries. Thus interaction-generated variation and an evolving population are foundations, not prospective discoveries here. [Sayama 1999](https://bingdev.binghamton.edu/sayama/papers/ALIFE5-4-343.pdf).

The Complexity paper goes beyond size reduction: genetic identities differ at a common loop size, colony morphology and mutation bias depend on gene arrangement, and population density and persistence can improve through evolution. It explicitly reports a **round-robin competition among all 15 size-4 species**, estimating relative population ratios after competition and averaging over competitors. It identifies conserved subsequences, investigates deliberately modified starting genotypes, and reports descendants generally inheriting mutational biases. Therefore, neither crossed competitors, inherited bias, same-size adaptation, nor an ecological extended phenotype is novel by itself. [Salzberg and Sayama 2004, text pp. 3–5 and figure 2](https://bingdev.binghamton.edu/sayama/papers/Complexity-preprint.pdf).

The BioSystems paper studies genealogical bias and hostile environments. Its treatments include a tenth-state pathogen with an extra lifetime layer and periodic block removal, both localized and distributed. The latter preserves the baseline nine-state transition law between interventions. Section 3.4 explicitly includes **transient species that produce stable self-replicators in their next cycle**, because many changes pass through this intermediate stage. Its inference of inherited bias arises from population histories, leaving room for a controlled common encounter panel to separate transferred organism properties from the encountered partner distribution. Ecological disturbances, mutational bias, and limited complexity growth have already been investigated. [Salzberg, Antony, and Sayama 2004](https://bingdev.binghamton.edu/sayama/papers/BioSystems-preprint.pdf).

The review distinguishes exact replication from reproduction supporting viable inherited variation; reviews asynchronous variants, self-protecting loops, sexyloops, continuous CA, and open-ended evolution; and discusses unresolved organism individuality and long-term convergence. An increase in size or population alone is insufficient to establish greater capacity for adaptive change. Its bibliography is a starting point for a broader review, particularly the sexyloop work on inheritance of a variation-generating mechanism. [Sayama and Nehaniv, arXiv v2](https://arxiv.org/html/2402.03961v2).

A newer relevant paper treats habitat degradation and spatial adaptation in probabilistic Darwinian CA with genetic-algorithm update rules. Its publisher abstract confirms this is a different model from embedded nine-state evoloops. Only its metadata and abstract were inspected; detailed comparisons require its full text. [Derets and Nehaniv 2025](https://doi.org/10.1162/artl_a_00457).

## What these interventions can add

The intended contribution is a reproducible **causal comparison of variation-generating outcomes**, conditional on a declared panel, horizon, and benefit assay. A crossed pair competition measures persistence; a crossed encounter atlas measures candidate production, inherited novelty after isolation, and eventual paired ecological benefit while preserving lethal and nonproductive encounters in the denominator. It also records unresolved outcomes and ambiguous parentage. This distinction must survive in the manuscript even if the current pilot observes no beneficial variants.

H2 requires differences in the focal-by-partner interaction, such as differences of differences or partner-dependent focal rankings. A large partner main effect is insufficient. Reciprocal focal labels applied to the same complete physical pair state are not independent replicates. Holding out geometry or phase configurations tests transfer across those configurations, not across independent evolutionary histories.

H1 will require evolved organisms from independent populations and matched ancestors assessed against the same held-out encounters. H3 will require two transplants: (a) history-derived organisms into a shared encounter distribution, and (b) shared organisms into history-derived encounter distributions. They hold encounter distribution or organism identity fixed, respectively. History is upstream: equal complete states have equal deterministic futures. No residual historical cause can be inferred after fixing complete state. These are proposed contrasts, not already completed results.

## Rule choice, variants, and licensing

The selected baseline is the original nine-state evoloop transition system, as exposed by CellPyLib's `Evoloop` and independently checked against EvoLoopS 1.0. Neighbors are **center, top, right, bottom, left (CTRBL)**; rotations apply to the four neighbors, not the center. All cells update synchronously. Boundary choice must be explicit in each configuration. CellPyLib's documented example uses `init_species13_loop((100,100),40,15)` and 700 stored time slices; indexing the initial slice differs from counting completed updates. [Implementation documentation](https://cellpylib.org/sdsr_evoloop.html).

A seed variant is not a new rule variant. Original paper section 3.8 names 2-, 3-, and 4-evoloops by the number of growth genes before turning genes; the old seed is an n-evoloop. EvoLoopS defaults to `13-2.img`, while CellPyLib's species13 matches the author's `13.img`. Reproducing the latter seed does not reproduce the former full-scale evolutionary demonstration. Self-protecting, SDSR, sexyloop, asynchronous, and pathogen rules must not be silently substituted. Full-table comparison results are recorded by engine verification; any nonzero mismatch must be investigated before scientific use.

[CellPyLib](https://github.com/lantunes/cellpylib) identifies Luis M. Antunes as author and supplies [Apache License 2.0](https://github.com/lantunes/cellpylib/blob/master/LICENSE.txt). The project may redistribute the needed reference components with the complete license, applicable notices, and explicit modification notices. The author-hosted EvoLoopS 1.0 README permits redistribution with accompanying files and documented modification, restricts commercial use of its program **and results**, and asks academic users to contact the author. The later [author software webpage](https://bingdev.binghamton.edu/sayama/sdsr/) states a different academic-use permission for its Java tool; that statement is not automatically a replacement license for the older C archive.

This project takes the Apache reference route: **do not incorporate EvoLoopS code, seed catalogue, website artwork, or movie assets**. The author archive is inspected temporarily for agreement and provenance. Simulation snapshots and natural variants used here are generated from the licensed documented CellPyLib seed. No author contact is authorized merely by this inspection. Papers are linked rather than redistributed; the arXiv non-exclusive hosting license is not a general redistribution grant.

## Source fingerprints

SHA-256 hashes cover exact bytes retrieved for inspection; references are URLs plus version or access date. Temporary downloads are excluded from Git. Pin the CellPyLib commit in retrieval scripts: `743e936d48f8520f6f4ac652570ac7bb46414189` (master observed 2026-10-10).

| Artifact | SHA-256 |
|---|---|
| arXiv v2 PDF | `e9efee87a771a705eb50e44a288fbfc27f02c5ec5e138e9bdfb268331970e951` |
| Original ALIFE PDF | `050dcfd88271edd129cf07a514992258447ecdec60eeb0c4d4a17bb169759d03` |
| Complexity author preprint | `cf384b74dade1384e82dc298e76477c80ae700ea856878271c1ad8201d5d97a8` |
| BioSystems author preprint | `8013fe2649c10704deb164c087a3b8990b28ba204bb4f69c0cf819fca4ba78bb` |
| Author software webpage | `a08835e8e67beec20b3ef534827325bf1756edfb90c8bd2e047719beb38fa426` |
| EvoLoopS 1.0 archive | `05a9f080e8a7a40c7db87e8055a9947699cd156d1a7f793d722503f362595169` |
| Author `evoloops.c` | `48180354dfac74e5bbf04abe965885a7078ae50d49a450416cf73b3f70112bbd` |
| Author `rule_evolvable` | `5bcab967259a2975ad94c24db2253ff8e5ad0c5f9a801885a130378f346f8722` |
| Author `13.img` | `bc25b672dd89800a417c5c839559d78d714778c133166751f7c2d55b60383d61` |
| CellPyLib `evoloop.py` | `dc6e47a50bfdd02ebab2e55f84ecab2b9d2d557e4146b32ba65dda94dae00fbd` |
| CellPyLib `LICENSE.txt` | `58d1e17ffe5109a7ae296caafcadfdbe6a7d176f0bc4ab01e12a689b0499d8bd` |
