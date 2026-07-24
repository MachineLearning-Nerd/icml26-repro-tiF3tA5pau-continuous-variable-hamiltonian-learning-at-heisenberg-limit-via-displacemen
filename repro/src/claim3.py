"""Claim 3: faithful D-RUT displacement-SPAM bound verification."""

from __future__ import annotations

import json
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import scipy
import sympy as sp

import faithful_drut as F


SEED = 303251008419
CUTOFF = 24
PHASE_COUNT = 29
MAX_ORDER = 2
RADIAL_INTERVAL = (0.15, 0.65)
DOMAIN_RADIUS = 0.70
PERTURBATION_MAGNITUDES = (1e-4, 3e-4, 1e-3, 3e-3, 1e-2)
DIRECTIONS_PER_MAGNITUDE = 12
BOUND_TOLERANCE = 1e-10
FOCK_RESPONSE_TOLERANCE = 2e-12
LINEAR_SLOPE_INTERVAL = (0.94, 1.06)


def parameter_vector() -> np.ndarray:
    # [Re(g10), Im(g10), Re(g20), Im(g20), g11]
    return np.array([0.20, 0.08, 0.06, -0.03, 0.35], dtype=float)


def coefficient_map(parameters: np.ndarray) -> F.CoefficientMap:
    a, b, c, d, e = parameters
    return {
        (1, 0): complex(a, b),
        (0, 1): complex(a, -b),
        (2, 0): complex(c, d),
        (0, 2): complex(c, -d),
        (1, 1): complex(e),
    }


def design_row(beta: complex) -> np.ndarray:
    x = float(beta.real)
    y = float(beta.imag)
    return np.array(
        [2.0 * x, 2.0 * y, 2.0 * (x * x - y * y), 4.0 * x * y, x * x + y * y]
    )


def response(parameters: np.ndarray, beta: complex) -> float:
    return float(design_row(beta) @ parameters)


def gradient(parameters: np.ndarray, beta: complex) -> np.ndarray:
    a, b, c, d, e = parameters
    x = float(beta.real)
    y = float(beta.imag)
    return np.array(
        [
            2.0 * a + (4.0 * c + 2.0 * e) * x + 4.0 * d * y,
            2.0 * b + 4.0 * d * x + (-4.0 * c + 2.0 * e) * y,
        ]
    )


