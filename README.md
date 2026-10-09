# Evoloop Levels

**Where does evolvability reside: organisms, encounters, or ecological history?**
Levels refers to levels of evolutionary causation. We are building reproducible
artificial-life evidence toward ALIFE 2027 or GECCO 2027.

The first checkpoint is a controlled crossed encounter atlas under the original
nine-state evoloop rules. H1 (transferable organism contribution) and H3
(historical pathways) remain untested. Interaction-generated mutation is already
known; this project measures conditional inherited-variant yield, with explicit
unsuccessful encounters, isolation checks, and a prospective benefit assay.

## Installation and verification

Python 3.10+, GCC, and the packages in requirements.txt are sufficient. No GPU,
interactive interface, or third-party simulation service is needed.

```sh
python -m venv .venv
.venv/bin/pip install -r requirements.txt
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m scripts.verify
```

The compiled C kernel uses uint8 grids and synchronous periodic updates. All
59,049 CTRBL transitions match the pinned CellPyLib reference and the original
author rule expansion. Species13 reproduction, grid-oracle agreement,
deterministic replay, and checkpoint/resume pass. See data/verification.json,
data/author_comparison.json, and docs/source_review.md for hashes and provenance.

An independent author-file comparison can be repeated with
`python -m scripts.compare_author /path/to/temporary/EvoLoopS-1.0` after retrieving
the linked author archive. Author code/assets are not incorporated or redistributed.
The bundled reference has its Apache license and attribution in evoloop/vendor.

Exploratory panel discovery: `OPENBLAS_NUM_THREADS=1 python -m scripts.explore`.
Main batch, analysis, and visualization commands will accompany the frozen panel.
Read protocols/000-scientific-contract.md before interpreting scientific outcomes.
