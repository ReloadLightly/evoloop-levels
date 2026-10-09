# Research state — atlas and candidate-fate calibration completed

Date: 2026-10-10. Repository: ReloadLightly/evoloop-levels, main.

Completed experiment IDs:

- EXP-verification-001: all 59,049 local transitions match CellPyLib and the
  independent author-rule expansion. Seed reproduction, grid oracle,
  deterministic replay, checkpoint/resume, and rotation checks pass.
- EXP-discovery-001: natural candidate at t=2910 stabilizes from an 11×13 core
  to a 12×12 N01 descendant sharing its changed signal word. Two further
  isolated generations transmit that identity. Input panel S13/N01 verified.
- EXP-atlas-001: 104 complete states × 1,600 updates: 32 main near encounters,
  8 held-out, 40 separated, 24 alone. Contact in 40/40 near and 0/40 separated;
  no boundary flags. Candidate word novelty 6/40 near, 0/64 controls. Seven
  run/identity candidates, 11 isolation paths, zero frozen confirmed stable
  novel paths. Five states provide extractable snapshots; one remains inseparable.
- EXP-lineage-followup-001: separately labeled exploratory extension,
  3×12 → 6×6 → 4×4 → dissolution. No stable path; main endpoint unchanged.
- EXP-fate-calibration-001: protocol 004 frozen at 658a521 before delayed
  observations; 36 complete cases. Seven candidate identities in six atlas
  states × four delays: 15 eligible, ten target losses, three shared components.
  Legacy and expanded searches confirm novelty in 0/15 eligible states;
  both recover original identity in all eight S13/N01 control-delay states.
  Expanded search executes 69 candidate and 16 control generations, no depth
  or simulation cap reached; 18 candidate generation states reach the three-
  offspring cap. Later paths and ineligible phases remain unresolved.

Candidate ΔΔ = +0.375 main, −0.500 held-out. Main candidate rankings reverse
by partner but do not persist held-out. Inherited-novelty ΔΔ = 0 in both panels.
This does not establish H2 for useful heritable variation or disprove underlying
encounter dependence. Frozen composite identity and added signal-word audit
agree on observed candidate classification. Ancestry remains pair-level ambiguous.

Benefit calibration and paired ecological assays: pending. Beneficial-heritable
variant yield is unknown, not zero. H1/H3 are untested. RSI unestablished.
Unresolved candidate fates and bounded phase/offspring searches prevent
classification of all candidates as ecological failures. Core loss is not
lineage extinction; control colonies reproduce after original cores disappear.
Calibration broadens the search and validates the tested known-parent states,
not universal assay sensitivity. C05's word reappears at a different native
core at encounter times 1150/1160; four overlapping windows observe the same
structural event, not four inherited offspring. Native boundary flags affect
16/28 candidate and 2/8 control windows; seam detection can miss structures.

Performance: benchmark 118.6 million cell updates/s
for 192×192 stepping; recorded atlas run time 1177.1 s,
peak runner RSS 63400 KiB, one acquisition worker. Read-only contact
acceleration passed 6,760 cases; original physics/code/protocol hashes unchanged.
Integrity: 104 initial/final states, 11 candidate snapshots, four full encounter
replays, and 17 isolated-generation replays pass.
Calibration: 511.2 s acquisition, peak RSS 65112 KiB (63.6 MiB), one worker;
36 native, 85 expanded-generation, and 41 legacy-generation terminal replays
and saved extractions pass. Frozen code/protocol/configuration hashes pass.

Figures: figures/manifest.json (raw sources, run IDs, regeneration commands).
Manuscript: paper/manuscript.md and readable paper/manuscript.pdf.
Analysis: data/atlas/analysis.md, analysis.json, outcomes.csv, inheritance.json.
Calibration: data/fate-calibration/analysis.md, outcomes.csv, source-index.md,
integrity.json; figures/fate-{calibration-matrix,native-trajectories,raw-comparison}.
Protocols: 000 scientific contract; 001 frozen atlas; 002 postfreeze identity
reporting audit; 003 exploratory lineage follow-up; 004 prospective calibration.

Single next action: predeclare selection of three or four naturally generated,
isolation-verified viable identities, then freeze a fresh crossed atlas and
held-out configurations. See docs/next-experiment.md. Keep boundary-safe native
measurement, pending benefit, and independent histories for H1/H3 explicit.
