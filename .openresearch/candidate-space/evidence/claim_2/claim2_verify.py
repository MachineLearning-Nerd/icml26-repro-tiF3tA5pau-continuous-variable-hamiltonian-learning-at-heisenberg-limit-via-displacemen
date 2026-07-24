"""Independent checker for Claim 2 evidence."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np


def verify(payload: dict) -> dict:
    failures = [
        name for name, passed in payload["acceptance_checks"].items() if not passed
    ]
    validation = payload["validation"]
    normalized = np.array(
        [
            item["median_evolution_time"]
            / math.log2(1 / item["target_rmse"])
            for item in validation
        ]
    )
    targets = np.array([item["target_rmse"] for item in validation])
    slope = float(np.polyfit(np.log(1 / targets), np.log(normalized), 1)[0])
    if abs(
        slope
        - payload["metrics"]["log_normalized_time_vs_log_inverse_target_slope"]
    ) > 1e-12:
        failures.append("resource_slope_reconstruction")
    if payload["symbolic_certificate"]["transform_determinant"] != "2":
        failures.append("quadratic_transform_determinant")
    for item in validation:
        if item["selected_level"] != payload["selected_first_hit_levels"][
            str(item["target_rmse"])
        ]:
            failures.append(f"first_hit_{item['target_rmse']}")
    if payload.get("verdict") != "VERIFIED":
        failures.append("verdict")
    return {
        "checker": "claim2_verify.py",
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
