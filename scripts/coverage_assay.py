"""Guarded, resumable acquisition of the prospectively frozen score coverage panel."""
import argparse
import json
import platform
import resource
import subprocess
import time
from collections import Counter
from fractions import Fraction
from pathlib import Path

import numpy as np
import scipy

from evoloop.engine import ROOT, RULE_HASH, advance, digest
from evoloop.ecology import observation as measured
from evoloop.fate import expanded_search
from evoloop.periodic_assays import offspring_generation
from scripts.coverage_protocol import verify as verify_design, sha, require

OUT = ROOT / "data/coverage-v1"
IMPLEMENTATION = ["scripts/coverage_assay.py", "scripts/verify_coverage.py",
                  "tests/test_coverage_assay.py", "tests/test_verify_coverage.py",
                  "scripts/verify_ecological.py", "scripts/verify_fresh.py",
                  "scripts/verify_impact.py", "scripts/memory_guard.py"]


def read(path):
    return json.loads(path.read_text())


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2) + "\n")
    temp.replace(path)


def atomic_npz(path, **arrays):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("wb") as handle:
        np.savez_compressed(handle, **arrays)
    temp.replace(path)


def inventory(folder):
    return {str(p.relative_to(folder)): sha(p) for p in sorted(folder.rglob("*"))
            if p.is_file() and p.name != "receipt.json" and not p.name.endswith(".tmp")}


def verify_receipt(folder, binding):
    path = folder / "receipt.json"
    if not path.exists():
        return False
    saved = read(path)
    require(saved["binding"] == binding, f"completed-case binding changed: {folder}")
    require(saved["artifact_sha256"] == inventory(folder), f"completed-case artifacts changed: {folder}")
    return True


def receipt(folder, binding):
    atomic_json(folder / "receipt.json", {"binding": binding, "artifact_sha256": inventory(folder)})


def readiness():
    m = verify_design()
    require(m["rule_hash"] == RULE_HASH, "rule hash changed")
    path = OUT / "readiness.json"
    saved = read(path)
    require(saved["manifest_sha256"] == sha(OUT / "manifest.json"), "design freeze changed")
    require(saved["code_hashes"] == {p: sha(ROOT / p) for p in IMPLEMENTATION},
            "implementation changed after readiness freeze")
    require(saved["validation_sha256"] == sha(OUT / "validation.txt"), "validation evidence changed")
    require(all(sha(ROOT / p) == h for p, h in saved["source_records_sha256"].items()),
            "original response records changed")
    return m


def freeze_readiness():
    m = verify_design()
    require(not (OUT / "readiness.json").exists(), "preserve readiness receipt; use a new version")
    validation = (OUT / "validation.txt").read_text()
    require("\nOK\n" in validation and "FAILED" not in validation, "validation must pass before readiness")
    atomic_json(OUT / "readiness.json", {
        "status": "ready_before_main_acquisition", "experiment_id": m["experiment_id"],
        "manifest_sha256": sha(OUT / "manifest.json"),
        "code_hashes": {p: sha(ROOT / p) for p in IMPLEMENTATION},
        "validation_sha256": sha(OUT / "validation.txt"),
        "source_records_sha256": {
            str(Path("data/impact-v1") / r["split"] / r["run_id"] / "result.json"):
            sha(ROOT / "data/impact-v1" / r["split"] / r["run_id"] / "result.json") for r in m["runs"]},
        "search_identity": "measured delayed snapshot identity; null only if that isolated snapshot is unknown; source class immutable",
        "environment": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
        "execution": m["config"]["execution"], "main_outcomes": "not acquired",
    })
    print("Implementation readiness frozen; main acquisition requires remote commit and benchmark", flush=True)


def classify_identity(identity, registry):
    return "unknown_identity" if identity is None else "scored" if identity in registry else "valid_unregistered"


