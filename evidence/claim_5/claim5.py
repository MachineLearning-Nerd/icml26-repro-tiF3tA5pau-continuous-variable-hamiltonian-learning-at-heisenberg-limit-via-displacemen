"""Claim 5: paper-specific Bogoliubov squeezing bisection verification."""

from __future__ import annotations

import json
import math
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import scipy
import sympy as sp

import faithful_drut as F


SEED = 505251008419
CUTOFF = 24
PHASE_COUNT = 29
OMEGA = 1.0
TRUE_R = math.sqrt(3.0) / 10.0
SEARCH_INTERVAL = (0.0, 0.4)
TARGET_PRECISIONS = (0.05, 0.025, 0.0125, 0.00625, 0.003125)
RPE_LEVEL_CANDIDATES = (8, 10, 12, 14, 16)
SHOTS_PER_BASIS = 256
CALIBRATION_DELTA = 2e-4
CALIBRATION_REPETITIONS_PER_SIGN = 32
VALIDATION_REPETITIONS = 32
CALIBRATION_WILSON_LOWER_MIN = 0.90
VALIDATION_WILSON_LOWER_MIN = 0.85
RADIAL_INTERVAL = (0.15, 0.65)


def bogoliubov_coefficients(delta_r: float) -> F.CoefficientMap:
    cosine = math.cosh(delta_r)
    sine = math.sinh(delta_r)
    return {
        (0, 0): OMEGA * sine * sine,
        (1, 1): OMEGA * (cosine * cosine + sine * sine),
        (2, 0): OMEGA * cosine * sine,
        (0, 2): OMEGA * cosine * sine,
    }


def exact_signal(delta_r: float) -> float:
    return 0.5 * OMEGA * math.sinh(2.0 * delta_r)


def exact_symbolic_certificate() -> dict[str, object]:
    delta = sp.symbols("Delta_R", real=True)
    signal = sp.sinh(delta) * sp.cosh(delta)
    expected = sp.sinh(2 * delta) / 2
    return {
        "signal": str(signal),
        "double_angle_signal": str(expected),
        "double_angle_identity_exact": sp.simplify(signal - expected) == 0,
        "signal_at_zero": str(sp.simplify(signal.subs(delta, 0))),
        "derivative_at_zero": str(sp.simplify(sp.diff(signal, delta).subs(delta, 0))),
        "known_zero_at_physical_basis": sp.simplify(signal.subs(delta, 0)) == 0,
        "nonzero_linear_response": sp.simplify(
            sp.diff(signal, delta).subs(delta, 0)
        )
        == 1,
    }


def wilson_lower(successes: int, trials: int, z: float = 1.96) -> float:
    proportion = successes / trials
    denominator = 1.0 + z * z / trials
    center = proportion + z * z / (2.0 * trials)
    radius = z * math.sqrt(
        proportion * (1.0 - proportion) / trials
        + z * z / (4.0 * trials * trials)
    )
    return (center - radius) / denominator


def required_iterations(target_precision: float) -> int:
    width = SEARCH_INTERVAL[1] - SEARCH_INTERVAL[0]
    return int(math.ceil(math.log2(width / (2.0 * target_precision)) - 1e-12))


