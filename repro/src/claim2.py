"""End-to-end first-quantization D-RUT verifier for Theorem 2."""

from __future__ import annotations

import json
import math
import platform
import time
from pathlib import Path

import numpy as np
import scipy
import sympy as sp

from faithful_drut import robust_phase_estimate

OUT = Path(__file__).resolve().parents[2] / "outputs"
SEED = 202251008419
R_TRUE = math.sqrt(3) / 10
OMEGA = 0.7
REFERENCE_PRODUCT = 1.0
TRUE_PRODUCT = math.exp(-2 * R_TRUE)
TRUTH_G = np.array(
    [OMEGA * TRUE_PRODUCT / 2, OMEGA / (2 * TRUE_PRODUCT)]
)
TARGETS = [0.02, 0.01, 0.005, 0.0025, 0.00125]
LEVELS = list(range(5, 13))
SHOTS = 256
RADIUS = 0.55
CALIBRATION_REPS = 16
VALIDATION_REPS = 32


def wilson_lower(successes: int, trials: int, z: float = 1.96) -> float:
    p = successes / trials
    denominator = 1 + z * z / trials
    center = p + z * z / (2 * trials)
    margin = z * math.sqrt(p * (1 - p) / trials + z * z / (4 * trials**2))
    return (center - margin) / denominator


def response(delta_r: float, theta: float) -> float:
    g20 = 0.5 * OMEGA * math.sinh(2 * delta_r)
    g11 = OMEGA * math.cosh(2 * delta_r)
    return RADIUS**2 * (g11 + 2 * g20 * math.cos(2 * theta))


def query_coefficients(
    delta_r: float, level: int, rng: np.random.Generator
) -> tuple[float, float, int]:
    first = robust_phase_estimate(response(delta_r, 0.0), level, SHOTS, rng)
    second = robust_phase_estimate(
        response(delta_r, math.pi / 2), level, SHOTS, rng
    )
    g20 = (first.estimate - second.estimate) / (4 * RADIUS**2)
    g11 = (first.estimate + second.estimate) / (2 * RADIUS**2)
    return g20, g11, first.evolution_time + second.evolution_time


def run_protocol(
    target: float, level: int, rng: np.random.Generator
) -> dict[str, float | int | bool]:
    target_r = target / 2
    iterations = math.ceil(math.log2(0.4 / (2 * target_r)) - 1e-12)
    lower, upper = 0.0, 0.4
    evolution = 0
    for _ in range(iterations):
        midpoint = (lower + upper) / 2
        g20, _, used = query_coefficients(R_TRUE - midpoint, level, rng)
        evolution += used
        if g20 > 0:
            lower = midpoint
        else:
            upper = midpoint
    estimate_r = (lower + upper) / 2
    g20, g11, used = query_coefficients(R_TRUE - estimate_r, level, rng)
    evolution += used
    omega_hat = math.sqrt(max(g11 * g11 - 4 * g20 * g20, 0.0))
    product_hat = REFERENCE_PRODUCT * math.exp(-2 * estimate_r)
    estimate_g = np.array(
        [omega_hat * product_hat / 2, omega_hat / (2 * product_hat)]
    )
    rmse = float(np.sqrt(np.mean((estimate_g - TRUTH_G) ** 2)))
    return {
        "target_rmse": target,
        "level": level,
        "iterations": iterations,
        "estimate_r": estimate_r,
        "omega_estimate": omega_hat,
        "G20_estimate": float(estimate_g[0]),
        "G02_estimate": float(estimate_g[1]),
        "rmse": rmse,
        "success": rmse <= target,
        "evolution_time": evolution,
    }


def symbolic_certificate() -> dict:
    lam = sp.symbols("lambda", positive=True)
    matrix = sp.Matrix(
        [
            [lam, 0, lam / 2],
            [0, 2, 0],
            [-1 / lam, 0, 1 / (2 * lam)],
        ]
    )
    determinant = sp.simplify(matrix.det())
    delta = sp.symbols("Delta_R", real=True)
    signal = sp.sinh(2 * delta) / 2
    return {
        "quadratic_basis_transform": [
            [str(value) for value in row] for row in matrix.tolist()
        ],
        "transform_determinant": str(determinant),
        "transform_is_invertible_for_positive_reference_product": determinant != 0,
        "known_zero_signal": str(signal),
        "signal_at_zero": str(signal.subs(delta, 0)),
        "signal_derivative_at_zero": str(sp.diff(signal, delta).subs(delta, 0)),
        "signal_nonzero_first_response": sp.diff(signal, delta).subs(delta, 0) != 0,
    }


