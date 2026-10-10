# Equivalent tiled execution of EXP-atlas-002

The frozen atlas began with the original dense kernel. Measured runs took
11–28 seconds, motivating an implementation optimization rather than reducing
the registered panel or horizon. The original runner, rule table, measurement,
search budgets, and configuration files remain unchanged.

A 16-cell tile is evaluated if it or any von Neumann neighboring tile contains
an occupied cell. Every skipped cell therefore has neighborhood 00000; the
selected lookup table maps that neighborhood to zero. Separate output buffers,
periodic pixel neighbors, complete copying, and the original provenance OR
preserve synchronous dynamics. The tile flags are recomputed from the complete
current grid, with no persistent hidden state. Partial tiles are supported.

Before use, all 59,049 local patterns (including complete five-square outputs),
480 random step comparisons across dense/sparse worlds and partial/seam tiles,
and two complete 1600-update atlas trajectories matched the original grids and
provenance exactly. Independent scientific review found no physics discrepancy.
The final 200-update benchmark was 0.513 s dense versus 0.0314 s tiled, about 16 times
faster for that kernel call. Full-run gains also depend on contact and detection.
Exact source hashes and timings are in `data/atlas-v2/tiled_verification.json`.

The original runner completed all 36 main encounters before interruption. A partial
held-out case is restarted from its identical frozen initial state; partial data
are not counted. `execution-interruption.json` records this boundary, and
`execution.json` records exactly which cases use each implementation. The same
verified tiled implementation can execute isolation searches without changing
the calibrated branching rules. Independent final evidence checks replay
selected complete encounters and every searched isolation generation using the
original dense kernel.

```sh
OPENBLAS_NUM_THREADS=1 python -m scripts.accelerated_fresh_atlas verify
OPENBLAS_NUM_THREADS=1 python -m scripts.accelerated_fresh_atlas run
OPENBLAS_NUM_THREADS=1 python -m scripts.accelerated_fresh_atlas inherit
```

Verification requires two completed original near/main cases; they are committed.
For reconstruction from an empty runs directory, generate those two cases with
`fresh_atlas.run_one` before checking the optimization, or use the original
`python -m scripts.fresh_atlas run` for the entire panel. Both routes reproduce
the same physical states and endpoints. Deterministic equivalence checks do not
supply independent samples.