def affine_gradient_parts(parameters: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    a, b, c, d, e = parameters
    offset = np.array([2.0 * a, 2.0 * b])
    linear = np.array(
        [[4.0 * c + 2.0 * e, 4.0 * d], [4.0 * d, -4.0 * c + 2.0 * e]]
    )
    return offset, linear


def exact_symbolic_certificate() -> dict[str, object]:
    x, y = sp.symbols("x y", real=True)
    a = sp.Rational(1, 5)
    b = sp.Rational(2, 25)
    c = sp.Rational(3, 50)
    d = -sp.Rational(3, 100)
    e = sp.Rational(7, 20)
    polynomial = (
        2 * a * x
        + 2 * b * y
        + 2 * c * (x**2 - y**2)
        + 4 * d * x * y
        + e * (x**2 + y**2)
    )
    expected_dx = 2 * a + (4 * c + 2 * e) * x + 4 * d * y
    expected_dy = 2 * b + 4 * d * x + (-4 * c + 2 * e) * y
    return {
        "polynomial": str(polynomial),
        "gradient_x": str(sp.diff(polynomial, x)),
        "gradient_y": str(sp.diff(polynomial, y)),
        "gradient_x_exact": sp.simplify(sp.diff(polynomial, x) - expected_dx) == 0,
        "gradient_y_exact": sp.simplify(sp.diff(polynomial, y) - expected_dy) == 0,
    }


def block_jacobian(parameters: np.ndarray, betas: list[complex]) -> np.ndarray:
    jacobian = np.zeros((len(betas), 2 * len(betas)))
    for index, beta in enumerate(betas):
        jacobian[index, 2 * index : 2 * index + 2] = gradient(parameters, beta)
    return jacobian


def perturbed_betas(
    betas: list[complex], perturbation: np.ndarray
) -> list[complex]:
    return [
        beta + complex(perturbation[2 * index], perturbation[2 * index + 1])
        for index, beta in enumerate(betas)
    ]


def main() -> bool:
    started = time.perf_counter()
    rng = np.random.default_rng(SEED)
    parameters = parameter_vector()
    coefficients = coefficient_map(parameters)
    annihilation = F.annihilation(CUTOFF)
    hamiltonian = F.build_hamiltonian(coefficients, annihilation)

    radii = F.chebyshev_nodes(
        MAX_ORDER + 1, RADIAL_INTERVAL[0], RADIAL_INTERVAL[1]
    )
    angles = F.algorithm_angles(MAX_ORDER)
    betas = [
        complex(radius * np.exp(1j * angle))
        for angle in angles
        for radius in radii
    ]
    design = np.vstack([design_row(beta) for beta in betas])
    singular_values = np.linalg.svd(design, compute_uv=False)
    sigma_min = float(singular_values[-1])
    pseudoinverse = np.linalg.pinv(design)
    pseudoinverse_norm = float(np.linalg.norm(pseudoinverse, ord=2))

    offset, linear = affine_gradient_parts(parameters)
    offset_norm = float(np.linalg.norm(offset))
    linear_norm = float(np.linalg.norm(linear, ord=2))
    lipschitz_upper = offset_norm + linear_norm * DOMAIN_RADIUS

    nominal_analytic = np.array([response(parameters, beta) for beta in betas])
    nominal_fock_values: list[float] = []
    maximum_twirl_residual = 0.0
    for beta in betas:
        constant, residual, _ = F.drut_constant(
            hamiltonian, beta, annihilation, PHASE_COUNT
        )
        nominal_fock_values.append(constant)
        maximum_twirl_residual = max(maximum_twirl_residual, residual)
    nominal_fock = np.array(nominal_fock_values)
    maximum_fock_response_error = float(
        np.max(np.abs(nominal_fock - nominal_analytic))
    )
    design_response_residual = float(
        np.max(np.abs(design @ parameters - nominal_analytic))
    )

    trials: list[dict[str, float | int]] = []
    median_errors: list[float] = []
    maximum_bound_ratio = 0.0
    maximum_perturbed_fock_error = maximum_fock_response_error
    all_points_within_domain = True
    paired_directions: list[np.ndarray] = []
    for _ in range(DIRECTIONS_PER_MAGNITUDE):
        direction = rng.normal(size=2 * len(betas))
        paired_directions.append(direction / np.linalg.norm(direction))
    for magnitude in PERTURBATION_MAGNITUDES:
        errors_for_magnitude: list[float] = []
        for direction_index, direction in enumerate(paired_directions):
            perturbation = magnitude * direction
            actual_betas = perturbed_betas(betas, perturbation)
            maximum_radius = max(abs(beta) for beta in actual_betas)
            all_points_within_domain &= maximum_radius <= DOMAIN_RADIUS
            actual_analytic = np.array(
                [response(parameters, beta) for beta in actual_betas]
            )
            actual_fock_list: list[float] = []
            for beta in actual_betas:
                constant, residual, _ = F.drut_constant(
                    hamiltonian, beta, annihilation, PHASE_COUNT
                )
                actual_fock_list.append(constant)
                maximum_twirl_residual = max(maximum_twirl_residual, residual)
            actual_fock = np.array(actual_fock_list)
            maximum_perturbed_fock_error = max(
                maximum_perturbed_fock_error,
                float(np.max(np.abs(actual_fock - actual_analytic))),
            )
            delta_response = actual_fock - nominal_fock
            delta_g = pseudoinverse @ delta_response
            spam_error = float(np.linalg.norm(delta_g))
            bound = float(lipschitz_upper / sigma_min * np.linalg.norm(perturbation))
            ratio = spam_error / bound
            maximum_bound_ratio = max(maximum_bound_ratio, ratio)
            errors_for_magnitude.append(spam_error)
            trials.append(
                {
                    "magnitude": magnitude,
                    "direction_index": direction_index,
                    "maximum_perturbed_radius": maximum_radius,
                    "response_delta_norm": float(np.linalg.norm(delta_response)),
                    "coefficient_spam_error_norm": spam_error,
                    "equation_43_bound": bound,
                    "bound_ratio": ratio,
                }
            )
        median_errors.append(float(np.median(errors_for_magnitude)))

    log_slope = float(
        np.polyfit(
            np.log(np.asarray(PERTURBATION_MAGNITUDES)),
            np.log(np.asarray(median_errors)),
            1,
        )[0]
    )

    # An adversarial infinitesimal direction for the complete local map. This
    # is used only as a negative control: arbitrarily shrinking L_C must make
    # the claimed upper bound fail.
    jacobian = block_jacobian(parameters, betas)
    composite = pseudoinverse @ jacobian
    _, _, right_vectors = np.linalg.svd(composite, full_matrices=False)
    control_magnitude = 1e-5
    control_perturbation = control_magnitude * right_vectors[0]
    control_betas = perturbed_betas(betas, control_perturbation)
    control_response = np.array(
        [response(parameters, beta) for beta in control_betas]
    )
    control_error = float(
        np.linalg.norm(pseudoinverse @ (control_response - nominal_analytic))
    )
    underestimated_lipschitz = lipschitz_upper / 1_000.0
    underestimated_bound = float(
        underestimated_lipschitz
        / sigma_min
        * np.linalg.norm(control_perturbation)
    )
    underestimated_ratio = control_error / underestimated_bound

    symbolic = exact_symbolic_certificate()
    acceptance_checks = {
        "symbolic_d_rut_response_gradient_is_exact": (
            symbolic["gradient_x_exact"] and symbolic["gradient_y_exact"]
        ),
        "algorithm1_combined_design_is_full_rank": (
            np.linalg.matrix_rank(design) == len(parameters) and sigma_min > 0.0
        ),
        "pseudoinverse_norm_equals_inverse_sigma_min": (
            abs(pseudoinverse_norm - 1.0 / sigma_min) < 1e-10
        ),
        "design_maps_physical_coefficients_to_d_rut_response": (
            design_response_residual < 1e-14
        ),
        "finite_fock_d_rut_matches_analytic_response": (
            maximum_perturbed_fock_error < FOCK_RESPONSE_TOLERANCE
        ),
        "discrete_twirl_is_number_diagonal": (
            maximum_twirl_residual < 2e-10
        ),
        "every_spam_trial_stays_in_certified_domain": all_points_within_domain,
        "every_spam_trial_satisfies_equation_43": (
            maximum_bound_ratio <= 1.0 + BOUND_TOLERANCE
        ),
        "small_spam_error_is_linear_in_perturbation_norm": (
            LINEAR_SLOPE_INTERVAL[0] <= log_slope <= LINEAR_SLOPE_INTERVAL[1]
        ),
        "underestimated_lipschitz_control_breaks_bound": (
            underestimated_ratio > 10.0
        ),
    }
    verdict = "VERIFIED" if all(acceptance_checks.values()) else "BLOCKED"
    payload: dict[str, object] = {
        "claim": 3,
        "verdict": verdict,
        "proof_statement": (
            "For the Algorithm 1 combined design K and every collection of "
            "displacement perturbations that remains in |beta|<=0.70, "
            "||K^+[C(beta+delta)-C(beta)]||_2 <= "
            "(L_C/sigma_min(K))||delta||_2, with the certified "
            "L_C=||h||_2+||H||_2*0.70 for grad C=h+H[x,y]."
        ),
        "source": {
            "arxiv_id": "2510.08419v1",
            "pdf_sha256": (
                "88c58a90096ad67bea10336322a33d15a76367d59a7195ef30266c702652b2c7"
            ),
            "anchors": [
                "Section 3.6",
                "Equations (36)-(46)",
            ],
        },
        "assumptions": [
            "single-mode Hermitian normal-ordered Hamiltonian of degree 2",
            "the combined Chebyshev/angle design K has full column rank",
            "nominal and perturbed displacements lie in |beta|<=0.70",
            "SPAM error is displacement miscalibration; RPE noise is excluded from delta_g_SPAM",
        ],
        "seed": SEED,
        "configuration": {
            "fock_cutoff": CUTOFF,
            "phase_count": PHASE_COUNT,
            "maximum_order": MAX_ORDER,
            "radial_interval": list(RADIAL_INTERVAL),
            "certified_domain_radius": DOMAIN_RADIUS,
            "radii": radii.tolist(),
            "angles": angles,
            "measurement_points": len(betas),
            "perturbation_magnitudes": list(PERTURBATION_MAGNITUDES),
            "directions_per_magnitude": DIRECTIONS_PER_MAGNITUDE,
        },
        "parameters": parameters.tolist(),
        "symbolic_certificate": symbolic,
        "lipschitz_certificate": {
            "gradient_offset": offset.tolist(),
            "gradient_linear_matrix": linear.tolist(),
            "gradient_offset_norm": offset_norm,
            "gradient_linear_spectral_norm": linear_norm,
            "domain_radius": DOMAIN_RADIUS,
            "certified_L_C": lipschitz_upper,
            "derivation": "sup ||h+Hz|| <= ||h|| + ||H|| sup||z||",
        },
        "design_certificate": {
            "shape": list(design.shape),
            "rank": int(np.linalg.matrix_rank(design)),
            "singular_values": singular_values.tolist(),
            "sigma_min": sigma_min,
            "pseudoinverse_spectral_norm": pseudoinverse_norm,
        },
        "metrics": {
            "maximum_nominal_fock_response_error": maximum_fock_response_error,
            "maximum_perturbed_fock_response_error": maximum_perturbed_fock_error,
            "maximum_twirl_off_diagonal_frobenius": maximum_twirl_residual,
            "design_response_residual": design_response_residual,
            "maximum_equation_43_bound_ratio": maximum_bound_ratio,
            "median_spam_errors": median_errors,
            "median_error_log_log_slope": log_slope,
            "spam_trials": len(trials),
        },
        "negative_control": {
            "description": "replace the derived L_C by L_C/1000",
            "adversarial_perturbation_norm": float(
                np.linalg.norm(control_perturbation)
            ),
            "coefficient_spam_error_norm": control_error,
            "underestimated_L_C": underestimated_lipschitz,
            "underestimated_equation_43_bound": underestimated_bound,
            "bound_ratio": underestimated_ratio,
        },
        "trials": trials,
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
            "scipy": scipy.__version__,
            "sympy": sp.__version__,
        },
    }
    artifact_dir = (
        Path(__file__).resolve().parents[2]
        / ".openresearch"
        / "artifacts"
        / "claim_3"
        / "generated"
    )
    artifact_dir.mkdir(parents=True, exist_ok=True)
    raw_path = artifact_dir / "raw_results.json"
    with raw_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")

    print("\n" + "=" * 78)
    print("CLAIM 3 FAITHFUL SPAM-BOUND RESULT")
    print("=" * 78)
    print(json.dumps(payload, sort_keys=True))
    checker = subprocess.run(
        [sys.executable, str(Path(__file__).with_name("claim3_verify.py")), str(raw_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    print("CLAIM 3 INDEPENDENT CHECKER")
    print(checker.stdout.strip())
    print("CLAIM 3 NEGATIVE CONTROL")
    print(json.dumps(payload["negative_control"], sort_keys=True))
    print(f"CLAIM 3 FINAL VERDICT: {verdict}")
    return verdict == "VERIFIED" and checker.returncode == 0


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