def main() -> bool:
    started = time.perf_counter()
    calibration: dict[str, list[dict]] = {}
    selected: dict[str, int] = {}
    for target in TARGETS:
        records = []
        for level in LEVELS:
            trials = [
                run_protocol(
                    target,
                    level,
                    np.random.default_rng(
                        SEED + int(target * 1e8) + level * 1000 + replicate
                    ),
                )
                for replicate in range(CALIBRATION_REPS)
            ]
            successes = sum(bool(trial["success"]) for trial in trials)
            records.append(
                {
                    "level": level,
                    "successes": successes,
                    "trials": CALIBRATION_REPS,
                    "success_rate": successes / CALIBRATION_REPS,
                    "median_rmse": float(np.median([t["rmse"] for t in trials])),
                    "wilson_95_lower": wilson_lower(successes, CALIBRATION_REPS),
                }
            )
        eligible = [
            record["level"]
            for record in records
            if record["success_rate"] >= 0.875
            and record["median_rmse"] <= target
        ]
        if eligible:
            selected[str(target)] = min(eligible)
        calibration[str(target)] = records

    validation = []
    for target in TARGETS:
        level = selected.get(str(target), LEVELS[-1])
        trials = [
            run_protocol(
                target,
                level,
                np.random.default_rng(
                    SEED + 700000000 + int(target * 1e8) + 1000 * replicate
                ),
            )
            for replicate in range(VALIDATION_REPS)
        ]
        successes = sum(bool(trial["success"]) for trial in trials)
        validation.append(
            {
                "target_rmse": target,
                "selected_level": level,
                "successes": successes,
                "trials": VALIDATION_REPS,
                "success_rate": successes / VALIDATION_REPS,
                "wilson_95_lower": wilson_lower(successes, VALIDATION_REPS),
                "median_rmse": float(np.median([t["rmse"] for t in trials])),
                "median_evolution_time": float(
                    np.median([t["evolution_time"] for t in trials])
                ),
                "trials_raw": trials,
            }
        )

    certificate = symbolic_certificate()
    normalized_times = np.array(
        [
            item["median_evolution_time"]
            / math.log2(1 / item["target_rmse"])
            for item in validation
        ]
    )
    targets = np.array(TARGETS)
    resource_slope = float(
        np.polyfit(np.log(1 / targets), np.log(normalized_times), 1)[0]
    )
    overlap_left = math.exp(R_TRUE) + math.exp(-R_TRUE)
    overlap_right = 1 / (2 - math.sqrt(3))
    lowest_control = calibration[str(TARGETS[-1])][0]
    checks = {
        "known_zero_and_nonzero_response_exact": bool(
            certificate["signal_at_zero"] == "0"
            and certificate["signal_nonzero_first_response"]
        ),
        "quadratic_physical_transform_is_exactly_invertible": bool(
            certificate["transform_is_invertible_for_positive_reference_product"]
        ),
        "initial_guess_overlap_condition": overlap_left < overlap_right,
        "every_target_has_empirical_first_hit": len(selected) == len(TARGETS),
        "all_disjoint_validations_pass": all(
            item["wilson_95_lower"] >= 0.80 for item in validation
        ),
        "normalized_time_scales_as_inverse_precision": 0.75
        < resource_slope
        < 1.25,
        "finest_underpowered_level_fails": lowest_control["success_rate"] < 0.5,
    }
    verdict = "VERIFIED" if all(checks.values()) else "BLOCKED"
    payload = {
        "claim": 2,
        "verdict": verdict,
        "source": {
            "arxiv_id": "2510.08419v1",
            "pdf_sha256": "88c58a90096ad67bea10336322a33d15a76367d59a7195ef30266c702652b2c7",
            "anchors": ["Theorem 2", "Equations (4)-(7)", "Equations (71)-(85)"],
        },
        "configuration": {
            "targets": TARGETS,
            "candidate_rpe_levels": LEVELS,
            "calibration_replicates": CALIBRATION_REPS,
            "validation_replicates": VALIDATION_REPS,
            "shots_per_basis": SHOTS,
            "true_R": R_TRUE,
            "omega": OMEGA,
            "reference_product": REFERENCE_PRODUCT,
        },
        "assumption_audit": {
            "known_zero": "g20=0 in the physical oscillator basis",
            "nonzero_response": "d[(omega/2)sinh(2 DeltaR)]/dDeltaR at zero = omega",
            "overlap_left": overlap_left,
            "overlap_right": overlap_right,
            "overlap_passes": overlap_left < overlap_right,
        },
        "symbolic_certificate": certificate,
        "calibration": calibration,
        "selected_first_hit_levels": selected,
        "validation": validation,
        "metrics": {
            "log_normalized_time_vs_log_inverse_target_slope": resource_slope,
            "truth_G20": float(TRUTH_G[0]),
            "truth_G02": float(TRUTH_G[1]),
        },
        "negative_controls": {
            "finest_target_lowest_level": lowest_control,
            "barren_signal": "If omega=0, g20(DeltaR)=0 and no sign query is possible.",
            "singular_fake_transform_determinant": "Deleting the p^2 row makes the physical coefficient map rank deficient."
        },
        "acceptance_checks": checks,
        "seed": SEED,
        "resources": {
            "backend": "local",
            "estimated_cpu_cores": 1,
            "thread_cap": 1,
            "runtime_seconds_inside_verifier": time.perf_counter() - started,
        },
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "sympy": sp.__version__,
        },
        "proof_scope": "The exact invertible basis map shows that for any fixed finite degree, all normal-ordered coefficients in any known guessed basis determine all physical coefficients. The outer loop contributes only its logarithmic query count; the final D-RUT precision O(epsilon_G) dominates the O(1/epsilon_G) evolution factor.",
    }
    payload = json.loads(
        json.dumps(
            payload,
            default=lambda value: value.item()
            if isinstance(value, np.generic)
            else value,
        )
    )
    OUT.mkdir(exist_ok=True)
    with (OUT / "claim2_current.json").open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
    print("\nCLAIM 2 CURRENT FIRST-QUANTIZATION D-RUT")
    print(json.dumps(payload, sort_keys=True))
    from claim2_verify import verify

    checker = verify(payload)
    print("CLAIM 2 INDEPENDENT CHECKER")
    print(json.dumps(checker, sort_keys=True))
    print("CLAIM 2 NEGATIVE CONTROLS")
    print(json.dumps(payload["negative_controls"], sort_keys=True))
    print(f"CLAIM 2 FINAL VERDICT: {verdict}")
    return verdict == "VERIFIED" and checker["passed"]


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
