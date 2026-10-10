# Independent review of coverage figures

Reviewed 10 October 2026 after the completed scientific audit and final rendering.
The four dark PNGs were inspected: recovery by delay, state-level observation
unions, native targets and isolated inheritance paths. The twelve corresponding
SVG/PDF/PNG exports are recorded in `figures/manifest.json`.

The recovery panel displays confirmed and extractable counts against every
selected source observation. Its footer reports the failed diagnostic gate:
30/30 original-identity phase controls and 109/120 scored delay-zero recoveries,
with RV02 at 18/24 below the required 80%. The state panel distinguishes measured
zero recovery from empty strata using numeric labels and hatching. Recoveries
across delays are counted once per source observation, and the caption identifies
the finite coordinate-selected sample and its descriptive interpretation.

The native illustration uses the first selected observation in each omitted
class. All six full 192-square periodic grids retain the source core outline,
native time and maturation delay. The titles explicitly call the reported search
classification an isolation outcome. The inheritance illustration contains twelve
complete components along three recorded paths, including the unknown isolated
sources. V01/RV01 is labeled as a shared registry identity. Detached-child times,
component dimensions and five-cell scales are legible; the scales lie below the
components. The caption separates isolation transmission from native ancestry
and benefit. The panels preserve literal cell-state colors and equal cell
geometry, with the nine-state legend separate from the blue quantitative scales.

The recorded-pixel check passed with zero mismatches. It reconstructed the
illustration selections from `recovery.json`, decoded the lossless SVG rasters
and verified all **225,524 recorded cell centers**, including **16,304 occupied
centers**, against the shared state palette. Raster colors contain no interpolated
or undeclared values, and cell geometry is square and shared between panels.
PNG comparisons retain the recorded orientation and scale, allowing at most four
pixels of translation for the different tight bounding boxes produced by the
SVG and PNG renderers. All twelve inheritance panels matched at every tested PNG
cell center. Native panels matched at least 99.644% of tested occupied centers
and 99.469% of all tested centers; their declared target outlines and scale
annotation regions are excluded from this PNG comparison. Every native SVG
raster center remains checked without those exclusions.

One native scale label overlaps occupied cells in the upper-right panel. This is
an annotation limitation of that overview: the full recorded raster is retained
and validated, and the native illustration is accompanied by complete source
grids. Text, titles, legends and captions otherwise remain readable without
overlapping one another. The overview should be read together with its recorded
grids when inspecting individual cells near an annotation.

The validator also verified all twelve new artifact hashes, experiment IDs,
regeneration commands, source hashes and style hashes. All **108 prior manifest
entries and artifact bytes** remain unchanged against commit
`3aa73b85892e3d06115e738978ccef1bc54bf53d`. No light coverage exports remain.
The auxiliary receipt is `data/coverage-v1/figure-integrity.json`; it records the
baseline commit, validator hash, commands and per-panel checks. This review
introduces no simulations or changes to frozen scientific outcomes.

Validation ran sequentially under the memory guard, exited successfully, and
retained at least 798.3 MiB available memory. Its invocation is preserved in
`data/coverage-v1/execution.jsonl`:

```bash
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m scripts.memory_guard \
  --minimum 200 --reserve 180 --log data/coverage-v1/execution.jsonl \
  .venv/bin/python -m scripts.verify_coverage_figures
```