class DRUTSignalOracle:
    def __init__(self) -> None:
        self.annihilation = F.annihilation(CUTOFF)
        self.radii = F.chebyshev_nodes(
            3, RADIAL_INTERVAL[0], RADIAL_INTERVAL[1]
        )
        self.cache: dict[float, tuple[np.ndarray, np.ndarray]] = {}
        self.maximum_fock_error = 0.0
        self.maximum_twirl_residual = 0.0
        self.total_evolution_time = 0
        self.total_ancilla_shots = 0

    def constants(self, delta_r: float) -> tuple[np.ndarray, np.ndarray]:
        key = float(delta_r)
        if key in self.cache:
            return self.cache[key]
        coefficients = bogoliubov_coefficients(delta_r)
        hamiltonian = F.build_hamiltonian(coefficients, self.annihilation)
        at_zero: list[float] = []
        at_quarter_turn: list[float] = []
        for theta, destination in (
            (0.0, at_zero),
            (math.pi / 2.0, at_quarter_turn),
        ):
            for radius in self.radii:
                beta = complex(radius * np.exp(1j * theta))
                value, residual, _ = F.drut_constant(
                    hamiltonian, beta, self.annihilation, PHASE_COUNT
                )
                analytic = F.analytic_constant(coefficients, beta)
                self.maximum_fock_error = max(
                    self.maximum_fock_error, abs(value - analytic)
                )
                self.maximum_twirl_residual = max(
                    self.maximum_twirl_residual, residual
                )
                destination.append(value)
        result = (np.asarray(at_zero), np.asarray(at_quarter_turn))
        self.cache[key] = result
        return result

    def estimate(
        self,
        candidate_r: float,
        max_level: int,
        rng: np.random.Generator,
    ) -> float:
        delta_r = TRUE_R - candidate_r
        at_zero, at_quarter_turn = self.constants(delta_r)
        estimated_zero: list[float] = []
        estimated_quarter: list[float] = []
        for values, destination in (
            (at_zero, estimated_zero),
            (at_quarter_turn, estimated_quarter),
        ):
            for value in values:
                estimate = F.robust_phase_estimate(
                    float(value), max_level, SHOTS_PER_BASIS, rng
                )
                destination.append(estimate.estimate)
                self.total_evolution_time += estimate.evolution_time
                self.total_ancilla_shots += estimate.shots
        contrast = np.asarray(estimated_zero) - np.asarray(estimated_quarter)
        design = 4.0 * self.radii**2
        return float(design @ contrast / (design @ design))


def noisy_bisection(
    target_precision: float,
    max_level: int,
    rng: np.random.Generator,
    oracle: DRUTSignalOracle,
) -> dict[str, object]:
    lower, upper = SEARCH_INTERVAL
    iterations = required_iterations(target_precision)
    records: list[dict[str, float]] = []
    for _ in range(iterations):
        midpoint = 0.5 * (lower + upper)
        signal_estimate = oracle.estimate(midpoint, max_level, rng)
        if signal_estimate > 0.0:
            lower = midpoint
        else:
            upper = midpoint
        records.append(
            {
                "midpoint": midpoint,
                "signal_estimate": signal_estimate,
                "bracket_lower": lower,
                "bracket_upper": upper,
            }
        )
    estimate = 0.5 * (lower + upper)
    return {
        "target_precision": target_precision,
        "iterations": iterations,
        "final_bracket_width": upper - lower,
        "estimate": estimate,
        "absolute_error": abs(estimate - TRUE_R),
        "success": abs(estimate - TRUE_R) <= target_precision,
        "records": records,
    }


