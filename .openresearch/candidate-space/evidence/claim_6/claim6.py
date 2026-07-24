"""Claim 6: faithful single-mode Algorithm 1 verification."""

from __future__ import annotations

import json
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import scipy
from scipy.linalg import expm

import faithful_drut as F


SEED = 251008419
CUTOFF = 24
MAX_ORDER = 2
PHASE_COUNT = 29
RADIAL_INTERVAL = (0.15, 0.65)
RPE_MAX_LEVEL = 12
SHOTS_PER_BASIS = 256
RMSE_THRESHOLD = 2.5e-3
QUANTUM_CONSTANT_THRESHOLD = 2.0e-6
TWIRL_RESIDUAL_THRESHOLD = 2.0e-10


def serializable_coefficients(
    coefficients: F.CoefficientMap,
) -> dict[str, dict[str, float]]:
    return {
        f"{p},{q}": {"real": float(value.real), "imag": float(value.imag)}
        for (p, q), value in sorted(coefficients.items())
    }


def main() -> bool:
    started = time.perf_counter()
    rng = np.random.default_rng(SEED)
    coefficients: F.CoefficientMap = {
        (0, 1): 0.20 - 0.08j,
        (1, 0): 0.20 + 0.08j,
        (0, 2): 0.06 + 0.03j,
        (1, 1): 0.35 + 0.00j,
        (2, 0): 0.06 - 0.03j,
    }
    annihilation = F.annihilation(CUTOFF)
    hamiltonian = F.build_hamiltonian(coefficients, annihilation)
    hermiticity_residual = float(
        np.linalg.norm(hamiltonian - hamiltonian.conj().T, ord="fro")
    )

    radii = F.chebyshev_nodes(
        MAX_ORDER + 1, RADIAL_INTERVAL[0], RADIAL_INTERVAL[1]
    )
    angles = F.algorithm_angles(MAX_ORDER)
    measurements: list[dict[str, object]] = []
    responses_by_angle: dict[float, list[float]] = {
        angle: [] for angle in angles
    }
    betas: list[complex] = []
    responses: list[float] = []
    analytic_responses: list[float] = []
    maximum_constant_error = 0.0
    maximum_twirl_residual = 0.0
    total_evolution_time = 0
    total_shots = 0

    for theta in angles:
        for radius in radii:
            beta = complex(radius * np.exp(1j * theta))
            analytic = F.analytic_constant(coefficients, beta)
            quantum, twirl_residual, _ = F.drut_constant(
                hamiltonian, beta, annihilation, PHASE_COUNT
            )
            rpe = F.robust_phase_estimate(
                quantum, RPE_MAX_LEVEL, SHOTS_PER_BASIS, rng
            )
            maximum_constant_error = max(
                maximum_constant_error, abs(quantum - analytic)
            )
            maximum_twirl_residual = max(
                maximum_twirl_residual, twirl_residual
            )
            total_evolution_time += rpe.evolution_time
            total_shots += rpe.shots
            responses_by_angle[theta].append(rpe.estimate)
            betas.append(beta)
            responses.append(rpe.estimate)
            analytic_responses.append(analytic)
            measurements.append(
                {
                    "radius": float(radius),
                    "theta": theta,
                    "beta_real": beta.real,
                    "beta_imag": beta.imag,
                    "analytic_constant": analytic,
                    "fock_drut_constant": quantum,
                    "rpe_estimate": rpe.estimate,
                    "rpe_absolute_error": abs(rpe.estimate - quantum),
                    "twirl_off_diagonal_frobenius": twirl_residual,
                    "rpe_records": rpe.records,
                }
            )

    intermediate = {
        angle: F.radial_recovery(
            radii, responses_by_angle[angle], MAX_ORDER
        )
        for angle in angles
    }
    recovered = F.inverse_dft_recovery(intermediate, MAX_ORDER)
    production_rmse = F.coefficient_rmse(recovered, coefficients)

    checker_recovered, checker_condition = F.direct_design_checker(
        betas, responses, MAX_ORDER
    )
    checker_rmse = F.coefficient_rmse(checker_recovered, coefficients)
    production_checker_disagreement = F.coefficient_rmse(
        checker_recovered, recovered
    )

    # Negative control 1: omit displacement. Every response is then zero
    # because the chosen Hamiltonian has no constant term.
    zero_responses = [0.0] * len(radii)
    zero_intermediate = {
        angle: F.radial_recovery(radii, zero_responses, MAX_ORDER)
        for angle in angles
    }
    zero_recovered = F.inverse_dft_recovery(
        zero_intermediate, MAX_ORDER
    )
    no_displacement_rmse = F.coefficient_rmse(
        zero_recovered, coefficients
    )

    # Negative control 2: omit the number-rotation twirl. The vacuum is no
    # longer an eigenstate and the scalar phase model used by RPE leaks.
    control_beta = complex(0.65 * np.exp(1j * np.pi / 3.0))
    displaced = F.displaced_hamiltonian(
        hamiltonian, control_beta, annihilation
    )
    vacuum_amplitude = expm(-1j * displaced)[0, 0]
    no_twirl_leakage = float(1.0 - abs(vacuum_amplitude) ** 2)

    acceptance_checks = {
        "hamiltonian_is_hermitian": hermiticity_residual < 1e-12,
        "fock_displacement_matches_polynomial_constant": (
            maximum_constant_error < QUANTUM_CONSTANT_THRESHOLD
        ),
        "discrete_twirl_is_number_diagonal": (
            maximum_twirl_residual < TWIRL_RESIDUAL_THRESHOLD
        ),
        "algorithm1_coefficient_rmse_below_threshold": (
            production_rmse < RMSE_THRESHOLD
        ),
        "independent_direct_design_rmse_below_threshold": (
            checker_rmse < RMSE_THRESHOLD
        ),
        "production_and_checker_agree": (
            production_checker_disagreement < RMSE_THRESHOLD
        ),
        "omit_displacement_control_fails_recovery": (
            no_displacement_rmse > 0.10
        ),
        "omit_twirl_control_breaks_vacuum_eigenphase_model": (
            no_twirl_leakage > 1e-4
        ),
    }
    verdict = (
        "VERIFIED" if all(acceptance_checks.values()) else "BLOCKED"
    )
    runtime_seconds = time.perf_counter() - started
    payload: dict[str, object] = {
        "claim": 6,
        "verdict": verdict,
        "scope": (
            "Exact Algorithm 1 path on a deterministic finite-Fock, "
            "single-mode degree-2 instance; no hardware claim."
        ),
        "source": {
            "arxiv_id": "2510.08419v1",
            "pdf_sha256": (
                "88c58a90096ad67bea10336322a33d15a76367d59a7195ef30266c702652b2c7"
            ),
            "anchors": [
                "Algorithm 1",
                "Eq. (2)",
                "Eqs. (24)-(30)",
                "Figure 1",
            ],
        },
        "seed": SEED,
        "configuration": {
            "fock_cutoff": CUTOFF,
            "max_order": MAX_ORDER,
            "phase_count": PHASE_COUNT,
            "radial_interval": list(RADIAL_INTERVAL),
            "rpe_max_level": RPE_MAX_LEVEL,
            "shots_per_basis_per_level": SHOTS_PER_BASIS,
            "radii": radii.tolist(),
            "angles": angles,
        },
        "resources": {
            "estimated_cpu_cores": 1,
            "thread_cap": 1,
            "backend": "local",
            "flavor": "local (no reserved flavor)",
            "host_visible_cpu_allocation": 8,
            "total_ancilla_shots": total_shots,
            "total_simulated_evolution_time": total_evolution_time,
            "runtime_seconds_inside_verifier": runtime_seconds,
        },
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "truth_coefficients": serializable_coefficients(coefficients),
        "recovered_coefficients": serializable_coefficients(recovered),
        "checker_coefficients": serializable_coefficients(checker_recovered),
        "metrics": {
            "hermiticity_residual": hermiticity_residual,
            "maximum_fock_vs_analytic_constant_error": maximum_constant_error,
            "maximum_twirl_off_diagonal_frobenius": maximum_twirl_residual,
            "algorithm1_coefficient_rmse": production_rmse,
            "independent_direct_design_rmse": checker_rmse,
            "production_checker_rmse": production_checker_disagreement,
            "independent_design_condition_number": checker_condition,
        },
        "negative_controls": {
            "omit_displacement_coefficient_rmse": no_displacement_rmse,
            "omit_twirl_vacuum_leakage_probability": no_twirl_leakage,
        },
        "acceptance_checks": acceptance_checks,
        "measurements": measurements,
    }

    artifact_dir = (
        Path(__file__).resolve().parents[2]
        / ".openresearch"
        / "artifacts"
        / "claim_6"
        / "generated"
    )
    artifact_dir.mkdir(parents=True, exist_ok=True)
    raw_path = artifact_dir / "raw_results.json"
    with raw_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")

    print("\n" + "=" * 78)
    print("CLAIM 6 FAITHFUL D-RUT RESULT")
    print("=" * 78)
    print(json.dumps(payload, sort_keys=True))
    checker = subprocess.run(
        [sys.executable, str(Path(__file__).with_name("claim6_verify.py")), str(raw_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    print("CLAIM 6 INDEPENDENT CHECKER")
    print(checker.stdout.strip())
    print("CLAIM 6 NEGATIVE CONTROLS")
    print(json.dumps(payload["negative_controls"], sort_keys=True))
    print(f"CLAIM 6 FINAL VERDICT: {verdict}")
    return verdict == "VERIFIED" and checker.returncode == 0


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
