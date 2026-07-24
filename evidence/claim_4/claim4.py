"""Proof-level verifier for hierarchical covariance domination (Claim 4)."""

from __future__ import annotations

import json
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import sympy as sp


SEED = 404251008419
RANDOM_CASES = 64
MONTE_CARLO_SAMPLES = 50_000
IDENTITY_TOLERANCE = 2e-10
PSD_TOLERANCE = 2e-10
MONTE_CARLO_RELATIVE_TOLERANCE = 0.03


def covariance_objects(
    single_design: np.ndarray, coupling_design: np.ndarray
) -> dict[str, np.ndarray]:
    m1 = np.asarray(single_design, dtype=complex)
    m2 = np.asarray(coupling_design, dtype=complex)
    full = np.column_stack([m1, m2])
    a = m1.conj().T @ m1
    b = m1.conj().T @ m2
    d = m2.conj().T @ m2
    a_inv = np.linalg.inv(a)
    d_inv = np.linalg.inv(d)
    gram = full.conj().T @ full
    simultaneous = np.linalg.inv(gram)

    map_stage1 = a_inv @ m1.conj().T
    map_stage2_own = d_inv @ m2.conj().T
    map_stage1_into_stage2 = -d_inv @ b.conj().T @ map_stage1
    zero = np.zeros((m1.shape[1], m1.shape[0]), dtype=complex)
    hierarchical_map = np.block(
        [
            [map_stage1, zero],
            [map_stage1_into_stage2, map_stage2_own],
        ]
    )
    hierarchical = hierarchical_map @ hierarchical_map.conj().T

    c = b.conj().T @ a_inv @ b
    q = d - c
    z = np.vstack([a_inv @ b, -d_inv @ c])
    factor = z @ np.linalg.inv(q) @ z.conj().T
    return {
        "A": a,
        "B": b,
        "D": d,
        "G": gram,
        "Q": q,
        "Z": z,
        "simultaneous": simultaneous,
        "hierarchical": hierarchical,
        "difference": simultaneous - hierarchical,
        "factor": factor,
        "hierarchical_map": hierarchical_map,
    }


def exact_sympy_certificate() -> dict[str, object]:
    m1 = sp.Matrix(
        [
            [1, 0],
            [0, 1],
            [1, 1],
            [2, -1],
            [0, 1],
        ]
    )
    m2 = sp.Matrix(
        [
            [1, 1],
            [1, 0],
            [0, 1],
            [1, 2],
            [2, 1],
        ]
    )
    full = m1.row_join(m2)
    a = m1.T * m1
    b = m1.T * m2
    d = m2.T * m2
    gram = full.T * full
    simultaneous = gram.inv()
    a_inv = a.inv()
    d_inv = d.inv()
    stage1 = a_inv * m1.T
    stage2_from_stage1 = -d_inv * b.T * stage1
    stage2_own = d_inv * m2.T
    hierarchical_map = stage1.row_join(sp.zeros(2, 5)).col_join(
        stage2_from_stage1.row_join(stage2_own)
    )
    hierarchical = hierarchical_map * hierarchical_map.T
    c = b.T * a_inv * b
    q = d - c
    z = (a_inv * b).col_join(-d_inv * c)
    factor = z * q.inv() * z.T
    difference = simultaneous - hierarchical
    exact_zero = sp.simplify(difference - factor) == sp.zeros(4)
    leading_minors = [
        sp.factor(q[:index, :index].det())
        for index in range(1, q.rows + 1)
    ]
    return {
        "identity_exact": bool(exact_zero),
        "A": str(a),
        "B": str(b),
        "D": str(d),
        "Q": str(q),
        "Z": str(z),
        "difference": str(difference),
        "factor": str(factor),
        "Q_leading_principal_minors": [str(value) for value in leading_minors],
        "Q_positive_definite_by_sylvester": all(value > 0 for value in leading_minors),
        "B_nonzero": b != sp.zeros(*b.shape),
        "difference_nonzero": difference != sp.zeros(*difference.shape),
    }