def select_strata(loops, registry, rid, t):
    strata = []; selected = []
    for label in ("scored", "valid_unregistered", "unknown_identity"):
        options = sorted((o for o in loops if classify_identity(o["genotype"], registry) == label),
                         key=lambda o: tuple(o["core"]))
        sid = f"{rid}-t{t}-{label}"
        strata.append({"stratum_id": sid, "source_time": t, "source_class": label,
                       "available_cores": len(options), "selected_cores": int(bool(options))})
        if options:
            o = options[0]
            selected.append({"observation_id": sid, "source_time": t, "source_class": label,
                             "source_identity": o["genotype"], "source_identity_unknown": o["genotype"] is None,
                             "core": o["core"], "delays": []})
    return strata, selected


def native_labels(o, samples, cfg):
    start = o["source_time"]; horizon = cfg["native"]["continuation_horizon_from_source"]
    window = [s for s in samples if start <= s["t"] <= start + horizon]
    require([s["t"] for s in window] == list(range(start, start + horizon + 1, cfg["native"]["sample_interval"])),
            "incomplete native window")
    at_core = [next((r for r in s["cores"] if r["core"] == o["core"]), None) for s in window]
    loss = next((s["t"] for s, r in zip(window, at_core) if r is None), None)
    recurrence = next((s["t"] for s, r in zip(window, at_core)
                       if loss is not None and s["t"] > loss and r is not None), None)
    word = o["source_identity"].split(":", 1)[1] if o["source_identity"] is not None else None
    matched = next((s["t"] for s in window if word is not None and any(
        r["core"] != o["core"] and r["identity"] is not None and
        r["identity"].split(":", 1)[1] == word for r in s["cores"])), None)
    return {"horizon": horizon, "sample_interval": cfg["native"]["sample_interval"],
            "fixed_core_first_loss_t": loss, "fixed_core_first_recurrence_t": recurrence,
            "endpoint_identity": at_core[-1]["identity"] if at_core[-1] is not None else None,
            "endpoint_core_present": at_core[-1] is not None,
            "matching_word_elsewhere_first_t": matched,
            "matching_word_status": "unknown_source_word" if word is None else "observed",
            "boundary_first_t": next((s["t"] for s in window if s.get("boundary_activity")), None),
            "interpretation": "overlapping structural continuations; no native offspring or genetic ancestry assignment"}


def delay_selection(o, loops, samples, t, registry, cfg):
    seen = [s for s in samples if o["source_time"] <= s["t"] <= t]
    lost = any(not any(r["core"] == o["core"] for r in s["cores"]) for s in seen)
    organism = next((r for r in loops if r["core"] == o["core"]), None)
    identity = organism["genotype"] if organism is not None else None
    snapshot = organism["isolation_snapshot"] if organism is not None else None
    if lost or organism is None:
        status = "sampled_target_lost"
    elif snapshot is None:
        raw = organism["extraction_status"]
        status = raw if raw in ("shared_component", "noncontractible_component") else "missing_complete_component"
    elif max(snapshot.shape) + cfg["extraction"]["minimum_empty_margin_total"] > cfg["shape"][0]:
        status = "component_too_large"
    else:
        status = "eligible"
    result = {"delay": t - o["source_time"], "t": t, "delayed_identity": identity,
              "delayed_class": classify_identity(identity, registry) if organism is not None else None,
              "delayed_core_present": organism is not None, "extraction_status": status,
              "snapshot_hash": digest(snapshot) if status == "eligible" else None,
              "extraction_bbox": organism.get("extraction_bbox") if organism is not None else None,
              "snapshot_file": None}
    return result, snapshot if status == "eligible" else None


