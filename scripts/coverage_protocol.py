"""Freeze/verify protocol 010 provenance without simulation or root selection.

Only the standard library is used. Acquisition is deliberately a separate step
whose implementation must be bound by a readiness receipt before main outcomes.
"""
import argparse
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = "configs/coverage-v1.json"
SCRIPT = "scripts/coverage_protocol.py"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def validate_config(cfg, source):
    """Reject incomplete condition panels and inconsistent frozen budgets."""
    require(cfg["schema_version"] == 1, "unsupported schema")
    require(cfg["states"] == source["config"]["states"], "all five source states required")
    require(set(cfg["treatments"]) == {"D", "U"} and len(cfg["treatments"]) == 2,
            "both treatments required")
    response = [c["id"] for c in source["config"]["conditions"]
                if c["split"] in ("development", "confirmation")]
    require(cfg["conditions"] == response, "all four response conditions required")
    require(cfg["shape"] == source["config"]["shape"] == [192, 192], "source shape changed")
    require(cfg["boundary"] == "periodic", "boundary changed")
    classes = cfg["sampling"]["classes"]
    require(classes == ["scored", "valid_unregistered", "unknown_identity"],
            "separate scored/unregistered/unknown classes required")
    require(cfg["sampling"]["per_stratum_cap"] == 1, "selection budget changed")
    times = cfg["sampling"]["source_times"]
    delays = cfg["native"]["maturation_delays"]
    require(times == [400, 800, 1200] and delays == [0, 100, 400], "time panel changed")
    interval = cfg["native"]["sample_interval"]
    require(interval == 20 and all(t % interval == 0 for t in times + delays),
            "native samples must include all declared times")
    horizon = cfg["native"]["continuation_horizon_from_source"]
    require(horizon == 1600 and horizon >= max(delays), "continuation horizon changed")
    require(cfg["native"]["maximum_world_update"] == max(times) + horizon,
            "native horizon cannot cover source windows")
    require(max(times) + max(delays) <= source["config"]["horizon"],
            "maturation snapshots outside original source window")
    search = cfg["search"]
    for key in ("isolation_shape", "generation_horizon", "detection_interval",
                "offspring_per_generation", "max_depth",
                "max_generation_simulations_per_root", "stable_transmissions"):
        require(search[key] == source["config"]["search"][key], f"search limit changed: {key}")
    require(search["unknown_root_initial_identity"] is None,
            "unknown identity must remain null")
    gate = cfg["controls"]["gate"]
    require(Fraction(gate["scored_selected_observation_recovery_fraction"]) == Fraction(9, 10),
            "overall gate changed")
    require(Fraction(gate["per_starting_state_scored_recovery_fraction"]) == Fraction(4, 5),
            "state gate changed")
    require(gate["phase_original_identity_recoveries_required"] == len(source["phases"]) == 30,
            "all phase controls required")
    require(cfg["benefit"]["assay"] is None, "no benefit assay in this calibration")
    require(cfg["execution"]["workers"] == 1 and
            cfg["execution"]["minimum_available_memory_mib"] >= 200,
            "memory/worker guard changed")
    worlds = len(cfg["states"]) * len(cfg["conditions"]) * len(cfg["treatments"])
    strata = worlds * len(times) * len(classes)
    roots = strata * len(delays)
    expected = {"worlds": worlds, "strata": strata,
                "maximum_selected_observations": strata, "maximum_delayed_roots": roots,
                "phase_controls": 30,
                "maximum_generation_simulations": (roots + 30) *
                search["max_generation_simulations_per_root"]}
    for key, value in expected.items():
        require(cfg["limits"][key] == value, f"budget mismatch: {key}")