def monte_carlo_check(
    objects: dict[str, np.ndarray], rng: np.random.Generator
) -> dict[str, float]:
    mapping = objects["hierarchical_map"]
    noise = (
        rng.normal(size=(mapping.shape[1], MONTE_CARLO_SAMPLES))
        + 1j * rng.normal(size=(mapping.shape[1], MONTE_CARLO_SAMPLES))
    ) / np.sqrt(2.0)
    errors = mapping @ noise
    empirical = errors @ errors.conj().T / MONTE_CARLO_SAMPLES
    relative = np.linalg.norm(
        empirical - objects["hierarchical"], ord="fro"
    ) / np.linalg.norm(objects["hierarchical"], ord="fro")
    return {
        "relative_frobenius_error": float(relative),
        "empirical_min_eigenvalue": float(
            np.linalg.eigvalsh(empirical).min()
        ),
    }


def correlated_noise_control() -> dict[str, float]:
    m1 = np.array([[1.0], [0.0]])
    m2 = np.array([[1.0], [1.0]])
    objects = covariance_objects(m1, m2)
    # Reuse the identical observation noise in the two stages, contrary to the
    # appendix's explicit independent-experiment assumption.
    a_inv = np.linalg.inv(m1.T @ m1)
    d_inv = np.linalg.inv(m2.T @ m2)
    b = m1.T @ m2
    stage1 = a_inv @ m1.T
    stage2 = d_inv @ m2.T - d_inv @ b.T @ stage1
    correlated_map = np.vstack([stage1, stage2])
    correlated_covariance = correlated_map @ correlated_map.T
    difference = objects["simultaneous"].real - correlated_covariance
    return {
        "minimum_eigenvalue_sim_minus_correlated_hierarchical": float(
            np.linalg.eigvalsh(difference).min()
        ),
        "determinant_sim_minus_correlated_hierarchical": float(
            np.linalg.det(difference)
        ),
    }


