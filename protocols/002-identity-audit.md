# Reporting sensitivity audit — added during atlas acquisition

10 October 2026. The main protocol, code, and states remain frozen and unchanged.
This audit was added after acquisition began and before inheritance analysis.
It addresses a measurement distinction, not an outcome-based exclusion.

The detector's historical field named `genotype` is a **composite identity**:
phase-normalized channel word plus sorted core dimensions. The frozen endpoint
therefore measures organism-identity novelty. A shape-only change can satisfy
that endpoint without a changed signal word. Report it transparently under
that name; do not call shape-only identity change genetic novelty.

Also report a stricter sensitivity endpoint: candidate channel-word novelty
requires the substring after `:` to differ from both inputs' words. Confirmed
signal inheritance requires the assay-stable word to differ from both inputs,
and an encounter-observed novel word initiating the tested path. Preserve
morphological novelty separately. Use the same complete-state denominators,
isolation budgets, and unresolved outcomes. No outcome is discarded from raw data.

N01 illustrates the distinction: the exploratory transient's 11×13 core and
stable descendant's 12×12 core share a channel word. Their difference is
morphological stabilization; that shared word differs from S13's word. The
code-level field remains unchanged for reproducibility. Manuscript and figures
must distinguish frozen composite and added signal-word endpoints explicitly.
