"""Post-acquisition descriptive grouping of identical complete isolation inputs.

This supplements, and never changes, the frozen source-observation endpoint.
Identical component hashes imply identical centered isolation inputs and futures
under the fixed search. They do not assign native ancestry or independence.
"""
import json
from collections import defaultdict

from evoloop.engine import ROOT, digest
from scripts.coverage_protocol import sha, require
from scripts.coverage_assay import atomic_json
import numpy as np

OUT = ROOT / "data/coverage-v1"


def main():
    integrity = json.loads((OUT / "integrity.json").read_text())
    require(integrity["status"] == "passed" and integrity["mismatches"] == 0, "audit must pass first")
    recovery = json.loads((OUT / "recovery.json").read_text())
    groups = defaultdict(list)
    for observation in recovery["observations"]:
        for delay in observation["delays"]:
            if delay["extraction_status"] != "eligible":
                continue
            with np.load(OUT / delay["snapshot_file"], allow_pickle=False) as saved:
                require(digest(saved["snapshot"]) == delay["snapshot_hash"], "root bytes changed")
            groups[delay["snapshot_hash"]].append({
                "observation_id": observation["observation_id"], "source_class": observation["source_class"],
                "delay": delay["delay"], "delayed_identity": delay["delayed_identity"],
                "transmission_confirmed": delay["transmission_confirmed"],
                "confirmed_identity": delay["confirmed_identity"],
                "outcome_sha256": sha(OUT / delay["search_dir"] / "result.json")})
    for rows in groups.values():
        require(len({r["delayed_identity"] for r in rows}) == 1, "identical component assigned different identity")
        require(len({r["outcome_sha256"] for r in rows}) == 1, "identical centered input has different search future")
    omitted_positive = [o for o in recovery["observations"] if o["source_class"] != "scored"
                        and any(d["transmission_confirmed"] for d in o["delays"])]
    initial_hashes = {d["snapshot_hash"] for o in omitted_positive for d in o["delays"]
                      if d["delay"] == 0 and d["transmission_confirmed"]}
    result = {"status": "passed", "scope": "descriptive post-acquisition complete-input equivalence; primary counts unchanged",
              "recovery_sha256": sha(OUT / "recovery.json"), "integrity_sha256": sha(OUT / "integrity.json"),
              "eligible_delays": sum(map(len, groups.values())), "distinct_complete_inputs": len(groups),
              "omitted_positive_observations": len(omitted_positive),
              "omitted_positive_delay0_distinct_complete_inputs": len(initial_hashes),
              "groups": [{"snapshot_hash": h, "observations": rows} for h, rows in sorted(groups.items())],
              "interpretation": "duplicate isolation states are not independent samples; distinct states also do not establish independent histories"}
    atomic_json(OUT / "component-equivalence.json", result)
    print("Complete input equivalence:", len(groups), "unique inputs; omitted delay-zero positive inputs:", len(initial_hashes))


if __name__ == "__main__":
    main()