def build_manifest(root=ROOT):
    """Bind source files and existing physics, without reading source outcomes to select cores."""
    cfg = json.loads((root / CONFIG).read_text())
    source = json.loads((root / cfg["source_manifest"]).read_text())
    validate_config(cfg, source)
    source_dir = Path(cfg["source_manifest"]).parent
    files = {CONFIG, cfg["protocol"], SCRIPT, cfg["source_manifest"],
             "protocols/000-scientific-contract.md", "protocols/009-impact-matched-paired-assay.md",
             "configs/impact-v1.json"}
    preserved = ["analysis.json", "benefit.json", "calibration-analysis.json", "integrity.json"]
    for name in preserved:
        files.add(str(source_dir / name))
    for name, expected in source["code_hashes"].items():
        require(sha(root / name) == expected, f"source implementation changed: {name}")
        files.add(name)
    require(sha(root / "configs/impact-v1.json") == source["config_sha256"],
            "source config hash mismatch")
    require(sha(root / "protocols/009-impact-matched-paired-assay.md") == source["protocol_sha256"],
            "source protocol hash mismatch")
    runs = []
    for spec in source["runs"]:
        if spec["split"] not in ("development", "confirmation"):
            continue
        rid = spec["run_id"]
        path = str(source_dir / "initial" / f"{rid}.npz")
        files.add(path)
        runs.append({"run_id": rid, "state": spec["state"], "split": spec["split"],
                     "condition": spec["condition"], "treatment": spec["treatment"],
                     "initial_file": path, "initial_hash": spec["initial_hash"],
                     "phase": spec["phase"], "pair_id": spec["pair_id"], "impact": spec["impact"]})
    expected_runs = {f"{state}-{condition}-{treatment}" for state in cfg["states"]
                     for condition in cfg["conditions"] for treatment in cfg["treatments"]}
    require({r["run_id"] for r in runs} == expected_runs and len(runs) == 40,
            "source response panel incomplete or duplicated")
    controls = []
    for phase in source["phases"]:
        path = str(source_dir / "phase" / f'{phase["name"]}.npz')
        files.add(path)
        controls.append({**phase, "file": path,
                         "identity": source["states"][phase["state"]]["identity"]})
    require({(c["state"], c["age"]) for c in controls} ==
            {(s, a) for s in cfg["states"] for a in (0, 20, 30, 100, 110, 120)},
            "phase control panel incomplete")
    integrity = json.loads((root / source_dir / "integrity.json").read_text())
    require(integrity["status"] == "passed" and integrity["mismatches"] == 0,
            "source integrity did not pass")
    for name, expected in integrity["evidence_sha256"].items():
        require(sha(root / source_dir / name) == expected, f"source evidence changed: {name}")
    return {"schema_version": 1, "experiment_id": cfg["experiment_id"],
            "freeze_scope": "design and input provenance only; no selected roots or acquired outcomes",
            "acquisition_status": "not_started; implementation readiness receipt required",
            "source_commit": cfg["source_commit"], "config": cfg,
            "rule_hash": source["rule_hash"], "registry": source["registry"],
            "states": source["states"], "runs": runs, "phase_controls": controls,
            "source_file_sha256": {name: sha(root / name) for name in sorted(files)},
            "preserved_outcomes": {str(source_dir / name): sha(root / source_dir / name)
                                   for name in preserved}}


def freeze(root=ROOT):
    manifest = build_manifest(root)
    target = root / manifest["config"]["output"] / "manifest.json"
    require(not target.exists(), "preserve frozen design; use verify or a new version")
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_suffix(".json.tmp")
    with temp.open("x") as handle:
        json.dump(manifest, handle, indent=2)
        handle.write("\n")
    try:
        os.link(temp, target)  # Exclusive publication; never replace an existing freeze.
    finally:
        temp.unlink()
    return manifest


def verify(root=ROOT):
    cfg = json.loads((root / CONFIG).read_text())
    target = root / cfg["output"] / "manifest.json"
    saved = json.loads(target.read_text())
    expected = build_manifest(root)
    require(saved == expected, "freeze manifest or bound source files changed")
    return saved


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("freeze", "verify"))
    args = parser.parse_args()
    manifest = {"freeze": freeze, "verify": verify}[args.command]()
    print(f'{args.command}: {manifest["experiment_id"]}; '
          f'{len(manifest["runs"])} worlds, {len(manifest["phase_controls"])} controls; '
          f'{len(manifest["source_file_sha256"])} file hashes verified; no simulation')


if __name__ == "__main__":
    main()
