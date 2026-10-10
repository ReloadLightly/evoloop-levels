# Visual review of the crossed figures and manuscript pages

Status: accepted

Reviewed 11 October 2026 after completed acquisition, passed independent scientific
replay, rendering and passed figure validation. This review visually inspected
all four new dark PNG figures and the supplied PDF previews for result page 21
and appended figure pages 64–67. After the discussion clarification, the final
page 23 preview was also inspected. It did not regenerate figures, replay native
worlds, run another pixel audit, or edit frozen implementation or measurement
files.

The figure-integrity receipt reports zero mismatches, all 126 prior exports
unchanged, 12 new SVG/PDF/PNG exports, 221,184 recorded native cell centers and
80 retention colors/interval labels checked. All six PNG panels have occupied-
and all-cell-center matching fractions 1.0. This review checked the receipt's
linkage to the current figure manifest and scientific/PDF validation receipt;
it relies on the separate validator for exhaustive cell correspondence. Manual
inspection complements that check by assessing legibility and scientific meaning.

The retention figure displays all five states across all four ages within A/B
and E/F: 80 conditions before aggregation. The grouped headers, age ticks,
state labels and lower-endpoint blue scale are readable. Labels preserve both
endpoints, including upper values above one; color encodes only the lower
endpoint. Display rounding is disclosed and exact Fractions remain in the
analysis. All observed condition intervals are finite: this rendering contains
no undefined or unbounded data example. The renderer nevertheless labels missing
values and hatches nonbounded cells separately from measured zero; this review
does not claim to have visually tested those absent cases.

The two interaction figures each show all 20 declared contrasts, with a shared
horizontal scale within each figure, labeled zero lines, and five named states
in each panel. B−A/F−E and 100−0/120−30 orientation is explicit in titles and the
footer formula. All retention interactions cross zero. The absolute disturbed-
count panels visibly preserve the two negative V03 development intervals; the
V03 confirmation 100−0 interval reaches zero and remains unresolved. Neither
plot uses statistical confidence-interval language. Units distinguish retention
from detected source observations per census. Captions retain incomplete
recovery, complete spatial challenge including removal position, nonhomologous
elapsed ages, distinct panel treatments, and absent H1/H3/evolvability/RSI inference.

The paired-state figure uses the first declared V01, age 0, layout A D/U pair,
with updates 0, 800 and 1600 fixed in manifest selection metadata. It is labeled
as a previously observed preparation, not a response-selected example or new
confirmation. Complete 192×192 periodic grids, intact arms, seam cells, square
cell geometry and common cell scale are visible. Nearest-cell rendering and the
fixed nine-state legend retain literal state meanings separately from the
blue quantitative plots. D/U row labels, time, Q/R/C, ten-cell bars and exact
one-third removal explanation are readable. Borders sit outside the recorded
cell area; neither border nor legend overwrites source evidence. The original
PNG-border validation failure remains in its retained log and is not represented
as a measurement change.

All four plots use the dark navy background, configured blue text, shared
sequential blue map, series roles and annotation contrast from
`configs/style.json` through `scripts.figures`. Additional hues occur only in
the labeled literal nine-state palette. No new light export is present. Each
new artifact's manifest records EXP-age-geometry-cross-001, regeneration command,
style hash and source hashes; the raw pair additionally records selection.

PDF page 21 retains all ten panel rows and six contrast rows without clipping.
The text distinguishes prior frozen calibration from main crossed recovery,
preserves both-origin/both-panel criteria and the confirmation-only RV01 positive,
and labels the 36/18/54 confirmed encounter denominators. Pages 64–67 preserve
the four plots' labels, scale bars and complete footers with separation from the
literal-state legend. Page 23 now explicitly assigns age/layout covariance to
protocol 009 and its crossing to protocol 012. The final PDF remains 67 pages
with 41 appended vector figure pages. The refreshed receipt records full decoding
of all pages; this reviewer visually inspected the named six pages, not every
page of the document.

No clipping, geometry, contrast-orientation, source-selection or interpretation
blocker remains in the reviewed outputs.

## Reviewed output provenance

The hashes below identify the final scientific inputs, render/validator sources,
current exports, manuscript and receipts. PNG/PDF previews were inspected through
`view_image`; the temporary preview paths follow the validation receipt's
Ghostscript commands, with final discussion preview `/tmp/crossed-final-discussion.png`.

| Input or output | SHA-256 |
|---|---|
| `configs/style.json` | `f015d8d719543dd947de72536cf45bb0dcfab9bf0220b6fec00c19632b294bb4` |
| `scripts/figures_crossed.py` | `a59c3bb11d84732a279372e73eb80683aa66cbe356359be6e8286a528619ed1f` |
| `scripts/verify_crossed_figures.py` | `58896449ed7b65cf7194076c306644131d6858ec2fc19eb1f044971d8a6ba4d5` |
| `data/crossed-v1/analysis.json` | `a9af4d9ee3aa8708b4c5d72ff3460cac660b4e34395b22e239ebb58e4c2b277b` |
| `data/crossed-v1/integrity.json` | `0f2ca50fb599022d55c6f21dd28484db5b35a9f4024745c211facc616bd8b159` |
| `data/crossed-v1/figure-integrity.json` | `9f5c2422cbd88e877d97296105a5dac7d7198f73cc20616a0e9a87caf6264d93` |
| `figures/manifest.json` | `fc49d6804a6dd4e2c211b17027732d2f428cfe324ba348d3a6722434561f0f97` |
| `figures/crossed1-retention-dark.png` | `2f7aab3560959c0f8ecbcd8515270e8d6b107ee6c03839745e063f3aa8f56d72` |
| `figures/crossed1-interactions-dark.png` | `28a8b8512e16b3821524f30816049fc83024c0470271f8967656783cd43cfe8a` |
| `figures/crossed1-disturbed-interactions-dark.png` | `89e327c48335a3e7c0e3b99c867b757f7232bd9cff7dc73a9085b9701d3c08a7` |
| `figures/crossed1-paired-states-dark.png` | `30aed3112539b5679465ff005e0dc5fd2f0fed5f4c2f76f069f731a9b9c1bf05` |
| `paper/manuscript.md` | `6898e5b9c954c0f8a23b175b720b05ac704279c3e7521276135e7fae270bb31d` |
| `paper/manuscript.pdf` | `26ba721dd7defa3320fdc92b20e8827a1032122c698285bf772f70681246e58d` |
| `docs/crossed_manuscript_validation.json` | `982adc7f899668fbb226748d3f59714dbe589170339d0b07c9febe46bd6485f1` |
