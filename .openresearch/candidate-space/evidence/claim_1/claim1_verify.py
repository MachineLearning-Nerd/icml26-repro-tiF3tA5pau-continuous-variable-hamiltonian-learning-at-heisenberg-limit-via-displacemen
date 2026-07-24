"""Independent structural checker for Claim 1 evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def verify(payload: dict) -> dict:
    failures = [
        name for name, passed in payload["acceptance_checks"].items() if not passed
    ]
    times = np.asarray(payload["evolution_times"], dtype=float)
    rpe = np.asarray(payload["median_rpe_rmse"], dtype=float)
    sql = np.asarray(payload["median_ramsey_sql_rmse"], dtype=float)
    reconstructed_rpe = float(np.polyfit(np.log(times), np.log(rpe), 1)[0])
    reconstructed_sql = float(np.polyfit(np.log(times), np.log(sql), 1)[0])
    if abs(reconstructed_rpe - payload["metrics"]["rpe_log_error_vs_log_time_slope"]) > 1e-12:
        failures.append("rpe_slope_reconstruction")
    if abs(reconstructed_sql - payload["metrics"]["ramsey_log_error_vs_log_time_slope"]) > 1e-12:
        failures.append("sql_slope_reconstruction")
    expected = [
        32 * 2 * 256 * (2 ** (level + 1) - 1)
        for level in payload["configuration"]["rpe_levels"]
    ]
    if expected != payload["evolution_times"]:
        failures.append("exact_evolution_time_schedule")
    if payload["proof_certificate"]["coupling_design_rank"] != 4:
        failures.append("coupling_design_rank")
    if payload.get("verdict") != "VERIFIED":
        failures.append("verdict")
    return {
        "checker": "claim1_verify.py",
        "passed": not failures,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence", type=Path)
    args = parser.parse_args()
    with args.evidence.open(encoding="utf-8") as handle:
        output = verify(json.load(handle))
    print(json.dumps(output, sort_keys=True))
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
