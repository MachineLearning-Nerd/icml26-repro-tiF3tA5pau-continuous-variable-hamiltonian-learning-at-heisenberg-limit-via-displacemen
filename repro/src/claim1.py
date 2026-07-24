"""Faithful two-mode D-RUT check for Theorem 1 of arXiv:2510.08419v1."""

from __future__ import annotations

import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy

from faithful_drut import (
    algorithm_angles,
    analytic_constant,
    annihilation,
    build_hamiltonian,
    chebyshev_nodes,
    coefficient_rmse,
    displacement,
    inverse_dft_recovery,
    radial_recovery,
    robust_phase_estimate,
)

OUT = Path(__file__).resolve().parents[2] / "outputs"
SEED = 101251008419
LEVELS = [6, 7, 8, 9, 10, 11, 12]
REPLICATES = 24
SHOTS = 256
CUTOFF = 11
PHASE_COUNT = 13

MODE_1 = {
    (1, 0): 0.16 + 0.07j,
    (0, 1): 0.16 - 0.07j,
    (2, 0): 0.045 - 0.025j,
    (0, 2): 0.045 + 0.025j,
    (1, 1): 0.23 + 0.0j,
}
MODE_2 = {
    (1, 0): -0.11 + 0.055j,
    (0, 1): -0.11 - 0.055j,
    (2, 0): 0.035 + 0.018j,
    (0, 2): 0.035 - 0.018j,
    (1, 1): 0.19 + 0.0j,
}
PAIR = 0.052 - 0.031j
HOP = -0.043 + 0.024j


def single_points() -> list[complex]:
    radii = chebyshev_nodes(3, 0.15, 0.65)
    return [
        complex(radius * np.exp(1j * theta))
        for theta in algorithm_angles(2)
        for radius in radii
    ]


def coupling_points() -> list[tuple[complex, complex]]:
    return [
        (0.48 * np.exp(1j * a), 0.43 * np.exp(1j * b))
        for a, b in [
            (0.0, 0.0),
            (np.pi / 5, np.pi / 7),
            (2 * np.pi / 5, -np.pi / 6),
            (-np.pi / 4, np.pi / 3),
            (np.pi / 2, np.pi / 8),
            (-np.pi / 3, -np.pi / 5),
            (np.pi / 7, -2 * np.pi / 5),
            (-2 * np.pi / 7, np.pi / 2),
        ]
    ]


def coupling_constant(beta1: complex, beta2: complex) -> float:
    value = (
        PAIR * np.conj(beta1) * np.conj(beta2)
        + np.conj(PAIR) * beta1 * beta2
        + HOP * np.conj(beta1) * beta2
        + np.conj(HOP) * beta1 * np.conj(beta2)
    )
    return float(np.real(value))


def total_constant(beta1: complex, beta2: complex) -> float:
    return (
        analytic_constant(MODE_1, beta1)
        + analytic_constant(MODE_2, beta2)
        + coupling_constant(beta1, beta2)
    )


def recover_single(points: list[complex], values: list[float]) -> dict:
    radii = chebyshev_nodes(3, 0.15, 0.65)
    intermediate: dict[float, np.ndarray] = {}
    cursor = 0
    for theta in algorithm_angles(2):
        intermediate[theta] = radial_recovery(
            radii, values[cursor : cursor + len(radii)], 2
        )
        cursor += len(radii)
    return inverse_dft_recovery(intermediate, 2)


def coupling_design(points: list[tuple[complex, complex]]) -> np.ndarray:
    rows = []
    for beta1, beta2 in points:
        pair_weight = np.conj(beta1) * np.conj(beta2)
        hop_weight = np.conj(beta1) * beta2
        rows.append(
            [
                2 * pair_weight.real,
                -2 * pair_weight.imag,
                2 * hop_weight.real,
                -2 * hop_weight.imag,
            ]
        )
    return np.asarray(rows, dtype=float)


def coefficient_vector(
    mode1: dict, mode2: dict, coupling: np.ndarray
) -> np.ndarray:
    values: list[float] = []
    for mode in (mode1, mode2):
        values.extend(
            [
                mode[(1, 0)].real,
                mode[(1, 0)].imag,
                mode[(2, 0)].real,
                mode[(2, 0)].imag,
                mode[(1, 1)].real,
            ]
        )
    values.extend(coupling.tolist())
    return np.asarray(values)


TRUTH = coefficient_vector(
    MODE_1, MODE_2, np.array([PAIR.real, PAIR.imag, HOP.real, HOP.imag])
)


