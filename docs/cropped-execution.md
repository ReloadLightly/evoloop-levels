# Equivalent cropped detection

The fresh atlas retains its frozen periodic detector. A separate execution
wrapper trims empty background only when no occupied cell touches a global
edge. Four zero cells around the complete occupied bounding rectangle preserve
exterior connectivity and the detector's margins. Coordinates are translated
back; occupied edges invoke the full reference detector.

Before use, comparison passed 75 random worlds, 35 organism translations,
644 sampled states from four complete trajectories, 58 completed final grids,
and 170 initial/final isolation arrays. A supplement passed 480 true-edge
placements, covering five real organisms, four rotations, four margins, and
six placements. Tests compare complete ordered dictionaries, all arrays and
hashes, and input preservation. Exact source hashes and benchmarks are in
`data/measurement-crop-verification/`. Eligible initial near states showed
1.39–2.05 times faster detection under concurrent acquisition; later states
and edge fallbacks gave little or no gain. This is a modest optimization.

The implementation switch retains all 62 completed cases. One interrupted
case is restarted from its frozen initial state and is not counted twice.
`data/atlas-v2/measurement-switch-interruption.json` records this boundary;
`cropped-execution.json` records each case's implementation. Scientific rules,
configurations, screens, search budgets, and denominators are unchanged.

```sh
OPENBLAS_NUM_THREADS=1 python -m scripts.verify_cropped_tracking
OPENBLAS_NUM_THREADS=1 python -m scripts.verify_cropped_edges
OPENBLAS_NUM_THREADS=1 python -m scripts.cropped_fresh_atlas run
OPENBLAS_NUM_THREADS=1 python -m scripts.cropped_fresh_atlas inherit
```

Committed proofs are required by the execution wrapper. The unchanged
`scripts.fresh_atlas` route remains available for full reconstruction in a
separate checkout. Final evidence verification uses the original dense kernel
and the original periodic detector independently of both optimizations.