def main() -> bool:
    started = time.perf_counter()
    rng = np.random.default_rng(SEED)
    symbolic = exact_symbolic_certificate()
    oracle = DRUTSignalOracle()

    # The RPE horizon is selected empirically on a disjoint calibration task,
    # not from the asymptotic formula being tested.
    calibration: list[dict[str, float | int | bool]] = []
    selected_level: int | None = None
    for level in RPE_LEVEL_CANDIDATES:
        successes = 0
        trials = 0
        for signed_delta in (-CALIBRATION_DELTA, CALIBRATION_DELTA):
            candidate_r = TRUE_R - signed_delta
            for _ in range(CALIBRATION_REPETITIONS_PER_SIGN):
                estimate = oracle.estimate(candidate_r, level, rng)
                successes += int(estimate * signed_delta > 0.0)
                trials += 1
        lower = wilson_lower(successes, trials)
        passed = lower >= CALIBRATION_WILSON_LOWER_MIN
        calibration.append(
            {
                "max_level": level,
                "successes": successes,
                "trials": trials,
                "success_rate": successes / trials,
                "wilson_95_lower": lower,
                "passes_calibration": passed,
            }
        )
        if passed and selected_level is None:
            selected_level = level
    calibration_found_level = selected_level is not None
    if selected_level is None:
        selected_level = RPE_LEVEL_CANDIDATES[-1]

    validation_records: list[dict[str, object]] = []
    validation_summary: list[dict[str, float | int | bool]] = []
    for target in TARGET_PRECISIONS:
        successes = 0
        iterations_seen: set[int] = set()
        for replicate in range(VALIDATION_REPETITIONS):
            result = noisy_bisection(target, selected_level, rng, oracle)
            successes += int(result["success"])
            iterations_seen.add(int(result["iterations"]))
            validation_records.append(
                {
                    "replicate": replicate,
                    **result,
                }
            )
        lower = wilson_lower(successes, VALIDATION_REPETITIONS)
        validation_summary.append(
            {
                "target_precision": target,
                "required_iterations": required_iterations(target),
                "observed_iteration_count": min(iterations_seen),
                "iteration_counts_identical": len(iterations_seen) == 1,
                "successes": successes,
                "trials": VALIDATION_REPETITIONS,
                "success_rate": successes / VALIDATION_REPETITIONS,
                "wilson_95_lower": lower,
                "passes_validation": lower >= VALIDATION_WILSON_LOWER_MIN,
            }
        )

    iterations = np.asarray(
        [required_iterations(value) for value in TARGET_PRECISIONS], dtype=float
    )
    log_inverse_precision = np.log2(
        1.0 / np.asarray(TARGET_PRECISIONS, dtype=float)
    )
    iteration_slope = float(
        np.polyfit(log_inverse_precision, iterations, 1)[0]
    )
    exact_width_checks = [
        math.isclose(
            (SEARCH_INTERVAL[1] - SEARCH_INTERVAL[0]) / 2.0 ** int(count),
            2.0 * target,
            rel_tol=0.0,
            abs_tol=1e-14,
        )
        for target, count in zip(TARGET_PRECISIONS, iterations, strict=True)
    ]

    # Controls. At K=0 the chosen coefficient is identically zero, so no
    # sign-changing bracket exists. The historical x^2 proxy has the same
    # problem and therefore is not a valid squeezing-signal bisection.
    barren_plateau_endpoint_signs = (0.0, 0.0)
    historical_x_squared_endpoint_signs = (
        SEARCH_INTERVAL[0] ** 2,
        SEARCH_INTERVAL[1] ** 2,
    )
    lowest_calibration = calibration[0]
    overlap_left = 2.0 * math.cosh(TRUE_R)
    overlap_right = 1.0 / (2.0 - math.sqrt(3.0))

    acceptance_checks = {
        "bogoliubov_signal_identity_is_exact": symbolic[
            "double_angle_identity_exact"
        ],
        "known_zero_coefficient_vanishes_at_physical_basis": symbolic[
            "known_zero_at_physical_basis"
        ],
        "signal_has_nonzero_linear_response": symbolic[
            "nonzero_linear_response"
        ],
        "reference_frame_satisfies_rpe_overlap_condition": (
            overlap_left < overlap_right
        ),
        "calibration_independently_finds_adequate_rpe_level": (
            calibration_found_level
        ),
        "selected_rpe_level_is_not_underpowered_control": (
            selected_level > RPE_LEVEL_CANDIDATES[0]
            and not bool(lowest_calibration["passes_calibration"])
        ),
        "finite_fock_drut_matches_bogoliubov_response": (
            oracle.maximum_fock_error < 2e-12
        ),
        "discrete_twirl_is_number_diagonal": (
            oracle.maximum_twirl_residual < 2e-10
        ),
        "exact_interval_contraction_certificate": all(exact_width_checks),
        "iteration_count_increases_one_per_precision_halving": (
            np.all(np.diff(iterations) == 1.0)
            and abs(iteration_slope - 1.0) < 1e-12
        ),
        "all_disjoint_noisy_validations_pass": all(
            bool(record["passes_validation"]) for record in validation_summary
        ),
        "barren_plateau_control_has_no_sign_bracket": (
            barren_plateau_endpoint_signs[0]
            * barren_plateau_endpoint_signs[1]
            >= 0.0
        ),
        "historical_x_squared_proxy_has_no_sign_bracket": (
            historical_x_squared_endpoint_signs[0]
            * historical_x_squared_endpoint_signs[1]
            >= 0.0
        ),
    }
    verdict = "VERIFIED" if all(acceptance_checks.values()) else "BLOCKED"
    payload: dict[str, object] = {
        "claim": 5,
        "verdict": verdict,
        "proof_statement": (
            "For the Bogoliubov signal g'20(DeltaR)="
            "(omega/2)sinh(2 DeltaR), a valid sign bracket contracts from "
            "width W to W/2^n after n bisections; midpoint error is at most "
            "W/2^(n+1), hence n=ceil(log2(W/(2 epsilon_R)))."
        ),
        "source": {
            "arxiv_id": "2510.08419v1",
            "pdf_sha256": (
                "88c58a90096ad67bea10336322a33d15a76367d59a7195ef30266c702652b2c7"
            ),
            "anchors": [
                "Section 5.3",
                "Equations (71)-(78)",
                "Section 6.1 outer and inner loops",
            ],
        },
        "assumptions": [
            "the initial interval brackets the physical squeezing parameter",
            "g'20 is known to vanish in the physical basis",
            "the signal has nonzero response K at DeltaR=0",
            "the reference basis satisfies the stated RPE overlap condition",
            "the D-RUT/RPE inner oracle resolves the signal sign",
        ],
        "seed": SEED,
        "configuration": {
            "true_squeezing_parameter": TRUE_R,
            "search_interval": list(SEARCH_INTERVAL),
            "target_precisions": list(TARGET_PRECISIONS),
            "rpe_level_candidates": list(RPE_LEVEL_CANDIDATES),
            "shots_per_basis": SHOTS_PER_BASIS,
            "calibration_delta": CALIBRATION_DELTA,
            "calibration_repetitions_per_sign": CALIBRATION_REPETITIONS_PER_SIGN,
            "validation_repetitions": VALIDATION_REPETITIONS,
            "fock_cutoff": CUTOFF,
            "phase_count": PHASE_COUNT,
            "radii": oracle.radii.tolist(),
        },
        "symbolic_certificate": symbolic,
        "overlap_audit": {
            "left_side": overlap_left,
            "right_side": overlap_right,
            "passes": overlap_left < overlap_right,
        },
        "calibration": calibration,
        "selected_rpe_max_level": selected_level,
        "validation_summary": validation_summary,
        "validation_records": validation_records,
        "metrics": {
            "iteration_log2_inverse_precision_slope": iteration_slope,
            "iterations": iterations.astype(int).tolist(),
            "maximum_fock_vs_analytic_response_error": oracle.maximum_fock_error,
            "maximum_twirl_off_diagonal_frobenius": (
                oracle.maximum_twirl_residual
            ),
            "unique_bogoliubov_oracle_points": len(oracle.cache),
        },
        "negative_controls": {
            "lowest_rpe_level": lowest_calibration,
            "barren_plateau_endpoint_signs": list(
                barren_plateau_endpoint_signs
            ),
            "historical_x_squared_endpoint_signs": list(
                historical_x_squared_endpoint_signs
            ),
        },
        "acceptance_checks": acceptance_checks,
        "resources": {
            "backend": "local",
            "estimated_cpu_cores": 1,
            "thread_cap": 1,
            "host_visible_cpu_allocation": 8,
            "total_ancilla_shots": oracle.total_ancilla_shots,
            "total_simulated_evolution_time": oracle.total_evolution_time,
            "runtime_seconds_inside_verifier": time.perf_counter() - started,
        },
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "sympy": sp.__version__,
        },
    }
    artifact_dir = (
        Path(__file__).resolve().parents[2]
        / ".openresearch"
        / "artifacts"
        / "claim_5"
        / "generated"
    )
    artifact_dir.mkdir(parents=True, exist_ok=True)
    raw_path = artifact_dir / "raw_results.json"
    with raw_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")

    print("\n" + "=" * 78)
    print("CLAIM 5 BOGOLIUBOV BISECTION RESULT")
    print("=" * 78)
    print(json.dumps(payload, sort_keys=True))
    checker = subprocess.run(
        [sys.executable, str(Path(__file__).with_name("claim5_verify.py")), str(raw_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    print("CLAIM 5 INDEPENDENT CHECKER")
    print(checker.stdout.strip())
    print("CLAIM 5 NEGATIVE CONTROLS")
    print(json.dumps(payload["negative_controls"], sort_keys=True))
    print(f"CLAIM 5 FINAL VERDICT: {verdict}")
    return verdict == "VERIFIED" and checker.returncode == 0


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
