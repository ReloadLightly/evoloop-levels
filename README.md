# Evoloop Levels

**Where does evolvability reside: organisms, encounters, or ecological history?**
Levels refers to levels of evolutionary causation. We are building reproducible
artificial-life evidence toward ALIFE 2027 or GECCO 2027.

The first checkpoint is a controlled crossed encounter atlas under the original
nine-state evoloop rules. H1 (transferable organism contribution) and H3
(historical pathways) remain untested. Interaction-generated mutation is already
known; this project measures conditional inherited-variant yield, with explicit
unsuccessful encounters, isolation checks, and a prospective benefit assay.

The completed atlas observed candidate signal changes in **6/40 near
configurations**, with **0/64 controls** showing candidate novelty. Eleven
isolation paths yielded **no confirmed stable novel inheritance** under the
frozen assay. Main candidate rankings reversed by partner, but the pattern
did not transfer to held-out configurations. This does not establish H2 for
useful heritable variation. Benefit remains pending; its yield is unknown.
A separate exploratory natural path did establish inherited novelty and supplied
the N01 input organism. H1, H3, and RSI remain unestablished.

[Completed analysis](data/atlas/analysis.md) ·
[Outcome matrix](figures/outcome-matrix-light.svg) ·
[Evidence stages](figures/evidence-stages-light.svg) ·
[Next experiment](docs/next-experiment.md)

## Installation and verification

Python 3.10+, GCC, and the packages in requirements.txt are sufficient. No GPU,
interactive interface, or third-party simulation service is needed.

```sh
python -m venv .venv
.venv/bin/pip install -r requirements-lock.txt
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
The frozen prospective atlas has 104 states: 32 main and eight held-out
near encounters, 40 separated controls, and 24 alone controls. All runs and initial inheritance checks are complete; details are in RESEARCH_STATE.md. The protocol is
[protocol 001](protocols/001-encounter-atlas.md); a transparent identity audit is
[protocol 002](protocols/002-identity-audit.md).

```sh
# Existing complete grids are committed; freeze is needed only in a fresh data tree.
OPENBLAS_NUM_THREADS=1 python -m scripts.atlas run
OPENBLAS_NUM_THREADS=1 python -m scripts.atlas inherit
OPENBLAS_NUM_THREADS=1 python -m scripts.analyze
OPENBLAS_NUM_THREADS=1 python -m scripts.figures
OPENBLAS_NUM_THREADS=1 python -m scripts.render_manuscript
OPENBLAS_NUM_THREADS=1 python -m scripts.check_evidence
sha256sum -c data/SHA256SUMS
```

The runner resumes by skipping completed run files. For a genuinely fresh rerun,
use a separate checkout and remove its `data/atlas/runs/` directory before running.
`python -m scripts.accelerated_atlas` optionally resumes with an independently
checked compiled contact diagnostic; dynamics and the frozen definitions are
unchanged. `data/atlas/execution.json` documents the original execution route.
To rebuild starting states, first reproduce exploration, then remove the copy's
`data/atlas/manifest.json` and run `python -m scripts.atlas freeze`; compare grid
hashes with the committed manifest. Never overwrite evidence in the primary copy.

![Recorded natural world](figures/world-overview-dark.png)

[World animation](figures/world-overview.webp) ·
[Exploratory inheritance evidence](figures/inheritance-path-light.svg) ·
[Working manuscript](paper/manuscript.md) · [Readable PDF](paper/manuscript.pdf)

Figures use literal state colors, exact cells, shared light/dark styles, and
recorded data. Source experiment IDs, crops, hashes, and regeneration commands
are in figures/manifest.json. No synthetic scientific artwork is used.
Read protocols/000-scientific-contract.md before interpreting scientific outcomes.

The recorded atlas run time was 19.6 minutes with a 61.9 MiB peak runner RSS.
The full data and figures fit ordinary Git; checksums are in data/SHA256SUMS.
Three selected replays illustrate a candidate-producing encounter, a configuration
with no detected core at the horizon, and a reproducing encounter without novelty:
[replay 1](figures/encounter-1.webp), [replay 2](figures/encounter-2.webp),
[replay 3](figures/encounter-3.webp). Selection is illustrative and occurred after analysis.

The compiled reference uses the original evoloop rules, not self-protecting or
asynchronous variants. Dependencies are pinned to tested versions in
requirements-lock.txt. Third-party notices: evoloop/vendor/NOTICE.md.