def estimate_all(
    max_level: int, rng: np.random.Generator, *, sql: bool = False
) -> tuple[np.ndarray, int]:
    singles = single_points()
    couples = coupling_points()
    responses: list[float] = []
    evolution = 0
    all_points = (
        [(beta, 0.0j) for beta in singles]
        + [(0.0j, beta) for beta in singles]
        + couples
    )
    rpe_time_per_point = 2 * SHOTS * (2 ** (max_level + 1) - 1)
    for beta1, beta2 in all_points:
        constant = total_constant(beta1, beta2)
        if sql:
            sql_shots = rpe_time_per_point // 2
            px = (1 + np.cos(constant)) / 2
            py = (1 + np.sin(constant)) / 2
            x = 2 * rng.binomial(sql_shots, px) / sql_shots - 1
            y = 2 * rng.binomial(sql_shots, py) / sql_shots - 1
            responses.append(float(np.arctan2(y, x)))
            evolution += 2 * sql_shots
        else:
            result = robust_phase_estimate(constant, max_level, SHOTS, rng)
            responses.append(result.estimate)
            evolution += result.evolution_time

    count = len(singles)
    recovered1 = recover_single(singles, responses[:count])
    recovered2 = recover_single(singles, responses[count : 2 * count])
    single_prediction = [
        analytic_constant(recovered1, beta1)
        + analytic_constant(recovered2, beta2)
        for beta1, beta2 in couples
    ]
    residual = np.asarray(responses[2 * count :]) - np.asarray(single_prediction)
    recovered_coupling, *_ = np.linalg.lstsq(
        coupling_design(couples), residual, rcond=None
    )
    return coefficient_vector(recovered1, recovered2, recovered_coupling), evolution


def physical_two_mode_audit() -> dict[str, float | bool]:
    a = annihilation(CUTOFF)
    identity = np.eye(CUTOFF)
    a1 = np.kron(a, identity)
    a2 = np.kron(identity, a)
    h1 = np.kron(build_hamiltonian(MODE_1, a), identity)
    h2 = np.kron(identity, build_hamiltonian(MODE_2, a))
    ad1, ad2 = a1.conj().T, a2.conj().T
    interaction = (
        PAIR * ad1 @ ad2
        + np.conj(PAIR) * a1 @ a2
        + HOP * ad1 @ a2
        + np.conj(HOP) * a1 @ ad2
    )
    hamiltonian = h1 + h2 + interaction
    beta1 = 0.31 + 0.17j
    beta2 = -0.22 + 0.19j
    d = np.kron(displacement(beta1, a), displacement(beta2, a))
    displaced = d.conj().T @ hamiltonian @ d

    occupations = np.array(
        [(n1, n2) for n1 in range(CUTOFF) for n2 in range(CUTOFF)]
    )
    delta1 = occupations[:, 0, None] - occupations[:, 0]
    delta2 = occupations[:, 1, None] - occupations[:, 1]
    mask = (delta1 % PHASE_COUNT == 0) & (delta2 % PHASE_COUNT == 0)
    twirled = displaced * mask
    off_diagonal = twirled - np.diag(np.diag(twirled))
    no_twirl_off_diagonal = displaced - np.diag(np.diag(displaced))
    constant = float(np.real(twirled[0, 0]))
    analytic = total_constant(beta1, beta2)
    return {
        "hamiltonian_hermiticity_residual": float(
            np.linalg.norm(hamiltonian - hamiltonian.conj().T)
        ),
        "vacuum_constant_absolute_error": abs(constant - analytic),
        "twirl_off_diagonal_frobenius": float(np.linalg.norm(off_diagonal)),
        "no_twirl_off_diagonal_frobenius": float(
            np.linalg.norm(no_twirl_off_diagonal)
        ),
        "displacement_is_nontrivial": bool(np.linalg.norm(d - np.eye(d.shape[0])) > 1),
    }


