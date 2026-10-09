# Runtime optimization during acquisition

The separated controls spend most of their diagnostic time proving absence of
contact in a large grid. After the first near panel and initial controls were
complete, a compiled **read-only** equivalent of the NumPy contact scan was added.
The frozen rule, stepping kernel, provenance propagation, initial states,
sampling schedule, outcomes, and original runner remain byte-for-byte unchanged.

Before use, scripts/accelerated_atlas.py compares all occupancy/provenance
assignments of adjacent and separated pairs, including torus seams, random
grids, and every update in four full recorded trajectories. It verifies exact
first-contact times and records source hashes and measured speed. The execution
sidecar lists runs completed by the original scanner before switching.

This is an implementation-equivalence optimization, not a scientific treatment
or panel amendment. The original `python -m scripts.atlas run` remains a slower
independent reproduction route. No claim of equivalence is made unless the
recorded check passes.
