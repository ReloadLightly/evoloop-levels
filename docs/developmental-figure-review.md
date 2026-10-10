# Independent visual review of developmental calibration figures

Reviewed 10 October 2026. **Accepted.** The review covers the two final PNG
exports, their manuscript captions, the figure manifest, and the separate
machine validation receipt. No response simulation, replay, or rendering was
performed during this review.

| Final PNG | SHA-256 |
|---|---|
| `figures/developmental1-resolution-dark.png` | `69766377d14a2092c9866f1caf2aebb884d3a05964574e336b097bc8b0583680` |
| `figures/developmental1-paired-states-dark.png` | `f3599816dfa0f9ae42486b3e849ae5641a8187969ce78d9a26806b5ed38f65bb` |

The resolution figure shows all five states and both treatments with exact
Q/C numerators and denominators, unresolved R, and textual gate status. Text is
readable against the shared sequential blue scale; labels, color bar, title,
and footer do not overlap or clip. The 4/5 threshold is explicit. The footer
retains the 30/30 original and 3/3 omitted-input control denominators and the
726/799 scored recovery denominator. It distinguishes source recovery from
total viable population and warns that repeated inputs and controls are not
independent populations. The manuscript caption correctly says each cell sums
ten source snapshots and preserves separate scored-recovery and resolved-share
checks. Passing this calibration does not relabel protocol 010's earlier failure.

The paired-state figure keeps equal square geometry for six complete 192×192
periodic grids at native updates 0, 800, and 1600. Coordinates and 10-cell scale
bars are visible. Cell shapes, small detached structures, extended arms, and
boundary activity remain legible; the final exports have no covering frame or
annotation inside the grids. The nine literal state colors are separately
identified in a readable legend. The D/U row labels and footer specify the
constructed age-20 colony, whole-component removal in D, and no removal in U.
The figure identifies this as the first declared state/layout illustration.

Q/R/C titles classify the source snapshots using subsequent isolated assays;
the footer and caption make that distinction explicit. The caption retains the
unknown source-genotype qualification and the single complete-input equivalence
behind ten recoverable unknown-source observations. It does not assign native
parents, retroactively identify source genotype, or make the displayed
structural multiplication a benefit or evolvability result.

The manifest records the experiment, regeneration command, common style hash,
analysis/integrity hashes, and the complete plotted grids and world records for
the raw panels. All six new SVG/PDF/PNG artifact hashes are recorded there. The
separate machine validator reports 221,184 correctly encoded SVG cell centers
and fully matching PNG centers, with 120 prior artifact bytes preserved; this
visual review does not substitute for that pixel/provenance check.

Review bindings:

- `figures/manifest.json`: `0f7118133726ce1cc032c4b4d4f4a83c459a2613d381890f9e85588e302a0c41`
- `data/developmental-v1/figure-integrity.json`: `3464e60f28215857dc57b9b5aa989f89c22e0998a164fcd6e6ea6c6dba74be3d`
- `data/developmental-v1/analysis.json`: `a73cc0c408c274dfb9e10db74fefc829de34d5be444799da0fd9ee46ca6799f8`
- `data/developmental-v1/integrity.json`: `2310ae1d82602eaf4bc3987b0a5669263c0b7baaf5ecfa51f264a187be586fb3`

No corrective figure changes are required for these reviewed exports.