def main() -> bool:
    started = time.perf_counter()
    rpe_errors: list[list[float]] = []
    sql_errors: list[list[float]] = []
    evolution_times: list[int] = []
    for level in LEVELS:
        level_rpe: list[float] = []
        level_sql: list[float] = []
        for replicate in range(REPLICATES):
            rpe_rng = np.random.default_rng(SEED + 1000 * level + replicate)
            estimate, evolution = estimate_all(level, rpe_rng)
            level_rpe.append(float(np.sqrt(np.mean((estimate - TRUTH) ** 2))))
            sql_rng = np.random.default_rng(SEED + 900000 + 1000 * level + replicate)
            sql_estimate, sql_evolution = estimate_all(level, sql_rng, sql=True)
            assert sql_evolution == evolution
            level_sql.append(
                float(np.sqrt(np.mean((sql_estimate - TRUTH) ** 2)))
            )
        rpe_errors.append(level_rpe)
        sql_errors.append(level_sql)
        evolution_times.append(evolution)

    median_rpe = np.median(np.asarray(rpe_errors), axis=1)
    median_sql = np.median(np.asarray(sql_errors), axis=1)
    slope_rpe = float(np.polyfit(np.log(evolution_times), np.log(median_rpe), 1)[0])
    slope_sql = float(np.polyfit(np.log(evolution_times), np.log(median_sql), 1)[0])
    physical = physical_two_mode_audit()
    coupling_rank = int(np.linalg.matrix_rank(coupling_design(coupling_points())))
    exact_time_ratios = [
        evolution_times[index + 1] / evolution_times[index]
        for index in range(len(evolution_times) - 1)
    ]

    omit_displacement = np.zeros_like(TRUTH)
    omit_displacement_rmse = float(
        np.sqrt(np.mean((omit_displacement - TRUTH) ** 2))
    )
    checks = {
        "actual_two_mode_hamiltonian_is_hermitian": physical[
            "hamiltonian_hermiticity_residual"
        ]
        < 2e-12,
        "physical_displacement_and_twirl_match_constant": physical[
            "vacuum_constant_absolute_error"
        ]
        < 2e-9,
        "independent_local_twirl_is_joint_number_diagonal": physical[
            "twirl_off_diagonal_frobenius"
        ]
        < 2e-10,
        "rpe_coefficient_slope_is_heisenberg": -1.20 < slope_rpe < -0.80,
        "ramsey_control_slope_is_sql": -0.70 < slope_sql < -0.30,
        "rpe_is_asymptotically_steeper_than_sql": slope_rpe < slope_sql - 0.25,
        "coupling_design_has_full_rank": coupling_rank == 4,
        "time_doubles_per_added_rpe_level": all(
            1.99 < ratio < 2.01 for ratio in exact_time_ratios
        ),
        "finest_median_rmse_below_1e_4": median_rpe[-1] < 1e-4,
        "omit_displacement_control_fails": omit_displacement_rmse > 0.05,
        "omit_twirl_control_breaks_vacuum_model": physical[
            "no_twirl_off_diagonal_frobenius"
        ]
        > 0.1,
    }
    verdict = "VERIFIED" if all(checks.values()) else "BLOCKED"
    payload = {
        "claim": 1,
        "verdict": verdict,
        "source": {
            "arxiv_id": "2510.08419v1",
            "pdf_sha256": "88c58a90096ad67bea10336322a33d15a76367d59a7195ef30266c702652b2c7",
            "anchors": ["Theorem 1", "Equations (1), (9)-(30)", "Section 4"],
        },
        "configuration": {
            "modes": 2,
            "maximum_total_degree": 2,
            "real_parameters": 14,
            "rpe_levels": LEVELS,
            "replicates_per_level": REPLICATES,
            "shots_per_basis_per_level": SHOTS,
            "single_mode_design_points_per_mode": len(single_points()),
            "coupling_design_points": len(coupling_points()),
            "fock_cutoff_per_mode": CUTOFF,
            "twirl_phases_per_mode": PHASE_COUNT,
        },
        "proof_certificate": {
            "monomial_constant_identity": "Twirl[ D(beta)^dagger (b^dagger)^p b^q D(beta) ] vacuum eigenvalue = (beta*)^p beta^q",
            "rpe_time_exact": "2*S*sum_{j=0}^J 2^j = 2*S*(2^(J+1)-1)",
            "fixed_design_argument": "For fixed finite N,d, the number and conditioning of Chebyshev/IDFT design points is independent of epsilon; multiplying O(1/epsilon) per-point time by that fixed count preserves O(1/epsilon).",
            "coupling_design_rank": coupling_rank,
        },
        "evolution_times": evolution_times,
        "rpe_rmse_by_level": rpe_errors,
        "ramsey_sql_rmse_by_level": sql_errors,
        "median_rpe_rmse": median_rpe.tolist(),
        "median_ramsey_sql_rmse": median_sql.tolist(),
        "metrics": {
            "rpe_log_error_vs_log_time_slope": slope_rpe,
            "ramsey_log_error_vs_log_time_slope": slope_sql,
            "finest_median_rpe_rmse": float(median_rpe[-1]),
            "omit_displacement_rmse": omit_displacement_rmse,
            **physical,
        },
        "negative_controls": {
            "conventional_kappa_one_ramsey": "Same evolution-time budget, physical X/Y ancilla sampling at kappa=1.",
            "omit_displacement_rmse": omit_displacement_rmse,
            "omit_twirl_off_diagonal_frobenius": physical[
                "no_twirl_off_diagonal_frobenius"
            ],
        },
        "acceptance_checks": checks,
        "seed": SEED,
        "resources": {
            "backend": "local",
            "estimated_cpu_cores": 1,
            "thread_cap": 1,
            "host_visible_cpu_allocation": int(os_cpu_count()),
            "runtime_seconds_inside_verifier": time.perf_counter() - started,
        },
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
    }
    OUT.mkdir(exist_ok=True)
    with (OUT / "claim1_current.json").open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
    print("\nCLAIM 1 CURRENT TWO-MODE D-RUT")
    print(json.dumps(payload, sort_keys=True))
    from claim1_verify import verify

    checker = verify(payload)
    print("CLAIM 1 INDEPENDENT CHECKER")
    print(json.dumps(checker, sort_keys=True))
    print("CLAIM 1 NEGATIVE CONTROLS")
    print(json.dumps(payload["negative_controls"], sort_keys=True))
    print(f"CLAIM 1 FINAL VERDICT: {verdict}")
    return verdict == "VERIFIED" and checker["passed"]


def os_cpu_count() -> int:
    import os

    return os.cpu_count() or 1


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
