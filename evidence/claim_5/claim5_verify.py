"""Independent checker for the Claim 5 bisection evidence."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence", type=Path)
    args = parser.parse_args()
    with args.evidence.open(encoding="utf-8") as handle:
        payload = json.load(handle)

    failures = [
        name for name, value in payload["acceptance_checks"].items() if not value
    ]
    lower, upper = payload["configuration"]["search_interval"]
    width = float(upper) - float(lower)
    for index, summary in enumerate(payload["validation_summary"]):
        epsilon = float(summary["target_precision"])
        expected = math.ceil(math.log2(width / (2.0 * epsilon)) - 1e-12)
        if int(summary["required_iterations"]) != expected:
            failures.append(f"summary_{index}_wrong_required_iterations")
        if int(summary["observed_iteration_count"]) != expected:
            failures.append(f"summary_{index}_wrong_observed_iterations")
        if float(summary["wilson_95_lower"]) < 0.85:
            failures.append(f"summary_{index}_validation_confidence")

    selected = int(payload["selected_rpe_max_level"])
    passing_levels = [
        int(record["max_level"])
        for record in payload["calibration"]
        if record["passes_calibration"]
    ]
    if not passing_levels or selected != min(passing_levels):
        failures.append("selected_level_is_not_calibrated_first_hit")
    if payload.get("verdict") != "VERIFIED":
        failures.append("verdict_is_verified")

    output = {
        "checker": "claim5_verify.py",
        "passed": not failures,
        "failures": failures,
    }
    print(json.dumps(output, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