def main() -> bool:
    started = time.perf_counter()
    rng = np.random.default_rng(SEED)
    exact = exact_sympy_certificate()

    strict_m1 = np.array(
        [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0], [2.0, -1.0], [0.0, 1.0]]
    )
    strict_m2 = np.array(
        [[1.0, 1.0], [1.0, 0.0], [0.0, 1.0], [1.0, 2.0], [2.0, 1.0]]
    )
    strict = covariance_objects(strict_m1, strict_m2)
    strict_identity_residual = float(
        np.linalg.norm(strict["difference"] - strict["factor"], ord="fro")
    )
    strict_min_eigenvalue = float(
        np.linalg.eigvalsh(strict["difference"]).min()
    )
    strict_trace_improvement = float(np.trace(strict["difference"]).real)

    orthogonal_m1 = np.array([[1.0], [0.0]])
    orthogonal_m2 = np.array([[0.0], [1.0]])
    equality = covariance_objects(orthogonal_m1, orthogonal_m2)
    equality_norm = float(np.linalg.norm(equality["difference"], ord="fro"))

    worst_identity_residual = 0.0
    worst_min_eigenvalue = float("inf")
    tested_dimensions: list[dict[str, int]] = []
    for case in range(RANDOM_CASES):
        single_parameters = 1 + case % 3
        coupling_parameters = 1 + (case // 3) % 3
        observations = single_parameters + coupling_parameters + 3
        while True:
            m1 = rng.normal(size=(observations, single_parameters))
            m2 = rng.normal(size=(observations, coupling_parameters))
            if np.linalg.matrix_rank(np.column_stack([m1, m2])) == (
                single_parameters + coupling_parameters
            ):
                break
        objects = covariance_objects(m1, m2)
        residual = np.linalg.norm(
            objects["difference"] - objects["factor"], ord="fro"
        )
        minimum = np.linalg.eigvalsh(objects["difference"]).min()
        worst_identity_residual = max(worst_identity_residual, float(residual))
        worst_min_eigenvalue = min(worst_min_eigenvalue, float(minimum))
        tested_dimensions.append(
            {
                "observations": observations,
                "single_parameters": single_parameters,
                "coupling_parameters": coupling_parameters,
            }
        )

    monte_carlo = monte_carlo_check(strict, rng)
    control = correlated_noise_control()
    acceptance_checks = {
        "exact_rational_matrix_identity": exact["identity_exact"],
        "schur_complement_positive_definite": exact[
            "Q_positive_definite_by_sylvester"
        ],
        "strict_correlated_block_case_improves_total_variance": (
            strict_trace_improvement > 1e-6
        ),
        "strict_case_factor_identity": (
            strict_identity_residual < IDENTITY_TOLERANCE
        ),
        "strict_case_difference_is_psd": (
            strict_min_eigenvalue > -PSD_TOLERANCE
        ),
        "orthogonal_blocks_reproduce_historical_equality": (
            equality_norm < IDENTITY_TOLERANCE
        ),
        "random_full_rank_matrix_certificates": (
            worst_identity_residual < IDENTITY_TOLERANCE
            and worst_min_eigenvalue > -PSD_TOLERANCE
        ),
        "monte_carlo_matches_hierarchical_covariance": (
            monte_carlo["relative_frobenius_error"]
            < MONTE_CARLO_RELATIVE_TOLERANCE
        ),
        "correlated_noise_control_breaks_domination": (
            control[
                "minimum_eigenvalue_sim_minus_correlated_hierarchical"
            ]
            < -0.05
        ),
    }
    verdict = "VERIFIED" if all(acceptance_checks.values()) else "BLOCKED"
    payload: dict[str, object] = {
        "claim": 4,
        "verdict": verdict,
        "proof_statement": (
            "For full-column-rank [M1 M2] with independent unit-covariance "
            "noise in the two hierarchical stages, Cov_sim-Cov_hier = "
            "Z Q^{-1} Z^dagger is positive semidefinite, where "
            "Q=D-B^dagger A^{-1}B and "
            "Z=[A^{-1}B; -D^{-1}B^dagger A^{-1}B]."
        ),
        "source": {
            "arxiv_id": "2510.08419v1",
            "pdf_sha256": (
                "88c58a90096ad67bea10336322a33d15a76367d59a7195ef30266c702652b2c7"
            ),
            "anchors": [
                "Section 4.1",
                "Appendix A",
                "Equations (92)-(108)",
            ],
        },
        "assumptions": [
            "A=M1^dagger M1 and D=M2^dagger M2 are positive definite",
            "G=[M1 M2]^dagger[M1 M2] is positive definite",
            "stage-1 and stage-2 hierarchical measurement noises are independent",
            "the compared observation noises have equal isotropic variance",
        ],
        "seed": SEED,
        "exact_symbolic_certificate": exact,
        "metrics": {
            "strict_identity_residual": strict_identity_residual,
            "strict_difference_min_eigenvalue": strict_min_eigenvalue,
            "strict_trace_improvement": strict_trace_improvement,
            "orthogonal_equality_difference_norm": equality_norm,
            "random_cases": RANDOM_CASES,
            "random_worst_identity_residual": worst_identity_residual,
            "random_worst_min_eigenvalue": worst_min_eigenvalue,
            "monte_carlo_samples": MONTE_CARLO_SAMPLES,
            **monte_carlo,
        },
        "negative_control": control,
        "acceptance_checks": acceptance_checks,
        "resources": {
            "backend": "local",
            "estimated_cpu_cores": 1,
            "thread_cap": 1,
            "host_visible_cpu_allocation": 8,
            "runtime_seconds_inside_verifier": time.perf_counter() - started,
        },
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "sympy": sp.__version__,
        },
        "tested_dimensions": tested_dimensions,
    }
    artifact_dir = (
        Path(__file__).resolve().parents[2]
        / ".openresearch"
        / "artifacts"
        / "claim_4"
        / "generated"
    )
    artifact_dir.mkdir(parents=True, exist_ok=True)
    raw_path = artifact_dir / "raw_results.json"
    with raw_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")

    print("\n" + "=" * 78)
    print("CLAIM 4 COVARIANCE PROOF RESULT")
    print("=" * 78)
    print(json.dumps(payload, sort_keys=True))
    checker = subprocess.run(
        [sys.executable, str(Path(__file__).with_name("claim4_verify.py")), str(raw_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    print("CLAIM 4 INDEPENDENT CHECKER")
    print(checker.stdout.strip())
    print("CLAIM 4 NEGATIVE CONTROL")
    print(json.dumps(control, sort_keys=True))
    print(f"CLAIM 4 FINAL VERDICT: {verdict}")
    return verdict == "VERIFIED" and checker.returncode == 0


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