def world(spec, m):
    cfg = m["config"]; folder = OUT / "worlds" / spec["run_id"]
    binding = {"manifest_sha256": sha(OUT / "manifest.json"), "readiness_sha256": sha(OUT / "readiness.json"),
               "initial_hash": spec["initial_hash"], "run_id": spec["run_id"]}
    if verify_receipt(folder, binding):
        print("REUSE WORLD", spec["run_id"], flush=True)
        return read(folder / "result.json")
    with np.load(ROOT / spec["initial_file"], allow_pickle=False) as saved:
        grid = saved["grid"].copy()
    require(digest(grid) == spec["initial_hash"], "initial physical hash mismatch")
    old = read(ROOT / "data/impact-v1" / spec["split"] / spec["run_id"] / "result.json")
    samples = []; strata = []; selected = []; then = time.perf_counter()
    sources = cfg["sampling"]["source_times"]
    capture = {t + d for t in sources for d in cfg["native"]["maturation_delays"]}
    interval = cfg["native"]["sample_interval"]
    for t in range(0, cfg["native"]["maximum_world_update"] + 1, interval):
        if t:
            advance(grid, interval)
        counts, records, loops = measured(grid, m["registry"])
        sample = {"t": t, **counts, "cores": records}
        if t <= 1600:
            require(sample == old["samples"][t // interval], f"original source records mismatch: {spec['run_id']}@{t}")
        sample["boundary_activity"] = bool(np.any(grid[[0, -1]]) or np.any(grid[:, [0, -1]]))
        samples.append(sample)
        if t in capture:
            atomic_npz(folder / f"grid-{t}.npz", grid=grid)
        if t in sources:
            ss, oo = select_strata(loops, m["registry"], spec["run_id"], t)
            strata.extend(ss)
            selected.extend({**o, "run_id": spec["run_id"], "state": spec["state"],
                             "treatment": spec["treatment"]} for o in oo)
        for o in selected:
            if t - o["source_time"] not in cfg["native"]["maturation_delays"]:
                continue
            delayed, snapshot = delay_selection(o, loops, samples, t, m["registry"], cfg)
            if snapshot is not None:
                path = folder / f'{o["observation_id"]}-delay{delayed["delay"]}.npz'
                atomic_npz(path, snapshot=snapshot)
                delayed["snapshot_file"] = str(path.relative_to(OUT))
            o["delays"].append(delayed)
    for o in selected:
        require([d["delay"] for d in o["delays"]] == cfg["native"]["maturation_delays"], "delay inventory")
        o["native_continuation"] = native_labels(o, samples, cfg)
    atomic_npz(folder / "final.npz", grid=grid)
    result = {**spec, "rule_hash": RULE_HASH, "completed_updates": cfg["native"]["maximum_world_update"],
              "final_hash": digest(grid), "samples": samples, "strata": strata, "observations": selected,
              "readiness_sha256": binding["readiness_sha256"], "seconds": time.perf_counter() - then}
    atomic_json(folder / "result.json", result); receipt(folder, binding)
    print("WORLD", spec["run_id"], "selections", len(selected), f'{result["seconds"]:.2f}s', flush=True)
    return result


def search_one(snapshot, identity, m, folder, original=False):
    binding = {"manifest_sha256": sha(OUT / "manifest.json"), "readiness_sha256": sha(OUT / "readiness.json"),
               "snapshot_hash": digest(snapshot), "input_identity": identity,
               "original_endpoint": original, "search_config": m["config"]["search"]}
    if verify_receipt(folder, binding):
        return read(folder / "result.json")
    folder.mkdir(parents=True, exist_ok=True)
    def persist(node, arrays):
        name = "confirmation" if "confirmation" in node else f'node-{node["node"]:02d}'
        atomic_json(folder / f"{name}.json", node)
        atomic_npz(folder / f"{name}.npz", **arrays)
    report = expanded_search(snapshot, identity, m["config"]["search"],
                             (lambda gt: gt == identity) if original else (lambda gt: True),
                             persist, generation=offspring_generation)
    atomic_json(folder / "result.json", report); receipt(folder, binding)
    return report


def search_fields(report, source_identity, registry):
    confirmed = bool(report and report["confirmation"])
    identity = report["confirmation"]["identity"] if confirmed else None
    censoring = list(report["truncations"]) if report else []
    if report:
        for node in report["nodes"]:
            stage = node["outcome"]
            if len(stage["children"]) == 3:
                censoring.append({"reason": "offspring_cap", "node": node["node"]})
            elif stage["status"] == "unresolved_at_horizon":
                censoring.append({"reason": "generation_horizon", "node": node["node"]})
    return {"root_reproduction_observed": bool(report["nodes"][0]["outcome"]["children"]) if report else None,
            "isolated_grid_extinction_nodes": [n["node"] for n in report["nodes"]
                                                if n["outcome"]["status"] == "assay_extinct"] if report else [],
            "transmission_confirmed": confirmed, "confirmed_identity": identity,
            "confirmed_identity_in_registry": identity in registry if confirmed else None,
            "same_as_source_identity": identity == source_identity if confirmed and source_identity is not None else None,
            "search_censoring": censoring, "inheritance_unresolved": not confirmed,
            "ancestry_ambiguous": True, "benefit_pending": True if confirmed else None}


def benchmark():
    m = readiness(); require(not (OUT / "benchmark.json").exists(), "preserve completed benchmark")
    phase = m["phase_controls"][0]
    with np.load(ROOT / phase["file"], allow_pickle=False) as saved:
        snapshot = saved["snapshot"].copy()
    then = time.perf_counter()
    result = search_one(snapshot, phase["identity"], m, OUT / "benchmark-control", True)
    require(result["status"] == "confirmed", "declared benchmark positive control did not recover")
    atomic_json(OUT / "benchmark.json", {"control": phase["name"], "workers": 1,
        "readiness_sha256": sha(OUT / "readiness.json"), "seconds": time.perf_counter() - then,
        "generation_simulations": result["generation_simulations"], "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "status": "passed", "scope": "timing and implementation control, not an independent observation"})
    print("BENCHMARK", read(OUT / "benchmark.json"), flush=True)


def acquire(commit):
    m = readiness(); cfg = m["config"]
    ready_bytes = subprocess.check_output(["git", "show", f"{commit}:data/coverage-v1/readiness.json"], cwd=ROOT)
    require(__import__("hashlib").sha256(ready_bytes).hexdigest() == sha(OUT / "readiness.json"), "readiness commit mismatch")
    b = read(OUT / "benchmark.json")
    require(b["status"] == "passed" and b["readiness_sha256"] == sha(OUT / "readiness.json"), "benchmark not ready")
    atomic_json(OUT / "acquisition.json", {"readiness_commit": commit, "readiness_sha256": sha(OUT / "readiness.json"),
        "interpretation": "readiness remotely verified before acquisition; deterministic reruns are checks"})
    then = time.perf_counter(); baselines = []
    for phase in m["phase_controls"]:
        with np.load(ROOT / phase["file"], allow_pickle=False) as saved:
            snapshot = saved["snapshot"].copy()
        require(digest(snapshot) == phase["snapshot_hash"], "phase physical hash mismatch")
        folder = OUT / "controls" / phase["name"]
        outcome = search_one(snapshot, phase["identity"], m, folder, True)
        baselines.append({"name": phase["name"], "state": phase["state"], "age": phase["age"],
                          "identity": phase["identity"], "snapshot_hash": phase["snapshot_hash"],
                          "search_dir": str(folder.relative_to(OUT)), "outcome": outcome})
        print("CONTROL", phase["name"], outcome["status"], flush=True)
    worlds = []; observations = []
    for spec in m["runs"]:
        result = world(spec, m)
        worlds.append({"run_id": spec["run_id"], "result_sha256": sha(OUT / "worlds" / spec["run_id"] / "result.json")})
        for o in result["observations"]:
            delays = []
            for d in o["delays"]:
                outcome = None; folder = None
                if d["extraction_status"] == "eligible":
                    with np.load(OUT / d["snapshot_file"], allow_pickle=False) as saved:
                        snapshot = saved["snapshot"].copy()
                    require(digest(snapshot) == d["snapshot_hash"], "delayed component hash mismatch")
                    folder = OUT / "searches" / f'{o["observation_id"]}-delay{d["delay"]}'
                    outcome = search_one(snapshot, d["delayed_identity"], m, folder)
                status = ("confirmed_stable_descendant" if outcome["status"] == "confirmed" else "unresolved_search") if outcome else d["extraction_status"]
                delays.append({**d, "search_dir": str(folder.relative_to(OUT)) if folder else None,
                               "outcome": outcome, "status": status, **search_fields(outcome, o["source_identity"], m["registry"])})
            observations.append({**o, "delays": delays})
            print("RECOVERY", o["observation_id"], [d["status"] for d in delays], flush=True)
    recovery = {"experiment_id": m["experiment_id"], "worlds": worlds, "baselines": baselines,
                "observations": observations, "readiness_sha256": sha(OUT / "readiness.json"),
                "seconds_this_invocation": time.perf_counter() - then,
                "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    atomic_json(OUT / "recovery.json", recovery)
    analyze()


def summarize(recovery, m):
    observations = recovery["observations"]; cfg = m["config"]
    def confirmed(o):
        return any(d["transmission_confirmed"] for d in o["delays"])
    def zero(o):
        return next(d for d in o["delays"] if d["delay"] == 0)["transmission_confirmed"]
    def summary(rows):
        delays = [d for o in rows for d in o["delays"]]
        return {"selected": len(rows), "confirmed": sum(confirmed(o) for o in rows),
                "eligible_observations": sum(any(d["extraction_status"] == "eligible" for d in o["delays"]) for o in rows),
                "planned_delays": len(delays), "eligible_delays": sum(d["extraction_status"] == "eligible" for d in delays),
                "confirmed_delays": sum(d["transmission_confirmed"] for d in delays),
                "root_reproduction_delays": sum(d["root_reproduction_observed"] is True for d in delays),
                "delay_statuses": dict(Counter(d["status"] for d in delays)),
                "confirmed_registered_descendant_observations": sum(any(d["confirmed_identity_in_registry"] is True for d in o["delays"]) for o in rows),
                "confirmed_outside_registry_descendant_observations": sum(any(d["confirmed_identity_in_registry"] is False for d in o["delays"]) for o in rows)}
    scored = [o for o in observations if o["source_class"] == "scored"]
    per_state = [{"state": state, "selected": sum(o["state"] == state for o in scored),
                  "confirmed_delay0": sum(o["state"] == state and zero(o) for o in scored)} for state in cfg["states"]]
    nc = sum(zero(o) for o in scored); nb = sum(b["outcome"]["status"] == "confirmed" for b in recovery["baselines"])
    gate = cfg["controls"]["gate"]
    checks = {"phase_controls": nb == gate["phase_original_identity_recoveries_required"],
              "overall_scored_delay0": Fraction(nc, len(scored)) >= Fraction(gate["scored_selected_observation_recovery_fraction"]) if scored else None,
              "each_state_scored_delay0": all(Fraction(r["confirmed_delay0"], r["selected"]) >= Fraction(gate["per_starting_state_scored_recovery_fraction"]) for r in per_state) if all(r["selected"] for r in per_state) else None}
    gate_status = "unresolved" if any(v is None for v in checks.values()) else "passed" if all(checks.values()) else "failed"
    by_class = [{"source_class": label, **summary([o for o in observations if o["source_class"] == label])}
                for label in cfg["sampling"]["classes"]]
    breakdown = []
    run_lookup = {r["run_id"]: r for r in m["runs"]}
    def value_of(o, dimension):
        if dimension == "condition":
            return run_lookup[o["run_id"]]["condition"]["id"]
        if dimension == "split":
            return run_lookup[o["run_id"]]["split"]
        return o[dimension]
    for dimension, values in (("state", cfg["states"]), ("treatment", cfg["treatments"]),
                              ("source_time", cfg["sampling"]["source_times"]),
                              ("condition", cfg["conditions"]), ("split", ["development", "confirmation"]),
                              ("run_id", [r["run_id"] for r in m["runs"]])):
        for value in values:
            for label in cfg["sampling"]["classes"]:
                breakdown.append({"dimension": dimension, "value": value, "source_class": label,
                                  **summary([o for o in observations if value_of(o, dimension) == value and o["source_class"] == label])})
    delays = [d for o in observations for d in o["delays"]]
    reports = [d["outcome"] for d in delays if d["outcome"]] + [b["outcome"] for b in recovery["baselines"]]
    omitted = [o for o in observations if o["source_class"] != "scored"]
    by_delay = []
    for delay in cfg["native"]["maturation_delays"]:
        for label in cfg["sampling"]["classes"]:
            rows = [d for o in observations if o["source_class"] == label for d in o["delays"] if d["delay"] == delay]
            by_delay.append({"delay": delay, "source_class": label, "planned": len(rows),
                             "eligible": sum(d["extraction_status"] == "eligible" for d in rows),
                             "confirmed": sum(d["transmission_confirmed"] for d in rows),
                             "identity_preserving": sum(d["same_as_source_identity"] is True for d in rows),
                             "statuses": dict(Counter(d["status"] for d in rows))})
    control_censoring = Counter()
    for b in recovery["baselines"]:
        control_censoring.update(c["reason"] for c in search_fields(b["outcome"], b["identity"], m["registry"])["search_censoring"])
    return {"experiment_id": m["experiment_id"], "complete_worlds": len(recovery["worlds"]),
            "phase_controls": {"confirmed": nb, "selected": len(recovery["baselines"])},
            "gate_status": gate_status, "gate_checks": checks,
            "scored_delay0": {"confirmed": nc, "selected": len(scored), "per_state": per_state},
            "by_class": by_class, "by_delay": by_delay, "breakdown": breakdown,
            "omitted": summary(omitted), "omitted_recoverability_observed": any(confirmed(o) for o in omitted),
            "generation_simulations": sum(r["generation_simulations"] for r in reports),
            "search_roots": len(reports),
            "search_censoring": dict(Counter(c["reason"] for d in delays for c in d["search_censoring"])),
            "phase_control_search_censoring": dict(control_censoring),
            "isolated_extinction_nodes": sum(n["outcome"]["status"] == "assay_extinct" for r in reports for n in r["nodes"]),
            "native_target_loss_observations": sum(o["native_continuation"]["fixed_core_first_loss_t"] is not None for o in observations),
            "native_target_recurrence_observations": sum(o["native_continuation"]["fixed_core_first_recurrence_t"] is not None for o in observations),
            "benefit": "not_assayed; prior registry and outcomes unchanged",
            "scope": "finite coordinate-selected diagnostic observations; not total viable population or independent histories"}


def analyze():
    m = readiness(); recovery = read(OUT / "recovery.json"); result = summarize(recovery, m)
    strata = [s for spec in m["runs"] for s in read(OUT / "worlds" / spec["run_id"] / "result.json")["strata"]]
    result["strata"] = strata
    result["recovery_sha256"] = sha(OUT / "recovery.json")
    result["readiness_sha256"] = sha(OUT / "readiness.json")
    atomic_json(OUT / "analysis.json", result)
    lines = ["# Paired-world score coverage", "", f'Gate: {result["gate_status"]}; phase controls {result["phase_controls"]["confirmed"]}/30; scored delay-zero {result["scored_delay0"]["confirmed"]}/{result["scored_delay0"]["selected"]}.', "",
             "| Source class | Recovered / selected observations | Confirmed / eligible / planned delays |", "|---|---|---|"]
    lines += [f'| {r["source_class"]} | {r["confirmed"]}/{r["selected"]} | {r["confirmed_delays"]}/{r["eligible_delays"]}/{r["planned_delays"]} |' for r in result["by_class"]]
    lines += ["", "Selection is diagnostic; losses, shared components and capped searches remain in denominators. Recoverability after imposed isolation does not identify native ancestry, total viable population or benefit. Earlier scores remain frozen.", ""]
    (OUT / "analysis.md").write_text("\n".join(lines))
    print("ANALYSIS", result["gate_status"], result["omitted"], flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("ready", "benchmark", "run", "analyze"))
    parser.add_argument("--readiness-commit")
    args = parser.parse_args()
    if args.command == "run":
        require(bool(args.readiness_commit), "supply remotely verified readiness commit")
        acquire(args.readiness_commit)
    else:
        {"ready": freeze_readiness, "benchmark": benchmark, "analyze": analyze}[args.command]()
